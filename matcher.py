"""
JobPilot matching engine.
Pipeline: hard filters -> keyword score -> semantic score -> weighted blend.
Only offers passing hard filters get the (paid) embedding call.
"""

import json
import math
import re
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone

# ---------- Config ----------

WEIGHTS = {
    "semantic": 0.50,
    "keyword": 0.35,
    "bonus": 0.15,
}
QUEUE_THRESHOLD = 0.75   # final_score above this -> review queue

# Normalize stack synonyms so "kubernetes" and "k8s" match
SYNONYMS = {
    "k8s": "kubernetes", "ms sentinel": "sentinel", "azure sentinel": "sentinel",
    "m365": "microsoft 365", "aws": "amazon web services", "gcp": "google cloud",
    "ci/cd": "cicd", "infosec": "cybersecurity", "cybersecurite": "cybersecurity",
}


def norm(term: str) -> str:
    t = term.lower().strip()
    return SYNONYMS.get(t, t)


# ---------- Hard filters ----------

@dataclass
class Profile:
    contract_wanted: list[str]
    locations_ok: list[str]
    hard_skills: list[str]
    target_roles: list[str]
    min_duration_months: int | None = None

    @classmethod
    def load(cls, db: sqlite3.Connection) -> "Profile":
        row = db.execute("SELECT * FROM profile WHERE id = 1").fetchone()
        return cls(
            contract_wanted=json.loads(row["contract_wanted"]),
            locations_ok=[c.lower() for c in json.loads(row["locations_ok"])],
            hard_skills=[norm(s) for s in json.loads(row["hard_skills"])],
            target_roles=[r.lower() for r in json.loads(row["target_roles"])],
            min_duration_months=row["min_duration_months"],
        )


def hard_filter(offer: sqlite3.Row, p: Profile) -> tuple[bool, str]:
    """Cheap knockout checks. Returns (pass, reason_if_failed)."""
    if offer["contract_type"] not in (*p.contract_wanted, "unknown"):
        return False, f"contract={offer['contract_type']}"

    city = (offer["city"] or "").lower()
    remote = offer["remote_policy"] or "unknown"
    location_ok = (
        remote == "full_remote"
        or "remote" in p.locations_ok and remote == "hybrid"
        or any(loc in city for loc in p.locations_ok)
        or not city  # unknown location: let it through, semantic will judge
    )
    if not location_ok:
        return False, f"location={city}/{remote}"

    if (p.min_duration_months and offer["duration_months"]
            and offer["duration_months"] < p.min_duration_months):
        return False, f"duration={offer['duration_months']}mo"

    return True, ""


# ---------- Keyword score ----------

def keyword_score(offer: sqlite3.Row, p: Profile) -> float:
    """Weighted overlap: skills in title count double vs description."""
    title = (offer["title"] or "").lower()
    desc = (offer["description"] or "").lower()
    tags = {norm(t) for t in json.loads(offer["stack_tags"] or "[]")}

    hits, weight_total = 0.0, 0.0
    for skill in p.hard_skills:
        weight_total += 1.0
        if skill in title or skill in tags:
            hits += 1.0
        elif re.search(rf"\b{re.escape(skill)}\b", desc):
            hits += 0.6

    role_hit = any(r in title for r in p.target_roles)
    base = hits / weight_total if weight_total else 0.0
    return min(1.0, base + (0.15 if role_hit else 0.0))


# ---------- Semantic score ----------

def cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    return dot / (na * nb) if na and nb else 0.0


def semantic_score(offer_text: str, profile_embedding: list[float],
                   embed_fn) -> float:
    """
    embed_fn: callable(text) -> list[float]
    Plug in voyage-3-lite, OpenAI text-embedding-3-small, or a local
    sentence-transformers model (all-MiniLM-L6-v2 runs fine on CPU).
    Truncate offer text: first 2000 chars carry the signal.
    """
    vec = embed_fn(offer_text[:2000])
    raw = cosine(vec, profile_embedding)
    # Cosine sims cluster in 0.3-0.8; stretch to a usable 0-1 range
    return max(0.0, min(1.0, (raw - 0.3) / 0.5))


# ---------- Bonus score ----------

def bonus_score(offer: sqlite3.Row) -> float:
    score = 0.0
    if offer["posted_at"]:
        age_days = (datetime.now(timezone.utc)
                    - datetime.fromisoformat(offer["posted_at"])).days
        if age_days <= 3:
            score += 0.5          # fresh offers = less competition
        elif age_days <= 7:
            score += 0.25
    if offer["remote_policy"] in ("hybrid", "full_remote"):
        score += 0.25
    if offer["salary_min"]:
        score += 0.25             # transparency signal, serious employer
    return min(1.0, score)


# ---------- CV variant picker ----------

def pick_variant(db: sqlite3.Connection, offer: sqlite3.Row) -> int | None:
    """Pick the CV variant whose keywords best overlap the offer."""
    text = f"{offer['title']} {offer['description'] or ''}".lower()
    best_id, best_hits = None, 0
    for v in db.execute("SELECT id, keywords FROM cv_variants"):
        hits = sum(1 for kw in json.loads(v["keywords"] or "[]")
                   if norm(kw) in text)
        if hits > best_hits:
            best_id, best_hits = v["id"], hits
    return best_id


# ---------- Main scoring pass ----------

def score_new_offers(db: sqlite3.Connection, embed_fn) -> int:
    """Score all offers without a match_scores row. Returns count queued."""
    p = Profile.load(db)
    prow = db.execute("SELECT embedding FROM profile WHERE id = 1").fetchone()
    profile_vec = json.loads(prow["embedding"])

    queued = 0
    unscored = db.execute("""
        SELECT o.* FROM offers o
        LEFT JOIN match_scores m ON m.offer_id = o.id
        WHERE m.offer_id IS NULL
    """).fetchall()

    for offer in unscored:
        ok, reason = hard_filter(offer, p)
        if not ok:
            db.execute("""INSERT INTO match_scores
                (offer_id, hard_filter_pass, hard_filter_reason, final_score)
                VALUES (?, 0, ?, 0)""", (offer["id"], reason))
            continue

        kw = keyword_score(offer, p)
        sem = semantic_score(
            f"{offer['title']}\n{offer['description'] or ''}",
            profile_vec, embed_fn)
        bon = bonus_score(offer)
        final = (WEIGHTS["semantic"] * sem
                 + WEIGHTS["keyword"] * kw
                 + WEIGHTS["bonus"] * bon)

        variant = pick_variant(db, offer)
        db.execute("""INSERT INTO match_scores
            (offer_id, hard_filter_pass, semantic_score, keyword_score,
             bonus_score, final_score, best_cv_variant_id)
            VALUES (?, 1, ?, ?, ?, ?, ?)""",
            (offer["id"], sem, kw, bon, final, variant))

        if final >= QUEUE_THRESHOLD:
            db.execute("""INSERT OR IGNORE INTO applications
                (offer_id, kind, status) VALUES (?, 'offer', 'queued')""",
                (offer["id"],))
            queued += 1

    db.commit()
    return queued

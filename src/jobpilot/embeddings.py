"""Local embeddings via sentence-transformers (all-MiniLM-L6-v2), lazy-loaded.

Provides the embed_fn(text) -> list[float] that matcher.semantic_score expects,
and caches the profile embedding into profile.embedding as JSON (matcher reads it
back with json.loads, so it must be a JSON string).
"""

from __future__ import annotations

import json
import sqlite3
from collections.abc import Callable
from functools import lru_cache
from typing import TYPE_CHECKING

from jobpilot.config import get_settings
from jobpilot.logging_conf import get_logger

if TYPE_CHECKING:
    from sentence_transformers import SentenceTransformer

log = get_logger("embeddings")

EmbedFn = Callable[[str], list[float]]


@lru_cache(maxsize=1)
def _model() -> SentenceTransformer:
    """Load the model once per process (heavy import kept out of module load)."""
    from sentence_transformers import SentenceTransformer

    name = get_settings().embed_model
    log.info("loading embedding model %s", name)
    return SentenceTransformer(name)


@lru_cache(maxsize=1)
def get_embed_fn() -> EmbedFn:
    model = _model()

    def embed(text: str) -> list[float]:
        vec = model.encode(text or "", normalize_embeddings=False)
        return [float(x) for x in vec]

    return embed


def _col(row: sqlite3.Row, name: str):
    return row[name] if name in row.keys() else None


def _as_list(row: sqlite3.Row, col: str) -> list[str]:
    raw = _col(row, col)
    if not raw:
        return []
    try:
        val = json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return [str(raw)]
    if isinstance(val, dict):
        return [f"{k} ({v})" for k, v in val.items()]
    if isinstance(val, list):
        return [str(v) for v in val]
    return [str(val)]


def build_profile_text(row: sqlite3.Row) -> str:
    """Build a natural-language candidate summary for embedding.

    Phrased like the "profil recherché" section of a job posting so the profile
    embedding lands near real offer descriptions (much stronger semantic signal
    than a bag of keywords). Purely data-driven from the profile row; the
    free-text `headline` carries education/framing.
    """
    sentences: list[str] = []

    headline = _col(row, "headline")
    if headline:
        sentences.append(str(headline).strip().rstrip(".") + ".")

    fields = [
        ("target_roles", "Profil et postes recherchés"),
        ("hard_skills", "Compétences et technologies maîtrisées"),
        ("certs", "Certifications"),
        ("contract_wanted", "Type de contrat recherché"),
        ("locations_ok", "Localisations acceptées"),
        ("languages", "Langues"),
    ]
    for col, label in fields:
        values = _as_list(row, col)
        if values:
            sentences.append(f"{label} : {', '.join(values)}.")

    return " ".join(sentences).lower()


def ensure_profile_embedding(
    db: sqlite3.Connection, embed_fn: EmbedFn | None = None, *, force: bool = False
) -> None:
    """Compute and cache profile.embedding if absent (or force recompute)."""
    row = db.execute("SELECT * FROM profile WHERE id = 1").fetchone()
    if row is None:
        raise RuntimeError("no profile row; run `jobpilot init-profile` first")
    if row["embedding"] and not force:
        return
    fn = embed_fn or get_embed_fn()
    text = build_profile_text(row)
    vec = fn(text)
    db.execute("UPDATE profile SET embedding = ? WHERE id = 1",
               (json.dumps(vec),))
    db.commit()
    log.info("cached profile embedding (dim=%d)", len(vec))

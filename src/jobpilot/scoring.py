"""Wires the vendored matcher.score_new_offers to the local embed_fn.

This module owns no scoring logic — matcher.py does (constitution). It only
ensures the profile embedding exists, then delegates.
"""

from __future__ import annotations

import sqlite3

import matcher

from jobpilot.config import get_settings
from jobpilot.embeddings import EmbedFn, ensure_profile_embedding, get_embed_fn
from jobpilot.logging_conf import get_logger

log = get_logger("scoring")


def score(
    db: sqlite3.Connection,
    embed_fn: EmbedFn | None = None,
    *,
    threshold: float | None = None,
) -> int:
    """Score all unscored offers. Returns the number newly queued.

    The queue threshold is JobPilot config (env JOBPILOT_QUEUE_THRESHOLD, default
    0.6). matcher.py reads its module-level QUEUE_THRESHOLD, so we set it at
    runtime rather than editing matcher.py — its scoring logic stays untouched.
    """
    fn = embed_fn or get_embed_fn()
    thr = threshold if threshold is not None else get_settings().queue_threshold
    matcher.QUEUE_THRESHOLD = thr
    ensure_profile_embedding(db, fn)
    queued = matcher.score_new_offers(db, fn)
    log.info("scoring pass complete: %d newly queued (threshold=%.2f)", queued, thr)
    return queued

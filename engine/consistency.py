"""WP3 — consistency across repeated advisor runs (same need, same configuration).

Deterministic, no model call. For every pair of runs: agreement on sufficient_information,
confidence spread, Jaccard overlap of the channel set and of the cited-source set, and
overlap of the required-asset vocabulary. Written to evaluations as metric 'consistency'
per need+config, with the per-pair detail in the notes."""
from __future__ import annotations

import json
import re
from itertools import combinations
from typing import Any

import psycopg

_STOP = {"the", "a", "an", "and", "or", "of", "for", "to", "in", "on", "with", "per", "by", "at", "from", "as", "is", "are"}


def _words(items: list[str]) -> set[str]:
    out: set[str] = set()
    for it in items:
        out |= {w for w in re.findall(r"[a-zà-ÿ0-9]+", it.lower()) if len(w) > 3 and w not in _STOP}
    return out


def _jaccard(a: set, b: set) -> float:
    return 1.0 if not a and not b else len(a & b) / max(1, len(a | b))


def features(s: dict[str, Any]) -> dict[str, Any]:
    recs = s.get("recommendations", [])
    return {
        "sufficient": bool(s.get("sufficient_information")),
        "confidence": float(s.get("confidence", 0)),
        "channels": {c.lower() for r in recs for c in r.get("channels", [])},
        "sources": {c.get("source", "").lower() for r in recs for c in r.get("citations", [])},
        "assets": _words(s.get("required_assets", [])),
        "actions": _words([r.get("action", "") for r in recs]),
    }


def score(conn: psycopg.Connection, need_id: str, config: str = "C") -> dict[str, Any]:
    rows = conn.execute("""select id, structured, created_at from advice where need_id = %s and kind = 'advice' and config = %s
                           and structured is not null order by created_at""", (need_id, config)).fetchall()
    if len(rows) < 2:
        return {"need_id": need_id, "config": config, "runs": len(rows), "note": "fewer than two runs"}
    fs = [features(r["structured"]) for r in rows]
    pairs = []
    for (i, a), (j, b) in combinations(enumerate(fs), 2):
        pairs.append({
            "runs": [str(rows[i]["id"])[:8], str(rows[j]["id"])[:8]],
            "same_sufficient": a["sufficient"] == b["sufficient"],
            "confidence_delta": round(abs(a["confidence"] - b["confidence"]), 3),
            "channels_jaccard": round(_jaccard(a["channels"], b["channels"]), 2),
            "sources_jaccard": round(_jaccard(a["sources"], b["sources"]), 2),
            "assets_overlap": round(_jaccard(a["assets"], b["assets"]), 2),
            "actions_overlap": round(_jaccard(a["actions"], b["actions"]), 2),
        })
    n = len(pairs)
    agg = {
        "need_id": need_id, "config": config, "runs": len(rows),
        "same_sufficient_share": sum(p["same_sufficient"] for p in pairs) / n,
        "max_confidence_delta": max(p["confidence_delta"] for p in pairs),
        "mean_channels_jaccard": round(sum(p["channels_jaccard"] for p in pairs) / n, 2),
        "mean_sources_jaccard": round(sum(p["sources_jaccard"] for p in pairs) / n, 2),
        "mean_assets_overlap": round(sum(p["assets_overlap"] for p in pairs) / n, 2),
        "mean_actions_overlap": round(sum(p["actions_overlap"] for p in pairs) / n, 2),
        "pairs": pairs,
    }
    # one number: decision agreement and channel agreement weigh most; confidence spread penalises
    agg["consistency"] = round(0.4 * agg["same_sufficient_share"] + 0.3 * agg["mean_channels_jaccard"]
                               + 0.2 * agg["mean_sources_jaccard"] + 0.1 * max(0.0, 1 - agg["max_confidence_delta"] * 2), 3)
    with conn.transaction():
        for r in rows:
            conn.execute("insert into evaluations (subject_kind, subject_id, metric, score, evaluator, notes) values ('advice', %s, 'consistency', %s, 'deterministic', %s)",
                         (r["id"], agg["consistency"], json.dumps({k: v for k, v in agg.items() if k != "pairs"})))
    return agg

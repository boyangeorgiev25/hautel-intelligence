"""Quality read model for the frontend: engine against the keyword baseline on the golden
cases, run-to-run consistency of the engine, and advice quality (automatic QC next to human
ratings). Read-only; ratings are written by the API's rate endpoint into `evaluations`.
"""
from __future__ import annotations

import pathlib
from typing import Any

import psycopg

from .baseline import baseline_pick
from .golden import load_cases

REPO = pathlib.Path(__file__).resolve().parent.parent
CASES = REPO / "tests" / "wp2_cases.yaml"
GUARD = "engine:empty_pool_guard"
HUMAN_METRICS = ("relevance", "groundedness", "consistency")


def _judge(exp: dict[str, Any], decision: str | None, top_id: str | None, top_score: float | None) -> bool | None:
    """Same rules as golden.judge_engine, on stored rows. None = no run yet."""
    if decision is None:
        return None
    accept = set(exp.get("consultants", []))
    escalated = decision in ("escalate", "failed")
    want = exp["decision"]
    if want == "escalate":
        return escalated or bool(exp.get("low_confidence_ok") and top_score is not None and top_score < 0.5)
    if want == "match":
        return decision == "match" and top_id in accept
    if want == "either":
        return escalated or top_id in accept
    return False


def golden_summary(conn: psycopg.Connection) -> dict[str, Any]:
    spec = load_cases(CASES)
    names = spec.get("consultants", {})
    rows = []
    for c in spec["cases"]:
        exp = c["expected"]
        if exp["decision"] == "rollback":
            continue
        runs = conn.execute("select decision, model_ref, raw_output, created_at from match_runs where need_id = %s order by created_at desc", (c["need_id"],)).fetchall()
        guard = c.get("kind") == "empty_pool"
        run = next((r for r in runs if (r["model_ref"] == GUARD) == guard), None)
        top = ((run["raw_output"] or {}).get("ranked") or [{}])[0] if run else {}
        top_id, top_score = top.get("consultant_id"), (float(top["score"]) if top.get("score") is not None else None)
        engine_ok = _judge(exp, run["decision"] if run else None, top_id, top_score)
        b = baseline_pick(conn, c["need_id"])
        base_ok = exp["decision"] != "escalate" and b.consultant_id in set(exp.get("consultants", []))
        rows.append({
            "id": c["id"], "label": c["label"], "language": c["language"], "kind": c.get("kind"),
            "expected": {"decision": exp["decision"], "consultants": [names.get(x, x).split(" (")[0] for x in exp.get("consultants", [])], "low_confidence_ok": bool(exp.get("low_confidence_ok"))},
            "engine": {"decision": run["decision"] if run else None, "top": top.get("consultant_name"), "score": top_score, "ok": engine_ok, "run_at": run["created_at"] if run else None},
            "baseline": {"pick": b.consultant_name, "hits": b.hits, "ok": base_ok},
        })
    scored = [r for r in rows if r["engine"]["ok"] is not None]
    by_lang: dict[str, dict[str, int]] = {}
    for r in rows:
        d = by_lang.setdefault(r["language"], {"cases": 0, "engine": 0, "baseline": 0})
        d["cases"] += 1; d["engine"] += 1 if r["engine"]["ok"] else 0; d["baseline"] += 1 if r["baseline"]["ok"] else 0
    return {"cases": rows, "engine_hits": sum(1 for r in rows if r["engine"]["ok"]), "baseline_hits": sum(1 for r in rows if r["baseline"]["ok"]),
            "total": len(rows), "run": len(scored), "by_language": by_lang}


def run_to_run(conn: psycopg.Connection, org_id: str | None) -> dict[str, Any]:
    where, params = ["r.model_ref <> %s"], [GUARD]
    if org_id:
        where.append("p.org_id = %s"); params.append(org_id)
    rows = conn.execute(f"""
        select r.need_id, r.decision, r.raw_output->'ranked'->0->>'consultant_id' as top
          from match_runs r join marketing_needs n on n.id = r.need_id join properties p on p.id = n.property_id
         where {' and '.join(where)} order by r.need_id, r.created_at""", tuple(params)).fetchall()
    by_need: dict[str, list[str]] = {}
    for r in rows:
        by_need.setdefault(str(r["need_id"]), []).append(r["top"] or r["decision"])
    multi = [v for v in by_need.values() if len(v) > 1]
    same = sum(1 for v in multi if all(x == v[0] for x in v))
    return {"multi": len(multi), "same": same}


def auto_scores(qc: dict[str, Any] | None) -> dict[str, float | None]:
    """Automatic QC → the three criteria a person rates, on a 1-5 scale."""
    if not qc:
        return {"relevance": None, "groundedness": None, "consistency": None}
    j = qc.get("judge") or {}
    cc = qc.get("citation_check") or {}
    rel = j.get("objective_alignment")
    gro = (cc["citations_verified"] / cc["citations_total"]) if cc.get("citations_total") else j.get("context_consistency")
    con = j.get("context_consistency")
    f = lambda x: round(float(x) * 5, 1) if x is not None else None  # noqa: E731
    return {"relevance": f(rel), "groundedness": f(gro), "consistency": f(con)}


def ratings_for(conn: psycopg.Connection, advice_ids: list[str]) -> dict[str, list[dict[str, Any]]]:
    """Human ratings per advice: the three criteria written together by the rate endpoint, grouped by evaluator and time."""
    if not advice_ids:
        return {}
    rows = conn.execute("""
        select subject_id, evaluator, created_at, metric, score, notes from evaluations
         where subject_kind = 'advice' and subject_id = any(%s::uuid[]) and evaluator like 'human:%%' and metric = any(%s)
         order by created_at""", (advice_ids, list(HUMAN_METRICS))).fetchall()
    out: dict[str, dict[tuple, dict[str, Any]]] = {}
    for r in rows:
        key = (r["evaluator"], r["created_at"])
        g = out.setdefault(str(r["subject_id"]), {}).setdefault(key, {"who": r["evaluator"].split(":", 1)[1], "at": r["created_at"], "notes": r["notes"]})
        g[r["metric"]] = round(float(r["score"]) * 5, 1)
    return {k: list(v.values()) for k, v in out.items()}


def advice_rows(conn: psycopg.Connection, org_id: str | None = None, advice_id: str | None = None) -> list[dict[str, Any]]:
    where, params = ["a.kind = 'advice'"], []
    if org_id:
        where.append("p.org_id = %s"); params.append(org_id)
    if advice_id:
        where.append("a.id = %s"); params.append(advice_id)
    rows = [dict(r) for r in conn.execute(f"""
        select a.id, a.need_id, a.property_id, n.title as need_title, p.name as property_name, a.config, a.status, a.language, a.body, a.structured, a.qc,
               a.model_ref, a.latency_ms, a.input_tokens, a.output_tokens, a.created_at, a.review_note, a.reviewed_at,
               row_number() over (partition by a.need_id order by a.created_at) as version
          from advice a join marketing_needs n on n.id = a.need_id join properties p on p.id = a.property_id
         where {' and '.join(where)} order by a.created_at desc""", tuple(params)).fetchall()]
    ratings = ratings_for(conn, [str(r["id"]) for r in rows])
    for r in rows:
        r["auto"] = auto_scores(r.get("qc"))
        r["ratings"] = ratings.get(str(r["id"]), [])
    return rows


def advice_quality(conn: psycopg.Connection, org_id: str | None) -> dict[str, Any]:
    rows = advice_rows(conn, org_id)
    mean = lambda xs: round(sum(xs) / len(xs), 1) if xs else None  # noqa: E731
    auto = {m: mean([r["auto"][m] for r in rows if r["auto"][m] is not None]) for m in HUMAN_METRICS}
    allr = [x for r in rows for x in r["ratings"]]
    human = {m: mean([x[m] for x in allr if x.get(m) is not None]) for m in HUMAN_METRICS}
    return {"total": len(rows), "ratings": len(allr), "auto": auto, "human": human}


def rate(conn: psycopg.Connection, advice_id: str, scores: dict[str, int], notes: str | None, evaluator: str) -> dict[str, Any]:
    if not conn.execute("select 1 from advice where id = %s", (advice_id,)).fetchone():
        raise LookupError("advice not found")
    with conn.transaction():
        for m in HUMAN_METRICS:
            conn.execute("insert into evaluations (subject_kind, subject_id, metric, score, evaluator, notes) values ('advice', %s, %s, %s, %s, %s)",
                         (advice_id, m, scores[m] / 5, evaluator, notes))
    return {"id": advice_id, "saved": True}

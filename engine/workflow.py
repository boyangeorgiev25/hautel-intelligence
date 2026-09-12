"""Decision -> workflow. One engine run = one transaction.

MATCH:    match_runs row + up to 3 matches rows + one task(origin_kind='match')
          routed to the org's marketing lead; need -> 'matched'.
ESCALATE: match_runs row + one task(origin_kind='escalation') routed the same
          way; need stays 'open'.
FAILED:   (model refused / unusable output) match_runs row with decision
          'failed' + an escalation task, so nothing is silently dropped.

Safety checks before writing: every consultant_id must exist in the pool the
model saw (an unknown id turns the run into an escalation), scores are clamped
to [0,1]. A sink failure mid-transaction rolls back everything.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import psycopg

from . import db
from .matcher import EngineResult, interpret, to_jsonable
from .schema import MatchDecision


class SinkUnavailable(RuntimeError):
    """Raised inside the write transaction to simulate an unavailable sink (test only)."""


@dataclass
class RunOutcome:
    run_id: str
    need_id: str
    decision: str                   # match | escalate | failed
    top_consultant_id: str | None
    top_consultant_name: str | None
    top_score: float | None
    brief_language: str | None
    task_id: str
    task_title: str
    assigned_to: str | None
    requires_group_signoff: bool
    escalation_reason: str | None
    model_ref: str
    latency_ms: int
    input_tokens: int
    output_tokens: int
    ranked: list[dict[str, Any]]


def run_need(
    conn: psycopg.Connection,
    need_id: str,
    *,
    candidate_filter: dict[str, Any] | None = None,
    fail_sink: bool = False,
    client=None,
) -> RunOutcome:
    need = db.load_need(conn, need_id)
    pool = db.load_pool(conn, candidate_filter)
    pool_ids = {c.id for c in pool}

    if not pool:
        # Empty candidate pool: decided locally, no model call, still fully logged.
        result = EngineResult(
            decision=MatchDecision(
                brief_language="other", need_summary=need.title, core_skills_needed=[],
                constraints_checked=["candidate pool is empty"], decision="escalate",
                escalation_reason="Candidate pool is empty after filtering; no consultant can be proposed. A human must widen the pool or source externally.",
                ranked=[], requires_group_signoff=False, signoff_rule=None,
            ),
            model_ref="engine:empty_pool_guard", latency_ms=0, input_tokens=0, output_tokens=0, stop_reason=None,
        )
    else:
        result = interpret(need, pool, client=client)

    decision = result.decision
    if decision is not None:
        unknown = [c.consultant_id for c in decision.ranked if c.consultant_id not in pool_ids]
        if unknown:
            decision.decision = "escalate"
            decision.escalation_reason = (
                f"Engine returned consultant ids not present in the pool ({', '.join(unknown)}); "
                "output rejected as ungrounded. " + (decision.escalation_reason or "")
            ).strip()
            decision.ranked = [c for c in decision.ranked if c.consultant_id in pool_ids]

    lead = db.marketing_lead(conn, need.org_id)
    with conn.transaction():
        run_id = _insert_run(conn, need, decision, result, len(pool))
        if result.refused or decision is None:
            task_id, title = _insert_escalation_task(
                conn, need, run_id, lead, result.failure or "engine produced no decision", decision
            )
            outcome_decision = "failed"
            top = None
        elif decision.decision == "match" and decision.ranked:
            match_ids = _insert_matches(conn, need, run_id, decision)
            if fail_sink:
                raise SinkUnavailable("simulated: task sink unavailable")
            task_id, title = _insert_match_task(conn, need, match_ids[0], lead, decision)
            conn.execute("update marketing_needs set status = 'matched' where id = %s", (need.id,))
            outcome_decision = "match"
            top = decision.ranked[0]
        else:
            if decision.ranked:   # partial fits listed alongside an escalation
                _insert_matches(conn, need, run_id, decision)
            task_id, title = _insert_escalation_task(conn, need, run_id, lead, decision.escalation_reason or "escalated", decision)
            outcome_decision = "escalate"
            top = decision.ranked[0] if decision.ranked else None

    return RunOutcome(
        run_id=run_id, need_id=need.id, decision=outcome_decision,
        top_consultant_id=top.consultant_id if top else None,
        top_consultant_name=top.consultant_name if top else None,
        top_score=top.score if top else None,
        brief_language=decision.brief_language if decision else None,
        task_id=task_id, task_title=title, assigned_to=str(lead["id"]) if lead else None,
        requires_group_signoff=bool(decision and decision.requires_group_signoff),
        escalation_reason=(decision.escalation_reason if decision else result.failure),
        model_ref=result.model_ref, latency_ms=result.latency_ms,
        input_tokens=result.input_tokens, output_tokens=result.output_tokens,
        ranked=[c.model_dump() for c in decision.ranked] if decision else [],
    )


# ── writers ────────────────────────────────────────────────────────────────

def _insert_run(conn, need, decision: MatchDecision | None, result: EngineResult, pool_size: int) -> str:
    row = conn.execute(
        """
        insert into match_runs (need_id, engine, decision, brief_language, need_summary, core_skills,
                                constraints_checked, escalation_reason, requires_group_signoff, signoff_rule,
                                candidate_count, model_ref, latency_ms, input_tokens, output_tokens, raw_output)
        values (%s, 'llm', %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        returning id
        """,
        (
            need.id,
            "failed" if decision is None else decision.decision,
            decision.brief_language if decision else None,
            decision.need_summary if decision else None,
            decision.core_skills_needed if decision else [],
            decision.constraints_checked if decision else [],
            (decision.escalation_reason if decision else result.failure),
            bool(decision and decision.requires_group_signoff),
            decision.signoff_rule if decision else None,
            pool_size, result.model_ref, result.latency_ms, result.input_tokens, result.output_tokens,
            psycopg.types.json.Jsonb(to_jsonable(decision)),
        ),
    ).fetchone()
    return str(row["id"])


def _insert_matches(conn, need, run_id: str, decision: MatchDecision) -> list[str]:
    ids = []
    for rank, cand in enumerate(decision.ranked[:3], start=1):
        rationale = cand.rationale
        if cand.evidence:
            rationale += "\n\nEvidence: " + " | ".join(f'"{e}"' for e in cand.evidence)
        if cand.gaps:
            rationale += "\n\nGaps: " + "; ".join(cand.gaps)
        row = conn.execute(
            """
            insert into matches (need_id, consultant_id, score, rationale, model_ref, status, run_id, rank)
            values (%s, %s, %s, %s, %s, 'proposed', %s, %s) returning id
            """,
            (need.id, cand.consultant_id, round(min(max(cand.score, 0.0), 1.0), 3), rationale,
             conn.execute("select model_ref from match_runs where id = %s", (run_id,)).fetchone()["model_ref"],
             run_id, rank),
        ).fetchone()
        ids.append(str(row["id"]))
    return ids


def _insert_match_task(conn, need, top_match_id: str, lead, decision: MatchDecision) -> tuple[str, str]:
    top = decision.ranked[0]
    title = f"Engagement proposal: {need.title} → {top.consultant_name}"
    lines = [
        f"Need: {need.title} ({need.property_name})",
        f"Interpretation: {decision.need_summary}",
        f"Proposed: {top.consultant_name} (confidence {top.score:.2f})",
        f"Why: {top.rationale}",
    ]
    if len(decision.ranked) > 1:
        lines.append("Alternatives: " + "; ".join(f"{c.consultant_name} ({c.score:.2f})" for c in decision.ranked[1:]))
    if decision.requires_group_signoff:
        lines.append(f"Sign-off required before external spend. Rule: {decision.signoff_rule}")
    lines.append(f"Provenance: match {top_match_id}; brief language {decision.brief_language}")
    return _insert_task(conn, need, title, "\n".join(lines), "match", top_match_id, lead)


def _insert_escalation_task(conn, need, run_id: str, lead, reason: str, decision: MatchDecision | None) -> tuple[str, str]:
    title = f"Needs human review: {need.title}"
    lines = [f"Need: {need.title} ({need.property_name})", f"Reason: {reason}"]
    if decision and decision.need_summary:
        lines.insert(1, f"Interpretation: {decision.need_summary}")
    if decision and decision.ranked:
        lines.append("Nearest partial fits: " + "; ".join(f"{c.consultant_name} ({c.score:.2f})" for c in decision.ranked))
    lines.append(f"Provenance: run {run_id}")
    return _insert_task(conn, need, title, "\n".join(lines), "escalation", run_id, lead)


def _insert_task(conn, need, title: str, detail: str, origin_kind: str, origin_id: str, lead) -> tuple[str, str]:
    row = conn.execute(
        """
        insert into tasks (property_id, title, detail, status, origin_kind, origin_id, assigned_to)
        values (%s, %s, %s, 'open', %s, %s, %s) returning id
        """,
        (need.property_id, title, detail, origin_kind, origin_id, lead["id"] if lead else None),
    ).fetchone()
    return str(row["id"]), title

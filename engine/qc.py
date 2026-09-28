"""WP3 — AI quality control: deterministic checks + an LLM judge over an advisor output.

Deterministic (own development, catches what can be caught without a model):
  - citation check: every quoted fragment must occur verbatim in the context the advisor saw;
  - policy check: 'sufficient_information' must agree with the presence of recommendations;
  - rule scan: organization documents mentioning sign-off/approval/IP are surfaced if the advice ignores them.
LLM judge (existing technology, fixed rubric, scores 0..1): objective alignment, context consistency,
unsupported claims, missing information, language consistency, plus concrete corrections.
Results are written to advice.qc and to evaluations (one row per metric) so the report can aggregate them.
"""
from __future__ import annotations

import json
import os
import re
import time
from typing import Any, Literal

import anthropic
import psycopg
from pydantic import BaseModel, Field

from . import db
from .advice import Advice, assemble_context, latest_match

MODEL = os.environ.get("HAUTEL_MODEL", "claude-opus-5")


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", s.replace("’", "'").replace("“", '"').replace("”", '"')).strip().lower()


def _citations(structured: dict[str, Any]) -> list[dict[str, Any]]:
    out = []
    for r in structured.get("recommendations", []) + structured.get("sections", []):
        out += r.get("citations", [])
    return out


def citation_check(structured: dict[str, Any], context: str) -> dict[str, Any]:
    ctx = _norm(context)
    total, found, missing = 0, 0, []
    for c in _citations(structured):
        if True:
            total += 1
            q = _norm(c.get("quote", ""))
            if q and q in ctx:
                found += 1
            else:
                missing.append({"source": c.get("source"), "quote": c.get("quote", "")[:160]})
    return {"citations_total": total, "citations_verified": found, "unverified": missing,
            "pass": total == 0 or not missing}


def policy_check(structured: dict[str, Any]) -> dict[str, Any]:
    if "sufficient_information" not in structured:   # drafts and localisations
        generic = [] if structured.get("hotel_specific", True) else ["document is not hotel-specific"]
        return {"pass": not generic, "problems": generic, "generic_recommendations": []}
    suff = structured.get("sufficient_information")
    recs = structured.get("recommendations", [])
    problems = []
    if suff and not recs:
        problems.append("sufficient_information is true but no recommendations were given")
    if not suff and recs:
        problems.append("sufficient_information is false but recommendations were given")
    if not suff and not structured.get("missing_information"):
        problems.append("insufficient information declared without saying what is missing")
    uncited = [r["action"][:80] for r in recs if not r.get("citations")]
    return {"pass": not problems, "problems": problems, "generic_recommendations": uncited}


def rule_scan(need: db.Need, structured: dict[str, Any]) -> dict[str, Any]:
    """Surface organization/property documents that carry rules the advice should acknowledge."""
    keywords = ("sign-off", "signoff", "approval", "intellectual property", "ip transfer", "exclusive property", "brand guideline", "not permitted", "must not")
    hits = []
    for d in need.org_documents + need.property_documents:
        body = (d.get("body") or "").lower()
        for k in keywords:
            if k in body:
                hits.append({"document": d.get("title"), "keyword": k}); break
    text = json.dumps(structured).lower()
    acknowledged = any(k in text for k in ("sign-off", "signoff", "approval", "ip", "intellectual property", "rule"))
    return {"documents_with_rules": hits, "acknowledged_in_advice": acknowledged, "pass": not hits or acknowledged}


class Correction(BaseModel):
    where: str = Field(description="Which field or recommendation.")
    issue: str
    suggested_fix: str


class QCJudgement(BaseModel):
    objective_alignment: float = Field(ge=0, le=1, description="Does the advice answer the request's actual objective?")
    context_consistency: float = Field(ge=0, le=1, description="Is it consistent with the hotel profile, documents and organization rules?")
    unsupported_claims: list[str] = Field(description="Hotel-specific claims in the advice that the context does not support. Empty if none.")
    missing_information_handled: float = Field(ge=0, le=1, description="Did the advice name what is missing instead of inventing it?")
    language_consistency: float = Field(ge=0, le=1, description="Terminology and audience consistent with the request and hotel context; output language as required.")
    actionability: float = Field(ge=0, le=1, description="Could the hotel start on this next week?")
    corrections: list[Correction]
    verdict: Literal["accept", "revise", "reject"]
    summary: str = Field(description="Two sentences for the human reviewer.")


JUDGE_PROMPT = """You are the quality-control step of the Hautel Intelligence platform. You receive the CONTEXT the generator saw (request, hotel, organization documents, match), possibly a SOURCE document the output was derived from (the advice a draft is based on, or the document a localisation translates), and the OUTPUT (advice, draft or localisation). Judge the output strictly against the context and, when present, the source: a draft must follow the advice it came from; a localisation must preserve the source's objective, audience, facts, hotel terminology and structure in the target language.

The advisor writes its advice in English by design, whatever the language of the request; localisation is a separate step. So language_consistency judges terminology, audience and market fit against the request and hotel context, not the output language.

Score each criterion from 0 to 1. List every hotel-specific claim that the context does not support (numbers, competitors, past results, facilities, people). Propose concrete corrections. Verdict rules: accept = a human can approve with at most cosmetic edits AND unsupported_claims is empty; revise = usable after the listed corrections, or any unsupported claim exists; reject = misreads the request or invents material facts. Never return accept together with a non-empty unsupported_claims list. Be terse and specific."""


def judge(context: str, structured: dict[str, Any], client: anthropic.Anthropic | None = None, source: str | None = None, kind: str = "advice") -> tuple[QCJudgement | None, dict[str, Any]]:
    client = client or anthropic.Anthropic()
    t0 = time.perf_counter()
    user = "CONTEXT:\n" + context + ("\n\nSOURCE:\n" + source if source else "") + f"\n\nOUTPUT ({kind}):\n" + json.dumps(structured, ensure_ascii=False, indent=1)
    response = client.messages.parse(
        model=MODEL, max_tokens=6000,
        system=[{"type": "text", "text": JUDGE_PROMPT, "cache_control": {"type": "ephemeral"}}],
        messages=[{"role": "user", "content": user}],
        output_format=QCJudgement,
    )
    meta = {"model_ref": response.model, "latency_ms": int((time.perf_counter() - t0) * 1000),
            "input_tokens": response.usage.input_tokens, "output_tokens": response.usage.output_tokens}
    return response.parsed_output, meta


def run_qc(conn: psycopg.Connection, advice_id: str, client: anthropic.Anthropic | None = None, with_judge: bool = True) -> dict[str, Any]:
    row = conn.execute("select id, kind, need_id, config, structured, status, run_id, parent_id from advice where id = %s", (advice_id,)).fetchone()
    if not row:
        raise LookupError("advice not found")
    if not row["structured"]:
        raise ValueError("advice has no structured output to check")
    need = db.load_need(conn, str(row["need_id"]))
    match = latest_match(conn, str(row["need_id"])) if row["config"] == "C" else None
    context = assemble_context(need, row["config"], match)
    s = row["structured"]
    report: dict[str, Any] = {
        "citation_check": citation_check(s, context),
        "policy_check": policy_check(s),
        "rule_scan": rule_scan(need, s),
    }
    deterministic_pass = all(report[k]["pass"] for k in ("citation_check", "policy_check", "rule_scan"))
    if with_judge:
        source = None
        if row["parent_id"]:
            src = conn.execute("select body from advice where id = %s", (row["parent_id"],)).fetchone()
            source = src["body"] if src else None
        j, meta = judge(context, s, client=client, source=source, kind=row["kind"])
        report["judge"] = (j.model_dump() if j else {"error": "no judgement"}) | meta
    verdict = (report.get("judge") or {}).get("verdict")
    if verdict == "accept" and (report.get("judge") or {}).get("unsupported_claims"):
        report["judge"]["verdict"] = verdict = "revise"   # enforce the rule even if the judge slipped
        report["judge"]["verdict_note"] = "downgraded: unsupported claims present"
    if not deterministic_pass or verdict == "reject":
        status = "flagged"
    elif verdict == "revise":
        status = "flagged"
    else:
        status = "draft"
    report["deterministic_pass"] = deterministic_pass
    report["status"] = status
    with conn.transaction():
        conn.execute("update advice set qc = %s, status = case when status in ('accepted','edited','rejected') then status else %s end where id = %s",
                     (json.dumps(report), status, advice_id))
        metrics = {
            "citations_verified_share": (report["citation_check"]["citations_verified"] / report["citation_check"]["citations_total"]) if report["citation_check"]["citations_total"] else 1.0,
            "policy_pass": 1.0 if report["policy_check"]["pass"] else 0.0,
            "rules_pass": 1.0 if report["rule_scan"]["pass"] else 0.0,
        }
        if report.get("judge") and "objective_alignment" in report["judge"]:
            jd = report["judge"]
            metrics |= {"relevance": jd["objective_alignment"], "groundedness": jd["context_consistency"],
                        "missing_info_handling": jd["missing_information_handled"],
                        "language_consistency": jd["language_consistency"], "actionability": jd["actionability"],
                        "unsupported_claims": 1.0 - min(1.0, len(jd["unsupported_claims"]) / 5)}
        for metric, score in metrics.items():
            conn.execute("insert into evaluations (subject_kind, subject_id, metric, score, evaluator, notes) values ('advice', %s, %s, %s, %s, %s)",
                         (advice_id, metric, round(float(score), 3), "llm_judge" if metric in ("relevance", "groundedness", "missing_info_handling", "language_consistency", "actionability", "unsupported_claims") else "deterministic",
                          f"config {row['config']}"))
    return report

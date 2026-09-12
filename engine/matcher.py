"""AI interpretation: need + hotel context + consultant pool -> MatchDecision.

Own development (ISS evidence line): the context assembly over mixed
structured/unstructured records, the grounding rules, the decision policy
(MATCH | ESCALATE) and the output contract. Existing technology: the hosted
LLM API. The system prompt is frozen text so it caches across needs.
"""
from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from typing import Any

import anthropic

from .db import Consultant, Need
from .schema import MatchDecision

MODEL = os.environ.get("HAUTEL_MODEL", "claude-opus-5")

SYSTEM_PROMPT = """You are the matching engine of the Hautel Intelligence platform. A hotel has a marketing need; you must decide which consultant from the pool should be proposed for it, or escalate to a human.

You receive: the NEED (title, brief, category, urgency, budget band), the HOTEL (profile fields and its documents), ORGANIZATION documents (rules that apply to all its hotels), and the CONSULTANT POOL (structured skills with level and evidence, free-text bios, languages, region, day-rate band, documents).

Rules:
1. Use only the records provided. Never invent a consultant, a skill, a fact or a number. Every consultant_id you return must be copied exactly from the pool.
2. Interpret the need first: what does the hotel actually have to buy? Briefs use different words than skill names ("pre-arrival flow" is email marketing/CRM; "findable in three languages" is multilingual SEO; "press push" is PR). Match on meaning, not on shared words.
3. Briefs can be in Dutch, French, English, German or a mix. Detect the language, interpret it natively, and report it as brief_language. Treat a stated language requirement in the brief or the hotel documents as a hard constraint against the consultant's languages.
4. Check constraints explicitly and list them in constraints_checked: language fit, region/proximity where it matters, budget band versus day-rate band, urgency versus what the records say about turnaround, and any organization rule in the documents.
5. Decision policy:
   - "match": at least one consultant clearly covers the core of the need. Return up to 3 candidates, best first. score = your confidence that the consultant can deliver the core of the need (1.0 = exact specialist with concrete evidence; 0.5 = partial fit, part of the need uncovered; below 0.5 means you should not be matching).
   - "escalate": the pool is empty, or no consultant covers the core skill (name the gap precisely), or the brief is too ambiguous to know what to buy (say which question a human should ask the hotel). When escalating for a skill gap, you may still list the nearest partial fits in ranked with honest low scores.
6. rationale must be grounded: every claim in it must be traceable to a fragment you quote in evidence. gaps must say what the consultant does not cover.
7. If an organization document sets a rule that applies to this need (for example a sign-off threshold for external spend), set requires_group_signoff and quote the rule verbatim in signoff_rule.
8. Write need_summary, rationale, gaps and escalation_reason in English regardless of the brief's language."""


@dataclass
class EngineResult:
    decision: MatchDecision | None
    model_ref: str
    latency_ms: int
    input_tokens: int
    output_tokens: int
    stop_reason: str | None
    failure: str | None = None   # set when the model refused / returned nothing usable

    @property
    def refused(self) -> bool:
        return self.failure is not None


def assemble_context(need: Need, pool: list[Consultant]) -> str:
    """Deterministic, human-readable context block. Same input -> same bytes."""
    payload = {
        "NEED": {
            "id": need.id, "title": need.title, "brief": need.description,
            "category": need.category, "urgency": need.urgency, "budget_band": need.budget_band,
        },
        "HOTEL": {
            "property_id": need.property_id, "name": need.property_name, "region": need.region,
            "profile": need.profile, "documents": need.property_documents,
        },
        "ORGANIZATION_DOCUMENTS": need.org_documents,
        "CONSULTANT_POOL": [
            {
                "consultant_id": c.id, "name": c.full_name, "kind": c.kind, "languages": c.languages,
                "region": c.region, "day_rate_band": c.day_rate_band, "bio": c.bio,
                "skills": c.expertise, "documents": c.documents,
            }
            for c in pool
        ],
        "POOL_SIZE": len(pool),
    }
    return json.dumps(payload, ensure_ascii=False, indent=1)


def interpret(need: Need, pool: list[Consultant], client: anthropic.Anthropic | None = None) -> EngineResult:
    client = client or anthropic.Anthropic()
    t0 = time.perf_counter()
    response = client.messages.parse(
        model=MODEL,
        max_tokens=16000,
        system=[{"type": "text", "text": SYSTEM_PROMPT, "cache_control": {"type": "ephemeral"}}],
        messages=[{"role": "user", "content": assemble_context(need, pool)}],
        output_format=MatchDecision,
    )
    latency = int((time.perf_counter() - t0) * 1000)
    usage = response.usage
    result = EngineResult(
        decision=None, model_ref=response.model, latency_ms=latency,
        input_tokens=usage.input_tokens, output_tokens=usage.output_tokens, stop_reason=response.stop_reason,
    )
    if response.stop_reason == "refusal":
        details = getattr(response, "stop_details", None)
        result.failure = f"model refused ({getattr(details, 'category', None)}): {getattr(details, 'explanation', '')}"
        return result
    if response.parsed_output is None:
        result.failure = f"no structured output (stop_reason={response.stop_reason})"
        return result
    result.decision = response.parsed_output
    return result


def to_jsonable(decision: MatchDecision | None) -> dict[str, Any] | None:
    return decision.model_dump() if decision else None

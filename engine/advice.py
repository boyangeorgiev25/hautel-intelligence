"""WP3 — AI marketing advisor: hotel context + marketing request (+ the WP2 match) -> structured recommendation.

Own development: the output contract, the three context configurations (A/B/C) that make the
grounding gain measurable, the "not enough information" policy and the writer. Existing technology:
the hosted LLM API, called exactly like the matching engine (structured output, cached system prompt).
"""
from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from typing import Any, Literal

import anthropic
import psycopg
from pydantic import BaseModel, Field

from . import db
from .db import Need

MODEL = os.environ.get("HAUTEL_MODEL", "claude-opus-5")
Config = Literal["A", "B", "C"]


class Citation(BaseModel):
    source: str = Field(description="Where the fragment comes from: 'brief', 'hotel profile', a document title, or 'match rationale'.")
    quote: str = Field(description="Verbatim fragment from the context that supports a claim. Never paraphrase.")


class Recommendation(BaseModel):
    action: str = Field(description="One concrete recommendation, in one or two sentences.")
    why: str = Field(description="Why this follows from the hotel's situation and the request.")
    channels: list[str] = Field(description="Channels or touchpoints this uses (instagram, OTA listing, LinkedIn, email, website, PR ...).")
    citations: list[Citation] = Field(description="Context fragments this recommendation rests on. Empty means it is a general best practice, not hotel-specific.")


class Advice(BaseModel):
    interpreted_objective: str = Field(description="What the hotel is actually trying to achieve, in one sentence.")
    sufficient_information: bool = Field(description="False when the context does not allow a hotel-specific recommendation; then recommendations stay empty and missing_information says what to ask.")
    missing_information: list[str] = Field(description="Facts that are missing or ambiguous and would change the recommendation. Empty only if nothing material is missing.")
    target_audience: str = Field(description="Who the marketing should reach, grounded in the hotel profile when available.")
    recommended_approach: str = Field(description="The strategy in a short paragraph.")
    recommendations: list[Recommendation] = Field(description="Three to five concrete recommendations, best first. Empty when sufficient_information is false.")
    required_assets: list[str] = Field(description="Content or assets that must exist or be produced (photos, reels, copy in which language, landing page ...).")
    next_actions: list[str] = Field(description="Immediate next steps for the hotel and, when a consultant is matched, for that consultant.")
    risks: list[str] = Field(description="What could go wrong or conflict with the hotel's rules and documents.")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence that this advice fits this hotel; low when the context is thin.")
    language_of_request: Literal["nl", "fr", "en", "de", "mixed", "other"]


SYSTEM_PROMPT = """You are the marketing advisor of the Hautel Intelligence platform, a hospitality marketing agency's AI layer. A hotel has a marketing request; you write a structured strategic recommendation the hotel's marketing lead can act on.

You receive a REQUEST (title, brief, category, urgency, budget band) and, depending on the configuration, HOTEL context (profile: segment, audience, positioning, channels, strengths, weaknesses; documents: briefs, tenders, proposals, shoot schedules), ORGANIZATION documents (rules for all hotels of the group) and a MATCH (the consultant proposed for the request, with rationale, evidence and gaps).

Rules:
1. Ground every hotel-specific claim in the context. Cite verbatim fragments in citations. If a recommendation does not rest on any fragment, leave its citations empty so the reader can see it is generic.
2. Never invent facts about the hotel: no room counts, prices, ratings, competitors, past results or people that are not in the context. If the request needs facts you do not have, list them in missing_information.
3. If the context is too thin for a hotel-specific recommendation (no profile, no documents, a brief without a goal or audience), set sufficient_information to false, leave recommendations empty, and make missing_information the questions to ask. Do not fill the gap with generic marketing advice.
4. Respect organization rules found in the documents (sign-off thresholds, IP clauses, brand rules) and surface conflicts in risks.
5. When a MATCH is provided, build on it: the consultant's gaps become required_assets or next_actions for someone else, not silent assumptions.
6. Keep it commercial and specific: what to do, on which channel, for whom, with which assets. Hospitality marketing is the domain: OTA visibility, direct bookings, social content, MICE, F&B, employer branding, seasonal campaigns.
7. Detect the language of the request and report it. Write the advice in English regardless of the request's language; localisation is a separate step."""


@dataclass
class AdviceResult:
    advice_id: str | None
    config: str
    advice: Advice | None
    model_ref: str
    latency_ms: int
    input_tokens: int
    output_tokens: int
    failure: str | None = None


def latest_match(conn: psycopg.Connection, need_id: str) -> dict[str, Any] | None:
    row = conn.execute(
        """select id as run_id, decision, need_summary, core_skills, constraints_checked, escalation_reason,
                  requires_group_signoff, signoff_rule, raw_output
             from match_runs where need_id = %s order by created_at desc limit 1""", (need_id,)).fetchone()
    if not row:
        return None
    ranked = ((row["raw_output"] or {}).get("ranked") or [])[:3]
    return {
        "run_id": str(row["run_id"]), "decision": row["decision"], "need_summary": row["need_summary"],
        "core_skills": row["core_skills"], "constraints_checked": row["constraints_checked"],
        "escalation_reason": row["escalation_reason"], "requires_group_signoff": row["requires_group_signoff"],
        "signoff_rule": row["signoff_rule"],
        "candidates": [{"name": c.get("consultant_name"), "score": c.get("score"), "rationale": c.get("rationale"),
                        "evidence": c.get("evidence"), "gaps": c.get("gaps")} for c in ranked],
    }


def assemble_context(need: Need, config: Config, match: dict[str, Any] | None) -> str:
    """A = request only. B = request + hotel and organization context. C = B + the WP2 match."""
    payload: dict[str, Any] = {
        "CONFIGURATION": config,
        "REQUEST": {"id": need.id, "title": need.title, "brief": need.description, "category": need.category,
                    "urgency": need.urgency, "budget_band": need.budget_band},
    }
    if config in ("B", "C"):
        payload["HOTEL"] = {"name": need.property_name, "region": need.region, "profile": need.profile,
                            "documents": need.property_documents}
        payload["ORGANIZATION_DOCUMENTS"] = need.org_documents
    else:
        payload["HOTEL"] = {"name": need.property_name, "note": "no profile or documents provided in this configuration"}
    if config == "C":
        payload["MATCH"] = match or {"note": "the request has not been matched yet"}
    return json.dumps(payload, ensure_ascii=False, indent=1)


def generate(need: Need, config: Config, match: dict[str, Any] | None, client: anthropic.Anthropic | None = None) -> AdviceResult:
    client = client or anthropic.Anthropic()
    t0 = time.perf_counter()
    response = client.messages.parse(
        model=MODEL, max_tokens=12000,
        system=[{"type": "text", "text": SYSTEM_PROMPT, "cache_control": {"type": "ephemeral"}}],
        messages=[{"role": "user", "content": assemble_context(need, config, match)}],
        output_format=Advice,
    )
    latency = int((time.perf_counter() - t0) * 1000)
    res = AdviceResult(advice_id=None, config=config, advice=None, model_ref=response.model, latency_ms=latency,
                       input_tokens=response.usage.input_tokens, output_tokens=response.usage.output_tokens)
    if response.stop_reason == "refusal":
        res.failure = "model refused"
    elif response.parsed_output is None:
        res.failure = f"no structured output (stop_reason={response.stop_reason})"
    else:
        res.advice = response.parsed_output
    return res


def render(a: Advice) -> str:
    """Human-readable body stored next to the structured output."""
    lines = [f"Objective: {a.interpreted_objective}", f"Audience: {a.target_audience}", "", "Approach:", a.recommended_approach, ""]
    if not a.sufficient_information:
        lines += ["Not enough information for a hotel-specific recommendation. Missing:"] + [f"- {m}" for m in a.missing_information]
    else:
        lines.append("Recommendations:")
        for i, r in enumerate(a.recommendations, 1):
            lines.append(f"{i}. {r.action} ({', '.join(r.channels)})")
            lines.append(f"   Why: {r.why}")
            for c in r.citations:
                lines.append(f"   Source [{c.source}]: \"{c.quote}\"")
        if a.missing_information:
            lines += ["", "Missing information:"] + [f"- {m}" for m in a.missing_information]
    if a.required_assets:
        lines += ["", "Required assets:"] + [f"- {x}" for x in a.required_assets]
    if a.next_actions:
        lines += ["", "Next actions:"] + [f"- {x}" for x in a.next_actions]
    if a.risks:
        lines += ["", "Risks:"] + [f"- {x}" for x in a.risks]
    lines.append(f"\nConfidence: {a.confidence:.2f}")
    return "\n".join(lines)


def advise(conn: psycopg.Connection, need_id: str, config: Config = "C", client: anthropic.Anthropic | None = None) -> AdviceResult:
    """Generate advice for a need under one configuration and store it. One transaction; a refusal is stored as a rejected row."""
    need = db.load_need(conn, need_id)
    match = latest_match(conn, need_id) if config == "C" else None
    res = generate(need, config, match, client=client)
    with conn.transaction():
        if res.advice is None:
            row = conn.execute(
                """insert into advice (property_id, need_id, body, grounding, model_ref, kind, config, structured, status,
                                       review_note, run_id, latency_ms, input_tokens, output_tokens)
                   values (%s, %s, %s, '[]', %s, 'advice', %s, null, 'rejected', %s, %s, %s, %s, %s) returning id""",
                (need.property_id, need.id, f"generation failed: {res.failure}", res.model_ref, config, res.failure,
                 match["run_id"] if match else None, res.latency_ms, res.input_tokens, res.output_tokens)).fetchone()
        else:
            a = res.advice
            grounding = [c.model_dump() for r in a.recommendations for c in r.citations]
            status = "flagged" if (not a.sufficient_information or a.confidence < 0.5) else "draft"
            row = conn.execute(
                """insert into advice (property_id, need_id, body, grounding, model_ref, kind, config, structured, status,
                                       language, run_id, latency_ms, input_tokens, output_tokens)
                   values (%s, %s, %s, %s, %s, 'advice', %s, %s, %s, 'en', %s, %s, %s, %s) returning id""",
                (need.property_id, need.id, render(a), json.dumps(grounding), res.model_ref, config,
                 json.dumps(a.model_dump()), status, match["run_id"] if match else None,
                 res.latency_ms, res.input_tokens, res.output_tokens)).fetchone()
        res.advice_id = str(row["id"])
    return res

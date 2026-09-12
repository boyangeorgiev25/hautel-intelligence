"""Structured output contract between the LLM and the engine.

The model must return exactly this shape (enforced via output_config json_schema
through the SDK's messages.parse). Everything the workflow writes to the database
comes from these fields, so the schema is the audit trail's vocabulary.
"""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class Candidate(BaseModel):
    consultant_id: str = Field(description="Exact id from the consultant pool. Never invent one.")
    consultant_name: str
    score: float = Field(ge=0.0, le=1.0, description="Confidence this consultant can deliver the core of the need. 1.0 = exact specialist with evidence, <0.5 = partial fit.")
    rationale: str = Field(description="Why this consultant, in 2-4 sentences, English.")
    evidence: list[str] = Field(description="Verbatim fragments from the consultant's records (skills, evidence, bio, documents) that support the rationale.")
    gaps: list[str] = Field(description="What this consultant does not cover in the need, if anything.")


class MatchDecision(BaseModel):
    brief_language: Literal["nl", "fr", "en", "de", "mixed", "other"] = Field(description="Language the brief is written in.")
    need_summary: str = Field(description="One-sentence interpretation of what the hotel actually needs to buy.")
    core_skills_needed: list[str] = Field(description="The 1-4 skills that define the core of the need.")
    constraints_checked: list[str] = Field(description="Constraints you verified: language fit, region, budget vs day rate, urgency, org rules.")
    decision: Literal["match", "escalate"]
    escalation_reason: str | None = Field(default=None, description="Required when decision is escalate: what is missing or ambiguous and what a human should ask or decide.")
    ranked: list[Candidate] = Field(description="Up to 3 candidates, best first. Empty when escalating because nobody fits.")
    requires_group_signoff: bool = Field(description="True if an organization rule in the documents requires sign-off for this need.")
    signoff_rule: str | None = Field(default=None, description="The rule quoted verbatim, when requires_group_signoff is true.")

"""WP3 — drafting and localisation on the shared context layer.

draft():     advice (+ hotel context) -> a first usable marketing document: a specialist brief,
             campaign brief, content brief, action plan or social draft. Stored as advice.kind='draft'.
localise():  a draft or advice -> another language/market (nl, fr, en), keeping hotel terminology,
             brand context, audience and objective. Stored as advice.kind='localisation'.
Both cite the context they used, so the QC citation check applies to them as well.
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
from .advice import Citation, assemble_context, latest_match

MODEL = os.environ.get("HAUTEL_MODEL", "claude-opus-5")
DraftKind = Literal["specialist_brief", "campaign_brief", "content_brief", "action_plan", "social_draft"]
Lang = Literal["nl", "fr", "en"]


class Section(BaseModel):
    heading: str
    content: str = Field(description="The section text, ready to use. Concrete: names, dates, channels, deliverables from the context.")
    citations: list[Citation] = Field(description="Context fragments this section rests on.")


class Draft(BaseModel):
    document_kind: DraftKind
    title: str
    addressed_to: str = Field(description="Who receives this document (the matched consultant, the hotel's marketing lead, the social team ...).")
    sections: list[Section] = Field(description="Four to eight sections. For a social draft: one section per post with the copy itself.")
    assets_needed: list[str]
    open_questions: list[str] = Field(description="What the recipient must confirm before starting; never fill these with assumptions.")
    hotel_specific: bool = Field(description="False if the document could be sent to any hotel; true when it uses this hotel's context.")


class Localisation(BaseModel):
    language: Lang
    title: str
    body: str = Field(description="The full localised document, same structure as the source, in the target language.")
    glossary_applied: list[str] = Field(description="Hotel or brand terms kept or rendered deliberately (names, outlet names, claims, campaign titles) and how.")
    adaptations: list[str] = Field(description="Changes beyond translation: audience, market conventions, formality, examples, units, dates. Each with the reason.")
    uncertain: list[str] = Field(description="Terms or passages where the right rendering depends on a decision the hotel must take.")


DRAFT_PROMPT = """You are the drafting step of the Hautel Intelligence platform. From an approved-in-principle marketing ADVICE, the REQUEST and the HOTEL context, write a first usable marketing document of the requested kind.

Rules:
1. Use the hotel's own facts, names, outlets, audiences and rules from the context. Cite the fragments you rely on per section. Never invent facts, figures, dates, competitors or results.
2. A document that could be sent to any hotel is a failure; if the context is too thin to make it hotel-specific, say so in open_questions and set hotel_specific to false.
3. Respect organization rules found in the documents (sign-off, IP, brand guidelines).
4. Write in English; localisation is a separate step. Keep hotel and brand names exactly as in the context.
5. Kinds: specialist_brief = the brief a consultant receives to start work (scope, deliverables, constraints, timing, inputs); campaign_brief = objective, audience, message, channels, timing, KPIs; content_brief = shot list / content plan with formats and channels; action_plan = week-by-week actions with owners; social_draft = three to five ready-to-post texts with channel and asset note."""

LOCALISE_PROMPT = """You are the localisation step of the Hautel Intelligence platform. You receive a SOURCE document (English) with the REQUEST and HOTEL context, and a TARGET language and market. Produce the document in the target language for that market.

Rules:
1. This is adaptation, not literal translation: keep the objective, audience and campaign logic; adapt formality, idiom, examples, date and price conventions to the market. Say what you changed and why in adaptations.
2. Keep hotel names, outlet names, brand claims and campaign titles as the hotel uses them in the context; if the context shows the hotel's own term in the target language (a Dutch brief, a French UGC script), use that term. List them in glossary_applied.
3. Do not add facts. If a passage needs a decision (formal or informal address, a claim that may not translate), list it in uncertain.
4. Output language must be exactly the target language throughout."""


@dataclass
class GenResult:
    id: str | None
    output: Any
    model_ref: str
    latency_ms: int
    input_tokens: int
    output_tokens: int
    failure: str | None = None


def _parse(client: anthropic.Anthropic, system: str, user: str, fmt: type[BaseModel], max_tokens: int = 10000) -> GenResult:
    t0 = time.perf_counter()
    r = client.messages.parse(model=MODEL, max_tokens=max_tokens,
                              system=[{"type": "text", "text": system, "cache_control": {"type": "ephemeral"}}],
                              messages=[{"role": "user", "content": user}], output_format=fmt)
    res = GenResult(None, None, r.model, int((time.perf_counter() - t0) * 1000), r.usage.input_tokens, r.usage.output_tokens)
    if r.stop_reason == "refusal":
        res.failure = "model refused"
    elif r.parsed_output is None:
        res.failure = f"no structured output ({r.stop_reason})"
    else:
        res.output = r.parsed_output
    return res


def render_draft(d: Draft) -> str:
    lines = [f"# {d.title}", f"To: {d.addressed_to}", f"Kind: {d.document_kind}", ""]
    for s in d.sections:
        lines += [f"## {s.heading}", s.content, ""]
    if d.assets_needed:
        lines += ["## Assets needed"] + [f"- {a}" for a in d.assets_needed] + [""]
    if d.open_questions:
        lines += ["## Open questions"] + [f"- {q}" for q in d.open_questions]
    return "\n".join(lines).strip()


def draft(conn: psycopg.Connection, advice_id: str, kind: DraftKind = "specialist_brief", client: anthropic.Anthropic | None = None) -> GenResult:
    client = client or anthropic.Anthropic()
    src = conn.execute("select id, need_id, property_id, config, body, structured, run_id from advice where id = %s and kind = 'advice'", (advice_id,)).fetchone()
    if not src:
        raise LookupError("advice not found")
    need = db.load_need(conn, str(src["need_id"]))
    match = latest_match(conn, str(src["need_id"])) if src["config"] == "C" else None
    ctx = assemble_context(need, src["config"], match)
    user = f"DOCUMENT KIND REQUESTED: {kind}\n\nADVICE:\n{json.dumps(src['structured'], ensure_ascii=False, indent=1)}\n\nCONTEXT:\n{ctx}"
    res = _parse(client, DRAFT_PROMPT, user, Draft)
    with conn.transaction():
        if res.output is None:
            row = conn.execute("""insert into advice (property_id, need_id, body, grounding, model_ref, kind, config, parent_id, status, review_note, run_id, latency_ms, input_tokens, output_tokens)
                                  values (%s,%s,%s,'[]',%s,'draft',%s,%s,'rejected',%s,%s,%s,%s,%s) returning id""",
                               (src["property_id"], src["need_id"], f"generation failed: {res.failure}", res.model_ref, src["config"], advice_id, res.failure, src["run_id"], res.latency_ms, res.input_tokens, res.output_tokens)).fetchone()
        else:
            d: Draft = res.output
            grounding = [c.model_dump() for s in d.sections for c in s.citations]
            row = conn.execute("""insert into advice (property_id, need_id, body, grounding, model_ref, kind, config, parent_id, language, structured, status, run_id, latency_ms, input_tokens, output_tokens)
                                  values (%s,%s,%s,%s,%s,'draft',%s,%s,'en',%s,%s,%s,%s,%s,%s) returning id""",
                               (src["property_id"], src["need_id"], render_draft(d), json.dumps(grounding), res.model_ref, src["config"], advice_id,
                                json.dumps(d.model_dump()), "draft" if d.hotel_specific else "flagged", src["run_id"], res.latency_ms, res.input_tokens, res.output_tokens)).fetchone()
        res.id = str(row["id"])
    return res


def localise(conn: psycopg.Connection, source_id: str, language: Lang, market: str | None = None, client: anthropic.Anthropic | None = None) -> GenResult:
    client = client or anthropic.Anthropic()
    src = conn.execute("select id, kind, need_id, property_id, config, body, structured, run_id from advice where id = %s and kind in ('advice','draft')", (source_id,)).fetchone()
    if not src:
        raise LookupError("source not found")
    need = db.load_need(conn, str(src["need_id"]))
    match = latest_match(conn, str(src["need_id"])) if src["config"] == "C" else None
    ctx = assemble_context(need, src["config"], match)
    user = f"TARGET LANGUAGE: {language}\nTARGET MARKET: {market or {'nl': 'Flanders and the Netherlands', 'fr': 'Wallonia, Brussels, Luxembourg and France', 'en': 'international'}[language]}\n\nSOURCE ({src['kind']}):\n{src['body']}\n\nCONTEXT:\n{ctx}"
    res = _parse(client, LOCALISE_PROMPT, user, Localisation)
    with conn.transaction():
        if res.output is None:
            row = conn.execute("""insert into advice (property_id, need_id, body, grounding, model_ref, kind, config, parent_id, language, status, review_note, run_id, latency_ms, input_tokens, output_tokens)
                                  values (%s,%s,%s,'[]',%s,'localisation',%s,%s,%s,'rejected',%s,%s,%s,%s,%s) returning id""",
                               (src["property_id"], src["need_id"], f"generation failed: {res.failure}", res.model_ref, src["config"], source_id, language, res.failure, src["run_id"], res.latency_ms, res.input_tokens, res.output_tokens)).fetchone()
        else:
            l: Localisation = res.output
            row = conn.execute("""insert into advice (property_id, need_id, body, grounding, model_ref, kind, config, parent_id, language, structured, status, run_id, latency_ms, input_tokens, output_tokens)
                                  values (%s,%s,%s,'[]',%s,'localisation',%s,%s,%s,%s,'draft',%s,%s,%s,%s) returning id""",
                               (src["property_id"], src["need_id"], f"# {l.title}\n\n{l.body}", res.model_ref, src["config"], source_id, l.language,
                                json.dumps(l.model_dump()), src["run_id"], res.latency_ms, res.input_tokens, res.output_tokens)).fetchone()
        res.id = str(row["id"])
    return res

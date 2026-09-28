"""Intelligence layer: reviews, rates and parity, OTA rank, AI-assistant visibility, local events.

Collectors pull from external sources into the tables of migration 006; the API reads them.
Each source is an adapter with the same contract: `configured()` says whether the host has
what it needs (keys, mappings), `collect(conn, prop)` writes rows for one property and
returns how many. Nothing here posts anything to a review site without a stored, approved
reply and a configured token.

Configuration (env, loaded from ~/.hautel/engine.env like the CLI):
  HAUTEL_GOOGLE_BUSINESS_TOKEN   OAuth access token for the Business Profile API (reviews + replies)
                                 per property: properties.branding->>'google_location' = "accounts/{a}/locations/{l}"
  HAUTEL_RATE_API_URL            rate shopper endpoint, {property_id} and {days} are substituted;
  HAUTEL_RATE_API_KEY            JSON response: [{"date","channel","competitor"|null,"rate","currency"?}]
  HAUTEL_RANK_API_URL / _KEY     OTA rank endpoint, same substitution; JSON: [{"site","query","rank","page"?}]
  OPENAI_API_KEY, GOOGLE_AI_API_KEY, ANTHROPIC_API_KEY
                                 assistants the visibility checker asks (Claude works with the engine key)
  PREDICTHQ_TOKEN                local events (PredictHQ). HAUTEL_EVENTS_DAYS (default 45)
"""
from __future__ import annotations

import datetime as dt
import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any

import anthropic
import psycopg
from pydantic import BaseModel, Field

from .matcher import MODEL

# ── helpers ────────────────────────────────────────────────────────────────────

def _get_json(url: str, headers: dict[str, str] | None = None, body: dict[str, Any] | None = None, timeout: int = 30) -> Any:
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, headers={"accept": "application/json", **({"content-type": "application/json"} if data else {}), **(headers or {})})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read() or b"null")


def city_of(prop: dict[str, Any]) -> str:
    return re.split(r"[,(]", prop.get("region") or "Brussels")[0].strip()


def short_name(name: str) -> str:
    return re.split(r"\s*\(", name)[0].strip()


def load_properties(conn: psycopg.Connection, org_id: str | None = None, property_id: str | None = None) -> list[dict[str, Any]]:
    where, params = ["true"], []
    if org_id:
        where.append("p.org_id = %s"); params.append(org_id)
    if property_id:
        where.append("p.id = %s"); params.append(property_id)
    return [dict(r) for r in conn.execute(f"""
        select p.id, p.name, p.region, p.org_id, p.branding, h.segment, h.audience, h.positioning, h.channels, h.strengths, h.weaknesses
          from properties p left join hotel_profiles h on h.property_id = p.id
         where {' and '.join(where)} order by p.name""", tuple(params)).fetchall()]


def _mark(conn: psycopg.Connection, name: str, configured: bool, status: str | None = None, count: int | None = None) -> None:
    conn.execute("""insert into intel_sources (name, configured, last_run_at, last_status, last_count)
                    values (%s, %s, case when %s is null then null else now() end, %s, %s)
                    on conflict (name) do update set configured = excluded.configured,
                      last_run_at = coalesce(excluded.last_run_at, intel_sources.last_run_at),
                      last_status = coalesce(excluded.last_status, intel_sources.last_status),
                      last_count = coalesce(excluded.last_count, intel_sources.last_count)""",
                 (name, configured, status, status, count))
    conn.commit()


# ── sources ────────────────────────────────────────────────────────────────────

class Source:
    name = "base"
    label = "Source"
    needs = ""          # what the host must provide, shown in the UI

    def configured(self) -> bool:
        return False

    def collect(self, conn: psycopg.Connection, prop: dict[str, Any]) -> int:
        raise NotImplementedError


class GoogleReviews(Source):
    """Google Business Profile reviews (API v4). Needs an OAuth token with the business.manage
    scope and, per property, its location name stored in properties.branding.google_location."""
    name = "google_reviews"
    label = "Google reviews"
    needs = "HAUTEL_GOOGLE_BUSINESS_TOKEN and properties.branding.google_location per hotel"
    STARS = {"ONE": 1, "TWO": 2, "THREE": 3, "FOUR": 4, "FIVE": 5}

    def configured(self) -> bool:
        return bool(os.environ.get("HAUTEL_GOOGLE_BUSINESS_TOKEN"))

    def collect(self, conn: psycopg.Connection, prop: dict[str, Any]) -> int:
        location = (prop.get("branding") or {}).get("google_location")
        if not location:
            return 0
        token = os.environ["HAUTEL_GOOGLE_BUSINESS_TOKEN"]
        n, page = 0, None
        while True:
            url = f"https://mybusiness.googleapis.com/v4/{location}/reviews?pageSize=50" + (f"&pageToken={page}" if page else "")
            data = _get_json(url, {"Authorization": f"Bearer {token}"})
            for r in data.get("reviews", []):
                conn.execute("""insert into reviews (property_id, source, external_id, author, rating, body, review_at, reply_text, posted_at)
                                values (%s, 'google', %s, %s, %s, %s, %s, %s, %s)
                                on conflict (source, external_id) do update set rating = excluded.rating, body = excluded.body,
                                  reply_text = coalesce(reviews.reply_text, excluded.reply_text), posted_at = coalesce(reviews.posted_at, excluded.posted_at)""",
                             (prop["id"], r.get("reviewId"), (r.get("reviewer") or {}).get("displayName"), self.STARS.get(r.get("starRating"), None),
                              r.get("comment") or "", r.get("createTime"), (r.get("reviewReply") or {}).get("comment"), (r.get("reviewReply") or {}).get("updateTime")))
                n += 1
            page = data.get("nextPageToken")
            if not page:
                break
        conn.commit()
        return n

    def post_reply(self, prop: dict[str, Any], external_id: str, text: str) -> bool:
        location = (prop.get("branding") or {}).get("google_location")
        if not (location and self.configured()):
            return False
        req = urllib.request.Request(f"https://mybusiness.googleapis.com/v4/{location}/reviews/{external_id}/reply", method="PUT",
                                     data=json.dumps({"comment": text}).encode(),
                                     headers={"Authorization": f"Bearer {os.environ['HAUTEL_GOOGLE_BUSINESS_TOKEN']}", "content-type": "application/json"})
        with urllib.request.urlopen(req, timeout=30):
            return True


class RateShopper(Source):
    """Generic rate-shopping feed (StayAPI, OTA Insight, a channel-manager export). The vendor
    endpoint is configured as a URL template; the response is normalised to one row per
    date, channel and competitor."""
    name = "rates"
    label = "Rates and parity"
    needs = "HAUTEL_RATE_API_URL (with {property_id} and {days}) and HAUTEL_RATE_API_KEY"

    def configured(self) -> bool:
        return bool(os.environ.get("HAUTEL_RATE_API_URL"))

    def collect(self, conn: psycopg.Connection, prop: dict[str, Any]) -> int:
        url = os.environ["HAUTEL_RATE_API_URL"].format(property_id=prop["id"], days=int(os.environ.get("HAUTEL_RATE_DAYS", "14")))
        rows = _get_json(url, {"Authorization": f"Bearer {os.environ.get('HAUTEL_RATE_API_KEY', '')}"})
        n = 0
        for r in rows or []:
            conn.execute("insert into rate_snapshots (property_id, stay_date, channel, competitor, rate, currency, source) values (%s, %s, %s, %s, %s, %s, 'rates')",
                         (prop["id"], r["date"], r["channel"], r.get("competitor"), r["rate"], r.get("currency", "EUR")))
            n += 1
        conn.commit()
        return n


class OtaRank(Source):
    """OTA search position for a city query, from the same kind of vendor feed."""
    name = "ota_rank"
    label = "OTA search rank"
    needs = "HAUTEL_RANK_API_URL (with {property_id}) and HAUTEL_RANK_API_KEY"

    def configured(self) -> bool:
        return bool(os.environ.get("HAUTEL_RANK_API_URL"))

    def collect(self, conn: psycopg.Connection, prop: dict[str, Any]) -> int:
        url = os.environ["HAUTEL_RANK_API_URL"].format(property_id=prop["id"], city=urllib.parse.quote(city_of(prop)))
        rows = _get_json(url, {"Authorization": f"Bearer {os.environ.get('HAUTEL_RANK_API_KEY', '')}"})
        n = 0
        for r in rows or []:
            conn.execute("insert into rank_snapshots (property_id, site, query, rank, page, source) values (%s, %s, %s, %s, %s, 'ota_rank')",
                         (prop["id"], r["site"], r.get("query") or f"hotels in {city_of(prop)}", r.get("rank"), r.get("page")))
            n += 1
        conn.commit()
        return n


class Recommendations(BaseModel):
    hotels: list[str] = Field(description="Hotel names recommended in the answer, in the order they appear.")


class AIVisibility(Source):
    """Asks each configured assistant the questions a guest would ask and records whether the
    hotel is named. Claude runs with the engine key; ChatGPT and Gemini need their own keys."""
    name = "ai_visibility"
    label = "AI-assistant visibility"
    needs = "ANTHROPIC_API_KEY (Claude, present with the engine), OPENAI_API_KEY (ChatGPT), GOOGLE_AI_API_KEY (Gemini)"

    def assistants(self) -> list[str]:
        out = []
        if os.environ.get("ANTHROPIC_API_KEY"): out.append("claude")
        if os.environ.get("OPENAI_API_KEY"): out.append("chatgpt")
        if os.environ.get("GOOGLE_AI_API_KEY"): out.append("gemini")
        return out

    def configured(self) -> bool:
        return bool(self.assistants())

    def queries(self, prop: dict[str, Any]) -> list[str]:
        c, seg = city_of(prop), (prop.get("segment") or "").lower()
        return [f"best {seg + ' ' if seg else ''}hotel in {c} for a weekend", f"hotel in {c} with meeting rooms near the centre", f"where to stay in {c} with family"]

    def ask(self, assistant: str, query: str) -> tuple[str, str]:
        prompt = f"{query}. Recommend up to five specific hotels by name, one line each, with one reason."
        if assistant == "claude":
            client = anthropic.Anthropic()
            r = client.messages.create(model=MODEL, max_tokens=600, messages=[{"role": "user", "content": prompt}])
            return "".join(getattr(b, "text", "") for b in r.content), r.model
        if assistant == "chatgpt":
            model = os.environ.get("HAUTEL_OPENAI_MODEL", "gpt-4o-mini")
            data = _get_json("https://api.openai.com/v1/chat/completions", {"Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}"},
                             {"model": model, "messages": [{"role": "user", "content": prompt}], "max_tokens": 600})
            return data["choices"][0]["message"]["content"], data.get("model", model)
        if assistant == "gemini":
            model = os.environ.get("HAUTEL_GEMINI_MODEL", "gemini-2.0-flash")
            data = _get_json(f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={os.environ['GOOGLE_AI_API_KEY']}",
                             None, {"contents": [{"parts": [{"text": prompt}]}]})
            return "".join(p.get("text", "") for p in data["candidates"][0]["content"]["parts"]), model
        raise ValueError(assistant)

    def extract(self, answer: str) -> list[str]:
        client = anthropic.Anthropic()
        r = client.messages.parse(model=MODEL, max_tokens=400, output_format=Recommendations,
                                  messages=[{"role": "user", "content": "List the hotel names recommended in this text, in order. Text:\n\n" + answer}])
        return r.parsed_output.hotels if r.parsed_output else []

    def collect(self, conn: psycopg.Connection, prop: dict[str, Any]) -> int:
        n = 0
        me = short_name(prop["name"]).lower()
        tokens = [t for t in re.findall(r"[a-zà-ÿ]+", me) if len(t) > 3 and t not in ("hotel", "hotels", "brussels", "city", "grand", "place", "the")]
        for assistant in self.assistants():
            for q in self.queries(prop):
                answer, model_ref = self.ask(assistant, q)
                hotels = self.extract(answer)
                hit = next((i for i, h in enumerate(hotels) if any(t in h.lower() for t in tokens) or me in h.lower()), None)
                others = [h for i, h in enumerate(hotels) if i != hit][:5]
                conn.execute("""insert into ai_answers (property_id, assistant, query, mentioned, position, others, answer, model_ref, source)
                                values (%s, %s, %s, %s, %s, %s, %s, %s, 'ai_visibility')""",
                             (prop["id"], assistant, q, hit is not None, (hit + 1) if hit is not None else None, others, answer, model_ref))
                n += 1
        conn.commit()
        return n


class Events(Source):
    """Local events from PredictHQ for the property's city."""
    name = "events"
    label = "Local events"
    needs = "PREDICTHQ_TOKEN"

    def configured(self) -> bool:
        return bool(os.environ.get("PREDICTHQ_TOKEN"))

    def collect(self, conn: psycopg.Connection, prop: dict[str, Any]) -> int:
        days = int(os.environ.get("HAUTEL_EVENTS_DAYS", "45"))
        today = dt.date.today()
        q = urllib.parse.urlencode({"q": city_of(prop), "active.gte": today.isoformat(), "active.lte": (today + dt.timedelta(days=days)).isoformat(),
                                    "category": "conferences,expos,concerts,festivals,sports,community", "sort": "start", "limit": 20})
        data = _get_json(f"https://api.predicthq.com/v1/events/?{q}", {"Authorization": f"Bearer {os.environ['PREDICTHQ_TOKEN']}"})
        n = 0
        for e in data.get("results", []):
            rank = e.get("rank") or 0
            impact = "high" if rank >= 70 else "medium" if rank >= 40 else "low"
            conn.execute("""insert into local_events (property_id, city, name, kind, starts_on, ends_on, impact, lift_pct, visitors, source, external_id)
                            values (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'events', %s)
                            on conflict (source, external_id) do update set starts_on = excluded.starts_on, ends_on = excluded.ends_on, impact = excluded.impact, visitors = excluded.visitors""",
                         (prop["id"], city_of(prop), e.get("title"), e.get("category"), e["start"][:10], (e.get("end") or e["start"])[:10],
                          impact, {"high": 20, "medium": 10, "low": 4}[impact], e.get("phq_attendance"), f"{prop['id']}:{e['id']}"))
            n += 1
        conn.commit()
        return n


SOURCES: list[Source] = [GoogleReviews(), RateShopper(), OtaRank(), AIVisibility(), Events()]


def status(conn: psycopg.Connection) -> list[dict[str, Any]]:
    last = {r["name"]: dict(r) for r in conn.execute("select * from intel_sources").fetchall()}
    return [{"name": s.name, "label": s.label, "configured": s.configured(), "needs": s.needs,
             "last_run_at": (last.get(s.name) or {}).get("last_run_at"), "last_status": (last.get(s.name) or {}).get("last_status"),
             "last_count": (last.get(s.name) or {}).get("last_count")} for s in SOURCES]


def collect(conn: psycopg.Connection, org_id: str | None = None, only: set[str] | None = None) -> dict[str, Any]:
    """Run every configured collector for the properties of an organisation. Unconfigured sources
    are recorded as skipped so the UI can say what is missing."""
    props = load_properties(conn, org_id)
    out: dict[str, Any] = {}
    for s in SOURCES:
        if only and s.name not in only:
            continue
        if not s.configured():
            _mark(conn, s.name, False)
            out[s.name] = {"skipped": True, "needs": s.needs}
            continue
        total, errors = 0, []
        for p in props:
            try:
                total += s.collect(conn, p)
            except Exception as e:  # one property failing must not stop the others
                conn.rollback()
                errors.append(f"{short_name(p['name'])}: {e}")
        _mark(conn, s.name, True, "ok" if not errors else f"{len(errors)} error(s): {errors[0]}", total)
        out[s.name] = {"rows": total, "errors": errors}
    return out


# ── reply drafting (Claude, grounded in the hotel profile) ─────────────────────

REPLY_SYSTEM = """You write replies to guest reviews on behalf of a hotel's marketing team. You receive the HOTEL (name, segment, audience, positioning, strengths, weaknesses) and one REVIEW (source, rating, language, author, text).

Rules:
1. Reply in the language of the review. Address the guest by first name if one is given, otherwise "Dear guest".
2. Be specific: refer to what the guest actually wrote. Never invent facts, offers, compensation or promises the hotel did not make.
3. For criticism: acknowledge it plainly, apologise once, say the point is passed to the team. Do not argue, do not over-explain.
4. For praise: thank the guest and pick up one concrete thing they enjoyed, tying it to the hotel's positioning where natural.
5. Length: 40 to 90 words. Warm, direct, no marketing slogans, no exclamation marks.
6. Sign with the hotel's short name and "the team"."""


class ReplyDraft(BaseModel):
    reply: str = Field(description="The reply text, ready to post.")
    language: str = Field(description="Language of the reply: nl, fr, en, de or other.")
    handles: list[str] = Field(description="The points from the review the reply responds to.")
    caution: str | None = Field(default=None, description="Anything a person should check before posting (a claim, a complaint that needs follow-up). Null if nothing.")


@dataclass
class DraftResult:
    draft: ReplyDraft | None
    model_ref: str
    latency_ms: int
    input_tokens: int
    output_tokens: int
    failure: str | None = None


def hotel_context(prop: dict[str, Any]) -> dict[str, Any]:
    return {"name": prop["name"], "short_name": short_name(prop["name"]), "city": city_of(prop), "segment": prop.get("segment"),
            "audience": prop.get("audience"), "positioning": prop.get("positioning"), "strengths": prop.get("strengths"), "weaknesses": prop.get("weaknesses")}


def draft_reply(prop: dict[str, Any], review: dict[str, Any], client: anthropic.Anthropic | None = None) -> DraftResult:
    client = client or anthropic.Anthropic()
    payload = {"HOTEL": hotel_context(prop), "REVIEW": {k: review.get(k) for k in ("source", "rating", "language", "author", "body")}}
    t0 = time.perf_counter()
    r = client.messages.parse(model=MODEL, max_tokens=1200,
                              system=[{"type": "text", "text": REPLY_SYSTEM, "cache_control": {"type": "ephemeral"}}],
                              messages=[{"role": "user", "content": json.dumps(payload, ensure_ascii=False, indent=1)}], output_format=ReplyDraft)
    res = DraftResult(draft=None, model_ref=r.model, latency_ms=int((time.perf_counter() - t0) * 1000),
                      input_tokens=r.usage.input_tokens, output_tokens=r.usage.output_tokens)
    if r.stop_reason == "refusal" or r.parsed_output is None:
        res.failure = f"no draft (stop_reason={r.stop_reason})"
        return res
    res.draft = r.parsed_output
    return res


def draft_stored_review(conn: psycopg.Connection, review_id: str, client: anthropic.Anthropic | None = None) -> DraftResult:
    row = conn.execute("select * from reviews where id = %s", (review_id,)).fetchone()
    if not row:
        raise LookupError("review not found")
    prop = load_properties(conn, property_id=str(row["property_id"]))[0]
    res = draft_reply(prop, dict(row), client)
    if res.draft:
        conn.execute("update reviews set reply_draft = %s, reply_draft_meta = %s where id = %s",
                     (res.draft.reply, json.dumps({"model": res.model_ref, "latency_ms": res.latency_ms, "input_tokens": res.input_tokens,
                                                    "output_tokens": res.output_tokens, "handles": res.draft.handles, "caution": res.draft.caution}), review_id))
        conn.commit()
    return res


def approve_reply(conn: psycopg.Connection, review_id: str, text: str, user_id: str | None) -> dict[str, Any]:
    """Store the approved reply. Posting happens only when the source has a configured adapter."""
    row = conn.execute("select r.*, p.branding, p.name from reviews r join properties p on p.id = r.property_id where r.id = %s", (review_id,)).fetchone()
    if not row:
        raise LookupError("review not found")
    conn.execute("update reviews set reply_text = %s, replied_at = now(), replied_by = %s where id = %s", (text, user_id, review_id))
    posted = False
    if row["source"] == "google" and row["external_id"]:
        try:
            posted = GoogleReviews().post_reply({"branding": row["branding"], "name": row["name"]}, row["external_id"], text)
        except Exception:
            posted = False
    if posted:
        conn.execute("update reviews set posted_at = now() where id = %s", (review_id,))
    conn.commit()
    return {"id": review_id, "posted": posted, "queued": not posted}


# ── read model for the API ─────────────────────────────────────────────────────

def property_intel(conn: psycopg.Connection, property_id: str) -> dict[str, Any]:
    q = lambda sql, *p: [dict(r) for r in conn.execute(sql, p).fetchall()]  # noqa: E731
    return {
        "reviews": q("select id, source, external_id, author, rating, language, body, review_at, reply_draft, reply_draft_meta, reply_text, replied_at, posted_at from reviews where property_id = %s order by review_at desc limit 200", property_id),
        # latest capture per (date, channel, competitor)
        "rates": q("""select distinct on (stay_date, channel, competitor) stay_date, channel, competitor, rate, currency, captured_at
                        from rate_snapshots where property_id = %s and stay_date >= current_date order by stay_date, channel, competitor, captured_at desc""", property_id),
        "ranks": q("""select distinct on (site, query) site, query, rank, page, captured_at from rank_snapshots where property_id = %s order by site, query, captured_at desc""", property_id),
        "ai_answers": q("""select distinct on (assistant, query) assistant, query, mentioned, position, others, model_ref, captured_at
                             from ai_answers where property_id = %s order by assistant, query, captured_at desc""", property_id),
        "events": q("select id, city, name, kind, starts_on, ends_on, impact, lift_pct, visitors, source from local_events where property_id = %s and ends_on >= current_date order by starts_on limit 50", property_id),
    }

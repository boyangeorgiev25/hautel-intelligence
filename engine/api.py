"""HTTP API for the demo frontend — a thin layer over the database and the WP2 engine.

Read endpoints return the same rows the reviewer login can see; the one write
endpoint runs the engine for a need (same code path as `hautel-engine match`).
Nothing here bypasses the engine's transaction: a failing sink still leaves nothing.

Run:  hautel-api            (port 8765; HAUTEL_API_PORT to change)
Env:  ~/.hautel/engine.env is loaded like the CLI. HAUTEL_DATABASE_URL selects the
      database — set it to the local test env for the frontend demo.
"""
from __future__ import annotations

import json
import os
import pathlib
import sys
import threading
import time
import urllib.error
import urllib.request
from typing import Any

import anthropic
import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from . import db
from .baseline import baseline_pick
from .cli import _load_env_file, _redact
from .workflow import SinkUnavailable, run_need

app = FastAPI(title="Hautel Intelligence — engine API", version="0.2.0")
# CORS: HAUTEL_CORS_ORIGINS="https://app.example,http://localhost:5173" (default: local dev servers only)
_origins = [o.strip() for o in os.environ.get("HAUTEL_CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",") if o.strip()]
app.add_middleware(CORSMiddleware, allow_origins=_origins, allow_methods=["*"], allow_headers=["*"])


# ── Authentication ─────────────────────────────────────────────────────────────
# Sign-in is Supabase Auth on the Frankfurt project. The app sends the user's access
# token; the API verifies it by asking Supabase who the token belongs to, and reads
# the role from app_metadata.role ('lead' may write, anything else is read-only).
# Set HAUTEL_API_AUTH=off for the local demo without sign-in.
SUPABASE_URL = os.environ.get("HAUTEL_SUPABASE_URL", "").rstrip("/")
SUPABASE_ANON_KEY = os.environ.get("HAUTEL_SUPABASE_ANON_KEY", "")
AUTH_ON = os.environ.get("HAUTEL_API_AUTH", "on" if SUPABASE_URL else "off").lower() != "off"
_user_cache: dict[str, tuple[float, dict[str, Any]]] = {}
_cache_lock = threading.Lock()


def _supabase_user(token: str) -> dict[str, Any]:
    now = time.time()
    with _cache_lock:
        hit = _user_cache.get(token)
        if hit and hit[0] > now:
            return hit[1]
    req = urllib.request.Request(f"{SUPABASE_URL}/auth/v1/user", headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {token}"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            user = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        raise HTTPException(401, "invalid or expired session") from e
    except Exception as e:  # network
        raise HTTPException(503, f"auth service unreachable: {e}") from e
    info = {"id": user.get("id"), "email": user.get("email"), "role": (user.get("app_metadata") or {}).get("role", "reviewer")}
    with _cache_lock:
        _user_cache[token] = (now + 60, info)
    return info


def current_user(request: Request) -> dict[str, Any]:
    if not AUTH_ON:
        return {"id": None, "email": "local-demo", "role": "lead"}
    auth = request.headers.get("authorization", "")
    if not auth.lower().startswith("bearer "):
        raise HTTPException(401, "sign in required")
    return _supabase_user(auth[7:].strip())


def writer(user: dict[str, Any] = Depends(current_user)) -> dict[str, Any]:
    if user["role"] != "lead":
        raise HTTPException(403, "read-only account")
    return user


@app.get("/me")
def me(user: dict[str, Any] = Depends(current_user)) -> dict[str, Any]:
    return {**user, "auth": "supabase" if AUTH_ON else "off"}


def _rows(conn, sql: str, params: tuple = ()) -> list[dict[str, Any]]:
    return [db.jsonable(dict(r)) for r in conn.execute(sql, params).fetchall()]


@app.get("/health")
def health() -> dict[str, Any]:  # public: liveness only
    with db.connect() as conn:
        v = conn.execute("select current_setting('server_version') as v").fetchone()["v"]
    return {"ok": True, "database": _redact(db.database_url()), "postgres": v}


@app.get("/datasets")
def datasets(user: dict[str, Any] = Depends(current_user)) -> list[dict[str, Any]]:
    with db.connect() as conn:
        return _rows(conn, """
            select d.name, d.description, d.loaded_at,
                   (select count(*) from consultants c where c.dataset = d.name) as consultants,
                   (select count(*) from marketing_needs n where n.dataset = d.name) as needs,
                   (select count(*) from marketing_needs n where n.dataset = d.name and n.status = 'open') as open_needs
              from datasets d order by d.name desc""")


@app.get("/organizations")
def organizations(dataset: str | None = Query(None, pattern="^(synthetic|real)$"), user: dict[str, Any] = Depends(current_user)) -> list[dict[str, Any]]:
    """Workspaces for the frontend: each organization with its properties (and hotel segment)."""
    where, params = ["o.name <> 'probe'"], []
    if dataset:
        where.append("o.dataset = %s"); params.append(dataset)
    with db.connect() as conn:
        return _rows(conn, f"""
            select o.id, o.name, o.kind, o.dataset,
                   coalesce((select jsonb_agg(jsonb_build_object('id', p.id, 'name', p.name, 'region', p.region, 'segment', h.segment) order by p.name)
                               from properties p left join hotel_profiles h on h.property_id = p.id where p.org_id = o.id), '[]') as properties,
                   (select count(*) from properties p where p.org_id = o.id) as property_count,
                   (select count(*) from marketing_needs n join properties p on p.id = n.property_id where p.org_id = o.id) as need_count
              from organizations o
             where {' and '.join(where)}
             order by o.dataset desc, o.name""", tuple(params))


LATEST_RUN = """left join lateral (select id as run_id, decision, brief_language, need_summary, core_skills, constraints_checked,
                                          escalation_reason, requires_group_signoff, signoff_rule, model_ref, latency_ms,
                                          input_tokens, output_tokens, raw_output, created_at as run_at
                                     from match_runs r where r.need_id = n.id order by created_at desc limit 1) lr on true"""


@app.get("/needs")
def needs(dataset: str | None = Query(None, pattern="^(synthetic|real)$"), status: str | None = None, org_id: str | None = None, user: dict[str, Any] = Depends(current_user)) -> list[dict[str, Any]]:
    where, params = ["true"], []
    if dataset:
        where.append("n.dataset = %s"); params.append(dataset)
    if status:
        where.append("n.status = %s"); params.append(status)
    if org_id:
        where.append("p.org_id = %s"); params.append(org_id)
    with db.connect() as conn:
        return _rows(conn, f"""
            select n.id, n.title, n.description, n.category, n.urgency, n.budget_band, n.status, n.dataset, n.created_at,
                   p.id as property_id, p.name as property_name, p.region, p.org_id, o.name as organization,
                   (select count(*) from match_runs r where r.need_id = n.id) as runs,
                   case when lr.run_id is null then null else to_jsonb(lr) end as latest_run
              from marketing_needs n
              join properties p on p.id = n.property_id
              join organizations o on o.id = p.org_id
              {LATEST_RUN}
             where {' and '.join(where)}
             order by n.dataset desc, n.created_at desc, n.title""", tuple(params))


class NewNeed(BaseModel):
    property_id: str
    title: str = Field(min_length=2, max_length=200)
    description: str = Field(min_length=10)
    category: str = Field(min_length=2, max_length=40)
    urgency: str = Field(pattern="^(low|normal|high)$", default="normal")
    budget_band: str | None = None


@app.post("/needs", status_code=201)
def create_need(body: NewNeed, user: dict[str, Any] = Depends(writer)) -> dict[str, Any]:
    """Save a brief. The need inherits the dataset of its property, so the engine picks the right pool."""
    with db.connect() as conn:
        prop = conn.execute("select id, dataset from properties where id = %s", (body.property_id,)).fetchone()
        if not prop:
            raise HTTPException(404, "property not found")
        with conn.transaction():
            row = conn.execute(
                """insert into marketing_needs (property_id, title, description, category, urgency, budget_band, status, dataset)
                   values (%s, %s, %s, %s, %s, %s, 'open', %s) returning id""",
                (body.property_id, body.title.strip(), body.description.strip(), body.category.strip().lower(),
                 body.urgency, body.budget_band, prop["dataset"]),
            ).fetchone()
        return {"id": str(row["id"]), "dataset": prop["dataset"]}


class NeedUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=2, max_length=200)
    description: str | None = Field(default=None, min_length=10)
    category: str | None = Field(default=None, min_length=2, max_length=40)
    urgency: str | None = Field(default=None, pattern="^(low|normal|high)$")
    budget_band: str | None = None
    clear_budget: bool = False


@app.patch("/needs/{need_id}")
def update_need(need_id: str, body: NeedUpdate, user: dict[str, Any] = Depends(writer)) -> dict[str, Any]:
    """Edit a brief. Refused once the engine has run on it (results must match the brief they came from); reset first."""
    with db.connect() as conn:
        row = conn.execute("select id, (select count(*) from match_runs r where r.need_id = n.id) as runs from marketing_needs n where id = %s", (need_id,)).fetchone()
        if not row:
            raise HTTPException(404, "need not found")
        if row["runs"]:
            raise HTTPException(409, "this brief has engine runs; reset it before editing so results keep matching the brief")
        sets, params = [], []
        for col in ("title", "description", "category", "urgency"):
            val = getattr(body, col)
            if val is not None:
                sets.append(f"{col} = %s"); params.append(val.strip().lower() if col == "category" else val.strip())
        if body.clear_budget:
            sets.append("budget_band = null")
        elif body.budget_band is not None:
            sets.append("budget_band = %s"); params.append(body.budget_band)
        if not sets:
            return {"id": need_id, "updated": False}
        with conn.transaction():
            conn.execute(f"update marketing_needs set {', '.join(sets)} where id = %s", (*params, need_id))
        return {"id": need_id, "updated": True}


@app.delete("/needs/{need_id}")
def delete_need(need_id: str, user: dict[str, Any] = Depends(writer)) -> dict[str, Any]:
    """Delete a brief and everything the engine produced for it (runs, matches, tasks, evaluations), in one transaction."""
    with db.connect() as conn:
        if not conn.execute("select 1 from marketing_needs where id = %s", (need_id,)).fetchone():
            raise HTTPException(404, "need not found")
        with conn.transaction():
            db.reset_need(conn, need_id)
            conn.execute("delete from marketing_needs where id = %s", (need_id,))
        return {"deleted": need_id}


@app.get("/needs/{need_id}")
def need_detail(need_id: str, user: dict[str, Any] = Depends(current_user)) -> dict[str, Any]:
    with db.connect() as conn:
        try:
            need = db.load_need(conn, need_id)
        except LookupError:
            raise HTTPException(404, "need not found")
        b = baseline_pick(conn, need_id)
        return {
            **db.jsonable(need.__dict__),
            "baseline": {"consultant_id": b.consultant_id, "consultant_name": b.consultant_name, "hits": b.hits, "matched_words": b.matched_words},
            "results": _results(conn, need_id),
        }


def _results(conn, need_id: str) -> dict[str, Any]:
    return {
        "runs": _rows(conn, """
            select id, decision, brief_language, need_summary, core_skills, constraints_checked, escalation_reason,
                   requires_group_signoff, signoff_rule, candidate_count, model_ref, latency_ms, input_tokens, output_tokens,
                   raw_output, created_at
              from match_runs where need_id = %s order by created_at desc""", (need_id,)),
        "matches": _rows(conn, """
            select m.id, m.run_id, m.rank, m.consultant_id, c.full_name as consultant_name, m.score, m.status,
                   m.rationale, m.model_ref, m.created_at
              from matches m join consultants c on c.id = m.consultant_id
             where m.need_id = %s order by m.created_at desc, m.rank""", (need_id,)),
        "tasks": _rows(conn, """
            select t.id, t.title, t.detail, t.status, t.origin_kind, t.origin_id, t.created_at,
                   u.full_name as assigned_to_name, u.email as assigned_to_email
              from tasks t left join users u on u.id = t.assigned_to
             where t.origin_kind in ('match','escalation')
               and (t.origin_id in (select id from matches where need_id = %(n)s)
                 or t.origin_id in (select id from match_runs where need_id = %(n)s))
             order by t.created_at desc""", {"n": need_id}),
    }


@app.get("/needs/{need_id}/results")
def need_results(need_id: str, user: dict[str, Any] = Depends(current_user)) -> dict[str, Any]:
    with db.connect() as conn:
        return _results(conn, need_id)


@app.get("/consultants")
def consultants(dataset: str | None = Query(None, pattern="^(synthetic|real)$"), user: dict[str, Any] = Depends(current_user)) -> list[dict[str, Any]]:
    with db.connect() as conn:
        pool = db.load_pool(conn, {"dataset": dataset} if dataset else None)
        return [db.jsonable(c.__dict__) for c in pool]


@app.get("/tasks")
def tasks(dataset: str | None = Query(None, pattern="^(synthetic|real)$"), status: str | None = None, org_id: str | None = None, user: dict[str, Any] = Depends(current_user)) -> list[dict[str, Any]]:
    where, params = ["t.origin_kind in ('match','escalation')"], []
    if dataset:
        where.append("p.dataset = %s"); params.append(dataset)
    if status:
        where.append("t.status = %s"); params.append(status)
    if org_id:
        where.append("p.org_id = %s"); params.append(org_id)
    with db.connect() as conn:
        return _rows(conn, f"""
            select t.id, t.title, t.detail, t.status, t.origin_kind, t.origin_id, t.created_at, t.closed_at,
                   t.property_id, p.name as property_name, p.org_id, u.full_name as assigned_to_name, u.email as assigned_to_email,
                   case t.origin_kind when 'match' then (select need_id from matches m where m.id = t.origin_id)
                                      when 'escalation' then (select need_id from match_runs r where r.id = t.origin_id) end as need_id
              from tasks t join properties p on p.id = t.property_id left join users u on u.id = t.assigned_to
             where {' and '.join(where)} order by t.created_at desc""", tuple(params))


class TaskUpdate(BaseModel):
    status: str = Field(pattern="^(open|in_progress|done|cancelled)$")


@app.patch("/tasks/{task_id}")
def update_task(task_id: str, body: TaskUpdate, user: dict[str, Any] = Depends(writer)) -> dict[str, Any]:
    with db.connect() as conn:
        with conn.transaction():
            row = conn.execute(
                "update tasks set status = %s, closed_at = case when %s in ('done','cancelled') then now() else null end where id = %s returning id, status, closed_at",
                (body.status, body.status, task_id),
            ).fetchone()
        if not row:
            raise HTTPException(404, "task not found")
        return db.jsonable(dict(row))


@app.post("/needs/{need_id}/match")
def match(need_id: str, user: dict[str, Any] = Depends(writer)) -> dict[str, Any]:
    """Run the engine for one need: interpretation → ranked match or escalation → routed task, one transaction."""
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise HTTPException(503, "ANTHROPIC_API_KEY not configured on the API host")
    client = anthropic.Anthropic()
    with db.connect() as conn:
        try:
            db.load_need(conn, need_id)
        except LookupError:
            raise HTTPException(404, "need not found")
        try:
            out = run_need(conn, need_id, client=client)
        except SinkUnavailable as e:
            conn.rollback()
            raise HTTPException(502, f"workflow sink unavailable, nothing written: {e}")
        return db.jsonable(out.__dict__)


@app.post("/needs/{need_id}/reset")
def reset(need_id: str, user: dict[str, Any] = Depends(writer)) -> dict[str, Any]:
    """Remove the engine's outputs for a need so it can be re-run. Inputs are never touched."""
    with db.connect() as conn:
        try:
            db.load_need(conn, need_id)
        except LookupError:
            raise HTTPException(404, "need not found")
        db.reset_need(conn, need_id)
        return {"reset": need_id}


def main() -> int:
    _load_env_file(pathlib.Path.home() / ".hautel" / "engine.env")
    print(f"database: {_redact(db.database_url())} | auth: {'supabase' if AUTH_ON else 'OFF'} | cors: {_origins}", file=sys.stderr)
    uvicorn.run(app, host=os.environ.get("HAUTEL_API_HOST", "127.0.0.1"), port=int(os.environ.get("HAUTEL_API_PORT", "8765")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Database access: context assembly (read) and workflow write-back.

Reads: the need, its hotel profile, the property's and org's documents, and the
consultant pool with expertise + documents. Writes: match_runs, matches, tasks,
in ONE transaction, so a failing sink leaves nothing half-written.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Any

import psycopg
from psycopg.rows import dict_row

LOCAL_URL = f"postgresql://postgres:{os.environ.get('HAUTEL_DB_PASS', 'hautel-dev-only')}@localhost:54329/hautel"


def database_url() -> str:
    return os.environ.get("HAUTEL_DATABASE_URL") or LOCAL_URL


def connect() -> psycopg.Connection:
    return psycopg.connect(database_url(), row_factory=dict_row)


@dataclass
class Need:
    id: str
    property_id: str
    org_id: str
    property_name: str
    region: str | None
    title: str
    description: str
    category: str
    urgency: str
    budget_band: str | None
    status: str
    profile: dict[str, Any] | None
    property_documents: list[dict[str, Any]] = field(default_factory=list)
    org_documents: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class Consultant:
    id: str
    full_name: str
    kind: str
    bio: str | None
    languages: list[str]
    region: str | None
    day_rate_band: str | None
    expertise: list[dict[str, Any]] = field(default_factory=list)
    documents: list[dict[str, Any]] = field(default_factory=list)


def load_need(conn: psycopg.Connection, need_id: str) -> Need:
    row = conn.execute(
        """
        select n.*, p.name as property_name, p.region, p.org_id,
               to_jsonb(h) - 'id' - 'property_id' - 'updated_at' as profile
          from marketing_needs n
          join properties p on p.id = n.property_id
          left join hotel_profiles h on h.property_id = p.id
         where n.id = %s
        """,
        (need_id,),
    ).fetchone()
    if not row:
        raise LookupError(f"need {need_id} not found")
    docs = conn.execute(
        """
        select id, kind, title, body, source, property_id, org_id
          from documents
         where consultant_id is null
           and (property_id = %s or (property_id is null and org_id = %s))
         order by property_id nulls last, created_at
        """,
        (row["property_id"], row["org_id"]),
    ).fetchall()
    return Need(
        id=str(row["id"]),
        property_id=str(row["property_id"]),
        org_id=str(row["org_id"]),
        property_name=row["property_name"],
        region=row["region"],
        title=row["title"],
        description=row["description"],
        category=row["category"],
        urgency=row["urgency"],
        budget_band=row["budget_band"],
        status=row["status"],
        profile=row["profile"],
        property_documents=[_doc(d) for d in docs if d["property_id"]],
        org_documents=[_doc(d) for d in docs if not d["property_id"]],
    )


def load_pool(conn: psycopg.Connection, candidate_filter: dict[str, Any] | None = None) -> list[Consultant]:
    """The consultant pool. `candidate_filter` narrows it (used by the empty-pool test)."""
    where, params = ["true"], []
    for key, value in (candidate_filter or {}).items():
        if key not in {"region", "kind", "day_rate_band"}:
            raise ValueError(f"unsupported candidate filter: {key}")
        where.append(f"c.{key} = %s")
        params.append(value)
    rows = conn.execute(
        f"""
        select c.*,
               coalesce((select jsonb_agg(jsonb_build_object('skill', e.skill, 'level', e.level, 'evidence', e.evidence) order by e.skill)
                           from consultant_expertise e where e.consultant_id = c.id), '[]') as expertise,
               coalesce((select jsonb_agg(jsonb_build_object('id', d.id, 'kind', d.kind, 'title', d.title, 'body', d.body) order by d.created_at)
                           from documents d where d.consultant_id = c.id), '[]') as documents
          from consultants c
         where {' and '.join(where)}
         order by c.full_name
        """,
        params,
    ).fetchall()
    return [
        Consultant(
            id=str(r["id"]), full_name=r["full_name"], kind=r["kind"], bio=r["bio"],
            languages=list(r["languages"] or []), region=r["region"], day_rate_band=r["day_rate_band"],
            expertise=r["expertise"], documents=r["documents"],
        )
        for r in rows
    ]


def marketing_lead(conn: psycopg.Connection, org_id: str) -> dict[str, Any] | None:
    return conn.execute(
        """
        select u.id, u.full_name, u.email
          from memberships m join users u on u.id = m.user_id
         where m.org_id = %s and m.role = 'org_admin' and m.property_id is null
         order by u.created_at limit 1
        """,
        (org_id,),
    ).fetchone()


def list_open_needs(conn: psycopg.Connection) -> list[str]:
    return [str(r["id"]) for r in conn.execute("select id from marketing_needs where status = 'open' order by id")]


def wp2_counts(conn: psycopg.Connection, need_id: str) -> dict[str, int]:
    r = conn.execute(
        """
        select (select count(*) from match_runs where need_id = %(n)s) as runs,
               (select count(*) from matches where need_id = %(n)s) as matches,
               (select count(*) from tasks t where t.origin_kind in ('match','escalation')
                   and (t.origin_id in (select id from matches where need_id = %(n)s)
                     or t.origin_id in (select id from match_runs where need_id = %(n)s))) as tasks
        """,
        {"n": need_id},
    ).fetchone()
    return {k: int(v) for k, v in r.items()}


def reset_need(conn: psycopg.Connection, need_id: str) -> None:
    """Remove every WP2 output for a need so it can be re-run. Inputs are never touched."""
    with conn.transaction():
        conn.execute(
            """
            delete from evaluations where (subject_kind = 'match' and subject_id in (select id from matches where need_id = %(n)s))
                                       or (subject_kind = 'match_run' and subject_id in (select id from match_runs where need_id = %(n)s))
            """,
            {"n": need_id},
        )
        conn.execute(
            """
            delete from tasks where origin_kind in ('match','escalation')
               and (origin_id in (select id from matches where need_id = %(n)s)
                 or origin_id in (select id from match_runs where need_id = %(n)s))
            """,
            {"n": need_id},
        )
        conn.execute("delete from matches where need_id = %s", (need_id,))
        conn.execute("delete from match_runs where need_id = %s", (need_id,))
        conn.execute("update marketing_needs set status = 'open' where id = %s", (need_id,))


def _doc(d: dict[str, Any]) -> dict[str, Any]:
    return {"id": str(d["id"]), "kind": d["kind"], "title": d["title"], "body": d["body"], "source": d.get("source")}


def jsonable(obj: Any) -> Any:
    return json.loads(json.dumps(obj, default=str))

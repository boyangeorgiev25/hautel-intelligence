"""Keyword-overlap baseline — the thing the AI engine has to beat.

Same idea as the SQL query in the WP1 Data Inventory §3: count how many words
of each consultant's skill names appear in the need's title + brief; highest
count wins. No interpretation, no language handling. Kept as a pure function
over the database so it can be re-run against real data later.
"""
from __future__ import annotations

from dataclasses import dataclass

import psycopg

STOPWORDS = {"and", "the", "for", "with", "ads", "nl/fr"}  # skill-name filler that would match anything


@dataclass
class BaselinePick:
    consultant_id: str | None
    consultant_name: str | None
    hits: int
    matched_words: list[str]


def baseline_pick(conn: psycopg.Connection, need_id: str) -> BaselinePick:
    row = conn.execute(
        """
        with need as (
          select lower(title || ' ' || description) as txt from marketing_needs where id = %s
        ),
        words as (
          select e.consultant_id, w
            from consultant_expertise e,
                 regexp_split_to_table(lower(e.skill), '[^a-z0-9]+') as w
           where length(w) > 2 and w <> all(%s)
        )
        select c.id, c.full_name, count(distinct w) as hits, array_agg(distinct w) as matched
          from words join need on need.txt like '%%' || w || '%%'
          join consultants c on c.id = words.consultant_id
         group by c.id, c.full_name
         order by hits desc, c.full_name
         limit 1
        """,
        (need_id, list(STOPWORDS)),
    ).fetchone()
    if not row:
        return BaselinePick(None, None, 0, [])
    return BaselinePick(str(row["id"]), row["full_name"], int(row["hits"]), list(row["matched"]))

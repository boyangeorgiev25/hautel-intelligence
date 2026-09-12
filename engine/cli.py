"""hautel-engine — WP2 command line.

  hautel-engine baseline [--need ID]        keyword baseline pick per open need (read-only)
  hautel-engine match --need ID | --all     run the AI engine and trigger the workflow
  hautel-engine show --need ID              print what the engine wrote for a need
  hautel-engine reset --need ID | --all     remove WP2 outputs (inputs untouched)
  hautel-engine test [--only T01,T07] [--report PATH]   golden-set run, baseline vs engine

Database: HAUTEL_DATABASE_URL (EU environment) or the local Docker test env.
"""
from __future__ import annotations

import argparse
import datetime as dt
import pathlib
import sys

from . import db
from .baseline import baseline_pick
from .golden import run_all
from .workflow import run_need

REPO = pathlib.Path(__file__).resolve().parent.parent


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="hautel-engine", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("baseline"); s.add_argument("--need")
    s = sub.add_parser("match"); s.add_argument("--need"); s.add_argument("--all", action="store_true")
    s = sub.add_parser("show"); s.add_argument("--need", required=True)
    s = sub.add_parser("reset"); s.add_argument("--need"); s.add_argument("--all", action="store_true")
    s = sub.add_parser("test")
    s.add_argument("--cases", default=str(REPO / "tests" / "wp2_cases.yaml"))
    s.add_argument("--report", default=None)
    s.add_argument("--only", default=None, help="comma-separated case ids")
    s.add_argument("--workers", type=int, default=4)

    a = p.parse_args(argv)
    _load_env_file(pathlib.Path.home() / ".hautel" / "engine.env")
    print(f"database: {_redact(db.database_url())}", file=sys.stderr)

    if a.cmd == "baseline":
        with db.connect() as conn:
            ids = [a.need] if a.need else [str(r["id"]) for r in conn.execute("select id from marketing_needs order by id")]
            print(f"{'need':<38} {'title':<42} {'baseline pick':<22} hits  words")
            for nid in ids:
                title = conn.execute("select title from marketing_needs where id=%s", (nid,)).fetchone()["title"]
                b = baseline_pick(conn, nid)
                print(f"{nid:<38} {title[:40]:<42} {(b.consultant_name or 'none')[:20]:<22} {b.hits:<5} {','.join(b.matched_words)}")
        return 0

    if a.cmd == "match":
        with db.connect() as conn:
            ids = [a.need] if a.need else (db.list_open_needs(conn) if a.all else [])
            if not ids:
                p.error("match needs --need ID or --all")
            for nid in ids:
                out = run_need(conn, nid)
                top = f"{out.top_consultant_name} ({out.top_score:.2f})" if out.top_consultant_id else "—"
                print(f"{nid}  {out.decision:<9} {top:<32} lang={out.brief_language} {out.latency_ms/1000:.1f}s  task: {out.task_title}")
        return 0

    if a.cmd == "show":
        with db.connect() as conn:
            for r in conn.execute("select id, decision, brief_language, need_summary, escalation_reason, requires_group_signoff, model_ref, latency_ms, created_at from match_runs where need_id=%s order by created_at", (a.need,)):
                print("run  ", dict(r))
            for r in conn.execute("select rank, consultant_id, score, status, left(rationale, 160) as rationale from matches where need_id=%s order by run_id, rank", (a.need,)):
                print("match", dict(r))
            for r in conn.execute("""select t.id, t.title, t.origin_kind, t.assigned_to, t.status, t.detail from tasks t
                                     where t.origin_id in (select id from matches where need_id=%(n)s)
                                        or t.origin_id in (select id from match_runs where need_id=%(n)s) order by t.created_at""", {"n": a.need}):
                print("task ", dict(r))
        return 0

    if a.cmd == "reset":
        with db.connect() as conn:
            ids = [a.need] if a.need else ([str(r["id"]) for r in conn.execute("select id from marketing_needs")] if a.all else [])
            if not ids:
                p.error("reset needs --need ID or --all")
            for nid in ids:
                db.reset_need(conn, nid)
            print(f"reset {len(ids)} need(s)")
        return 0

    if a.cmd == "test":
        report = pathlib.Path(a.report) if a.report else REPO / "docs" / "wp2" / f"golden-run-{dt.date.today():%Y-%m-%d}.md"
        only = set(a.only.split(",")) if a.only else None
        results = run_all(pathlib.Path(a.cases), report, only=only, workers=a.workers)
        scored = [r for r in results if r.case["expected"]["decision"] != "rollback"]
        print(f"\nbaseline {sum(1 for r in scored if r.baseline_ok)}/{len(scored)}   engine {sum(1 for r in scored if r.engine_ok)}/{len(scored)}   "
              f"robustness rollback: {'ok' if all(r.engine_ok for r in results if r.case['expected']['decision']=='rollback') else 'FAILED'}")
        for r in results:
            print(f"  {r.case['id']} {_mark(r.engine_ok)} {r.verdict_note}" + (f"\n{r.error}" if r.error else ""))
        print(f"\nreport: {report}")
        return 0 if all(r.engine_ok for r in results) else 1

    return 2


def _mark(ok):  # noqa: ANN001
    return "PASS" if ok else "FAIL"


def _load_env_file(path: pathlib.Path) -> None:
    """Credentials live outside the repo (WP1 convention: ~/.hautel/). KEY=value lines;
    the shell environment wins over the file. Expected keys: ANTHROPIC_API_KEY,
    optionally HAUTEL_DATABASE_URL (EU environment) and HAUTEL_MODEL."""
    import os
    if not path.is_file():
        return
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.removeprefix("export ").strip()
        os.environ.setdefault(key, value.strip().strip('"').strip("'"))


def _redact(url: str) -> str:
    import re
    return re.sub(r"://([^:]+):[^@]+@", r"://\1:***@", url)


if __name__ == "__main__":
    raise SystemExit(main())

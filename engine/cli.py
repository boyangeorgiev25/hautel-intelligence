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

    s = sub.add_parser("baseline"); s.add_argument("--need"); s.add_argument("--dataset", choices=["synthetic", "real"], default=None, help="restrict to one dataset")
    s = sub.add_parser("match"); s.add_argument("--need"); s.add_argument("--all", action="store_true"); s.add_argument("--dataset", choices=["synthetic", "real"], default=None, help="with --all: only needs of this dataset")
    s = sub.add_parser("show"); s.add_argument("--need", required=True)
    s = sub.add_parser("reset"); s.add_argument("--need"); s.add_argument("--all", action="store_true")
    s = sub.add_parser("advise"); s.add_argument("--need", required=True); s.add_argument("--config", choices=["A", "B", "C"], default="C")
    s = sub.add_parser("advice"); s.add_argument("--need", required=True)
    s = sub.add_parser("draft"); s.add_argument("--advice", required=True); s.add_argument("--kind", default="specialist_brief", choices=["specialist_brief","campaign_brief","content_brief","action_plan","social_draft"])
    s = sub.add_parser("localise"); s.add_argument("--source", required=True); s.add_argument("--lang", required=True, choices=["nl","fr","en"]); s.add_argument("--market", default=None)
    s = sub.add_parser("qc"); s.add_argument("--advice", required=True); s.add_argument("--no-judge", action="store_true")
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
            if a.need:
                ids = [a.need]
            elif a.dataset:
                ids = [str(r["id"]) for r in conn.execute("select id from marketing_needs where dataset = %s order by id", (a.dataset,))]
            else:
                ids = [str(r["id"]) for r in conn.execute("select id from marketing_needs order by id")]
            print(f"{'need':<38} {'title':<42} {'baseline pick':<22} hits  words")
            for nid in ids:
                title = conn.execute("select title from marketing_needs where id=%s", (nid,)).fetchone()["title"]
                b = baseline_pick(conn, nid)
                print(f"{nid:<38} {title[:40]:<42} {(b.consultant_name or 'none')[:20]:<22} {b.hits:<5} {','.join(b.matched_words)}")
        return 0

    if a.cmd == "match":
        with db.connect() as conn:
            ids = [a.need] if a.need else (db.list_open_needs(conn, a.dataset) if a.all else [])
            if not ids:
                p.error("match needs --need ID or --all [--dataset real]")
            for nid in ids:
                out = run_need(conn, nid)
                top = f"{out.top_consultant_name} ({out.top_score:.2f})" if out.top_consultant_id else "—"
                print(f"{nid}  {out.decision:<9} {top:<32} lang={out.brief_language} {out.latency_ms/1000:.1f}s  task: {out.task_title}")
        return 0

    if a.cmd == "advise":
        from .advice import advise
        with db.connect() as conn:
            res = advise(conn, a.need, a.config)
            if res.advice is None:
                print(f"{a.need}  config={a.config}  FAILED: {res.failure}"); return 1
            ad = res.advice
            print(f"{a.need}  config={a.config}  advice={res.advice_id}  sufficient={ad.sufficient_information}  conf={ad.confidence:.2f}  {res.latency_ms/1000:.1f}s  tokens {res.input_tokens}/{res.output_tokens}")
            print(f"  objective: {ad.interpreted_objective}")
            for i, r in enumerate(ad.recommendations, 1):
                print(f"  {i}. {r.action[:110]}  [{len(r.citations)} citations]")
            if ad.missing_information:
                print("  missing: " + " | ".join(ad.missing_information)[:300])
        return 0

    if a.cmd == "draft":
        from .draft import draft
        with db.connect() as conn:
            res = draft(conn, a.advice, a.kind)
            if res.output is None:
                print(f"FAILED: {res.failure}"); return 1
            d = res.output
            print(f"draft={res.id}  kind={d.document_kind}  to={d.addressed_to}  sections={len(d.sections)}  hotel_specific={d.hotel_specific}  {res.latency_ms/1000:.1f}s  tokens {res.input_tokens}/{res.output_tokens}")
            for sec in d.sections: print(f"  ## {sec.heading}  [{len(sec.citations)} citations]")
            if d.open_questions: print("  open: " + " | ".join(d.open_questions)[:300])
        return 0

    if a.cmd == "localise":
        from .draft import localise
        with db.connect() as conn:
            res = localise(conn, a.source, a.lang, a.market)
            if res.output is None:
                print(f"FAILED: {res.failure}"); return 1
            l = res.output
            print(f"localisation={res.id}  lang={l.language}  glossary={len(l.glossary_applied)}  adaptations={len(l.adaptations)}  uncertain={len(l.uncertain)}  {res.latency_ms/1000:.1f}s  tokens {res.input_tokens}/{res.output_tokens}")
            print("  " + l.body[:400].replace("\n", " "))
            for g in l.glossary_applied[:4]: print(f"  glossary: {g[:120]}")
            for x in l.adaptations[:3]: print(f"  adapted: {x[:140]}")
        return 0

    if a.cmd == "qc":
        from .qc import run_qc
        with db.connect() as conn:
            r = run_qc(conn, a.advice, with_judge=not a.no_judge)
            cc, pc, rs = r["citation_check"], r["policy_check"], r["rule_scan"]
            print(f"advice {a.advice}  status={r['status']}  deterministic={'pass' if r['deterministic_pass'] else 'FAIL'}")
            print(f"  citations {cc['citations_verified']}/{cc['citations_total']} verified" + (f"; unverified: {[u['quote'][:60] for u in cc['unverified']]}" if cc['unverified'] else ""))
            print(f"  policy {'pass' if pc['pass'] else pc['problems']}; generic recommendations: {len(pc['generic_recommendations'])}")
            print(f"  rules: {len(rs['documents_with_rules'])} document(s) with rules, acknowledged={rs['acknowledged_in_advice']}")
            if "judge" in r and "verdict" in r["judge"]:
                j = r["judge"]
                print(f"  judge: {j['verdict']}  alignment={j['objective_alignment']:.2f} consistency={j['context_consistency']:.2f} missing_info={j['missing_information_handled']:.2f} language={j['language_consistency']:.2f} actionable={j['actionability']:.2f}  unsupported={len(j['unsupported_claims'])}  corrections={len(j['corrections'])}")
                print(f"  summary: {j['summary']}")
                for u in j['unsupported_claims'][:4]: print(f"    unsupported: {u[:140]}")
        return 0

    if a.cmd == "advice":
        with db.connect() as conn:
            for r in conn.execute("select id, kind, config, status, language, model_ref, latency_ms, created_at, left(body, 200) as body from advice where need_id=%s order by created_at", (a.need,)):
                print(dict(r))
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

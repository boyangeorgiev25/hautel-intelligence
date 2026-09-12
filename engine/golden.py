"""Golden-set runner: baseline vs engine on the documented WP2 test cases.

For every case: run the keyword baseline, run the engine (with the case's
overrides), judge both against the expected outcome fixed in the YAML, write
the judgement to `evaluations` (evaluator 'golden_set') and produce a markdown
report. This is WP2's "initial test cases"; WP3 extends it into the full
evaluation harness.
"""
from __future__ import annotations

import datetime as dt
import pathlib
import traceback
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from typing import Any

import anthropic
import psycopg
import yaml

from . import db
from .baseline import BaselinePick, baseline_pick
from .workflow import RunOutcome, SinkUnavailable, run_need


@dataclass
class CaseResult:
    case: dict[str, Any]
    baseline: BaselinePick | None = None
    baseline_ok: bool | None = None
    outcome: RunOutcome | None = None
    engine_ok: bool | None = None
    verdict_note: str = ""
    error: str | None = None
    rows_before: dict[str, int] = field(default_factory=dict)
    rows_after: dict[str, int] = field(default_factory=dict)


def load_cases(path: pathlib.Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text())


def judge_baseline(case: dict[str, Any], pick: BaselinePick) -> bool:
    exp = case["expected"]
    if exp["decision"] == "rollback":
        return False
    if exp["decision"] == "escalate":
        return False   # the baseline cannot escalate; a pick here is by definition wrong
    return pick.consultant_id in exp.get("consultants", [])


def judge_engine(case: dict[str, Any], out: RunOutcome) -> tuple[bool, str]:
    exp = case["expected"]
    want = exp["decision"]
    accept = set(exp.get("consultants", []))
    if want == "escalate":
        if out.decision in ("escalate", "failed"):
            return True, "escalated as expected"
        if exp.get("low_confidence_ok") and out.top_score is not None and out.top_score < 0.5:
            return True, f"matched with low confidence {out.top_score:.2f} (gap flagged)"
        return False, f"matched {out.top_consultant_name} at {out.top_score:.2f} where an escalation was expected"
    if want == "match":
        if out.decision == "match" and out.top_consultant_id in accept:
            return True, f"top-1 correct ({out.top_consultant_name}, {out.top_score:.2f})"
        if out.decision == "match":
            return False, f"top-1 {out.top_consultant_name} not in expected set"
        return False, f"escalated where a match was expected: {out.escalation_reason}"
    if want == "either":
        if out.decision in ("escalate", "failed"):
            return True, "escalated (accepted)"
        if out.top_consultant_id in accept:
            return True, f"top-1 correct ({out.top_consultant_name}, {out.top_score:.2f})"
        return False, f"top-1 {out.top_consultant_name} not in expected set"
    return False, f"unknown expectation {want}"


def run_case(case: dict[str, Any], client: anthropic.Anthropic) -> CaseResult:
    res = CaseResult(case=case)
    overrides = case.get("overrides") or {}
    with db.connect() as conn:
        try:
            res.baseline = baseline_pick(conn, case["need_id"])
            res.baseline_ok = judge_baseline(case, res.baseline)
            res.rows_before = db.wp2_counts(conn, case["need_id"])
            if case["expected"]["decision"] == "rollback":
                try:
                    run_need(conn, case["need_id"], fail_sink=True, client=client)
                    res.engine_ok, res.verdict_note = False, "sink failure did not raise"
                except SinkUnavailable as e:
                    conn.rollback()
                    res.rows_after = db.wp2_counts(conn, case["need_id"])
                    clean = res.rows_after == res.rows_before
                    res.engine_ok = clean
                    res.verdict_note = f"error surfaced ({e}); rows unchanged={clean} {res.rows_after}"
                return res
            res.outcome = run_need(
                conn, case["need_id"],
                candidate_filter=overrides.get("candidate_filter"),
                fail_sink=bool(overrides.get("fail_sink")),
                client=client,
            )
            res.rows_after = db.wp2_counts(conn, case["need_id"])
            res.engine_ok, res.verdict_note = judge_engine(case, res.outcome)
            _write_evaluation(conn, res)
        except Exception:
            res.error = traceback.format_exc(limit=3)
            res.engine_ok = False
            res.verdict_note = "exception"
    return res


def _write_evaluation(conn: psycopg.Connection, res: CaseResult) -> None:
    out = res.outcome
    if not out:
        return
    conn.execute(
        """
        insert into evaluations (subject_kind, subject_id, metric, score, evaluator, notes)
        values ('match_run', %s, 'golden_top1', %s, 'golden_set', %s)
        """,
        (out.run_id, 1 if res.engine_ok else 0, f"{res.case['id']} {res.case['label']}: {res.verdict_note}"),
    )
    conn.commit()


def run_all(cases_path: pathlib.Path, report_path: pathlib.Path, only: set[str] | None = None, workers: int = 4) -> list[CaseResult]:
    spec = load_cases(cases_path)
    cases = [c for c in spec["cases"] if not only or c["id"] in only]
    client = anthropic.Anthropic(max_retries=3)
    # Robustness cases that share a need with a standard case must run first so the
    # rollback check compares against a stable baseline of rows.
    ordered = sorted(cases, key=lambda c: 0 if c["expected"]["decision"] == "rollback" else 1)
    rollback_cases = [c for c in ordered if c["expected"]["decision"] == "rollback"]
    other_cases = [c for c in ordered if c["expected"]["decision"] != "rollback"]
    results = [run_case(c, client) for c in rollback_cases]
    with ThreadPoolExecutor(max_workers=workers) as pool:
        results += list(pool.map(lambda c: run_case(c, client), other_cases))
    results.sort(key=lambda r: r.case["id"])
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(render_report(results, spec))
    return results


def render_report(results: list[CaseResult], spec: dict[str, Any]) -> str:
    names = spec.get("consultants", {})
    scored = [r for r in results if r.case["expected"]["decision"] != "rollback"]
    b_ok = sum(1 for r in scored if r.baseline_ok)
    e_ok = sum(1 for r in scored if r.engine_ok)
    by_lang: dict[str, list[CaseResult]] = {}
    for r in scored:
        by_lang.setdefault(r.case["language"], []).append(r)
    tokens_in = sum(r.outcome.input_tokens for r in results if r.outcome)
    tokens_out = sum(r.outcome.output_tokens for r in results if r.outcome)
    lat = [r.outcome.latency_ms for r in results if r.outcome and r.outcome.latency_ms]
    model_refs = sorted({r.outcome.model_ref for r in results if r.outcome and r.outcome.model_ref.startswith("claude")})

    lines = [
        f"# WP2 golden-set run — {dt.datetime.now():%Y-%m-%d %H:%M}",
        "",
        f"Model: {', '.join(model_refs) or 'n/a'}. Cases: {len(results)} ({len(scored)} scored + {len(results)-len(scored)} rollback).",
        "",
        "## Summary",
        "",
        "| | Keyword baseline | AI engine |",
        "|---|---|---|",
        f"| Correct outcomes (of {len(scored)}) | {b_ok} | {e_ok} |",
    ]
    for lang, rs in sorted(by_lang.items()):
        lines.append(f"| … of which language = {lang} (of {len(rs)}) | {sum(1 for r in rs if r.baseline_ok)} | {sum(1 for r in rs if r.engine_ok)} |")
    if lat:
        lines.append(f"| Latency per need (median / max, s) | 0 | {sorted(lat)[len(lat)//2]/1000:.1f} / {max(lat)/1000:.1f} |")
    lines.append(f"| Tokens in / out (total) | 0 | {tokens_in:,} / {tokens_out:,} |")
    lines += ["", "## Per case", "", "| Case | Need | Lang | Kind | Expected | Baseline pick | Engine decision → top-1 (score) | Baseline | Engine | Note |", "|---|---|---|---|---|---|---|---|---|---|"]
    for r in results:
        c, exp = r.case, r.case["expected"]
        expected = exp["decision"] if exp["decision"] != "match" else "match: " + " or ".join(_short(names, x) for x in exp.get("consultants", []))
        if exp["decision"] == "either":
            expected = "either: " + " or ".join(_short(names, x) for x in exp.get("consultants", [])) + " / escalate"
        bpick = f"{_short(names, r.baseline.consultant_id)} ({r.baseline.hits})" if r.baseline and r.baseline.consultant_id else "none"
        if r.outcome:
            o = r.outcome
            eng = f"{o.decision} → {o.top_consultant_name or '—'}" + (f" ({o.top_score:.2f})" if o.top_score is not None else "")
        else:
            eng = "rollback verified" if r.engine_ok else "error"
        lines.append(
            f"| {c['id']} | {c['label']} | {c['language']} | {c['kind']} | {expected} | {bpick} | {eng} | "
            f"{_mark(r.baseline_ok) if exp['decision'] != 'rollback' else 'n/a'} | {_mark(r.engine_ok)} | {r.verdict_note} |"
        )
    lines += ["", "## Engine reasoning per case", ""]
    for r in results:
        if not r.outcome:
            if r.error:
                lines += [f"### {r.case['id']} — {r.case['label']}", "", "```", r.error.strip(), "```", ""]
            else:
                lines += [f"### {r.case['id']} — {r.case['label']}", "", r.verdict_note, ""]
            continue
        o = r.outcome
        lines += [f"### {r.case['id']} — {r.case['label']}", "",
                  f"- Decision: **{o.decision}**; brief language detected: {o.brief_language}; task: “{o.task_title}”"
                  + (f"; routed to {o.assigned_to}" if o.assigned_to else "; unrouted"),
                  ]
        if o.requires_group_signoff:
            lines.append("- Group sign-off flagged (org rule applied from documents)")
        if o.escalation_reason:
            lines.append(f"- Escalation reason: {o.escalation_reason}")
        for i, cand in enumerate(o.ranked, start=1):
            lines.append(f"- #{i} {cand['consultant_name']} — {cand['score']:.2f}: {cand['rationale']}")
            if cand.get("gaps"):
                lines.append(f"  - gaps: {'; '.join(cand['gaps'])}")
        lines.append(f"- Run {o.run_id}; {o.latency_ms/1000:.1f}s; {o.input_tokens}/{o.output_tokens} tokens; model {o.model_ref}")
        lines.append("")
    return "\n".join(lines)


def _short(names: dict[str, str], cid: str | None) -> str:
    if not cid:
        return "—"
    return names.get(cid, cid).split(" (")[0]


def _mark(ok: bool | None) -> str:
    return "✔" if ok else "✘"

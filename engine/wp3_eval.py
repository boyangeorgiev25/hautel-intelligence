"""WP3 evaluation runner: executes tests/wp3_cases.yaml, judges each actual output against the
expectation fixed in the file, writes evaluations rows and a markdown report in Anton's format
(input, expected, actual, pass/fail, observation). Deterministic QC cases run without the model."""
from __future__ import annotations

import copy
import datetime as dt
import json
import pathlib
from dataclasses import dataclass, field
from typing import Any

import anthropic
import psycopg
import yaml

from . import db
from .advice import advise
from .draft import draft, localise
from .qc import citation_check, policy_check, run_qc
from .workflow import run_need

REPO = pathlib.Path(__file__).resolve().parents[1]


@dataclass
class CaseResult:
    case: dict[str, Any]
    ok: bool | None = None
    actual: str = ""
    observation: str = ""
    ref_id: str | None = None          # advice/draft/localisation id or run id
    structured: dict[str, Any] | None = None
    tokens: tuple[int, int] = (0, 0)
    latency_ms: int = 0
    error: str | None = None


def _ensure_vague(conn: psycopg.Connection, need_id: str) -> None:
    conn.execute("""insert into marketing_needs (id, property_id, title, description, category, urgency, status, dataset)
                    values (%s, (select id from properties where dataset='synthetic' order by name limit 1),
                            'Something about marketing', 'We need to do something about marketing. Can someone help?', 'other', 'low', 'open', 'synthetic')
                    on conflict (id) do nothing""", (need_id,))
    conn.commit()


def _check(exp: dict[str, Any], s: dict[str, Any], extra: dict[str, Any], results: dict[str, CaseResult]) -> tuple[bool, list[str]]:
    notes = []
    ok = True
    def fail(msg): 
        nonlocal ok; ok = False; notes.append(msg)
    text = json.dumps(s, ensure_ascii=False).lower()
    if "sufficient" in exp and bool(s.get("sufficient_information")) != exp["sufficient"]:
        fail(f"sufficient_information={s.get('sufficient_information')}, expected {exp['sufficient']}")
    cites = [c for r in s.get("recommendations", []) + s.get("sections", []) for c in r.get("citations", [])]
    if "min_citations" in exp and len(cites) < exp["min_citations"]:
        fail(f"{len(cites)} citations, expected ≥{exp['min_citations']}")
    if "min_confidence" in exp and float(s.get("confidence", 0)) < exp["min_confidence"]:
        fail(f"confidence {s.get('confidence')}, expected ≥{exp['min_confidence']}")
    if "max_recommendations" in exp and len(s.get("recommendations", [])) > exp["max_recommendations"]:
        fail(f"{len(s.get('recommendations', []))} recommendations, expected ≤{exp['max_recommendations']}")
    if "min_missing" in exp and len(s.get("missing_information", [])) < exp["min_missing"]:
        fail(f"{len(s.get('missing_information', []))} missing items, expected ≥{exp['min_missing']}")
    for m in exp.get("mentions", []):
        if m.lower() not in text: fail(f"does not mention '{m}'")
    if "mentions_any" in exp and not any(m.lower() in text for m in exp["mentions_any"]):
        fail(f"mentions none of {exp['mentions_any']}")
    for m in exp.get("missing_mentions", []):
        if m.lower() not in json.dumps(s.get("missing_information", [])).lower(): fail(f"missing_information does not mention '{m}'")
    for m in exp.get("risks_mention", []):
        if m.lower() not in json.dumps(s.get("risks", [])).lower(): fail(f"risks do not mention '{m}'")
    if "citation_sources_only" in exp:
        srcs = {c.get("source", "").lower() for c in cites}
        bad = [x for x in srcs if not any(a in x for a in exp["citation_sources_only"])]
        if bad: fail(f"citations from outside {exp['citation_sources_only']}: {bad[:3]}")
    if "compare_confidence_below" in exp:
        other = results.get(exp["compare_confidence_below"])
        if other and other.structured and float(s.get("confidence", 0)) >= float(other.structured.get("confidence", 0)):
            fail(f"confidence {s.get('confidence')} not below {exp['compare_confidence_below']} ({other.structured.get('confidence')})")
    if "rule_acknowledged" in exp and extra.get("rule_acknowledged") is not None and extra["rule_acknowledged"] != exp["rule_acknowledged"]:
        fail(f"rule acknowledged={extra['rule_acknowledged']}")
    if "hotel_specific" in exp and bool(s.get("hotel_specific")) != exp["hotel_specific"]:
        fail(f"hotel_specific={s.get('hotel_specific')}, expected {exp['hotel_specific']}")
    if "sections_between" in exp:
        lo, hi = exp["sections_between"]; n = len(s.get("sections", []))
        if not (lo <= n <= hi): fail(f"{n} sections, expected {lo}–{hi}")
    for m in exp.get("open_questions_mention", []):
        if m.lower() not in json.dumps(s.get("open_questions", [])).lower(): fail(f"open questions do not mention '{m}'")
    if "language" in exp and s.get("language") != exp["language"]:
        fail(f"language={s.get('language')}, expected {exp['language']}")
    for m in exp.get("body_contains", []):
        if m.lower() not in (s.get("body", "") or "").lower(): fail(f"body does not contain '{m}'")
    if "min_glossary" in exp and len(s.get("glossary_applied", [])) < exp["min_glossary"]:
        fail(f"{len(s.get('glossary_applied', []))} glossary entries, expected ≥{exp['min_glossary']}")
    if "min_adaptations" in exp and len(s.get("adaptations", [])) < exp["min_adaptations"]:
        fail(f"{len(s.get('adaptations', []))} adaptations, expected ≥{exp['min_adaptations']}")
    if "max_adaptations" in exp and len(s.get("adaptations", [])) > exp["max_adaptations"]:
        fail(f"{len(s.get('adaptations', []))} adaptations, expected ≤{exp['max_adaptations']}")
    if "decision" in exp and s.get("decision") != exp["decision"]:
        fail(f"decision={s.get('decision')}, expected {exp['decision']}")
    # QC report expectations
    q = extra.get("qc") or {}
    if "citations_all_verified" in exp and q:
        allv = q["citation_check"]["pass"]
        if allv != exp["citations_all_verified"]: fail(f"citations verified={allv}")
    if "deterministic_pass" in exp and q and q["deterministic_pass"] != exp["deterministic_pass"]:
        fail(f"deterministic_pass={q['deterministic_pass']}")
    if "policy_pass" in exp and q and q["policy_check"]["pass"] != exp["policy_pass"]:
        fail(f"policy_pass={q['policy_check']['pass']}")
    if "verdict_in" in exp and q.get("judge", {}).get("verdict") not in exp["verdict_in"]:
        fail(f"verdict={q.get('judge', {}).get('verdict')}, expected one of {exp['verdict_in']}")
    if "min_unsupported" in exp and len(q.get("judge", {}).get("unsupported_claims", [])) < exp["min_unsupported"]:
        fail("judge listed no unsupported claims")
    return ok, notes


def run_all(cases_path: pathlib.Path, report_path: pathlib.Path, only: set[str] | None = None, use_model: bool = True) -> list[CaseResult]:
    spec = yaml.safe_load(cases_path.read_text())
    needs = spec["needs"]
    results: dict[str, CaseResult] = {}
    client = anthropic.Anthropic() if use_model else None
    with db.connect() as conn:
        _ensure_vague(conn, needs["vague"])
        for case in spec["cases"]:
            if only and case["id"] not in only:
                continue
            r = CaseResult(case=case)
            try:
                cap, exp = case["capability"], case.get("expect", {})
                extra: dict[str, Any] = {}
                if cap == "advisor":
                    res = advise(conn, needs[case["need"]], case["config"], client=client)
                    if res.advice is None: raise RuntimeError(res.failure)
                    r.structured = res.advice.model_dump(); r.ref_id = res.advice_id
                    r.tokens, r.latency_ms = (res.input_tokens, res.output_tokens), res.latency_ms
                    q = run_qc(conn, res.advice_id, client=client, with_judge=False)
                    extra["rule_acknowledged"] = q["rule_scan"]["acknowledged_in_advice"]; extra["qc"] = q
                    r.actual = (f"sufficient={r.structured['sufficient_information']} conf={r.structured['confidence']:.2f} "
                                f"recs={len(r.structured['recommendations'])} citations={sum(len(x['citations']) for x in r.structured['recommendations'])} "
                                f"missing={len(r.structured['missing_information'])}")
                elif cap == "match":
                    out = run_need(conn, needs[case["need"]], client=client)
                    raw = conn.execute("select raw_output from match_runs where id=%s", (out.run_id,)).fetchone()["raw_output"] or {}
                    r.structured = raw; r.ref_id = out.run_id; r.tokens, r.latency_ms = (out.input_tokens, out.output_tokens), out.latency_ms
                    r.actual = f"decision={raw.get('decision')} conf={raw.get('confidence')} missing={len(raw.get('missing_information', []))} top={out.top_consultant_name} {out.top_score}"
                elif cap == "draft":
                    src = results[case["source_case"]]
                    res = draft(conn, src.ref_id, case["kind"], client=client)
                    if res.output is None: raise RuntimeError(res.failure)
                    r.structured = res.output.model_dump(); r.ref_id = res.id; r.tokens, r.latency_ms = (res.input_tokens, res.output_tokens), res.latency_ms
                    r.actual = f"kind={r.structured['document_kind']} sections={len(r.structured['sections'])} citations={sum(len(x['citations']) for x in r.structured['sections'])} hotel_specific={r.structured['hotel_specific']} open={len(r.structured['open_questions'])}"
                elif cap == "localise":
                    src = results[case["source_case"]]
                    res = localise(conn, src.ref_id, case["lang"], case.get("market"), client=client)
                    if res.output is None: raise RuntimeError(res.failure)
                    r.structured = res.output.model_dump(); r.ref_id = res.id; r.tokens, r.latency_ms = (res.input_tokens, res.output_tokens), res.latency_ms
                    r.actual = f"language={r.structured['language']} glossary={len(r.structured['glossary_applied'])} adaptations={len(r.structured['adaptations'])} uncertain={len(r.structured['uncertain'])} words={len(r.structured['body'].split())}"
                elif cap == "qc":
                    src = results[case["source_case"]]
                    s = copy.deepcopy(src.structured or {})
                    if case.get("tamper") == "inject_fake_citation":
                        s["recommendations"][0]["citations"].append({"source": "hotel profile", "quote": "The hotel has 240 rooms and a rooftop pool."})
                        need = db.load_need(conn, str(conn.execute("select need_id from advice where id=%s", (src.ref_id,)).fetchone()["need_id"]))
                        from .advice import assemble_context, latest_match
                        ctx = assemble_context(need, src.case["config"], latest_match(conn, need.id))
                        cc = citation_check(s, ctx); extra["qc"] = {"citation_check": cc, "policy_check": policy_check(s), "deterministic_pass": cc["pass"] and policy_check(s)["pass"]}
                        r.actual = f"deterministic: citations {cc['citations_verified']}/{cc['citations_total']} verified, pass={extra['qc']['deterministic_pass']}"
                    elif case.get("tamper") == "add_recommendation_to_insufficient":
                        s["recommendations"] = [{"action": "Post more on Instagram", "why": "generic", "channels": ["instagram"], "citations": []}]
                        pc = policy_check(s); extra["qc"] = {"citation_check": {"pass": True}, "policy_check": pc, "deterministic_pass": pc["pass"]}
                        r.actual = f"deterministic: policy pass={pc['pass']} problems={pc['problems']}"
                    else:
                        q = run_qc(conn, src.ref_id, client=client, with_judge=use_model); extra["qc"] = q
                        j = q.get("judge", {})
                        r.actual = (f"citations {q['citation_check']['citations_verified']}/{q['citation_check']['citations_total']}, deterministic={q['deterministic_pass']}, "
                                    f"verdict={j.get('verdict')} unsupported={len(j.get('unsupported_claims', []))} alignment={j.get('objective_alignment')}")
                    r.structured = s; r.ref_id = src.ref_id
                r.ok, notes = _check(exp, r.structured or {}, extra, results)
                r.observation = "; ".join(notes) if notes else "as expected"
                if r.ref_id and cap != "qc":
                    conn.execute("insert into evaluations (subject_kind, subject_id, metric, score, evaluator, notes) values (%s, %s, 'wp3_case', %s, 'wp3_cases', %s)",
                                 ("match_run" if cap == "match" else "advice", r.ref_id, 1 if r.ok else 0, f"{case['id']} {case['label']}: {r.observation}"))
                    conn.commit()
            except Exception as e:  # keep going; the report shows the failure
                r.ok, r.error, r.observation = False, str(e)[:300], f"error: {str(e)[:200]}"
            results[case["id"]] = r
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(render(results, spec))
    return list(results.values())


def render(results: dict[str, CaseResult], spec: dict[str, Any]) -> str:
    rows = list(results.values())
    n_ok = sum(1 for r in rows if r.ok)
    tin, tout = sum(r.tokens[0] for r in rows), sum(r.tokens[1] for r in rows)
    out = [f"# WP3 test run — {dt.date.today().isoformat()}", "",
           f"{n_ok} of {len(rows)} cases pass. Tokens: {tin:,} in / {tout:,} out.", "",
           "| Case | Capability | Input | Expected | Actual | Result | Observation |", "|---|---|---|---|---|---|---|"]
    for r in rows:
        c = r.case
        inp = c.get("label", "")
        exp = ", ".join(f"{k}={v}" for k, v in (c.get("expect") or {}).items())
        out.append(f"| {c['id']} | {c['capability']} | {inp} | {exp} | {r.actual or r.error or ''} | {'pass' if r.ok else 'FAIL'} | {r.observation} |")
    out += ["", "## Per capability", "", "| Capability | Pass | Total |", "|---|---|---|"]
    for cap in ("advisor", "qc", "draft", "localise", "match"):
        sub = [r for r in rows if r.case["capability"] == cap]
        if sub: out.append(f"| {cap} | {sum(1 for r in sub if r.ok)} | {len(sub)} |")
    return "\n".join(out) + "\n"

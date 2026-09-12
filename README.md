# Hautel Intelligence — ISS Technical Sprint

Platform foundation + AI matching/advice PoC for the VLAIO ISS work packages (WP1–WP3).
Architecture reference: `Documents/Research & Development/WP1 - Architecture Dossier (draft).md`.
Sprint scope: `ISS Sprint Plan (70h).md`. Evidence: `WP Evidence Log.md` (same folder).

## Layout

```
db/migrations/  001 core platform spine (orgs→properties→users/tasks/messages/content)
                002 ISS datasets (hotel profiles, marketing needs, consultants,
                    documents) + PoC outputs (matches, advice, evaluations)
                003 WP2 run-level provenance (match_runs; escalation tasks)
db/seed/        synthetic_seed.sql   v1 (all names fictional) — replaced/extended
                                     when real client data arrives
                wp2_test_needs.sql   v1.1: NL/FR/mixed/ambiguous needs, FR documents,
                                     one marketing lead per org (task routing)
engine/         WP2 matching & workflow engine (Python, uv) — see below
tests/wp2_cases.yaml        the 20 golden test cases with expected outcomes
docs/wp2/                   generated golden-run reports
scripts/db.sh   local secure test environment (Postgres 17, Docker, 127.0.0.1-only)
scripts/deploy_supabase.sh  deploy schema (+seed) to the EU-hosted Supabase project;
                            refuses non-EU hosts, enables RLS, revokes anon access;
                            --upgrade applies new migrations/seeds to an existing project
scripts/inventory.sh        live data inventory (rows, real vs synthetic, consumer WP)
scripts/validate.sh         16 PASS/FAIL checks (region, RLS, grants, counts, integrity,
                            write refusal); runs under the read-only reviewer role
```

## WP2 engine

```sh
uv sync                                     # once; Python 3.13 via uv
uv run hautel-engine baseline               # keyword baseline per need (read-only)
uv run hautel-engine match --need <id>      # interpret → match/escalate → routed task
uv run hautel-engine show --need <id>       # run, matches, task written for a need
uv run hautel-engine test                   # 20 cases, baseline vs engine, report in docs/wp2/
uv run hautel-engine reset --all            # drop WP2 outputs, keep inputs
```

Pipeline: `db.py` assembles context (need + hotel profile + property/org documents +
full consultant pool with skills, bios, documents) → `matcher.py` asks the model for a
`MatchDecision` (structured JSON: language, interpretation, constraints checked, ranked
candidates with score / rationale / quoted evidence / gaps, sign-off flag) →
`workflow.py` writes `match_runs` + `matches` + a task routed to the org's marketing
lead, in one transaction. Escalation (skill gap, ambiguous brief, empty pool, model
refusal) is a first-class outcome with its own task. Credentials: `~/.hautel/engine.env`
(`ANTHROPIC_API_KEY`; optional `HAUTEL_DATABASE_URL` for the EU env, `HAUTEL_MODEL`).

## Quick start

```sh
scripts/db.sh up        # start Postgres (container hautel-iss-db, port 54329)
scripts/db.sh migrate   # apply migrations
scripts/db.sh seed      # load synthetic data
scripts/db.sh psql      # open a SQL shell
scripts/db.sh reset     # wipe & rebuild
```

Password via `HAUTEL_DB_PASS` (dev default in the script — change for any shared deployment).

## Design notes

- **Generic spine, ISS payload.** The core model (tasks with provenance, layered
  content, channel-agnostic messages) carries the marketing/intelligence use case
  now and the guest & ops use cases later without schema change — per the WP1
  dossier §7 and Anton's 31 Aug scope decision.
- **Provenance end-to-end**: `matches.rationale`, `advice.grounding`,
  `evaluations` — every AI output is traceable to inputs and scored. This is the
  VLAIO evidence trail, designed in from the first migration.
- **EU/GDPR posture**: deployed on Supabase eu-central-1 (Frankfurt), project
  `hautel-iss-test`; RLS on every table, anon/authenticated revoked. Credentials
  live in `~/.hautel/supabase.env`, never in the repo. Transfer to a Hautel
  organization pending.

## WP status

- WP1: closed 9 Sep 2026 at ~10h ✔ schema, synthetic dataset, EU-hosted test env (Supabase Frankfurt, RLS, read-only reviewer role), deploy/inventory/validate scripts, data inventory + handover + validation guide · reserved ~8h: real data ingestion (Drive access), VLAIO doc formatting (ISS texts), project transfer to a Hautel org
- WP2: closed 13 Sep 2026 at ~10h ✔ engine + 20 golden cases; run of record on the EU env: engine 19/19 vs keyword baseline 11/19 (`docs/wp2/golden-run-2026-09-12-eu.md`); migration 003 + seed v1.1 applied on Frankfurt via `deploy_supabase.sh --upgrade --seed`; `validate.sh` has 23 checks · reserved ~14h: real-data run (needs consultant roster), demo page, repeat runs for WP3
- WP3 (advice + quality control): builds on `advice` + `evaluations`

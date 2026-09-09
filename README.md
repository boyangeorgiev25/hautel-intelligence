# Hautel Intelligence — ISS Technical Sprint

Platform foundation + AI matching/advice PoC for the VLAIO ISS work packages (WP1–WP3).
Architecture reference: `Documents/Research & Development/WP1 - Architecture Dossier (draft).md`.
Sprint scope: `ISS Sprint Plan (70h).md`. Evidence: `WP Evidence Log.md` (same folder).

## Layout

```
db/migrations/  001 core platform spine (orgs→properties→users/tasks/messages/content)
                002 ISS datasets (hotel profiles, marketing needs, consultants,
                    documents) + PoC outputs (matches, advice, evaluations)
db/seed/        synthetic dataset v1 (all names fictional) — replaced/extended
                when real client data arrives
scripts/db.sh   local secure test environment (Postgres 17, Docker, 127.0.0.1-only)
scripts/deploy_supabase.sh  deploy schema (+seed) to the EU-hosted Supabase project;
                            refuses non-EU hosts, enables RLS, revokes anon access
scripts/inventory.sh        live data inventory (rows, real vs synthetic, consumer WP)
scripts/validate.sh         16 PASS/FAIL checks (region, RLS, grants, counts, integrity,
                            write refusal); runs under the read-only reviewer role
```

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
- WP2 (matching/workflow engine): next — builds on `matches` + `tasks(origin_kind='match')`
- WP3 (advice + quality control): builds on `advice` + `evaluations`

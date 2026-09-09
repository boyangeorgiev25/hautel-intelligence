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
- **EU/GDPR posture**: local now; target deployment is an EU-region managed
  Postgres (Supabase Frankfurt proposed, Hautel-owned account — pending Anton).

## WP status

- WP1: schema + test environment + synthetic dataset ✔ · real data ingestion + VLAIO doc formatting pending Anton's deliveries
- WP2 (matching/workflow engine): next — builds on `matches` + `tasks(origin_kind='match')`
- WP3 (advice + quality control): builds on `advice` + `evaluations`

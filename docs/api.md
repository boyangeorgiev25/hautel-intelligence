# Engine API — contract for the demo frontend

Thin HTTP layer over the database and the WP2 engine (`engine/api.py`). Start with
`hautel-api` (port 8765). It loads `~/.hautel/engine.env` like the CLI; set
`HAUTEL_DATABASE_URL` to the local test env for the frontend demo:

```
HAUTEL_DATABASE_URL="postgresql://postgres:hautel-dev-only@localhost:54329/hautel" uv run hautel-api
```

CORS is open (demo). JSON everywhere. IDs are UUID strings. `dataset` is `synthetic` or `real`.

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | `{ok, database (redacted), postgres}` |
| GET | `/datasets` | the two datasets with consultant / need / open-need counts |
| GET | `/needs?dataset=real&status=open` | need list with property, organization, last decision, run count |
| GET | `/needs/{id}` | need + hotel profile + documents + keyword baseline + results |
| GET | `/needs/{id}/results` | `{runs, matches, tasks}` for that need, newest first |
| GET | `/consultants?dataset=real` | the pool with expertise and documents (what the engine sees) |
| GET | `/tasks?dataset=real&status=open` | routed tasks with property and assignee |
| POST | `/needs/{id}/match` | run the engine: returns the run outcome (decision, top consultant, score, language, task, tokens) |
| POST | `/needs/{id}/reset` | remove the engine's outputs for the need so it can be re-run |
| GET | `/intel/status` | intelligence collectors: configured on this host, what each needs, last run |
| POST | `/intel/collect?org_id=&source=` | run the configured collectors for an organisation (writer) |
| GET | `/organizations/{id}/intel` | per property: reviews, rate and rank snapshots, AI-assistant answers, local events |
| GET | `/properties/{id}/intel` | the same for one property |
| POST | `/properties/{id}/reviews/draft` | Claude drafts a reply for a review text, grounded in the hotel profile (writer) |
| POST | `/reviews/{id}/draft` | draft (or redraft) the reply of a stored review and keep it on the row (writer) |
| POST | `/reviews/{id}/reply` | a person approves the reply; posted only through a configured connector (writer) |

## Shapes

`GET /needs` item:
```json
{"id":"…","title":"…","category":"content","urgency":"high","budget_band":"1-5k","status":"open",
 "dataset":"real","property_id":"…","property_name":"Cocoon Hotel La Rive, Bourscheid-Plage","region":"Luxembourg (Ardennes)",
 "organization":"Cocoon Hotels","last_decision":null,"last_language":null,"last_run_at":null,"runs":0}
```

`POST /needs/{id}/match` response (the engine's RunOutcome):
```json
{"run_id":"…","need_id":"…","decision":"match|escalate|failed","top_consultant_id":"…","top_consultant_name":"…",
 "top_score":0.82,"brief_language":"nl","task_id":"…","task_title":"…","assigned_to":"…",
 "requires_group_signoff":false,"escalation_reason":null,"model_ref":"claude-opus-5",
 "latency_ms":9800,"input_tokens":6100,"output_tokens":900,
 "ranked":[{"consultant_id":"…","consultant_name":"…","score":0.82,"rationale":"…","evidence":["…"],"gaps":["…"]}]}
```

`GET /needs/{id}/results`: `runs[]` (decision, brief_language, need_summary, escalation_reason, model_ref, latency_ms, tokens),
`matches[]` (rank, consultant_name, score, status, rationale, model_ref; evidence and gaps come back in the POST response's `ranked[]`), `tasks[]` (title, detail, status, origin_kind, assigned_to_name).

## Suggested screens

1. **Needs board** — `GET /needs?dataset=real`: cards per need with property, category, urgency, status, last decision.
2. **Need page** — `GET /needs/{id}`: brief, hotel profile, source documents, baseline pick; a "Run matching" button → `POST /needs/{id}/match`; then the ranked matches with rationale, evidence and gaps, and the routed task.
3. **Pool** — `GET /consultants?dataset=real`: who the engine can choose from.
4. **Tasks** — `GET /tasks?dataset=real`: what the workflow created and for whom.

Errors: 404 unknown need; 503 no model key on the API host; 502 workflow sink unavailable (nothing written).

## Reaching the API from a hosted frontend

The API binds to 127.0.0.1. A locally served frontend (Lovable export, `npm run dev`) can call it directly.
A frontend hosted elsewhere (Lovable preview) needs a public URL: `cloudflared tunnel --url http://localhost:8765`
(or ngrok) gives an HTTPS address; put it in the frontend as the API base URL.

## Intelligence sources (migration 006)

Collectors live in `engine/intel.py`. Each runs only when its configuration is present in
`~/.hautel/engine.env` on the API host:

| Source | Needs |
|---|---|
| Google reviews and replies | `HAUTEL_GOOGLE_BUSINESS_TOKEN` (Business Profile API, `business.manage` scope) and per hotel `properties.branding.google_location` = `accounts/{a}/locations/{l}` |
| Rates and parity | `HAUTEL_RATE_API_URL` (template with `{property_id}` and `{days}`) and `HAUTEL_RATE_API_KEY`; JSON `[{"date","channel","competitor"|null,"rate"}]` |
| OTA search rank | `HAUTEL_RANK_API_URL` (template with `{property_id}`, `{city}`) and `HAUTEL_RANK_API_KEY`; JSON `[{"site","query","rank","page"}]` |
| AI-assistant visibility | `ANTHROPIC_API_KEY` (Claude, already present), `OPENAI_API_KEY` (ChatGPT), `GOOGLE_AI_API_KEY` (Gemini) |
| Local events | `PREDICTHQ_TOKEN`, optional `HAUTEL_EVENTS_DAYS` (default 45) |

Claude reply drafts need no extra configuration. After adding keys, restart `hautel-api` and call
`POST /intel/collect?org_id=…` (or "Collect now" on the Settings page). Migration 006 was applied
directly; run `scripts/deploy_supabase.sh --upgrade` once to apply the RLS lock-down to the new tables.

-- 006 — Intelligence layer: reviews, rates, OTA rank, AI-assistant answers, local events.
-- Additive. Every row is keyed by property and carries `source` (which collector wrote
-- it), so live feeds and manual imports coexist. `intel_sources` is the registry the API
-- reports: which collectors are configured on the host and when they last ran.

create table reviews (
  id             uuid primary key default gen_random_uuid(),
  property_id    uuid not null references properties(id),
  source         text not null check (source in ('google','booking','expedia','agoda','tripadvisor','other')),
  external_id    text,                     -- id at the source; unique per source
  author         text,
  rating         numeric(2,1) check (rating >= 0 and rating <= 5),
  language       text,                     -- nl, fr, en, de, ...
  body           text not null,
  review_at      timestamptz not null default now(),
  reply_draft    text,                     -- AI draft, never posted without a person
  reply_draft_meta jsonb,                  -- model, tokens, latency, grounding
  reply_text     text,                     -- the approved reply
  replied_by     uuid references users(id),
  replied_at     timestamptz,
  posted_at      timestamptz,              -- set when the reply reached the source
  created_at     timestamptz not null default now(),
  unique (source, external_id)
);
create index on reviews (property_id, review_at desc);

create table rate_snapshots (
  id           uuid primary key default gen_random_uuid(),
  property_id  uuid not null references properties(id),
  stay_date    date not null,
  channel      text not null,              -- direct, booking, expedia, agoda, ...
  competitor   text,                       -- null = this hotel; otherwise the competitor's name
  rate         numeric(8,2) not null,
  currency     text not null default 'EUR',
  source       text not null,
  captured_at  timestamptz not null default now()
);
create index on rate_snapshots (property_id, stay_date, captured_at desc);

create table rank_snapshots (
  id           uuid primary key default gen_random_uuid(),
  property_id  uuid not null references properties(id),
  site         text not null,              -- booking, expedia, google_hotels, tripadvisor
  query        text not null,
  rank         int,                        -- null = not in the first pages
  page         int,
  source       text not null,
  captured_at  timestamptz not null default now()
);
create index on rank_snapshots (property_id, captured_at desc);

create table ai_answers (
  id           uuid primary key default gen_random_uuid(),
  property_id  uuid not null references properties(id),
  assistant    text not null,              -- chatgpt, gemini, perplexity, claude, copilot
  query        text not null,
  mentioned    boolean not null,
  position     int,
  others       text[] not null default '{}',   -- other hotels the assistant named
  answer       text,                       -- the raw answer, for audit
  model_ref    text,
  source       text not null,
  captured_at  timestamptz not null default now()
);
create index on ai_answers (property_id, captured_at desc);

create table local_events (
  id           uuid primary key default gen_random_uuid(),
  property_id  uuid not null references properties(id),
  city         text,
  name         text not null,
  kind         text,
  starts_on    date not null,
  ends_on      date not null,
  impact       text not null default 'medium' check (impact in ('low','medium','high')),
  lift_pct     int,                        -- suggested rate lift
  visitors     int,
  source       text not null,
  external_id  text,
  created_at   timestamptz not null default now(),
  unique (source, external_id)
);
create index on local_events (property_id, starts_on);

create table intel_sources (
  name         text primary key,
  configured   boolean not null default false,
  last_run_at  timestamptz,
  last_status  text,
  last_count   int
);

-- registry marker for deploy --upgrade
create table intel_marker (applied_at timestamptz not null default now());
insert into intel_marker default values;
alter table intel_marker enable row level security;

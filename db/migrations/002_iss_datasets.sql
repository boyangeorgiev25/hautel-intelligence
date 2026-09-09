-- WP1 · Migration 002 — AI data foundation for the ISS use case
-- Datasets the WP2 matching engine and WP3 advice module operate on:
-- hotel profiles, marketing needs, consultant/expertise records, and
-- unstructured documents. Plus the output tables both PoCs write to
-- (matches, advice, evaluations) so provenance is queryable end-to-end.

-- ── Structured inputs ──────────────────────────────────────────────────────

create table hotel_profiles (
  id            uuid primary key default gen_random_uuid(),
  property_id   uuid not null references properties(id) unique,
  segment       text not null,           -- 'boutique','business','resort','budget',...
  audience      text,                    -- primary guest audience, free text
  positioning   text,                    -- how the hotel wants to be perceived
  channels      text[] not null default '{}',  -- active marketing channels
  strengths     text[] not null default '{}',
  weaknesses    text[] not null default '{}',
  updated_at    timestamptz not null default now()
);

create table marketing_needs (
  id            uuid primary key default gen_random_uuid(),
  property_id   uuid not null references properties(id),
  title         text not null,
  description   text not null,           -- may be unstructured brief text
  category      text not null,           -- 'branding','content','social','campaign','website','photography',...
  urgency       text not null default 'normal' check (urgency in ('low','normal','high')),
  budget_band   text,                    -- '<1k','1-5k','5-15k','15k+'
  status        text not null default 'open' check (status in ('open','matched','closed')),
  created_at    timestamptz not null default now()
);

create table consultants (
  id            uuid primary key default gen_random_uuid(),
  full_name     text not null,
  kind          text not null default 'freelancer' check (kind in ('freelancer','agency','internal')),
  bio           text,                    -- unstructured: the AI reads this
  languages     text[] not null default '{}',
  region        text,
  day_rate_band text,
  created_at    timestamptz not null default now()
);

create table consultant_expertise (
  consultant_id uuid not null references consultants(id),
  skill         text not null,           -- 'brand identity','SEO','hotel photography',...
  level         text not null default 'senior' check (level in ('junior','mid','senior','expert')),
  evidence      text,                    -- unstructured: portfolio notes, past work
  primary key (consultant_id, skill)
);

-- Unstructured source documents (briefs, bios, positioning docs) —
-- ingested as text now; chunking/embedding metadata lives alongside
-- so WP2 can retrieve without a separate vector store in the PoC.
create table documents (
  id            uuid primary key default gen_random_uuid(),
  org_id        uuid references organizations(id),
  property_id   uuid references properties(id),
  consultant_id uuid references consultants(id),
  kind          text not null,           -- 'brief','bio','positioning','case_study',...
  title         text not null,
  body          text not null,
  source        text,                    -- filename / drive ref
  created_at    timestamptz not null default now()
);

-- ── WP2 output: matches & triggered workflows ──────────────────────────────

create table matches (
  id            uuid primary key default gen_random_uuid(),
  need_id       uuid not null references marketing_needs(id),
  consultant_id uuid not null references consultants(id),
  score         numeric(4,3) not null check (score >= 0 and score <= 1),
  rationale     text not null,           -- AI's stated reasoning (VLAIO evidence)
  model_ref     text not null,           -- model + version used
  status        text not null default 'proposed' check (status in ('proposed','accepted','rejected')),
  created_at    timestamptz not null default now()
);
-- a proposed match triggers a workflow: a task with origin_kind='match'

-- ── WP3 output: advice + quality control ───────────────────────────────────

create table advice (
  id            uuid primary key default gen_random_uuid(),
  property_id   uuid not null references properties(id),
  need_id       uuid references marketing_needs(id),
  body          text not null,           -- the strategic recommendation
  grounding     jsonb not null,          -- source refs the advice cites
  model_ref     text not null,
  created_at    timestamptz not null default now()
);

create table evaluations (
  id            uuid primary key default gen_random_uuid(),
  subject_kind  text not null check (subject_kind in ('match','advice')),
  subject_id    uuid not null,
  metric        text not null,           -- 'relevance','groundedness','consistency','human_rating'
  score         numeric(4,3) not null,
  evaluator     text not null,           -- 'golden_set','llm_judge','human:<name>'
  notes         text,
  created_at    timestamptz not null default now()
);

create index on marketing_needs (property_id, status);
create index on matches (need_id, score desc);
create index on evaluations (subject_kind, subject_id);

-- 005 — WP3: advice module and quality control. Additive.
-- The advice table (002) becomes the home of every WP3 output: the strategic
-- advice itself, drafts made from it and localisations of a draft. `config`
-- records which context the model saw (A = brief only, B = brief + hotel
-- context, C = B + the WP2 match and a validation pass), so the A/B/C
-- comparison in the evaluation report is reproducible. `qc` holds the
-- AI quality-control report; `status` is the human approval gate.

alter table advice
  add column kind          text not null default 'advice' check (kind in ('advice','draft','localisation')),
  add column config        text not null default 'C' check (config in ('A','B','C')),
  add column parent_id     uuid references advice(id),
  add column language      text,                    -- output language: en, nl, fr
  add column structured    jsonb,                   -- the full structured output (audit)
  add column qc            jsonb,                   -- AI quality-control report
  add column status        text not null default 'draft' check (status in ('draft','flagged','accepted','edited','rejected')),
  add column review_note   text,                    -- human validation: reason for accept/edit/reject
  add column reviewed_by   uuid references users(id),
  add column reviewed_at   timestamptz,
  add column run_id        uuid references match_runs(id),   -- the WP2 run the advice builds on (config C)
  add column latency_ms    int,
  add column input_tokens  int,
  add column output_tokens int;

create index on advice (need_id, kind, created_at desc);

-- registry marker for deploy --upgrade
create table wp3_marker (applied_at timestamptz not null default now());
insert into wp3_marker default values;
alter table wp3_marker enable row level security;

-- WP2 · Migration 003 — run-level provenance for the matching engine
-- Additive only. WP1 tables are untouched except for two widened check
-- constraints. Every engine invocation (match OR escalation OR failure) is one
-- match_runs row, so the escalation path has provenance even when no match
-- row exists (dossier §6: MATCH | ESCALATE decision policy; §9 uncertainty 4).

create table match_runs (
  id                      uuid primary key default gen_random_uuid(),
  need_id                 uuid not null references marketing_needs(id),
  engine                  text not null default 'llm' check (engine in ('llm','keyword_baseline')),
  decision                text not null check (decision in ('match','escalate','failed')),
  brief_language          text,                    -- detected: nl, fr, en, de, mixed, other
  need_summary            text,                    -- the engine's one-line interpretation
  core_skills             text[] not null default '{}',
  constraints_checked     text[] not null default '{}',
  escalation_reason       text,
  requires_group_signoff  boolean not null default false,
  signoff_rule            text,                    -- the org rule quoted from the documents
  candidate_count         int not null,            -- size of the pool the engine saw
  model_ref               text not null,           -- model id as served, or 'keyword_baseline_v1'
  latency_ms              int,
  input_tokens            int,
  output_tokens           int,
  raw_output              jsonb,                   -- full structured output, for audit
  created_at              timestamptz not null default now()
);

alter table matches
  add column run_id uuid references match_runs(id),
  add column rank   int check (rank >= 1);

-- an escalation is a task too, but it has no match row to point to: it points to the run
alter table tasks drop constraint tasks_origin_kind_check;
alter table tasks add constraint tasks_origin_kind_check
  check (origin_kind in ('message','match','advice','manual','pms_event','escalation'));

-- golden-set outcomes are scored per run so escalations can be scored as well
alter table evaluations drop constraint evaluations_subject_kind_check;
alter table evaluations add constraint evaluations_subject_kind_check
  check (subject_kind in ('match','advice','match_run'));

create index on match_runs (need_id, created_at desc);
create index on matches (run_id, rank);

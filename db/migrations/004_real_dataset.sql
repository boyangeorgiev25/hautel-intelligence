-- 004 — dataset provenance: synthetic seed vs real data from the Hautel Drive.
-- Real rows live next to the synthetic ones (the WP2 run of record and the golden
-- cases keep their foreign keys); the engine scopes the consultant pool to the
-- dataset of the need it is matching. The `datasets` table is the marker for this
-- migration (deploy_supabase.sh --upgrade) and the registry of what was loaded.

create table datasets (
  name         text primary key check (name in ('synthetic','real')),
  description  text not null,
  loaded_at    timestamptz not null default now()
);
insert into datasets (name, description) values
  ('synthetic', 'Synthetic seed v1 + v1.1: 8 hotels, 10 consultants, 18 needs. Golden cases and the WP2 run of record.'),
  ('real',      'Real roster, hotels and briefs reconstructed from the Hautel Company Drive (28 Sep 2026).');

alter table organizations   add column dataset text not null default 'synthetic' references datasets(name);
alter table properties      add column dataset text not null default 'synthetic' references datasets(name);
alter table marketing_needs add column dataset text not null default 'synthetic' references datasets(name);
alter table consultants     add column dataset text not null default 'synthetic' references datasets(name);

create index on marketing_needs (dataset, status);
create index on consultants (dataset);

alter table datasets enable row level security;

#!/usr/bin/env bash
# WP1 — deploy the schema (+ optional seed) to the EU-hosted test environment.
#
# Target: a Supabase project in an EU region (Frankfurt, eu-central-1) on the
# Hautel-owned account. Anyone with the project's database URL can run this;
# it is idempotent-safe for a fresh project and refuses to run twice by default.
#
# Usage:
#   HAUTEL_DATABASE_URL='postgresql://postgres.<ref>:<password>@aws-0-eu-central-1.pooler.supabase.com:5432/postgres' \
#     scripts/deploy_supabase.sh            # migrations only
#   ... scripts/deploy_supabase.sh --seed   # migrations + synthetic seed
#   ... scripts/deploy_supabase.sh --force  # re-apply even if tables exist (drops nothing)
#   ... scripts/deploy_supabase.sh --upgrade [--seed]
#                                            # existing project: apply only the migrations not yet
#                                            # present (WP2: 003), re-run the lock-down, extend the
#                                            # read-only reviewer role, load only new seed files
set -euo pipefail
DIR="$(cd "$(dirname "$0")/.." && pwd)"
URL="${HAUTEL_DATABASE_URL:-}"
[ -n "$URL" ] || { echo "set HAUTEL_DATABASE_URL to the Supabase connection string (Project settings > Database > Connection string, 'URI')"; exit 1; }

SEED=0; FORCE=0; UPGRADE=0
for a in "$@"; do case "$a" in --seed) SEED=1;; --force) FORCE=1;; --upgrade) UPGRADE=1;; esac; done

# marker table per migration: present => that migration has been applied
marker_for() { case "$(basename "$1")" in
  001_*) echo organizations;; 002_*) echo hotel_profiles;; 003_*) echo match_runs;; *) echo "";; esac; }
has_table() { [ "$(psql "$URL" -At -c "select count(*) from information_schema.tables where table_schema='public' and table_name='$1'")" != "0" ]; }

# 1. Region check: refuse anything that is not an EU host (dossier §8, EU-resident by default)
HOST="$(printf '%s' "$URL" | sed -E 's#.*@([^:/]+).*#\1#')"
case "$HOST" in
  *eu-central-1*|*eu-west-1*|*eu-west-2*|*eu-west-3*|*eu-north-1*|*europe-*) ;;
  *) echo "refusing: host '$HOST' is not an EU region"; exit 1;;
esac

# 2. Fresh-project guard
EXISTS="$(psql "$URL" -At -c "select count(*) from information_schema.tables where table_schema='public' and table_name='organizations'")"
if [ "$EXISTS" != "0" ] && [ "$FORCE" = "0" ] && [ "$UPGRADE" = "0" ]; then
  echo "schema already present on $HOST; pass --upgrade to apply new migrations, or --force to re-apply"; exit 1
fi

# 3. Apply migrations in order (with --upgrade: only those whose marker table is missing)
for f in "$DIR"/db/migrations/*.sql; do
  if [ "$UPGRADE" = "1" ] && m="$(marker_for "$f")" && [ -n "$m" ] && has_table "$m"; then
    echo "skipping $(basename "$f") (already applied)"; continue
  fi
  echo "applying $(basename "$f")"; psql "$URL" -v ON_ERROR_STOP=1 -q -f "$f"
done

# 4. Lock the schema down: no anonymous/PostgREST access to any table.
#    The PoC talks to Postgres directly with the service role; RLS policies per
#    tenant are added when the first client data lands (dossier §3).
psql "$URL" -v ON_ERROR_STOP=1 -q <<'SQL'
do $$ declare t text; begin
  for t in select table_name from information_schema.tables where table_schema='public' loop
    execute format('alter table public.%I enable row level security', t);
    execute format('revoke all on public.%I from anon, authenticated', t);
  end loop;
end $$;
SQL
echo "RLS enabled on all tables; anon/authenticated roles revoked"

# 4b. Read-only reviewer role (created 9 Sep, WP1): extend select-only access to any new table
psql "$URL" -v ON_ERROR_STOP=1 -q <<'SQL'
do $$ declare t text; begin
  if exists (select 1 from pg_roles where rolname = 'anton_readonly') then
    for t in select table_name from information_schema.tables where table_schema='public' loop
      execute format('grant select on public.%I to anton_readonly', t);
      if not exists (select 1 from pg_policies where schemaname='public' and tablename=t and policyname='readonly_review') then
        execute format('create policy readonly_review on public.%I for select to anton_readonly using (true)', t);
      end if;
    end loop;
  end if;
end $$;
SQL
echo "read-only reviewer role covers all tables (if present)"

# 5. Optional seed. Fresh deploy: v1 + v1.1. Upgrade: only the seed files not yet loaded.
if [ "$SEED" = "1" ]; then
  if [ "$UPGRADE" = "0" ] || [ "$(psql "$URL" -At -c "select count(*) from organizations")" = "0" ]; then
    psql "$URL" -v ON_ERROR_STOP=1 -q -f "$DIR/db/seed/synthetic_seed.sql"; echo "synthetic seed v1 loaded"
  fi
  if [ "$(psql "$URL" -At -c "select count(*) from marketing_needs where id='d0000000-0000-0000-0000-000000000013'")" = "0" ]; then
    psql "$URL" -v ON_ERROR_STOP=1 -q -f "$DIR/db/seed/wp2_test_needs.sql"; echo "synthetic seed v1.1 (WP2 test needs) loaded"
  else
    echo "seed v1.1 already present"
  fi
fi

echo "done: $HOST"

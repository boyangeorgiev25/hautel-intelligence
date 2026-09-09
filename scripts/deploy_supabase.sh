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
set -euo pipefail
DIR="$(cd "$(dirname "$0")/.." && pwd)"
URL="${HAUTEL_DATABASE_URL:-}"
[ -n "$URL" ] || { echo "set HAUTEL_DATABASE_URL to the Supabase connection string (Project settings > Database > Connection string, 'URI')"; exit 1; }

SEED=0; FORCE=0
for a in "$@"; do case "$a" in --seed) SEED=1;; --force) FORCE=1;; esac; done

# 1. Region check: refuse anything that is not an EU host (dossier §8, EU-resident by default)
HOST="$(printf '%s' "$URL" | sed -E 's#.*@([^:/]+).*#\1#')"
case "$HOST" in
  *eu-central-1*|*eu-west-1*|*eu-west-2*|*eu-west-3*|*eu-north-1*|*europe-*) ;;
  *) echo "refusing: host '$HOST' is not an EU region"; exit 1;;
esac

# 2. Fresh-project guard
EXISTS="$(psql "$URL" -At -c "select count(*) from information_schema.tables where table_schema='public' and table_name='organizations'")"
if [ "$EXISTS" != "0" ] && [ "$FORCE" = "0" ]; then
  echo "schema already present on $HOST; pass --force to re-apply"; exit 1
fi

# 3. Apply migrations in order
for f in "$DIR"/db/migrations/*.sql; do
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

# 5. Optional seed
if [ "$SEED" = "1" ]; then
  psql "$URL" -v ON_ERROR_STOP=1 -q -f "$DIR/db/seed/synthetic_seed.sql"; echo "synthetic seed loaded"
fi

echo "done: $HOST"

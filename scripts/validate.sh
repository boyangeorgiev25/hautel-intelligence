#!/usr/bin/env bash
# WP1 — validation checks. Runs against any environment (read-only login is enough)
# and prints PASS/FAIL per check with the expected and actual values.
# Usage: scripts/validate.sh "<connection url>"
set -uo pipefail
URL="${1:-${HAUTEL_READONLY_URL:-}}"
[ -n "$URL" ] || { echo "usage: scripts/validate.sh <connection url>"; exit 1; }
q() { psql "$URL" -At -X -c "$1" 2>&1 | tr -d '\r'; }
fail=0
check() { # name, expected, sql
  local got; got="$(q "$3")"
  if [ "$got" = "$2" ]; then printf 'PASS  %-58s %s\n' "$1" "$got"
  else printf 'FAIL  %-58s expected %s, got %s\n' "$1" "$2" "$got"; fail=1; fi
}
echo "Hautel Intelligence — WP1 validation — $(date '+%Y-%m-%d %H:%M')"
echo "host: $(printf '%s' "$URL" | sed -E 's#.*@([^:/]+).*#\1#')"
echo
check "1. Region is EU (Frankfurt)"                 "eu-central-1" "select case when '$URL' like '%eu-central-1%' then 'eu-central-1' else 'NOT EU' end"
check "2. Postgres major version"                    "17"           "select split_part(current_setting('server_version'),'.',1)"
check "3. Tables in the platform schema"             "19"           "select count(*) from pg_tables where schemaname='public'"
check "4. Tables with row-level security enabled"    "19"           "select count(*) from pg_tables where schemaname='public' and rowsecurity"
check "5. Grants held by anonymous/API roles"        "0"            "select count(*) from information_schema.role_table_grants where grantee in ('anon','authenticated') and table_schema='public'"
check "6. Hotels with a profile"                     "8"            "select count(*) from hotel_profiles"
check "7. Consultants in the pool"                   "10"           "select count(*) from consultants"
check "8. Skill records"                             "27"           "select count(*) from consultant_expertise"
check "9. Open marketing needs"                      "12"           "select count(*) from marketing_needs where status='open'"
check "10. Unstructured documents"                   "6"            "select count(*) from documents"
check "11. Real (non-synthetic) organizations"       "0"            "select count(*) from organizations where id::text not like 'a0000000-%'"
check "12. WP2 output tables exist and are empty"    "0"            "select (select count(*) from matches)+(select count(*) from tasks)"
check "13. WP3 output tables exist and are empty"    "0"            "select (select count(*) from advice)+(select count(*) from evaluations)"
check "14. Every need belongs to a real hotel row"   "0"            "select count(*) from marketing_needs n left join properties p on p.id=n.property_id where p.id is null"
check "15. Every skill row belongs to a consultant"  "0"            "select count(*) from consultant_expertise e left join consultants c on c.id=e.consultant_id where c.id is null"
got="$(q "insert into organizations(name) values ('probe')")"
case "$got" in *"permission denied"*) printf 'PASS  %-58s %s\n' "16. Writes are refused for this login" "permission denied";;
  *) printf 'FAIL  %-58s expected permission denied, got %s\n' "16. Writes are refused for this login" "$got"; fail=1;; esac
echo
[ $fail = 0 ] && echo "ALL CHECKS PASSED" || echo "SOME CHECKS FAILED"
exit $fail

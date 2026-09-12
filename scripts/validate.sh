#!/usr/bin/env bash
# WP1+WP2 — validation checks. Runs against any environment (read-only login is enough)
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
echo "Hautel Intelligence — WP1/WP2 validation — $(date '+%Y-%m-%d %H:%M')"
echo "host: $(printf '%s' "$URL" | sed -E 's#.*@([^:/]+).*#\1#')"
echo
check "1. Region is EU (Frankfurt)"                 "eu-central-1" "select case when '$URL' like '%eu-central-1%' then 'eu-central-1' else 'NOT EU' end"
check "2. Postgres major version"                    "17"           "select split_part(current_setting('server_version'),'.',1)"
check "3. Tables in the platform schema"             "20"           "select count(*) from pg_tables where schemaname='public'"
check "4. Tables with row-level security enabled"    "20"           "select count(*) from pg_tables where schemaname='public' and rowsecurity"
check "5. Grants held by anonymous/API roles"        "0"            "select count(*) from information_schema.role_table_grants where grantee in ('anon','authenticated') and table_schema='public'"
check "6. Hotels with a profile"                     "8"            "select count(*) from hotel_profiles"
check "7. Consultants in the pool"                   "10"           "select count(*) from consultants"
check "8. Skill records"                             "27"           "select count(*) from consultant_expertise"
check "9. Marketing needs (seed v1 + v1.1)"            "18"           "select count(*) from marketing_needs"
check "10. Unstructured documents"                   "8"            "select count(*) from documents"
check "11. Real (non-synthetic) organizations"       "0"            "select count(*) from organizations where id::text not like 'a0000000-%'"
check "12. WP2 has run: engine runs recorded"         "yes"          "select case when count(*)>0 then 'yes' else 'no (WP2 not run yet)' end from match_runs"
check "13. WP3 outputs not yet present (advice, non-golden evals)" "0"  "select (select count(*) from advice)+(select count(*) from evaluations where evaluator<>'golden_set')"
check "14. Every need belongs to a real hotel row"   "0"            "select count(*) from marketing_needs n left join properties p on p.id=n.property_id where p.id is null"
check "15. Every skill row belongs to a consultant"  "0"            "select count(*) from consultant_expertise e left join consultants c on c.id=e.consultant_id where c.id is null"
# ── WP2: matching & workflow engine outputs ──
check "17. Every match points to a recorded run"     "0"            "select count(*) from matches m left join match_runs r on r.id=m.run_id where r.id is null"
check "18. Every proposal task points to a match"    "0"            "select count(*) from tasks t where t.origin_kind='match' and not exists (select 1 from matches m where m.id=t.origin_id)"
check "19. Every escalation task points to a run"    "0"            "select count(*) from tasks t where t.origin_kind='escalation' and not exists (select 1 from match_runs r where r.id=t.origin_id)"
check "20. Every engine task is routed to a person"  "0"            "select count(*) from tasks where origin_kind in ('match','escalation') and assigned_to is null"
check "21. Engine escalates instead of guessing"     "yes"          "select case when count(*)>0 then 'yes' else 'no' end from match_runs where decision='escalate'"
check "22. Every match carries a written rationale"  "0"            "select count(*) from matches where length(rationale) < 40"
check "23. Golden-set judgements recorded"           "yes"          "select case when count(*)>0 then 'yes' else 'no' end from evaluations where evaluator='golden_set'"
got="$(q "insert into organizations(name) values ('probe')")"
case "$got" in *"permission denied"*) printf 'PASS  %-58s %s\n' "16. Writes are refused for this login" "permission denied";;
  *) printf 'FAIL  %-58s expected permission denied, got %s\n' "16. Writes are refused for this login" "$got"; fail=1;; esac
echo
[ $fail = 0 ] && echo "ALL CHECKS PASSED" || echo "SOME CHECKS FAILED"
exit $fail

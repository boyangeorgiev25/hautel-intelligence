#!/usr/bin/env bash
# WP1 — local secure test environment (Postgres 17 in Docker, isolated container).
# Usage: scripts/db.sh up | migrate | seed | psql | reset | down
set -euo pipefail

CONTAINER=hautel-iss-db
PORT=54329
DB=hautel
PASS="${HAUTEL_DB_PASS:-hautel-dev-only}"   # override in real deployments
DIR="$(cd "$(dirname "$0")/.." && pwd)"
CONN="postgresql://postgres:${PASS}@localhost:${PORT}/${DB}"

case "${1:-}" in
  up)
    docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER}$" && docker start ${CONTAINER} || \
    docker run -d --name ${CONTAINER} \
      -e POSTGRES_PASSWORD="${PASS}" -e POSTGRES_DB=${DB} \
      -p 127.0.0.1:${PORT}:5432 postgres:17
    echo "waiting for postgres..."; until docker exec ${CONTAINER} pg_isready -q 2>/dev/null; do sleep 0.5; done
    echo "up on localhost:${PORT} (bound to 127.0.0.1 only)"
    ;;
  migrate)
    for f in "${DIR}"/db/migrations/*.sql; do
      echo "applying $(basename "$f")"; psql "${CONN}" -v ON_ERROR_STOP=1 -q -f "$f"
    done
    ;;
  seed)
    psql "${CONN}" -v ON_ERROR_STOP=1 -q -f "${DIR}/db/seed/synthetic_seed.sql"
    echo "seeded"
    ;;
  psql)  exec psql "${CONN}" ;;
  reset) docker rm -f ${CONTAINER} 2>/dev/null || true; "$0" up; "$0" migrate; "$0" seed ;;
  down)  docker stop ${CONTAINER} ;;
  *) echo "usage: $0 up|migrate|seed|psql|reset|down"; exit 1 ;;
esac

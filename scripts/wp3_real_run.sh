#!/bin/zsh
# WP3 real-data run on the EU environment (29 Sep 2026): match the two unmatched real briefs,
# generate configuration-C advice for the real briefs that have none, QC every un-checked advice,
# and draft one specialist brief from every real advice. Uses the engine CLI; env from ~/.hautel/engine.env.
set -u
cd "$(dirname "$0")/.."
LOG=docs/wp3/real-run-2026-09-29.log
mkdir -p docs/wp3

ids() {  # advice ids of real needs: without_qc | without_draft
  uv run python scripts/wp3_real_ids.py "$1"
}

echo "=== real-data WP3 run on Frankfurt, start $(date '+%F %T')" | tee -a "$LOG"
for n in e3000000-0000-0000-0000-000000000005 e3000000-0000-0000-0000-000000000006; do
  echo "--- match $n $(date '+%T')" | tee -a "$LOG"
  uv run hautel-engine match --need "$n" 2>&1 | tail -5 | tee -a "$LOG"
done
for n in e3000000-0000-0000-0000-000000000001 e3000000-0000-0000-0000-000000000003 e3000000-0000-0000-0000-000000000008 e3000000-0000-0000-0000-000000000005 e3000000-0000-0000-0000-000000000006; do
  echo "--- advise C $n $(date '+%T')" | tee -a "$LOG"
  uv run hautel-engine advise --need "$n" --config C 2>&1 | tail -6 | tee -a "$LOG"
done
for a in $(ids without_qc); do
  echo "--- qc $a $(date '+%T')" | tee -a "$LOG"
  uv run hautel-engine qc --advice "$a" 2>&1 | tail -6 | tee -a "$LOG"
done
for a in $(ids without_draft); do
  echo "--- draft specialist_brief from $a $(date '+%T')" | tee -a "$LOG"
  uv run hautel-engine draft --advice "$a" --kind specialist_brief 2>&1 | tail -5 | tee -a "$LOG"
done
echo "=== done $(date '+%F %T')" | tee -a "$LOG"

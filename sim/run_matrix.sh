#!/usr/bin/env bash
# Every persona against every tutor model, in parallel (one server each), then graded.
#   sim/run_matrix.sh "00,01" aws/anthropic/bedrock-claude-sonnet-5-5 nvidia/nvidia/nemotron-3.5-super-vl
# Prints the run directories; summarize with: npx tsx sim/summarize.ts runs/<id>...
set -u
cd "$(dirname "$0")/.."
modules=$1; shift
port=8821
pids=()
for model in "$@"; do
  for p in sim/personas/p*.md; do
    (
      line=$(npx tsx sim/app_sim.ts --persona "$p" --tutor "$model" --modules "$modules" --port $port 2>&1 | grep -v "npm notice" | tail -1)
      echo "$line"
      id=$(echo "$line" | sed -n 's/^\[\([^]]*\)\].*/\1/p')
      [ -n "$id" ] && npx tsx sim/grade.ts "runs/$id" 2>&1 | grep -v "npm notice" | head -1
    ) &
    pids+=($!)
    port=$((port + 1))
    sleep 5
  done
done
wait "${pids[@]}"

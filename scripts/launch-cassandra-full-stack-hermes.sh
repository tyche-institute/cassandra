#!/usr/bin/env bash
set -euo pipefail

ROOT="${CASSANDRA_ROOT:-/home/anton/projects/cassandra}"
PROMPT_FILE="${1:-$ROOT/notes/hermes-full-stack-publication-directive-2026-05-27.md}"
STOP_FILE="$ROOT/STOP_CASSANDRA_HERMES"
LOG_DIR="$ROOT/logs/hermes-cassandra-full-stack"
ITERATION_TIMEOUT="${HERMES_ITERATION_TIMEOUT:-14400}"
SLEEP_SECONDS="${HERMES_SLEEP_SECONDS:-300}"

cd "$ROOT"
mkdir -p "$LOG_DIR"

if [ ! -f "$PROMPT_FILE" ]; then
  echo "Missing prompt file: $PROMPT_FILE" >&2
  exit 2
fi

while [ ! -e "$STOP_FILE" ]; do
  timestamp="$(date -u +%Y%m%dT%H%M%SZ)"
  log="$LOG_DIR/$timestamp.log"
  {
    echo "Cassandra full-stack Hermes iteration: $timestamp"
    echo "Root: $ROOT"
    echo "Prompt: $PROMPT_FILE"
    echo "Stop file: $STOP_FILE"
    echo
  } > "$log"

  set +e
  timeout "$ITERATION_TIMEOUT" hermes --yolo -z "$(cat "$PROMPT_FILE")" >> "$log" 2>&1
  rc=$?
  set -e

  {
    echo
    echo "Hermes exit code: $rc"
    date -u +%Y-%m-%dT%H:%M:%SZ
  } >> "$log"

  if [ -e "$STOP_FILE" ]; then
    break
  fi
  sleep "$SLEEP_SECONDS"
done

echo "Cassandra Hermes lane stopped because $STOP_FILE exists."

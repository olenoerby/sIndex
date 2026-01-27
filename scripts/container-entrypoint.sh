#!/bin/sh
set -e
# Simple entrypoint that logs startup and shutdown messages with timestamps
SERVICE_NAME=${SERVICE_NAME:-container}
ts() { date -u +"%Y-%m-%dT%H:%M:%SZ"; }
echo "$(ts) [${SERVICE_NAME}] starting"

# Start the main process
"$@" &
CHILD_PID=$!

shutdown() {
  echo "$(ts) [${SERVICE_NAME}] stopping"
  if kill -0 "$CHILD_PID" 2>/dev/null; then
    kill -TERM "$CHILD_PID" 2>/dev/null
    wait "$CHILD_PID"
  fi
}

trap shutdown TERM INT

wait "$CHILD_PID"
EXIT_CODE=$?
echo "$(ts) [${SERVICE_NAME}] exited with ${EXIT_CODE}"
exit ${EXIT_CODE}

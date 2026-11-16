#!/bin/bash
# Restart the dev server in the background; pid in server.pid, log in server.log.
cd "$(dirname "$0")/.."
[ -f server.pid ] && kill "$(cat server.pid)" 2>/dev/null && sleep 1
port=${PORT:-8765}
if ss -ltn 2>/dev/null | grep -q "127.0.0.1:$port "; then
  echo "Port $port is held by a server this script didn't start (e.g. npm start in a terminal). Stop it there, then rerun." >&2
  exit 1
fi
nohup node --import tsx server/index.ts > server.log 2>&1 &
echo $! > server.pid
for i in $(seq 30); do grep -q "cuPhoton Learn on" server.log && break; sleep 0.5; done
cat server.log

#!/bin/bash
# Restart the dev server in the background; pid in server.pid, log in server.log.
cd "$(dirname "$0")/.."
[ -f server.pid ] && kill "$(cat server.pid)" 2>/dev/null && sleep 1
port=${PORT:-8765}
# On a Brev instance the secure link's proxy arrives over Brev's NetBird mesh (interface wt0), not on
# 127.0.0.1. Listen on that address, looked up at each start: it's reachable by the proxy and not by the
# instance's public interface. An explicit HOST (environment or .env) wins.
if [ -z "${HOST:-}" ] && ! grep -qs '^HOST=' .env; then
  mesh=$(ip -4 -o addr show wt0 2>/dev/null | awk '{print $4}' | cut -d/ -f1)
  [ -n "$mesh" ] && export HOST=$mesh
fi
if ss -ltn 2>/dev/null | grep -qE "[0-9.*]:$port "; then
  echo "Port $port is held by a server this script didn't start (e.g. npm start in a terminal). Stop it there, then rerun." >&2
  exit 1
fi
nohup node --import tsx server/index.ts > server.log 2>&1 &
echo $! > server.pid
for i in $(seq 30); do grep -q "cuPhoton Learn on" server.log && break; sleep 0.5; done
cat server.log

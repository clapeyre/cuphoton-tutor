#!/bin/bash
# Restart the dev server in the background; pid in server.pid, log in server.log.
cd "$(dirname "$0")/.."
[ -f server.pid ] && kill "$(cat server.pid)" 2>/dev/null && sleep 1
nohup node --import tsx server/index.ts > server.log 2>&1 &
echo $! > server.pid
for i in $(seq 30); do grep -q "cuPhoton Learn on" server.log && break; sleep 0.5; done
cat server.log

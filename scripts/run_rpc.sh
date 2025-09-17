#!/bin/bash
set -euo pipefail
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
ROOT_DIR=$(cd "$SCRIPT_DIR/.." && pwd)
export PYTHONPATH="$ROOT_DIR:${PYTHONPATH:-}"
python3 "$ROOT_DIR/src/rpc_master.py" --data "$ROOT_DIR/data" --workers http://localhost:9001 http://localhost:9002 http://localhost:9003 --top 20 | cat


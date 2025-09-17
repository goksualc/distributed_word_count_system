#!/bin/bash
set -euo pipefail
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
ROOT_DIR=$(cd "$SCRIPT_DIR/.." && pwd)
export PYTHONPATH="$ROOT_DIR:${PYTHONPATH:-}"
python3 "$ROOT_DIR/src/process_threads.py" --data "$ROOT_DIR/data" --proc-workers 3 --thread-workers 4 --top 20 | cat


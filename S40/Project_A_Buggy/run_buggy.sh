#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
cd "$PROJECT_DIR"

if [ ! -d .venv_buggy ]; then
  bash setup_buggy.sh
fi

if [[ "$(uname -s)" == CYGWIN* || "$(uname -s)" == MINGW* || "$(uname -s)" == MSYS* ]]; then
  source .venv_buggy/Scripts/activate
else
  source .venv_buggy/bin/activate
fi

start_ts=$(python - <<'PY'
import time
print(f"{time.time():.6f}")
PY
)

# Run tests and capture output even on failure (expected for buggy implementation).
set +e
pytest --maxfail=1 --disable-warnings -q | tee log_buggy.txt
pytest_exit=${PIPESTATUS[0]}
set -e

end_ts=$(python - <<'PY'
import time
print(f"{time.time():.6f}")
PY
)

duration=$(python - <<PY
start = float("$start_ts")
end = float("$end_ts")
print(f"{end - start:.6f}")
PY
)

cat > time_buggy.txt <<EOF
start_time_seconds=$start_ts
end_time_seconds=$end_ts
elapsed_seconds=$duration
pytest_exit_code=$pytest_exit
EOF

exit $pytest_exit

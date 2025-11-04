#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
cd "$PROJECT_DIR"

if [ ! -d .venv_fixed ]; then
  bash setup_fixed.sh
fi

if [[ "$(uname -s)" == CYGWIN* || "$(uname -s)" == MINGW* || "$(uname -s)" == MSYS* ]]; then
  source .venv_fixed/Scripts/activate
else
  source .venv_fixed/bin/activate
fi

start_ts=$(python - <<'PY'
import time
print(f"{time.time():.6f}")
PY
)

pytest --disable-warnings -q | tee log_fixed.txt
exit_code=${PIPESTATUS[0]}

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

cat > time_fixed.txt <<EOF
start_time_seconds=$start_ts
end_time_seconds=$end_ts
elapsed_seconds=$duration
pytest_exit_code=$exit_code
EOF

exit $exit_code

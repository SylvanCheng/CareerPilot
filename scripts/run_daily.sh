#!/bin/bash
# Daily run: fetch new postings and build output/<date>.xlsx (date in the profile's timezone).
# Usage: scripts/run_daily.sh            -> prints the path of the report on stdout
# Env: JOB_REPORT_HOME (workspace with profile.json), JOB_REPORT_PROFILE, JOB_REPORT_OUT, JOB_REPORT_TZ
set -e
DIR="$(cd "$(dirname "$0")" && pwd)"
read -r OUT TZ_NAME < <(python3 - "$DIR" <<'EOF'
import sys; sys.path.insert(0, sys.argv[1]); import config
p = config.load_profile(); print(config.out_dir(p), config.tz(p))
EOF
)
D=$(TZ="$TZ_NAME" date +%F)
mkdir -p "$OUT/raw"
python3 "$DIR/fetch_jobs.py" "$OUT/raw/jobs_$D.json"
python3 "$DIR/build_report.py" "$OUT/raw/jobs_$D.json" "$OUT/$D.xlsx" >&2
echo "$OUT/$D.xlsx"

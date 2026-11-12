# Shared settings. Everything personal lives in the user's workspace (profile.json, cv/, output/),
# never inside the skill folder, so the skill itself can be shared and updated with git pull.
#
# Workspace resolution (first that applies):
#   1. env JOB_REPORT_HOME
#   2. ./job-report-workspace  if it exists in the current directory
#   3. ~/job-daily-report
import json, os, re

SKILL_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def workspace():
    if os.environ.get("JOB_REPORT_HOME"):
        return os.path.abspath(os.path.expanduser(os.environ["JOB_REPORT_HOME"]))
    local = os.path.abspath("job-report-workspace")
    if os.path.isdir(local):
        return local
    return os.path.expanduser("~/job-daily-report")


HOME = workspace()
PROFILE_PATH = os.path.abspath(os.path.expanduser(os.environ.get("JOB_REPORT_PROFILE", os.path.join(HOME, "profile.json"))))


def resolve(path):
    """Paths in profile.json: absolute, ~/..., 'skill:...' (relative to the skill), or relative to the workspace."""
    if not path:
        return path
    if path.startswith("skill:"):
        return os.path.join(SKILL_ROOT, path[len("skill:"):])
    path = os.path.expanduser(path)
    return path if os.path.isabs(path) else os.path.join(HOME, path)


def load_profile(path=None):
    path = path or PROFILE_PATH
    if not os.path.exists(path):
        raise SystemExit(f"profile not found: {path}\nRun the intake first (see references/intake-questionnaire.md), "
                         f"or set JOB_REPORT_HOME / JOB_REPORT_PROFILE.")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def out_dir(profile):
    return resolve(os.environ.get("JOB_REPORT_OUT") or profile.get("output_dir", "output"))


def tz(profile):
    return os.environ.get("JOB_REPORT_TZ") or profile.get("timezone", "UTC")


def tier_sheet_names(profile):
    lang = profile.get("report_language", "zh")
    names = []
    for i, t in enumerate(profile["tiers"], 1):
        n = t.get("sheet_name") or (f"{t['name']}公司" if lang == "zh" else f"{t['name']} companies")
        names.append(re.sub(r"[\[\]\*\?/\\:]", "-", n)[:31])  # Excel sheet name rules
    return names

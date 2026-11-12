---
name: job-daily-report
description: Personalised daily job report (求职日报) for anyone, in any country. First run - an intake questionnaire plus the user's CV produce a profile with target directions, tiers of matching companies and visa-sponsor rules. Every day after - fetch LinkedIn postings from the last 24h, keep those at the user's target companies and directions, check visa sponsorship, and write a dated Excel workbook. Use when someone wants to set up, run, rerun, schedule, tune or reset their job daily report, or asks for daily job alerts matched to their CV.
---

# Job daily report（求职日报）

One Excel workbook per day, `output/<YYYY-MM-DD>.xlsx`, with these sheets:

| Sheet (zh / en) | Content |
|---|---|
| 今日概览 / Overview | New jobs per sheet, filter rules, direction → CV, data source, sponsor register link |
| 第一梯队公司 … 第N梯队公司 / Tier 1…N companies | New postings at each tier's target companies; company cells merged; apply link, careers page, why-this-company, hints, status tracking columns |
| 适合我投递的其他公司 / Other companies | Matching postings at companies outside the tiers (only visa sponsors when a register exists) |
| 个人背景 / Profile | The user's background and the direction → CV table |
| 投递渠道 / Channels | Job boards and channels for the target country |

The number of tiers, the directions, the companies and the visa rules all come from the user's `profile.json`. Reply to the user in their language (Chinese if they write Chinese).

## Step 0: find the workspace

Personal data never lives in the skill folder. The workspace is `$JOB_REPORT_HOME`, else `./job-report-workspace` if it exists, else `~/job-daily-report`:

```
<workspace>/profile.json      # everything the scripts need (generated in onboarding)
<workspace>/cv/               # the user's CV files
<workspace>/output/           # daily reports + raw/jobs_<date>.json
<workspace>/notes.md          # feedback log for later tuning
```

- `profile.json` exists → go to **Daily run**.
- It does not → **Onboarding**. If the user says "reset" / "重新设置", back up the old profile to `profile.<date>.bak.json` and onboard again.

## Onboarding (first time, ~15 minutes)

1. **Questionnaire.** Ask the questions in `references/intake-questionnaire.md`. Mostly multiple choice: use a structured question tool (e.g. AskUserQuestion) when the agent has one, otherwise send the questionnaire as one numbered message the user can answer as `1B 2A,C 3 ...`. Ask in batches of at most 4–6 questions; skip questions already answered by the CV.
2. **CV.** Ask the user to upload their CV (PDF/DOCX/text; several CVs for several directions is fine). Save copies to `<workspace>/cv/`. Read it fully.
3. **Analyse and research.** Follow `references/build-profile.md`: derive directions (2–5) from the CV and the answers, decide the number of tiers (2–5, the agent decides from the user's industry background), pick companies per tier, set filters, sponsorship mode and channels. Use web search when available to check company names, careers URLs and sponsor status; never invent a sponsor status (use `U` when unsure).
4. **Write** `<workspace>/profile.json` (schema in `references/build-profile.md`; full examples in `examples/`). Then run:
   ```bash
   pip install openpyxl                       # only dependency, Python 3.9+
   python3 scripts/validate_profile.py <workspace>/profile.json
   ```
   Fix every ERROR. If sponsorship uses an official register, download it into `<workspace>/data/` (see `references/sponsor-registers.md`).
5. **Confirm with the user** in one short summary: directions → CV, tiers (name, why, number of companies, 3–5 example companies each), filters (experience cap, language, exclusions), sponsor mode. Apply their changes.
6. **Test run** (≈1–2 min): `python3 scripts/fetch_jobs.py <ws>/output/raw/test.json --max-pages=3` then `python3 scripts/build_report.py <ws>/output/raw/test.json <ws>/output/test.xlsx`. Look at the titles that matched and at the "other companies" sheet: add obvious false positives to `filters.exclude_title_regex`, missing LinkedIn spellings of tier companies to `aliases`. Then do the first full run and deliver the file.
7. **Offer scheduling** (see Daily run → Scheduling).

## Daily run

```bash
curl -sI https://www.linkedin.com/jobs | head -1    # must not be 403 (see Network)
JOB_REPORT_HOME=<workspace> scripts/run_daily.sh   # 5–20 min; prints the report path
```

`run_daily.sh` = `fetch_jobs.py <ws>/output/raw/jobs_<date>.json` + `build_report.py jobs.json <date>.xlsx`. A saved JSON can be rebuilt without network any time (`build_report.py`), e.g. after changing labels or the background sheet. Changes to directions, title filters or companies need a new fetch.

Check the run: stderr ends with `raw N, unique N, matched N, others N`. A keyword with 0 results usually means rate limiting; rerun later. Deliver the xlsx and summarise in 2–3 lines (new jobs per tier, best 3 postings).

**Scheduling.** `run_daily.sh` is cron-friendly (`0 6 * * * JOB_REPORT_HOME=... /path/scripts/run_daily.sh`). In an agent that supports scheduled tasks or routines, schedule: "Run the job-daily-report skill for workspace X and send me today's report". Pick a time shortly after the user wakes up in `profile.timezone`.

## Feedback and iteration

When the user reviews a report ("这个岗位不相关", "add company X", "I don't want consulting roles"):

- Irrelevant title → add a word to `filters.exclude_title_regex` (narrow, whole words).
- Missing/extra company → edit `tiers[].companies`; LinkedIn spelling differs → `aliases`.
- Wrong direction → adjust `directions[].title_regex` or `search.keywords`.
- Too senior / language → `filters.max_years_experience`, `filters.local_language`.
- Log each change with the date in `<workspace>/notes.md`, validate, and rebuild today's report if the fix is in the build step.

## Files

| Path | What it holds |
|---|---|
| `references/intake-questionnaire.md` | Onboarding questions (choices + short answers) and how each maps to the profile |
| `references/build-profile.md` | How to turn CV + answers into directions, tiers, filters; full `profile.json` schema |
| `references/sponsor-registers.md` | Visa-sponsor registers per country and how to configure them |
| `references/maintenance.md` | Updating registers, tuning filters, checking quality, troubleshooting |
| `scripts/fetch_jobs.py` | LinkedIn guest search (all locations × keywords), title/direction/company classification, description checks (experience, fluent local language) |
| `scripts/build_report.py` | Builds the workbook |
| `scripts/filters.py`, `scripts/sponsor.py` | Matching rules and sponsor-register lookup |
| `scripts/validate_profile.py` | Profile checks |
| `examples/profile.netherlands-tech.json` | Full example (4 tiers, 169 companies, IND register) — the original Netherlands report |
| `examples/profile.germany-data.en.json` | Small English example, no register (research mode) |
| `data/registers/` | Bundled registers (Netherlands IND, 2026-10-05) |

## Network

The fetch needs `www.linkedin.com` (guest job pages, no login). Some cloud sandboxes block it (HTTP 403 from a proxy): the environment then needs network access to `linkedin.com`, or the user runs the script on their own computer. LinkedIn may rate-limit heavy use; keep `parallel` ≤ 5 and the keyword × location count ≤ ~40.

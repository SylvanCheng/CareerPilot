# Maintenance（维护指南）

## Check a run

- `fetch_jobs.py` stderr ends with `raw N, unique N, matched N, others N`. A keyword returning 0 means rate limiting or a block; rerun later. `raw 0` exits with code 2.
- Open 今日概览 for totals. Scan the tier sheets for titles that don't fit and the other-companies sheet for big companies that should be in a tier.
- Expect roughly: a country-wide search with 20–25 keywords → 2,000–4,000 unique cards, 20–80 tier matches. A city-only search or a niche field gives far fewer; widen keywords or locations if a week of reports is nearly empty.

## Tune

| Problem | Change in profile.json |
|---|---|
| Irrelevant titles | add whole words to `filters.exclude_title_regex` |
| Relevant titles missing | widen `directions[].title_regex`, add `search.keywords` |
| Tier company never matches | check its LinkedIn company name; add `aliases` |
| Wrong company matched (e.g. "ING" vs "Ingram") | anchor `aliases` (`^ING$`), or add to `filters.exclude_companies_regex` |
| Wrong register entity | `sponsor_patterns` with `^` anchors, or `sponsorship.register_exclude_regex` |
| Too many senior postings | lower `filters.max_years_experience` |
| Postings needing the local language | `filters.local_language` + `extra_*` words in that language |
| Recruiter postings in "other companies" | `sponsorship.agency_regex` (replaces the default list, so copy it from `scripts/sponsor.py` and extend) |

Build-step-only changes (labels, background, channels, overview notes, tier titles) → rerun `build_report.py` on the saved JSON. Anything about matching → rerun the fetch. Run `validate_profile.py` after each edit and log the change in `<workspace>/notes.md`.

## Update a sponsor register

Download the new file into `<workspace>/data/`, point `sponsorship.register.file` at it, update `version`, validate (prints the number of organisations), rebuild today's report and look at tier companies whose ✅/❌ flipped.

## Troubleshooting

- `403` / `connect_rejected` on linkedin.com: the network blocks LinkedIn. Allow `linkedin.com` in the sandbox network policy or run on the user's computer.
- `profile not found`: set `JOB_REPORT_HOME` or run from a folder containing `job-report-workspace/`.
- Excel shows `#REF` in 今日概览 totals: a sheet was renamed by hand; rebuild.
- Sheet names are cut at 31 characters (Excel limit); use `tiers[].sheet_name` for long names.

## Release hygiene (skill repo)

Never commit a real `profile.json`, CVs or reports. The `.gitignore` covers `profile.json`, `job-report-workspace/`, `output/`, `cv/`, `*.docx`, `*.pdf`. Note changes in `CHANGELOG.md`.

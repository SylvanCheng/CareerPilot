# Building profile.json from the CV and the questionnaire

The goal is a profile as useful as `examples/profile.netherlands-tech.json`: precise directions, a few hundred well-chosen companies at most, honest sponsor information.

## 1. Read the CV

Extract: current/last roles and years of experience, industry (domain knowledge is the strongest differentiator), core skills and tools, degrees, languages, notable achievements, visa situation. Write 5–8 `background.rows` from this (`[label, text]`), e.g. 姓名/所在地, 学历, 核心经历, 技能, 语言, 差异化卖点, 签证目标. Keep it factual; it is shown on the 个人背景 sheet.

## 2. Directions (2–5)

A direction = one family of job titles the user can credibly apply for, ideally one CV each. Derive from CV + Q6. For each:

| Field | How |
|---|---|
| `code` | One unique character (A, M, S, T, D, …). Order = priority (first direction wins when a title matches several). |
| `name` | Short label shown in the report, e.g. "AI 工程师", "Data analyst". |
| `title_regex` | Case-insensitive regex on the job **title**. Use `\b(...)\b` with alternatives incl. local-language titles (e.g. Dutch "ontwikkelaar", German "Entwickler"). Broad enough to catch variants, but a word like "engineer" alone is too broad. |
| `cv_file` | File name from `<workspace>/cv/`. |
| `pitch`, `target_titles` | One-line positioning; titles to aim for (shown on 个人背景). |

`search.keywords`: 10–25 LinkedIn search terms covering all directions (each keyword × location costs 30–60 s). Mix exact titles ("data engineer") and skills ("python", "LLM").

## 3. Tiers (the agent decides how many: usually 3–5)

Tiers rank **companies** by how well the user's background fits them, not by prestige. Decide the number from the user's background; explain the logic to the user in one line per tier and store it in `tiers[].rationale`. A pattern that worked well (original Netherlands report, ex-semiconductor-fab engineer moving into AI/data):

1. **Tier 1 – own industry**: companies in the user's current industry/supply chain where domain knowledge is a direct advantage (there: semiconductor equipment & suppliers).
2. **Tier 2 – adjacent industries** where the skills transfer with a short story (there: industrial automation, digital twins, Industry 4.0).
3. **Tier 3 – large employers that hire many people in the directions**: big tech, banks, consulting and IT-services/outsourcing firms (often reliable visa sponsors).
4. **Tier 4 – other suitable industries** and startups.

Use fewer tiers for a narrow market or junior profile, more for a broad one. Sizes: 15–60 companies per tier, 60–200 in total. Respect Q12–Q15 (preferred/avoided industries, company types, must-haves).

Per company:

| Field | Required | Notes |
|---|---|---|
| `name` | yes | Display name, unique across tiers |
| `sector`, `cities` | yes | Short; cities in the target country |
| `directions` | yes | Direction codes this company hires for, e.g. "AMS" |
| `priority` | yes | A = strong fit, apply first; B = fit; C = backup / higher bar / language risk |
| `match` | yes | One line: why the user fits, which roles to target |
| `careers_url` | yes | Real careers page (verify with web search when possible) |
| `aliases` | no | Regexes on the LinkedIn company name. Omit → matched by normalised name (legal suffixes like B.V./GmbH/Ltd removed; also "Name …" prefix). Add when LinkedIn uses another name (e.g. `["^EY\\b", "^Ernst"]`) or the name is short/ambiguous (`["^ING$"]`). |
| `sponsor_patterns` | no | Regexes on register entity names (register mode). Omit → normalised-name lookup. |
| `sponsor_status` | no | Research mode only: `Y` known sponsor (evidence found), `U` unknown. Never guess `Y`. |
| `sponsor_note` | no | e.g. "only the subsidiary X is in the register" |

## 4. Filters

```json
"filters": {
  "exclude_summary": "实习、毕业设计、PhD、经理及以上管理岗、销售",   // shown in 今日概览
  "exclude_title_regex": "\\b(intern|internship|thesis|phd|director|head of|manager|sales|...)\\b",
  "senior_title_regex": "\\b(senior|sr\\.?|lead|expert)\\b",          // only adds a hint
  "max_years_experience": 5,          // drop postings whose description demands MORE; null = off
  "exclude_companies_regex": [],      // never show these LinkedIn names
  "local_language": {                 // omit when the local language is English
    "name": "荷兰语", "regex": "dutch|nederlands\\w*", "drop_if_fluent_required": true,
    "title_hint_regex": "\\b(medewerker|ontwikkelaar|m/v/x)\\b",
    "extra_fluent_words": "vloeiend\\w*|uitstekend\\w*", "extra_required_words": "vereist|verplicht",
    "extra_soft_words": "pluspunt|wenselijk", "extra_context_words": "markt|klanten"
  }
}
```

Start `exclude_title_regex` from the example profiles (internships, management, sales/HR/legal/finance, unrelated engineering) and adapt to the user's directions: don't exclude "consultant" for someone who wants consulting. The language rule drops a posting only when its description explicitly requires fluent/native/C1 level; "X is a plus" is kept. Add the local-language words for "fluent / required / nice to have" via the `extra_*` fields (regex alternatives).

## 5. Sponsorship

- Q4 = no → `"sponsorship": {"required": false}` (no sponsor column; other-companies sheet shows all matching non-agency companies).
- Q4 = yes and the country publishes a register → register mode (see `sponsor-registers.md`), `others_sheet.only_sponsors: true`.
- Q4 = yes, no register → research mode: `required: true`, no `register`, `sponsor_status` per tier company, `info_url` to the official visa page, `others_sheet.only_sponsors: false`.
- Put visa facts the user needs (salary thresholds, permit names, source links) in `overview_notes` as `[label, text]` rows. Only facts you verified; add the source URL.

## 6. Channels

8–20 rows for the 投递渠道 sheet: the big boards for the country, expat/English-language boards, startup boards, recruiters for the field, government job portals, the sponsor register, salary sites, industry events. Fields: `name, type, url, directions, feature, tips, priority (A/B/C)`.

## 7. Full schema

```json
{
  "version": 1,
  "report_language": "zh",                    // zh | en
  "report_title": "荷兰求职日报",
  "timezone": "Asia/Taipei",                  // IANA name; dates the report, pick the user's own timezone
  "output_dir": "output",                     // relative to the workspace
  "search": {
    "locations": [{"name": "Netherlands", "geo_id": "102890719", "label": "荷兰境内"}],  // name = LinkedIn location text; geo_id optional
    "time_window_hours": 24,                  // 24 daily, 168 weekly
    "keywords": ["AI engineer", "data scientist"],
    "max_pages_per_keyword": 100,             // 10 cards per page
    "parallel": 5,
    "work_types": ["hybrid", "remote"],       // optional: onsite | hybrid | remote
    "experience_levels": ["entry", "associate", "mid-senior"]  // optional LinkedIn filter: internship | entry | associate | mid-senior | director | executive
  },
  "directions": [{"code": "A", "name": "AI 工程师", "title_regex": "...", "cv_file": "CV_AI.pdf", "pitch": "...", "target_titles": "..."}],
  "filters": { ... see 4 ... },
  "sponsorship": {"required": true, "label": "IND 担保资质", "register": { ... see sponsor-registers.md ... }, "agency_regex": "(optional override)", "register_exclude_regex": []},
  "others_sheet": {"enabled": true, "only_sponsors": true, "max_companies": null},
  "tiers": [{"name": "第一梯队", "title": "第一梯队：…", "rationale": "…", "sheet_name": "(optional)", "companies": [ ... see 3 ... ]}],
  "background": {"title": "个人背景与求职定位", "rows": [["学历", "…"]]},
  "channels": [{"name": "LinkedIn Jobs", "type": "综合招聘平台", "url": "https://www.linkedin.com/jobs", "directions": "全部", "feature": "…", "tips": "…", "priority": "A"}],
  "overview_notes": [["签证要点", "…"]]
}
```

Comments above are for reading only; `profile.json` must be plain JSON. Paths: relative = workspace, `skill:` prefix = inside the skill folder (bundled registers).

LinkedIn `geo_id` values seen in LinkedIn URLs (optional, the location text alone also works): Netherlands 102890719, Germany 101282230, United Kingdom 101165590, Ireland 104738515, France 105015875, United States 103644278, Canada 101174742, Singapore 102454443, Australia 101452733. Check by opening a LinkedIn job search for the place and reading `geoId=` from the URL.

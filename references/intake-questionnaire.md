# Intake questionnaire（信息收集表）

Ask in the user's language. Multiple choice first, a short free answer only where needed. Pre-fill anything the CV already answers and ask the user to confirm instead of asking again. The right column says where each answer goes in `profile.json` (schema: `build-profile.md`).

Send at most 4–6 questions per message. Suggested batches: **A** (1–5) → ask for the CV → **B** (6–11) after reading the CV, with suggestions pre-filled → **C** (12–17).

## Batch A — target and visa

| # | Question (中文 / English) | Options | → profile |
|---|---|---|---|
| 1 | 日报用什么语言？/ Report language? | A 中文  B English | `report_language` |
| 2 | 目标国家/地区（可多选）/ Target country or region (multi) | Free text, e.g. 荷兰 / Germany / UK / Singapore / "EU remote" | `search.locations` |
| 3 | 目标城市？/ Target cities? | A 全国都可以 / anywhere in the country  B 只要这些城市：___ / only these cities: ___ | `search.locations` (one entry per city, or the country) |
| 4 | 你是否需要雇主提供工作签证 / 担保？/ Do you need the employer to sponsor a work visa? | A 需要 / yes  B 不需要（已有工作许可、公民或永居）/ no (already allowed to work)  C 不确定 / not sure | `sponsorship.required` (C → research the user's case and explain, then decide with them) |
| 5 | （选 A 时）你目前的身份？/ (if A) Current status? | A 在目标国的毕业生求职签 / post-study or job-seeker permit there  B 在目标国的学生签 / student visa there  C 在其他国家 / living elsewhere  D 其他：___ | `background` row "签证目标", `overview_notes` (visa tips, e.g. reduced salary threshold for graduates) |
| — | 请上传你的 CV（可上传多份，对应不同方向）/ Please upload your CV (several for different directions is fine) | file | read fully; save to `<workspace>/cv/` |

## Batch B — directions and level (after reading the CV)

Present suggestions from the CV as pre-ticked options, e.g. "根据你的 CV，我建议 3 个方向：① AI 工程师 ② 数据分析 ③ 技术咨询，可增删".

| # | Question | Options | → profile |
|---|---|---|---|
| 6 | 想投的岗位方向（2–5 个）/ Job directions (2–5) | Suggested list from the CV + "其他：___" | `directions[]` (name, title_regex, keywords) |
| 7 | 每个方向用哪份 CV？/ Which CV for each direction? | Map uploaded files to directions; one CV for all is fine | `directions[].cv_file` |
| 8 | 你的经验水平？/ Experience level? | A 应届/0–1 年 / graduate  B 1–3 年 / junior  C 3–5 年 / medior  D 5–8 年 / senior  E 8 年以上 / expert | `filters.max_years_experience` (A→2, B→3 or user's years+2, C→5, D→8, E→null), `search.experience_levels` |
| 9 | 是否保留标题带 Senior/Lead 的岗位？/ Keep "Senior/Lead" titles? | A 保留，标注提示即可 / keep with a hint  B 排除 / exclude | B → add `senior|lead` to `filters.exclude_title_regex` |
| 10 | 要排除哪些类型？（多选）/ Exclude which kinds? (multi) | A 实习/毕业设计/PhD  B 管理岗（Manager/Director）  C 销售/市场  D 纯硬件/嵌入式  E 不排除  F 其他：___ | `filters.exclude_title_regex`, `filters.exclude_summary` |
| 11 | 当地语言水平？/ Your level in the local language? | A 不会 / none  B 基础 A1–A2  C 中级 B1–B2  D 流利 C1+ / 母语 | A–C → `filters.local_language.drop_if_fluent_required = true`; D → false (keep the hint only). Skip if the local language is English |

## Batch C — companies and routine

| # | Question | Options | → profile |
|---|---|---|---|
| 12 | 偏好的行业（多选，可空）/ Preferred industries (multi, optional) | Suggest 4–8 from the CV (e.g. 半导体、金融科技、医疗科技、咨询) + 其他 | weights tier composition |
| 13 | 不想去的行业或公司？/ Industries or companies to avoid? | Free text, may be empty | omit from tiers; `filters.exclude_companies_regex` |
| 14 | 公司类型偏好？（多选）/ Company types (multi) | A 大公司 / large  B 中型 / mid-size  C 初创 / startups  D 咨询/外包 / consulting & IT services  E 不限 / any | tier composition |
| 15 | 一定要包含的公司？/ Must-have companies? | Free text, may be empty | put into tier 1 or 2 |
| 16 | 工作方式？/ Work mode? | A 不限  B 现场  C 混合  D 远程 | `search.work_types` (A → omit) |
| 17 | 多久生成一次、几点？/ How often and when? | A 每天（过去 24 小时）+ 时间 ___  B 每周（过去 7 天）+ 星期几 ___ | `search.time_window_hours` (24 / 168), `timezone`, schedule |

Optional, only if the user wants: show "其他公司" sheet (default yes); report title (default "<国家>求职日报"); salary floor for visa (put into `overview_notes`).

## After the questionnaire

Summarise what you understood in ≤10 lines (target, visa, directions → CV, level, exclusions, industries) and ask "对吗？/ Correct?" before researching companies. Then follow `build-profile.md`.

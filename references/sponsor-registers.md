# Visa-sponsor registers

Some countries publish the list of employers allowed to sponsor work visas. When one exists, the report checks every company against it (register mode). Otherwise the profile carries the agent's research per company (research mode). Visa rules change: verify the current rules on the official page before writing them into `overview_notes`, and cite the source.

## Register mode config

```json
"sponsorship": {
  "required": true,
  "label": "IND 担保资质",                  // column header in the report
  "register": {
    "name": "IND 担保名录",                  // how the register is called in sentences
    "file": "data/uk_sponsors_2026-11.csv",  // xlsx or csv; relative = workspace, "skill:..." = bundled
    "name_column": "Organisation Name",      // header text of the company-name column (header row is found automatically)
    "id_column": "Town/City",                // optional second column shown next to the entity
    "id_label": "",                           // prefix for that value, e.g. "KVK"
    "version": "2026-11-01",                  // register date, shown in the report
    "url": "https://..."                      // official page, linked in 今日概览
  },
  "register_exclude_regex": []                // entity names that false-match a tier company's patterns
}
```

Matching: tier companies use `sponsor_patterns` (regex on entity names) when given, else the normalised company name (legal suffixes such as B.V., GmbH, Ltd, Inc removed; exact match, or the register name starts with the company name). The other-companies sheet uses the normalised-name lookup and skips recruiters/job boards (`sponsorship.agency_regex`, default list in `scripts/sponsor.py`).

## Known registers

| Country | Register | Format / notes |
|---|---|---|
| Netherlands | IND *Public register Work* (recognised sponsors, erkend referent): https://ind.nl/en/public-register-recognised-sponsors/public-register-work | **Bundled**: `skill:data/registers/NL_IND_public_register_work_2026-10-05.xlsx`, `name_column: "Organisation"`, `id_column: "KVK (Chamber of Commerce) number"`, `id_label: "KVK"`. Updated monthly by IND; the web page can be exported/copied to Excel with the same two columns. Highly skilled migrant salary thresholds: IND page "Required amounts income requirements". |
| United Kingdom | *Register of licensed sponsors: workers* on gov.uk (search the title): a CSV updated almost daily | Columns include `Organisation Name`, `Town/City`, `County`, `Type & Rating`, `Route` (check the header after downloading). Use `name_column: "Organisation Name"`, `id_column: "Town/City"`. Filter rows to route "Skilled Worker" first if the file is large. |
| United States | No list of "allowed" sponsors. USCIS *H-1B Employer Data Hub* (past petitions per employer) is the usual evidence | Research mode, or export the Data Hub for the target years as CSV and use it as a register (`name_column` = employer column). Note: a past H-1B filer is not a promise to sponsor. |
| Canada | No sponsor register. Employers that received positive LMIAs are published quarterly on open.canada.ca | Research mode, or use the LMIA employer CSV as an evidence register. |
| Germany, Ireland, France, most EU | No sponsor licence; the EU Blue Card / national permits depend on the job (salary, degree), not on a listed employer | `required: true` without register (research mode) if the user needs a permit; put the Blue Card salary threshold in `overview_notes`. Ireland: Critical Skills Employment Permit occupations list. |
| Sweden, Denmark, Norway | No public employer list (Denmark has a certified-companies "fast-track" list on nyidanmark.dk) | Research mode; Denmark's fast-track list can be used as a register. |
| Singapore | No register; Employment Pass uses COMPASS scoring | Research mode. |
| Australia | Approved sponsors are not published as a full list | Research mode. |

If unsure whether a list exists, search "<country> list of licensed/recognised visa sponsors official" and prefer government domains.

## Research mode

Per tier company set `sponsor_status`: `Y` only with evidence (company on an official list, an official statement, or many visa-sponsored hires documented), else `U`. Shown as "✅ 有担保记录（待核实）" / "❓ 待核实". The other-companies sheet then shows all matching non-agency companies with "❓ 待核实".

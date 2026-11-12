# Fetch new postings from LinkedIn's public guest job search, classify them with profile.json.
# Usage: python3 fetch_jobs.py out.json [--profile=path] [--max-pages=N] [--keywords=a,b]
#   --max-pages / --keywords are for quick tests.
import sys, os, re, json, time, html, datetime, urllib.request, urllib.parse
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config
from filters import CompanyMatcher, TitleRules, LanguageRule, min_years

UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36",
      "Accept-Language": "en-US,en;q=0.9"}
SEARCH = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?"
POSTING = "https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/"
CARD = re.compile(r"<li>(.*?)</li>", re.S)
WT = {"onsite": "1", "remote": "2", "hybrid": "3"}
EXP = {"internship": "1", "entry": "2", "associate": "3", "mid-senior": "4", "director": "5", "executive": "6"}


def field(rx, s):
    m = re.search(rx, s, re.S)
    return html.unescape(re.sub(r"<[^>]+>", "", m.group(1))).strip() if m else ""


def get(url, tries=4):
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=25) as r:
                return r.read().decode("utf-8", "ignore")
        except Exception as e:
            if "400" in str(e) or "404" in str(e):
                return ""
            if "403" in str(e) and i == tries - 1:
                print(f"403 from LinkedIn: network policy blocks linkedin.com or rate-limited ({url[:80]})", file=sys.stderr)
            time.sleep(3 * (i + 1))
    return ""


def search(kw, loc, s, max_pages):
    out = []
    params = {"keywords": kw, "location": loc["name"], "f_TPR": f"r{int(s.get('time_window_hours', 24)) * 3600}"}
    if loc.get("geo_id"):
        params["geoId"] = loc["geo_id"]
    if s.get("work_types"):
        params["f_WT"] = ",".join(WT[w] for w in s["work_types"] if w in WT)
    if s.get("experience_levels"):
        params["f_E"] = ",".join(EXP[e] for e in s["experience_levels"] if e in EXP)
    if s.get("distance_km") and loc.get("name"):
        params["distance"] = str(int(s["distance_km"] / 1.609))
    for start in range(0, max_pages * 10, 10):
        page = get(SEARCH + urllib.parse.urlencode({**params, "start": start}))
        cards = CARD.findall(page)
        if not cards:
            break
        for c in cards:
            link = field(r'class="base-card__full-link[^"]*"[^>]*href="([^"?]+)', c) or field(r'href="(https://[a-z]+\.linkedin\.com/jobs/view/[^"?]+)', c)
            out.append({
                "title": field(r'class="base-search-card__title"[^>]*>(.*?)</h3>', c),
                "company": field(r'class="base-search-card__subtitle"[^>]*>(.*?)</h4>', c),
                "location": field(r'class="job-search-card__location"[^>]*>(.*?)</span>', c),
                "date": field(r'datetime="([^"]+)"', c),
                "ago": field(r"<time[^>]*>(.*?)</time>", c),
                "url": re.sub(r"https://[a-z]+\.linkedin\.com", "https://www.linkedin.com", link),
            })
        time.sleep(1.2)
    return out


def description(job_id):
    page = get(POSTING + job_id)
    m = re.search(r"show-more-less-html__markup[^>]*>(.*?)</div>", page, re.S)
    return html.unescape(re.sub(r"<[^>]+>", "\n", m.group(1))) if m else ""


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    opts = dict(a[2:].split("=", 1) for a in sys.argv[1:] if a.startswith("--") and "=" in a)
    profile = config.load_profile(opts.get("profile"))
    out = args[0] if args else "jobs.json"
    s = profile.get("search") or {}
    keywords = opts["keywords"].split(",") if "keywords" in opts else s["keywords"]
    max_pages = int(opts.get("max-pages", s.get("max_pages_per_keyword", 100)))
    locs = s.get("locations") or [{"name": s.get("location", "")}]
    f = profile.get("filters") or {}
    max_years = f.get("max_years_experience")
    lang_rule = LanguageRule(profile)
    titles = TitleRules(profile)
    matcher = CompanyMatcher(profile, None)
    others_on = (profile.get("others_sheet") or {}).get("enabled", True)

    tasks = [(kw, loc) for loc in locs for kw in keywords]
    with ThreadPoolExecutor(int(s.get("parallel", 5))) as ex:
        results = list(ex.map(lambda t: search(t[0], t[1], s, max_pages), tasks))

    seen, jobs, others, raw = set(), [], [], 0
    for (kw, loc), res in zip(tasks, results):
        raw += len(res)
        print(f"{loc['name']} | {kw}: {len(res)}", file=sys.stderr)
        for j in res:
            m = re.search(r"(\d{8,})", j["url"])
            key = m.group(1) if m else j["title"] + j["company"]
            if key in seen or not j["company"]:
                continue
            seen.add(key)
            dirs = titles.directions(j["title"])
            if not dirs:
                continue
            j.update(dirs=dirs, **titles.flags(j["title"]))
            hit = matcher.match(j["company"])
            if hit:
                j.update(tier=hit[0], company_key=hit[1]["name"])
                jobs.append(j)
            elif others_on:
                others.append(j)

    need_desc = max_years is not None or lang_rule.on
    if need_desc:
        def one(j):
            m = re.search(r"(\d{8,})", j["url"])
            text = description(m.group(1)) if m else ""
            j["min_years"] = min_years(text) if text else None
            j["fluent_local"] = lang_rule.requires_fluent(text) if text else False
        with ThreadPoolExecutor(5) as ex:
            list(ex.map(one, jobs + others))

    def keep(j):
        return not ((max_years is not None and (j.get("min_years") or 0) > max_years) or j.get("fluent_local"))
    n_years = sum(1 for j in jobs + others if max_years is not None and (j.get("min_years") or 0) > max_years)
    n_lang = sum(1 for j in jobs + others if j.get("fluent_local"))
    jobs, others = [j for j in jobs if keep(j)], [j for j in others if keep(j)]
    if need_desc:
        print(f"dropped {n_years} postings asking for more than {max_years} years, {n_lang} requiring fluent local language", file=sys.stderr)
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    json.dump({"fetched_at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
               "raw_cards": raw, "unique_cards": len(seen), "jobs": jobs, "others": others},
              open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"raw {raw}, unique {len(seen)}, matched {len(jobs)}, others {len(others)} -> {out}", file=sys.stderr)
    if raw == 0:
        print("WARNING: 0 cards fetched. LinkedIn is unreachable or rate-limiting; check `curl -sI https://www.linkedin.com/jobs`.", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()

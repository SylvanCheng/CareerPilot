# Check a profile.json before the first run. Prints problems and a short summary; exit 1 on errors.
# Usage: python3 validate_profile.py [profile.json]
import sys, os, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else config.PROFILE_PATH
    p = config.load_profile(path)
    err, warn = [], []

    def rx(label, pat):
        try:
            re.compile(pat)
        except re.error as e:
            err.append(f"{label}: bad regex ({e})")

    s = p.get("search") or {}
    if not s.get("locations"): err.append("search.locations is empty")
    if not s.get("keywords"): err.append("search.keywords is empty")
    elif len(s["keywords"]) * len(s.get("locations", [1])) > 60: warn.append("more than 60 keyword×location searches: a run may take over 30 min")
    dirs = p.get("directions") or []
    if not dirs: err.append("directions is empty")
    codes = [d.get("code", "") for d in dirs]
    if len(set(codes)) != len(codes) or any(len(c) != 1 for c in codes): err.append("direction codes must be unique single characters")
    for d in dirs:
        rx(f"direction {d.get('name')}", d.get("title_regex", ""))
        if not d.get("title_regex"): err.append(f"direction {d.get('name')}: title_regex missing")
        cv = d.get("cv_file")
        if cv and not os.path.exists(config.resolve(os.path.join("cv", cv))) and not os.path.exists(config.resolve(cv)):
            warn.append(f"CV file not found in workspace: {cv} (only shown as text in the report, fine if kept elsewhere)")
    f = p.get("filters") or {}
    rx("filters.exclude_title_regex", f.get("exclude_title_regex", ""))
    for x in f.get("exclude_companies_regex", []): rx("filters.exclude_companies_regex", x)
    ll = f.get("local_language") or {}
    for k in ("regex", "title_hint_regex", "extra_fluent_words", "extra_required_words", "extra_soft_words", "extra_context_words"):
        if ll.get(k): rx(f"local_language.{k}", ll[k])
    tiers = p.get("tiers") or []
    if not tiers: err.append("tiers is empty")
    names = set()
    for t in tiers:
        if not t.get("companies"): warn.append(f"tier {t.get('name')} has no companies")
        for c in t.get("companies", []):
            if c["name"] in names: err.append(f"company listed twice: {c['name']}")
            names.add(c["name"])
            for x in c.get("aliases", []) + c.get("sponsor_patterns", []): rx(f"company {c['name']}", x)
            if c.get("priority", "B") not in "ABC": err.append(f"company {c['name']}: priority must be A/B/C")
            bad = set(c.get("directions", "")) - set(codes)
            if bad: warn.append(f"company {c['name']}: unknown direction codes {''.join(bad)}")
    sp = p.get("sponsorship") or {}
    reg = (sp.get("register") or {}).get("file")
    if sp.get("required") and reg:
        if not os.path.exists(config.resolve(reg)): err.append(f"sponsor register not found: {config.resolve(reg)}")
        else:
            from sponsor import Register
            try:
                n = len(Register(sp["register"]).rows)
                print(f"sponsor register: {n:,} organisations")
            except SystemExit as e:
                err.append(str(e))
    if len(config.tier_sheet_names(p)) != len(set(config.tier_sheet_names(p))): err.append("tier sheet names collide (shortened to 31 chars)")
    print(f"profile: {path}")
    print(f"locations: {[l['name'] for l in s.get('locations', [])]} | keywords: {len(s.get('keywords', []))} | directions: {codes}")
    print("tiers: " + ", ".join(f"{t['name']} ({len(t.get('companies', []))})" for t in tiers) + f" | companies: {len(names)}")
    print(f"sponsorship: {'required' if sp.get('required') else 'not needed'}{' + register' if reg else ''} | max years: {f.get('max_years_experience')} | local language filter: {ll.get('name') or '-'}")
    for w in warn: print("WARN  " + w)
    for e in err: print("ERROR " + e)
    sys.exit(1 if err else 0)


if __name__ == "__main__":
    main()

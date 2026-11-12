# Offline smoke test: builds reports for the example profiles from a synthetic fetch JSON and checks the sheets.
# Usage: python3 tests/smoke_test.py
import json, os, subprocess, sys, tempfile
import openpyxl

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S = os.path.join(ROOT, "scripts")
sys.path.insert(0, S)
from filters import CompanyMatcher, TitleRules, LanguageRule, min_years

CARDS = [
    ("AI Engineer", "ASML", "Veldhoven"), ("Senior Data Engineer", "Booking.com", "Amsterdam"),
    ("Python Developer", "Adyen", "Amsterdam"), ("Data Engineer", "Adyen", "Amsterdam"), ("Data Engineer", "Adyen", "Utrecht"),
    ("Marketing Manager", "ASML", "Veldhoven"), ("Data Scientist", "Metyis", "Amsterdam"), ("Data Scientist", "Randstad", "Amsterdam"),
    ("Data Analyst", "Zalando", "Berlin"), ("Analytics Engineer", "Some Unknown Startup GmbH", "Berlin"),
]
DESC_OK = "We need 3+ years of experience with Python. Dutch is a plus."
DESC_SENIOR = "You have at least 8 years of experience in data engineering."
DESC_DUTCH = "Je spreekt vloeiend Nederlands. Fluent Dutch is required."


def fake_fetch(profile):
    titles, matcher = TitleRules(profile), CompanyMatcher(profile, None)
    jobs, others = [], []
    for i, (t, c, loc) in enumerate(CARDS):
        d = titles.directions(t)
        if not d:
            continue
        j = {"title": t, "company": c, "location": loc, "date": "2026-11-12", "ago": "3 hours ago",
             "url": f"https://www.linkedin.com/jobs/view/{40000000 + i}", "dirs": d, **titles.flags(t)}
        hit = matcher.match(c)
        if hit:
            j.update(tier=hit[0], company_key=hit[1]["name"]); jobs.append(j)
        else:
            others.append(j)
    return {"fetched_at": "2026-11-12T04:00:00Z", "raw_cards": len(CARDS), "unique_cards": len(CARDS), "jobs": jobs, "others": others}


def main():
    nl = json.load(open(os.path.join(ROOT, "examples/profile.netherlands-tech.json"), encoding="utf-8"))
    assert min_years(DESC_OK) == 3 and min_years(DESC_SENIOR) == 8
    lr = LanguageRule(nl)
    assert not lr.requires_fluent(DESC_OK) and lr.requires_fluent(DESC_DUTCH)
    assert not lr.requires_fluent("Experience with the Dutch market is required.")
    tmp = tempfile.mkdtemp()
    for name in ["profile.netherlands-tech.json", "profile.germany-data.en.json"]:
        prof = os.path.join(ROOT, "examples", name)
        p = json.load(open(prof, encoding="utf-8"))
        data = fake_fetch(p)
        jp, xp = os.path.join(tmp, name + ".jobs.json"), os.path.join(tmp, name + ".xlsx")
        json.dump(data, open(jp, "w"))
        subprocess.run([sys.executable, os.path.join(S, "build_report.py"), jp, xp, f"--profile={prof}"], check=True, capture_output=True)
        wb = openpyxl.load_workbook(xp)
        n_t = len(p["tiers"])
        assert len(wb.sheetnames) == n_t + 4, wb.sheetnames
        print(f"OK {name}: {wb.sheetnames}; tier jobs {len(data['jobs'])}, others {len(data['others'])}")
    # NL: Adyen Data Engineer in two cities -> one row; Randstad (agency) excluded from others
    wb = openpyxl.load_workbook(os.path.join(tmp, "profile.netherlands-tech.json.xlsx"))
    t3 = [r for r in wb["第三梯队公司"].iter_rows(min_row=3, values_only=True) if r[3]]
    adyen = [r for r in t3 if r[3] == "Data Engineer"]
    assert len(adyen) == 1 and "；" in adyen[0][6], adyen
    oth = [r[1] for r in wb["适合我投递的其他公司"].iter_rows(min_row=3, values_only=True) if r[1]]
    assert "Randstad" not in oth, oth
    assert not any(r[3] == "Marketing Manager" for r in t3)
    print("all checks passed")


if __name__ == "__main__":
    main()

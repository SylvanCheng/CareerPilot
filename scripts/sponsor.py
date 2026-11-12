# Visa-sponsor checks.
#   mode "none"     : user needs no sponsorship -> no sponsor column at all
#   mode "register" : an official register file (xlsx/csv) is matched by company name / regex
#   mode "research" : no public register; status comes from profile companies' sponsor_status (AI research), others = "verify"
import csv, os, re
import config

LEGAL = (r"\b(b\.?\s?v\.?|n\.?\s?v\.?|bv|nv|holding|holdings|group|groep|gruppe|nederland|netherlands|the netherlands|deutschland|germany|uk|"
         r"united kingdom|europe|emea|international|benelux|inc\.?|ltd\.?|limited|llc|llp|gmbh|mbh|ag|se|kg|s\.a\.|sa|sas|sarl|srl|spa|ab|as|oy|aps|plc|"
         r"pty|pte|co\.?|corporation|corp\.?|company|vof|c\.v\.|stichting|kk|k\.k\.)\b")
DEFAULT_AGENCY = (r"(jobgether|randstad|adecco|manpower|hays|michael page|page personnel|robert walters|robert half|brunel|olympia|tempo-team|start people|"
                  r"undutchables|jooble|talent\.com|indeed|recruit|staffing|detachering|uitzend|headhunt|executive search|search partners|careers|vacatures|"
                  r"personalvermittlung|personaldienst|zeitarbeit|interim|jobs\b|crossover|toptal|hunter|talent|computer futures|harvey nash|nigel frank|"
                  r"jefferson frank|huxley|teksystems|experis|dice|hirexpert|wearetechwomen|bluetown|xpand|orange quarter|darwin)")
AMBIG = {"builders", "frank", "bank", "mars", "global", "digital", "tech", "solutions", "consulting", "services", "group"}


def norm(s):
    s = str(s).lower().replace("&", " and ").replace('""', "")
    s = re.sub(r"\(.*?\)", " ", s)
    s = re.sub(LEGAL, " ", s)
    s = re.sub(r"[^a-z0-9à-ÿ ]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def mode(profile):
    sp = profile.get("sponsorship") or {}
    if not sp.get("required"):
        return "none"
    return "register" if (sp.get("register") or {}).get("file") else "research"


def label(profile, lab):
    return (profile.get("sponsorship") or {}).get("label") or lab["sp_label"]


class Register:
    """Loads an official sponsor list. Config keys (profile.sponsorship.register):
    file, name_column (header text, default first column), id_column (optional), id_label, version, url, sheet (xlsx), city_column (optional)."""

    def __init__(self, cfg):
        self.cfg = cfg
        path = config.resolve(cfg["file"])
        rows = self._read(path)
        name_col = cfg.get("name_column")
        id_col = cfg.get("id_column")
        hdr_i = 0
        if name_col:  # find the header row (some registers have a preamble)
            hdr_i = next((i for i, r in enumerate(rows[:50]) if any(str(c or "").strip() == name_col for c in r)), None)
            if hdr_i is None:
                raise SystemExit(f"sponsor register: column '{name_col}' not found in {path}")
        hdr = [str(c or "").strip() for c in rows[hdr_i]]
        ni = hdr.index(name_col) if name_col else 0
        ii = hdr.index(id_col) if id_col and id_col in hdr else None
        self.rows = []
        seen = set()
        for r in rows[hdr_i + 1:]:
            if len(r) <= ni or not r[ni]:
                continue
            n = str(r[ni]).replace('""', '"').strip()
            k = r[ii] if ii is not None and len(r) > ii else None
            if (n, k) in seen:
                continue
            seen.add((n, k))
            self.rows.append((n, k))
        self.idx = {}
        for n, k in self.rows:
            self.idx.setdefault(norm(n), []).append((n, k))
        self.id_label = cfg.get("id_label", "ID")

    @staticmethod
    def _read(path):
        if path.lower().endswith((".xlsx", ".xlsm")):
            import openpyxl
            wb = openpyxl.load_workbook(path, read_only=True)
            ws = wb[wb.sheetnames[0]]
            return [list(r) for r in ws.iter_rows(values_only=True)]
        with open(path, encoding="utf-8-sig", errors="ignore", newline="") as f:
            return list(csv.reader(f))

    def fmt(self, hits):
        def one(n, k):
            return f"{n} ({self.id_label} {k})" if k not in (None, "") else n
        return "; ".join(one(n, k) for n, k in hits[:3]) + (f" (+{len(hits) - 3})" if len(hits) > 3 else "")

    def by_patterns(self, pats, excl=()):
        return [(n, k) for n, k in self.rows if any(re.search(p, n, re.I) for p in pats) and not any(re.search(x, n, re.I) for x in excl)]

    def by_name(self, company):
        q = norm(company)
        if len(q) < 3 or q in AMBIG:
            return []
        hits = list(self.idx.get(q, []))
        if not hits and len(q) >= 5:  # "Mendix" -> "Mendix Technology"
            hits = [h for key, hs in self.idx.items() if key.startswith(q + " ") for h in hs]
        return hits


class Checker:
    def __init__(self, profile, lab):
        self.p, self.lab = profile, lab
        self.mode = mode(profile)
        sp = profile.get("sponsorship") or {}
        self.agency = sp.get("agency_regex") or DEFAULT_AGENCY
        self.excl = sp.get("register_exclude_regex", [])
        self.reg = Register(sp["register"]) if self.mode == "register" else None

    def is_agency(self, company):
        return bool(re.search(self.agency, company, re.I))

    def tier_company(self, c):
        """-> (status_text, ok_bool, entity_text) for a tier company dict."""
        lab = self.lab
        if self.mode == "register":
            hits = self.reg.by_patterns(c["sponsor_patterns"], self.excl) if c.get("sponsor_patterns") else self.reg.by_name(c["name"])
            ent = self.reg.fmt(hits)
            if c.get("sponsor_note"):
                ent = (ent + "。" if ent else "") + c["sponsor_note"]
            return (lab["sp_yes"], True, ent) if hits else (lab["sp_no"], False, c.get("sponsor_note", ""))
        st = (c.get("sponsor_status") or "U").upper()
        return (lab["sp_known"], True, c.get("sponsor_note", "")) if st == "Y" else (lab["sp_unknown"], False, c.get("sponsor_note", ""))

    def other_company(self, company):
        """-> ('agency'|'yes'|'no'|'unknown', entity_text)"""
        if self.is_agency(company):
            return "agency", ""
        if self.mode == "register":
            hits = self.reg.by_name(company)
            return ("yes", self.reg.fmt(hits)) if hits else ("no", "")
        return "unknown", ""

    def version(self):
        sp = self.p.get("sponsorship") or {}
        return (sp.get("register") or {}).get("version", "")

    def url(self):
        sp = self.p.get("sponsorship") or {}
        return (sp.get("register") or {}).get("url") or sp.get("info_url", "")

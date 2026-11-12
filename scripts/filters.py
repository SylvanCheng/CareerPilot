# Title / description filters, all driven by profile.json.
import re

DEFAULT_SENIOR = r"\b(senior|sr\.?|lead|expert)\b"

# ---------- company matching ----------
from sponsor import norm


class CompanyMatcher:
    def __init__(self, profile, tier_sheets):
        self.excl = (profile.get("filters") or {}).get("exclude_companies_regex", [])
        self.items = []  # (tier_index, company dict, regexes, normalized name)
        for ti, t in enumerate(profile["tiers"]):
            for c in t["companies"]:
                self.items.append((ti, c, c.get("aliases", []), norm(c["name"])))

    def match(self, name):
        n = name.strip()
        if any(re.search(x, n, re.I) for x in self.excl):
            return None
        q = norm(n)
        for ti, c, pats, cn in self.items:
            if pats:
                if any(re.search(p, n, re.I) for p in pats):
                    return ti, c
            elif cn and len(cn) >= 2 and (q == cn or q.startswith(cn + " ")):
                return ti, c
        return None


# ---------- titles ----------
class TitleRules:
    def __init__(self, profile):
        f = profile.get("filters") or {}
        self.excl = f.get("exclude_title_regex") or ""
        self.senior = f.get("senior_title_regex") or DEFAULT_SENIOR
        lang = f.get("local_language") or {}
        self.local_hint = lang.get("title_hint_regex") or ""
        self.dirs = [(d["code"], d["title_regex"]) for d in profile["directions"]]

    def directions(self, title):
        if self.excl and re.search(self.excl, title, re.I):
            return ""
        return "".join(code for code, rx in self.dirs if re.search(rx, title, re.I))

    def flags(self, title):
        return {"senior": bool(re.search(self.senior, title, re.I)),
                "local_title": bool(self.local_hint and re.search(self.local_hint, title, re.I))}


# ---------- description: minimum years of experience ----------
_EXP = r"(?:experience|ervaring|werkervaring|erfahrung|berufserfahrung|expérience|experiencia|esperienza|erfarenhet|erfaring|kokemus|doświadczeni\w*|work(?:ing)? in|background)"
_YRS = r"(?:years?|yrs|jaar|jaren|jahre?n?|ans?|años|anni|år|vuotta|lat)"
_NUM = r"(\d{1,2})\s*(?:\+|plus)?\s*(?:(?:-|–|to|tot|bis|à|a)\s*\d{1,2}\s*)?\+?\s*" + _YRS


def min_years(text):
    """Strictest explicit minimum years of experience in a job description, or None."""
    found = []
    for m in re.finditer(_NUM, text, re.I):
        ctx = text[max(0, m.start() - 80): m.end() + 80]
        if re.search(_EXP, ctx, re.I):
            n = int(m.group(1))
            if 1 <= n <= 20:
                found.append(n)
    return max(found) if found else None


# ---------- description: fluent local language required ----------
# Context nouns after the language name that mean "the Dutch market", "German clients" etc., not a language requirement.
_CTX = (r"market|markets|company|companies|organi[sz]ation\w*|government|law|laws|clients?|customers?|landscape|context|regulat\w*|tax\w*|pension\w*|"
        r"bank\w*|health\w*|energy|econom\w*|cultur\w*|society|business|labou?r|financ\w*|public|sector|universit\w*|startup\w*|scale-?up\w*|team|teams|"
        r"office|headquarters|operations|grid|cities|railway\w*|infrastructure|speaking (?:market|region|countries)")
_FLUENT_EN = r"fluent\w*|fluency|native|proficien\w+|excellent|strong|perfect\w*|business[- ]level|full professional"
_REQ_EN = r"fluent\w*|fluency|native|c1|c2|required|mandatory|a must|must|essential"
_SOFT_EN = (r"plus|pre|pré|nice|advantage|bonus|preferred|preferably|desirable|benefit|asset|not required|not necessary|not a requirement|"
            r"no \w+ required|not need|don't need|do not need|optional")


class LanguageRule:
    """profile.filters.local_language = {name, regex, drop_if_fluent_required, extra_fluent_words, extra_required_words, extra_soft_words, extra_context_words}"""

    def __init__(self, profile):
        cfg = (profile.get("filters") or {}).get("local_language") or {}
        self.on = bool(cfg.get("regex")) and cfg.get("drop_if_fluent_required", True)
        if not self.on:
            return
        j = lambda base, extra: base + ("|" + extra if extra else "")
        ctx = j(_CTX, cfg.get("extra_context_words", ""))
        lang = r"\b(?:" + cfg["regex"] + r")\b(?!\W+(?:" + ctx + r")\b)"
        fluent = r"(?:" + j(_FLUENT_EN, cfg.get("extra_fluent_words", "")) + r")"
        req = r"(?:" + j(_REQ_EN, cfg.get("extra_required_words", "")) + r")\b"
        speak = r"\b(?:speak|" + (cfg.get("extra_speak_words") or "spreek\\w*|beheers\\w*|sprich\\w*|beherrsch\\w*") + r")"
        self.req = [re.compile(fluent + r"\W+(?:\w+\W+){0,4}?" + lang, re.I),
                    re.compile(lang + r"\W+(?:\w+\W+){0,4}?" + req, re.I),
                    re.compile(speak + r"\W+(?:\w+\W+){0,2}?" + lang + r"\W+(?:\w+\W+){0,1}?(?:fluently|vloeiend|fließend)", re.I)]
        self.soft = re.compile(r"\b(?:" + j(_SOFT_EN, cfg.get("extra_soft_words", "")) + r")\b", re.I)

    def requires_fluent(self, text):
        if not self.on:
            return False
        for sent in re.split(r"[\n.;!?•]+", text):
            if any(p.search(sent) for p in self.req) and not self.soft.search(sent):
                return True
        return False

# Build the daily workbook from a fetch JSON and profile.json.
# Sheets (same layout as the original Netherlands report):
#   今日概览 · <tier 1..N>公司 · 适合我投递的其他公司 · 个人背景 · 投递渠道
# Usage: python3 build_report.py jobs.json out.xlsx [--profile=path]
import sys, os, json, datetime
from zoneinfo import ZoneInfo
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config, labels
from sponsor import Checker
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

FONT = "Arial"
HDR_FILL = PatternFill("solid", fgColor="1F3864")
HDR_FONT = Font(name=FONT, bold=True, color="FFFFFF", size=10)
BODY = Font(name=FONT, size=10); BOLD = Font(name=FONT, size=10, bold=True)
TITLE = Font(name=FONT, size=14, bold=True, color="1F3864")
LINK = Font(name=FONT, size=10, color="0563C1", underline="single")
NOTE = Font(name=FONT, size=9, italic=True, color="808080")
INPUT_FILL = PatternFill("solid", fgColor="FFF2CC")
GREEN = PatternFill("solid", fgColor="E2EFDA"); RED = PatternFill("solid", fgColor="FCE4D6"); GREY = PatternFill("solid", fgColor="F2F2F2")
thin = Side(style="thin", color="BFBFBF")
BORDER = Border(left=thin, right=thin, top=thin, bottom=thin)
WRAP = Alignment(wrap_text=True, vertical="center")
CENTER = Alignment(horizontal="center", vertical="center", wrap_text=True)
TOP = Alignment(wrap_text=True, vertical="top")
TOPC = Alignment(horizontal="center", vertical="top", wrap_text=True)
PRI = {"A": 0, "B": 1, "C": 2}


def header(ws, row, cols, widths):
    for i, (c, w) in enumerate(zip(cols, widths), 1):
        cell = ws.cell(row=row, column=i, value=c); cell.font = HDR_FONT; cell.fill = HDR_FILL; cell.alignment = CENTER; cell.border = BORDER
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.row_dimensions[row].height = 30


def dedupe(items, keyf):
    """Same title at the same company in several cities -> one row, locations joined with ；"""
    uniq = {}
    for j in items:
        k = keyf(j)
        if k in uniq:
            if j["location"] not in uniq[k]["location"]:
                uniq[k]["location"] += "；" + j["location"]
        else:
            uniq[k] = dict(j)
    return list(uniq.values())


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    opts = dict(a[2:].split("=", 1) for a in sys.argv[1:] if a.startswith("--") and "=" in a)
    p = config.load_profile(opts.get("profile"))
    jobs_path, out = args[0], args[1]
    J = json.load(open(jobs_path, encoding="utf-8"))
    lab = labels.get(p)
    win = labels.window(p, lab)
    chk = Checker(p, lab)
    has_sp = chk.mode != "none"
    sp_label = (p.get("sponsorship") or {}).get("label") or lab["sp_label"]
    dirs = p["directions"]
    DIRNAME = {d["code"]: d["name"] for d in dirs}
    CV = {d["code"]: d.get("cv_file", "") for d in dirs}
    DPRI = {d["code"]: i for i, d in enumerate(dirs)}
    f = p.get("filters") or {}
    lang_name = (f.get("local_language") or {}).get("name", "")
    loc_text = " / ".join(l.get("label") or l["name"] for l in (p.get("search") or {}).get("locations", []))
    tier_sheets = config.tier_sheet_names(p)
    status_list = f'"{lab["status_list"]}"'
    today = datetime.datetime.fromisoformat(J["fetched_at"].replace("Z", "+00:00")).astimezone(ZoneInfo(config.tz(p))).date()

    def fit_note(j):
        n = []
        if j.get("senior"): n.append(lab["senior"])
        if j.get("local_title") and lang_name: n.append(lab["local"].format(lang=lang_name))
        return "；".join(n) if lab is labels.L["zh"] else "; ".join(n)

    def dir_text(j):
        return " / ".join(DIRNAME.get(c, c) for c in j["dirs"])

    wb = openpyxl.Workbook(); wb.remove(wb.active)
    stats = []

    # ---------- tier sheets ----------
    cols = [c.replace("{sp}", sp_label) for c in lab["tier_cols"]]
    widths = [6, 26, 16, 44, 14, 26, 20, 12, 14, 26, 36, 26, 20, 11, 12]
    keep = [i for i in range(len(cols)) if has_sp or i != 2]
    cols = [cols[i] for i in keep]; widths = [widths[i] for i in keep]
    keys = ["no", "company", "sp", "title", "dir", "cv", "loc", "posted", "apply", "careers", "match", "hint", "note", "status", "date"]
    ci = {k: n for n, k in enumerate([k for k in keys if has_sp or k != "sp"], 1)}
    n_comp = sum(len(t["companies"]) for t in p["tiers"])
    uniq = dedupe(J["jobs"], lambda j: (j["company_key"], j["title"].strip().lower()))
    for ti, (t, sname) in enumerate(zip(p["tiers"], tier_sheets)):
        ws = wb.create_sheet(sname)
        ws["A1"] = lab["tier_head"].format(title=t.get("title") or t["name"], date=f"{today:%Y-%m-%d}", window=win); ws["A1"].font = TITLE
        header(ws, 2, cols, widths)
        info = {c["name"]: c for c in t["companies"]}
        comps = {}
        for j in uniq:
            if j["tier"] == ti and j["company_key"] in info:
                comps.setdefault(j["company_key"], []).append(j)
        order = sorted(comps, key=lambda c: (PRI.get(info[c].get("priority", "B"), 3), -len(comps[c])))
        r, n_jobs, n_sp = 3, 0, 0
        for idx, cname in enumerate(order, 1):
            c = info[cname]
            st, ok, ent = chk.tier_company(c) if has_sp else ("", False, "")
            n_sp += ok
            js = sorted(comps[cname], key=lambda j: (j.get("senior", False), j["title"]))
            r0 = r
            for j in js:
                vals = {"title": j["title"], "dir": dir_text(j), "cv": CV.get(j["dirs"][0], ""), "loc": j["location"],
                        "posted": j.get("ago") or j.get("date"), "apply": lab["apply"], "hint": fit_note(j), "status": lab["status_default"]}
                for k, col in ci.items():
                    cell = ws.cell(row=r, column=col, value=vals.get(k)); cell.font = BODY; cell.border = BORDER
                    cell.alignment = CENTER if k in ("dir", "posted", "apply", "status", "date") else WRAP
                lk = ws.cell(row=r, column=ci["apply"]); lk.hyperlink = j["url"]; lk.font = LINK
                ws.cell(row=r, column=ci["title"]).font = BOLD
                for k in ("note", "status", "date"): ws.cell(row=r, column=ci[k]).fill = INPUT_FILL
                ws.cell(row=r, column=ci["date"]).number_format = "yyyy-mm-dd"
                r += 1
            cvals = [("no", idx), ("company", cname), ("careers", c.get("careers_url", "")), ("match", c.get("match", ""))]
            if has_sp: cvals.insert(2, ("sp", st + ("\n" + ent if ent else "")))
            for k, v in cvals:
                cell = ws.cell(row=r0, column=ci[k], value=v); cell.border = BORDER
                cell.font = BOLD if k == "company" else (LINK if k == "careers" and v else BODY)
                cell.alignment = CENTER if k == "no" else WRAP
                if k == "careers" and v and str(v).startswith("http"): cell.hyperlink = v
                if k == "sp": cell.fill = GREEN if ok else (RED if chk.mode == "register" else GREY)
                if r - r0 > 1: ws.merge_cells(start_row=r0, start_column=ci[k], end_row=r - 1, end_column=ci[k])
            n_jobs += len(js)
        last_col = get_column_letter(len(cols))
        if not order:
            ws.cell(row=3, column=1, value=lab["none_tier"]).font = BODY
            ws.merge_cells(start_row=3, start_column=1, end_row=3, end_column=len(cols)); r = 4
        else:
            dv = DataValidation(type="list", formula1=status_list, allow_blank=True)
            ws.add_data_validation(dv); sc = get_column_letter(ci["status"]); dv.add(f"{sc}3:{sc}{r-1}")
            ws.auto_filter.ref = f"A2:{last_col}{r-1}"
        ws.freeze_panes = get_column_letter(ci["title"]) + "3"
        spn = lab["tier_note_sp"].format(label=sp_label, ver=chk.version() or today) if chk.mode == "register" else ""
        ws.cell(row=r + 1, column=2, value=lab["tier_note"].format(sp=spn)).font = NOTE
        stats.append((sname, len(order), n_jobs, n_sp if has_sp else None))

    # ---------- other companies ----------
    oc = p.get("others_sheet") or {}
    if oc.get("enabled", True):
        OTHER = lab["others"]
        ou = dedupe(J.get("others", []), lambda j: (j["company"].strip().lower(), j["title"].strip().lower()))
        only_sp = chk.mode == "register" and oc.get("only_sponsors", True)
        ocomp, n_agency, n_drop = {}, 0, 0
        for j in ou:
            st, ent = chk.other_company(j["company"]) if has_sp else ("agency" if chk.is_agency(j["company"]) else "unknown", "")
            if st == "agency": n_agency += 1; continue
            if st == "no" and only_sp: n_drop += 1; continue
            ocomp.setdefault(j["company"].strip(), {"st": st, "ent": ent, "jobs": []})["jobs"].append(j)
        maxc = oc.get("max_companies")
        ws = wb.create_sheet(OTHER)
        nt = len(p["tiers"])
        tiers_txt = labels.count(p, nt) + "个梯队" if lab is labels.L["zh"] else f"{nt} tiers"
        reg_name = ((p.get("sponsorship") or {}).get("register") or {}).get("name") or ("担保名录" if lab is labels.L["zh"] else "sponsor register")
        scope = lab["other_scope_reg"].format(reg=(" " + reg_name if lab is labels.L["zh"] and reg_name[:1].isascii() else reg_name)) if only_sp else lab["other_scope_any"]
        ws["A1"] = lab["other_head"].format(tiers=tiers_txt, scope=scope, date=f"{today:%Y-%m-%d}", window=win); ws["A1"].font = TITLE
        ocols = [c.replace("{sp}", sp_label) for c in lab["other_cols"]]
        owidths = [6, 26, 30, 44, 14, 26, 20, 12, 14, 26, 20, 11, 12]
        okeys = ["no", "company", "sp", "title", "dir", "cv", "loc", "posted", "apply", "hint", "note", "status", "date"]
        if not has_sp:
            ocols.pop(2); owidths.pop(2); okeys.remove("sp")
        oci = {k: i for i, k in enumerate(okeys, 1)}
        header(ws, 2, ocols, owidths)
        order = sorted(ocomp, key=lambda c: (min(DPRI[j["dirs"][0]] for j in ocomp[c]["jobs"]), -len(ocomp[c]["jobs"]), c.lower()))
        if maxc: order = order[:int(maxc)]
        r, on_jobs, on_sp = 3, 0, 0
        for idx, cname in enumerate(order, 1):
            d = ocomp[cname]
            js = sorted(d["jobs"], key=lambda j: (DPRI[j["dirs"][0]], j.get("senior", False), j["title"]))
            r0 = r
            for j in js:
                vals = {"title": j["title"], "dir": dir_text(j), "cv": CV.get(j["dirs"][0], ""), "loc": j["location"],
                        "posted": j.get("ago") or j.get("date"), "apply": lab["apply"], "hint": fit_note(j), "status": lab["status_default"]}
                for k, col in oci.items():
                    cell = ws.cell(row=r, column=col, value=vals.get(k)); cell.font = BODY; cell.border = BORDER
                    cell.alignment = CENTER if k in ("dir", "posted", "apply", "status", "date") else WRAP
                lk = ws.cell(row=r, column=oci["apply"]); lk.hyperlink = j["url"]; lk.font = LINK
                ws.cell(row=r, column=oci["title"]).font = BOLD
                for k in ("note", "status", "date"): ws.cell(row=r, column=oci[k]).fill = INPUT_FILL
                ws.cell(row=r, column=oci["date"]).number_format = "yyyy-mm-dd"
                r += 1
            cv = [("no", idx), ("company", cname)]
            if has_sp:
                ok = d["st"] == "yes"; on_sp += ok
                txt = {"yes": lab["sp_yes"], "no": lab["sp_no"]}.get(d["st"], lab["sp_unknown"])
                cv.append(("sp", txt + ("\n" + d["ent"] if d["ent"] else "")))
            for k, v in cv:
                cell = ws.cell(row=r0, column=oci[k], value=v); cell.border = BORDER
                cell.font = BOLD if k == "company" else BODY; cell.alignment = CENTER if k == "no" else WRAP
                if k == "sp": cell.fill = GREEN if d["st"] == "yes" else (RED if d["st"] == "no" else GREY)
                if r - r0 > 1: ws.merge_cells(start_row=r0, start_column=oci[k], end_row=r - 1, end_column=oci[k])
            on_jobs += len(js)
        last_col = get_column_letter(len(ocols))
        if order:
            dv = DataValidation(type="list", formula1=status_list, allow_blank=True)
            sc = get_column_letter(oci["status"]); ws.add_data_validation(dv); dv.add(f"{sc}3:{sc}{r-1}"); ws.auto_filter.ref = f"A2:{last_col}{r-1}"
        else:
            ws.cell(row=3, column=1, value=lab["none_other"]).font = BODY; r = 4
        ws.freeze_panes = get_column_letter(oci["title"]) + "3"
        dorder = " → ".join(d["name"] for d in dirs)
        if only_sp:
            note = lab["other_note"].format(rule=lab["other_note_reg"], n_drop=n_drop, n_agency=n_agency, order=dorder)
        else:
            note = lab["other_note_any"].format(n_agency=n_agency)
        ws.cell(row=r + 1, column=2, value=note).font = NOTE
        stats.append((OTHER, len(order), on_jobs, on_sp if has_sp else None))

    # ---------- 个人背景 ----------
    bg = p.get("background") or {}
    ws = wb.create_sheet(lab["background"])
    ws.column_dimensions["A"].width = 22; ws.column_dimensions["B"].width = 100
    ws.column_dimensions["C"].width = 50; ws.column_dimensions["D"].width = 60
    ws["A1"] = bg.get("title") or lab["bg_title"]; ws["A1"].font = TITLE
    r = 3
    for k, v in bg.get("rows", []):
        a = ws.cell(row=r, column=1, value=k); a.font = BOLD; a.alignment = TOP; a.border = BORDER
        b = ws.cell(row=r, column=2, value=v); b.font = BODY; b.alignment = TOP; b.border = BORDER
        r += 1
    r += 1
    ws.cell(row=r, column=1, value=bg.get("directions_title") or lab["bg_dirs"]).font = TITLE; r += 1
    for i, c in enumerate(lab["bg_dir_cols"], 1):
        cell = ws.cell(row=r, column=i, value=c); cell.font = HDR_FONT; cell.fill = HDR_FILL; cell.alignment = CENTER; cell.border = BORDER
    r += 1
    for d in dirs:
        for i, v in enumerate([d["name"], d.get("cv_file", ""), d.get("pitch", ""), d.get("target_titles", "")], 1):
            c = ws.cell(row=r, column=i, value=v); c.font = BODY; c.alignment = TOP; c.border = BORDER
        r += 1
    ws.cell(row=r, column=1, value=lab["bg_note"]).font = NOTE

    # ---------- 投递渠道 ----------
    ws = wb.create_sheet(lab["channels"])
    ws["A1"] = lab["ch_title"]; ws["A1"].font = TITLE
    header(ws, 2, lab["ch_cols"], [6, 26, 16, 44, 14, 46, 50, 8])
    chs = p.get("channels") or []
    for i, ch in enumerate(chs, 1):
        r = i + 2
        vals = [i, ch.get("name"), ch.get("type"), ch.get("url"), ch.get("directions"), ch.get("feature"), ch.get("tips"), ch.get("priority")]
        for c, v in enumerate(vals, 1):
            cell = ws.cell(row=r, column=c, value=v); cell.border = BORDER
            cell.font = BOLD if c == 2 else BODY
            cell.alignment = TOPC if c in (1, 5, 8) else TOP
            if c == 4 and v and str(v).startswith("http"): cell.hyperlink = v; cell.font = LINK
    ws.freeze_panes = "C3"
    if chs: ws.auto_filter.ref = f"A2:H{len(chs) + 2}"

    # ---------- 今日概览 ----------
    ws = wb.create_sheet(lab["overview"], 0)
    for col, w in zip("ABCDE", [22, 16, 16, 18, 60]): ws.column_dimensions[col].width = w
    ws["A1"] = lab["ov_title"].format(title=p.get("report_title") or lab["report_title"], date=f"{today:%Y-%m-%d}"); ws["A1"].font = TITLE
    ws["A2"] = lab["ov_sub"].format(at=J["fetched_at"][:16].replace("T", " "), loc=loc_text, window=win, n_tiers=labels.count(p, len(p["tiers"])), n_dirs=len(dirs)); ws["A2"].font = BODY
    r = 4
    hdr = lab["ov_cols"][:3]
    if has_sp: hdr.append(lab["ov_cols"][3])
    for i, h in enumerate(hdr, 1):
        c = ws.cell(row=r, column=i, value=h); c.font = HDR_FONT; c.fill = HDR_FILL; c.alignment = CENTER; c.border = BORDER
    for t, nc, nj, ni in stats:
        r += 1
        for i, v in enumerate([t, nc, nj, ni][:len(hdr)], 1):
            c = ws.cell(row=r, column=i, value=v); c.font = BODY; c.border = BORDER; c.alignment = WRAP if i == 1 else CENTER
            if i == 1: c.hyperlink = f"#'{t}'!A1"; c.font = LINK
    r += 1
    c = ws.cell(row=r, column=1, value=lab["total"]); c.font = BOLD; c.border = BORDER
    for i in range(2, len(hdr) + 1):
        col = get_column_letter(i)
        c = ws.cell(row=r, column=i, value=f"=SUM({col}5:{col}{r-1})"); c.font = BOLD; c.border = BORDER; c.alignment = CENTER
    r += 2
    excl = [f.get("exclude_summary") or lab["excl_title"]]
    if f.get("max_years_experience") is not None: excl.append(lab["excl_years"].format(n=f["max_years_experience"]))
    if (f.get("local_language") or {}).get("regex") and (f.get("local_language") or {}).get("drop_if_fluent_required", True):
        excl.append(lab["excl_lang"].format(lang=lang_name))
    sep = "；" if lab is labels.L["zh"] else "; "
    rules = sep.join([lab["rule_company"].format(n_tiers=labels.count(p, len(p["tiers"])), n_comp=n_comp), lab["rule_time"].format(window=win),
                      lab["rule_dir"].format(dirs=" / ".join(d["name"] for d in dirs)), lab["rule_excl"].format(items=("、" if sep == "；" else ", ").join(excl))])
    notes = [(lab["n_rules"], rules),
             (lab["n_dirs"], sep.join(f"{d['name']} → {d.get('cv_file', '')}" for d in dirs)),
             (lab["n_hint"], lab["hint_text"].format(lang=lang_name) if lang_name else lab["hint_text_nolang"]),
             (lab["n_src"], lab["src_text"].format(loc=loc_text, window=win, uniq=J.get("unique_cards", 0), matched=len(J["jobs"])))]
    notes += [tuple(x) for x in p.get("overview_notes", [])]
    if has_sp and chk.url(): notes.append((lab["n_reg"], chk.url()))
    for k, v in notes:
        a = ws.cell(row=r, column=1, value=k); a.font = BOLD; a.alignment = Alignment(vertical="top", wrap_text=True)
        ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=5)
        b = ws.cell(row=r, column=2, value=v); b.alignment = Alignment(vertical="top", wrap_text=True)
        islink = str(v).startswith("http")
        b.font = LINK if islink else BODY
        if islink: b.hyperlink = v
        ws.row_dimensions[r].height = 15 * max(1, len(str(v)) // 55 + 1)
        r += 1

    wb.active = 0
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    wb.save(out)
    print(out, stats)


if __name__ == "__main__":
    main()

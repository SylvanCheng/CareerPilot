# UI strings of the report, per report_language ("zh" default, "en").
L = {
 "zh": {
  "overview": "今日概览", "others": "适合我投递的其他公司", "background": "个人背景", "channels": "投递渠道",
  "report_title": "求职日报",
  "tier_cols": ["序号", "公司", "{sp}", "岗位名称", "方向", "推荐 CV", "工作地点", "发布时间", "投递入口", "公司招聘页", "公司匹配点", "提示", "备注（你来填）", "投递状态", "投递日期"],
  "other_cols": ["序号", "公司", "{sp}", "岗位名称", "方向", "推荐 CV", "工作地点", "发布时间", "投递入口", "提示", "备注（你来填）", "投递状态", "投递日期"],
  "status_list": "未投递,已投递,面试中,Offer,被拒,暂缓", "status_default": "未投递",
  "apply": "立即投递 ↗",
  "tier_head": "{title}　｜　{date} 过去 {window}新增岗位",
  "other_head": "补充：{tiers}以外{scope}的公司　｜　{date} 过去 {window}新增岗位",
  "other_scope_reg": "、在{reg}中", "other_scope_any": "、符合投递方向",
  "none_tier": "今日该梯队没有符合你投递方向的新增岗位。", "none_other": "今日没有符合条件的其他公司岗位。",
  "sp_yes": "✅ 在名录中", "sp_no": "❌ 不在名录", "sp_known": "✅ 有担保记录（待核实）", "sp_unknown": "❓ 待核实",
  "senior": "资深岗，经验要求可能偏高，可试投", "local": "标题为{lang}，可能要求{lang}",
  "tier_note": "“立即投递”链接到岗位发布页；公司招聘页为备用入口。{sp}",
  "tier_note_sp": "{label}按 {ver} 版名录核对，投递时确认雇佣实体。",
  "other_note": "{rule}另有 {n_drop} 个岗位所在公司未在名录中找到、{n_agency} 个来自中介/招聘平台，已略去。公司按方向优先级（{order}）排序。",
  "other_note_reg": "只收录能在担保名录中找到对应实体的公司（按公司名自动匹配，投递前请核对雇佣实体）。",
  "other_note_any": "收录梯队以外、岗位方向匹配的公司（已略去 {n_agency} 个中介/招聘平台岗位）。",
  "ov_title": "{title}　{date}",
  "ov_sub": "数据抓取时间：{at} UTC　|　范围：{loc}、过去 {window}发布、{n_tiers}个梯队目标公司、符合 {n_dirs} 个投递方向",
  "ov_cols": ["标签页", "有新岗位的公司", "新增岗位数", "其中有担保资质的公司"],
  "total": "合计",
  "n_rules": "筛选规则", "n_dirs": "方向与 CV", "n_hint": "提示列", "n_src": "数据来源", "n_reg": "担保名录",
  "rule_company": "① 公司：{n_tiers}个梯队名单内公司（共 {n_comp} 家）", "rule_time": "② 时间：平台标注为过去 {window}内发布（含重新发布）",
  "rule_dir": "③ 方向：标题命中 {dirs} 关键词", "rule_excl": "④ 排除：{items}。没有新增岗位的公司当天不显示。",
  "excl_title": "标题黑名单（实习/管理岗等，见 profile.filters）", "excl_years": "职位描述明确要求超过 {n} 年经验（{n} 年及以内保留）",
  "excl_lang": "职位描述明确要求流利{lang}", "excl_sp": "其他公司页仅保留在担保名录中的公司",
  "hint_text": "“资深岗”= 标题含 Senior/Lead 等，可择优试投；“可能要求{lang}”= 标题为{lang}，投递前看 JD 语言要求。",
  "hint_text_nolang": "“资深岗”= 标题含 Senior/Lead 等，经验要求可能偏高，可择优试投。",
  "src_text": "LinkedIn 公开职位搜索（{loc}，过去 {window}）。本次共扫描 {uniq} 个不重复岗位，命中目标公司且符合方向的 {matched} 个。仅在公司官网发布的岗位可能遗漏，重点公司建议每周看一次官网。",
  "hours": "{n} 小时", "days": "{n} 天",
  "bg_title": "个人背景与求职定位", "bg_dirs": "投递方向与对应 CV", "bg_dir_cols": ["方向", "对应 CV 文件", "定位一句话", "目标岗位关键词"],
  "bg_note": "注：CV 原件只保存在你自己的工作目录，不随 skill 发布。",
  "ch_title": "投递渠道汇总", "ch_cols": ["序号", "渠道", "类型", "网址", "适用方向", "签证友好度 / 特点", "使用建议", "优先级"],
  "sp_label": "担保资质",
 },
 "en": {
  "overview": "Overview", "others": "Other companies", "background": "Profile", "channels": "Channels",
  "report_title": "Job daily report",
  "tier_cols": ["#", "Company", "{sp}", "Job title", "Direction", "Suggested CV", "Location", "Posted", "Apply", "Careers page", "Why this company", "Hints", "Notes (yours)", "Status", "Applied on"],
  "other_cols": ["#", "Company", "{sp}", "Job title", "Direction", "Suggested CV", "Location", "Posted", "Apply", "Hints", "Notes (yours)", "Status", "Applied on"],
  "status_list": "Not applied,Applied,Interviewing,Offer,Rejected,On hold", "status_default": "Not applied",
  "apply": "Apply ↗",
  "tier_head": "{title}  |  {date}, new postings in the last {window}",
  "other_head": "Extra: companies outside the {tiers}{scope}  |  {date}, new postings in the last {window}",
  "other_scope_reg": ", listed in the {reg}", "other_scope_any": " matching your directions",
  "none_tier": "No new matching postings at this tier today.", "none_other": "No other matching companies today.",
  "sp_yes": "✅ In register", "sp_no": "❌ Not in register", "sp_known": "✅ Known sponsor (verify)", "sp_unknown": "❓ Verify",
  "senior": "Senior title, may ask for more experience", "local": "Title in {lang}, may require {lang}",
  "tier_note": "'Apply' opens the posting; the careers page is a fallback. {sp}",
  "tier_note_sp": "{label} checked against the {ver} register; confirm the hiring entity when applying.",
  "other_note": "{rule}{n_drop} postings at companies not found in the register and {n_agency} from agencies/job boards were left out. Sorted by direction priority ({order}).",
  "other_note_reg": "Only companies found in the sponsor register (matched by name, check the hiring entity). ",
  "other_note_any": "Companies outside the tiers with postings in your directions ({n_agency} agency/job-board postings left out).",
  "ov_title": "{title}  {date}",
  "ov_sub": "Fetched {at} UTC  |  Scope: {loc}, posted in the last {window}, {n_tiers} company tiers, {n_dirs} directions",
  "ov_cols": ["Sheet", "Companies with new jobs", "New jobs", "With sponsorship"],
  "total": "Total",
  "n_rules": "Rules", "n_dirs": "Directions & CVs", "n_hint": "Hints column", "n_src": "Source", "n_reg": "Sponsor register",
  "rule_company": "1) Companies: the {n_tiers} tier lists ({n_comp} companies)", "rule_time": "2) Time: posted in the last {window} (incl. reposts)",
  "rule_dir": "3) Directions: title matches {dirs}", "rule_excl": "4) Excluded: {items}. Companies without new postings are hidden.",
  "excl_title": "title blocklist (internships, management etc., see profile.filters)", "excl_years": "descriptions explicitly asking for more than {n} years",
  "excl_lang": "descriptions explicitly requiring fluent {lang}", "excl_sp": "the Other sheet only keeps sponsor-register companies",
  "hint_text": "'Senior' = title has Senior/Lead etc.; 'may require {lang}' = title written in {lang}, check the JD.",
  "hint_text_nolang": "'Senior' = title has Senior/Lead etc., may ask for more experience.",
  "src_text": "LinkedIn public job search ({loc}, last {window}). Scanned {uniq} unique postings; {matched} at target companies in your directions. Jobs only on company sites can be missed; check key companies' sites weekly.",
  "hours": "{n} hours", "days": "{n} days",
  "bg_title": "Background and positioning", "bg_dirs": "Directions and CVs", "bg_dir_cols": ["Direction", "CV file", "Pitch", "Target titles"],
  "bg_note": "CV files stay in your own workspace and are never part of the skill.",
  "ch_title": "Application channels", "ch_cols": ["#", "Channel", "Type", "URL", "Directions", "Visa-friendliness / notes", "How to use", "Priority"],
  "sp_label": "Sponsorship",
 },
}


def get(profile):
    return L.get(profile.get("report_language", "zh"), L["zh"])


def window(profile, lab):
    h = int(profile.get("search", {}).get("time_window_hours", 24))
    return lab["days"].format(n=h // 24) if h % 24 == 0 and h > 24 else lab["hours"].format(n=h)


def count(profile, n):
    if profile.get("report_language", "zh") == "zh" and 1 <= n <= 10:
        return "一两三四五六七八九十"[n - 1]
    return str(n)

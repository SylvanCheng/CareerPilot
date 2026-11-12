# job-daily-report · 求职日报 skill

一个给任何人用的 AI agent skill：回答一张以选择题为主的问答表、上传 CV，AI 就会分析出适合你的岗位方向、按梯度划分的目标公司和签证担保规则，之后每天自动生成一份 Excel 求职日报（过去 24 小时 LinkedIn 新岗位，只保留你的目标公司和方向）。

An AI agent skill for anyone: answer a short (mostly multiple-choice) questionnaire and upload your CV; the agent works out your job directions, tiers of target companies and visa-sponsor rules, then builds a daily Excel report of new LinkedIn postings (last 24 h) at those companies.

## 日报长什么样 / What the report contains

| 标签页 | 内容 |
|---|---|
| 今日概览 | 各标签页新增岗位数、筛选规则、方向与 CV 对应、数据来源、担保名录链接 |
| 第一梯队公司 … 第 N 梯队公司 | 梯队数量由 AI 结合你的行业背景决定；每个岗位带投递链接、推荐 CV、公司匹配点、提示，以及可填写的投递状态 |
| 适合我投递的其他公司 | 梯队以外、方向匹配的公司（需要签证时只保留担保名录内的公司） |
| 个人背景 | 根据 CV 整理的背景与求职定位、方向与 CV 对照 |
| 投递渠道 | 目标国家的招聘平台和渠道 |

English reports use the same layout (`report_language: "en"`).

## 安装 / Install

```bash
git clone <this repo> ~/.claude/skills/job-daily-report
pip install openpyxl          # Python 3.9+
```

其他 agent：把仓库放到该 agent 读取 skills 的目录，或把 `SKILL.md` 作为说明交给 agent。Other agents: put the folder where your agent loads skills, or give it `SKILL.md` as instructions.

## 使用 / Use

1. 对 agent 说「帮我设置求职日报」/ "Set up my job daily report"。
2. 回答问答表（目标国家、是否需要工作签证担保、经验水平、语言、偏好行业……），上传 CV。
3. 确认 AI 给出的方向、梯度和公司名单，它会先跑一次测试，再生成第一份日报。
4. 设置每天定时运行；之后对日报的反馈（「这类岗位不要」「加上某公司」）会直接改进筛选规则。

你的个人数据（profile.json、CV、日报）只保存在你自己的工作目录（默认 `~/job-daily-report`，可用 `JOB_REPORT_HOME` 修改），不会进入这个仓库。

Your data (profile, CVs, reports) stays in your own workspace (`~/job-daily-report` or `$JOB_REPORT_HOME`), never in this repo.

## 要求 / Requirements

- Python 3.9+ 与 `openpyxl`
- 能访问 `www.linkedin.com`（公开职位页，无需登录）。部分云端沙箱默认屏蔽 LinkedIn，需要放开网络或在本机运行。

## 文件 / Files

- `SKILL.md` — agent 的操作说明（入口）
- `references/` — 问答表、建档方法与 profile 格式、各国担保名录、维护指南
- `scripts/` — 抓取、筛选、生成 Excel、校验 profile
- `examples/` — 完整示例：荷兰科技岗（4 个梯队、169 家公司、IND 名录）；德国数据岗（英文、无名录）
- `data/registers/` — 内置的荷兰 IND 认可担保人名录（2026-10-05）
- `tests/smoke_test.py` — 离线自测

本项目源自一个已经稳定运行的荷兰求职日报。

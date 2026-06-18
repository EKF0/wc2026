# World Cup 2026 — Master Workflow & Agent Coordination

> **MANDATORY:** Every agent must read this file before working on World Cup 2026 tasks.
> **Purpose:** Prevent duplicate work, conflicting schedules, and missed handoffs.

**Last Updated:** 2026-06-18  
**Applies To:** All EKF agents + Ehab manual tasks  
**Enforced By:** Hermes (orchestrator) + Roadmap system

---

## 1. Agent Role Assignments (Who Does What)

### Direct Automation (Hermes handles)

| Task | Agent | Model/Tool | Why This Agent |
|---|---|---|---|
| **Match result fetching** | Hermes | Python + web scraping | Direct file I/O, JSON updates |
| **Prediction generation (DeepSeek)** | Hermes | OpenRouter DeepSeek V4 Pro | In-session, fastest |
| **Prediction generation (Qwen)** | Hermes | OpenCode Go `qwen3.7-plus` | Terminal automation |
| **Prediction generation (Kimi)** | Hermes | OpenCode Go `kimi-k2.6` | Terminal automation |
| **Prediction generation (Minimax)** | Hermes | OpenCode Go `minimax-m3` | Terminal automation |
| **Prediction generation (GLM)** | Hermes | OpenCode Go `glm-5.2` | Terminal automation |
| **Prediction generation (Nemotron)** | Hermes | OpenClaw gateway loopback:18789 | API call, 1M context |
| **Tweet content generation** | Hermes | DeepSeek V4 Pro | In-session, formats JSON |
| **Tweet queuing (OpenTweet)** | Hermes | OpenTweet MCP | Direct MCP integration |
| **Site build (build.py)** | Hermes | Python stdlib | File generation, deploy |
| **Site deploy (Netlify)** | Hermes | Netlify CLI | Terminal automation |
| **Roadmap updates** | Hermes | road_sync.py | Existing system |

### Ehab Manual Tasks (Ehab runs, reports back)

| Task | Agent/Tool | How Ehab Runs It | Why Manual |
|---|---|---|---|
| **Prediction (MiMo v2.5)** | OpenCode Go | `opencode run --model opencode-go/mimo-v2.5` | Ehab's personal model preference |
| **Prediction (Gemini/Antigravity)** | Antigravity 2.0 desktop | Copy Hermes prompt → paste into app | Antigravity has no API/SDK bridge |
| **Prediction (Claude)** | claude.ai web | Copy Hermes prompt → paste into browser | No API key for Claude |
| **Prediction (Codex)** | Codex CLI | `codex exec` in terminal | Ehab's preference for manual control |
| **Redbubble upload** | Browser | Manual drag-and-drop + copy/paste listings | Platform requires human auth + CAPTCHA |
| **Netlify auth** | Browser | `netlify login` or personal access token | Auth requires browser OAuth |
| **Antigravity website builds** | Antigravity desktop | Full-stack UI / browser QA tasks | Visual verification needed |

### Other Agent Tasks (delegate_task when needed)

| Task | Best Agent | Why | How to Dispatch |
|---|---|---|---|
| **Architecture review** | Archon | Nemotron Ultra 550B, free, best at systems design | `delegate_task` with architecture context |
| **Code quality review** | Sentinel | GPT-OSS-120B, free, security-focused | `delegate_task` with code diff |
| **Financial tracking** | Cairo | Nemotron 3 Super, free, CFO role | `delegate_task` with finance data |
| **Legal/IP audit** | Lex | GPT-OSS-120B, free, legal specialist | `delegate_task` with designs/content |
| **Research/content** | Scribe | GLM-5.2, cheap, multilingual writer | `delegate_task` with research brief |
| **Creative/unconventional** | Joker | Nex N2 Pro, free, wildcard | `delegate_task` for experimental ideas |
| **Planning/strategy** | Strategos | Kimi K2.6, cheap, best planner | `delegate_task` with goal description |
| **Volume code** | Swift | Grok 4.1 Fast, free, fast generation | `delegate_task` for bulk scripts |
| **Production code** | Forge | DeepSeek V4 Pro, paid, highest quality | Reserve for critical features |
| **General overflow** | Nexus | Qwen 3.7 Plus, cheap, generalist | `delegate_task` for misc tasks |

---

## 2. Master Cron Job Schedule

### Already Scheduled (DO NOT RESCHEDULE)

| Job ID | Name | Schedule | Next Run | Agent |
|---|---|---|---|---|
| `b9994104` | Daily Plan — 5AM Cairo | `0 5 * * *` | Daily 05:00 EET | Cairo |
| `c4e718f6` | Daily Report — 11PM Cairo | `0 23 * * *` | Daily 23:00 EET | Cairo |
| `774d0fab` | Weekly Report — Sunday 11PM | `0 23 * * 0` | Sun 23:00 EET | Cairo |
| `1597a4e6` | Monthly Report — 1st 11PM | `0 23 1 * *` | 1st 23:00 EET | Cairo |
| `a4915ace` | WC Tweet 4: Canada | once at 2026-06-18 21:40Z | Jun 18 21:40 UTC | Hermes |
| `9885f995` | WC Tweet 5: Mexico | once at 2026-06-19 00:40Z | Jun 19 00:40 UTC | Hermes |
| `81a7796d` | WC Tweet 6: Night Thread | once at 2026-06-19 03:00Z | Jun 19 03:00 UTC | Hermes |

### To Be Scheduled (Hermes will create)

| Job Name | Schedule | Agent | Description |
|---|---|---|---|
| `wc-fetch-results` | Every 2 hours | Hermes | Scrape FIFA.com, update matches.json |
| `wc-gen-predictions` | Every 6 hours | Hermes | Generate predictions for next 48h matches |
| `wc-gen-tweets` | After predictions | Hermes | Generate 3 tweets per upcoming match |
| `wc-queue-tweets` | After gen-tweets | Hermes | Queue tweets via OpenTweet MCP |
| `wc-daily-summary` | Daily 23:00 UTC | Hermes | Post daily prediction accuracy summary |
| `wc-weekly-merch` | Sun 18:00 UTC | Hermes | Post weekly merch/service funnel tweet |
| `wc-rebuild-site` | After data update | Hermes | Run build.py + deploy to Netlify |

### Coordination Rule

> **CRITICAL:** Before creating ANY new cron job, check this schedule. If a similar job exists, do NOT create a duplicate. Update the existing job instead.

---

## 3. Website Workflow

### Data Flow

```
FIFA.com / Yahoo Sports
        ↓
matches.json (scores, status)
        ↓
predictions.json (AI model outputs)
        ↓
groups.json (standings, team data)
        ↓
build.py → generates 100+ HTML pages
        ↓
Netlify deploy → wc2026.ehabkhedr.com
```

### Step-by-Step

| Step | Who | Action | Output |
|---|---|---|---|
| 1 | Hermes | Fetch results from FIFA.com every 2h | Updated matches.json |
| 2 | Hermes | Generate predictions for next 48h matches | Updated predictions.json |
| 3 | Hermes | Run `python3 build.py` | All HTML files generated |
| 4 | Hermes | Run `netlify deploy --dir=. --prod` | Live site updated |
| 5 | Hermes | Write report + update Roadmap | Report in reports/tasks/ |

### Prediction Generation Sub-Flow

| Step | Who | Action | Tool |
|---|---|---|---|
| 1 | Hermes | Identify upcoming matches (next 48h) | Python script |
| 2 | Hermes | Generate DeepSeek prediction | Direct in-session |
| 3 | Hermes | Call OpenCode Go Qwen 3.7 Plus | `opencode run --model opencode-go/qwen3.7-plus` |
| 4 | Hermes | Call OpenCode Go Kimi K2.6 | `opencode run --model opencode-go/kimi-k2.6` |
| 5 | Hermes | Call OpenCode Go Minimax M3 | `opencode run --model opencode-go/minimax-m3 --effort max` |
| 6 | Hermes | Call OpenCode Go GLM 5.2 | `opencode run --model opencode-go/glm-5.2` |
| 7 | Hermes | Call OpenClaw Nemotron Ultra | `curl http://127.0.0.1:18789/` or gateway API |
| 8 | Ehab (manual) | Run MiMo v2.5 via OpenCode | `opencode run --model opencode-go/mimo-v2.5` |
| 9 | Ehab (manual) | Run Gemini via Antigravity desktop | Copy prompt → paste into app |
| 10 | Ehab (manual) | Run Claude via claude.ai | Copy prompt → paste into browser |
| 11 | Ehab (manual) | Run Codex CLI | `codex exec` in terminal |
| 12 | Hermes | Collect all predictions, write to predictions.json | File write |

---

## 4. Twitter Workflow

### Tweet Types Per Match

| Type | When | Content | Link |
|---|---|---|---|
| **Pre-match preview** | 2h before kickoff | All 6 AI predictions + consensus | `wc2026.ehabkhedr.com/matches/{id}` |
| **Match hype** | 20min before kickoff | Win probabilities + most confident | `wc2026.ehabkhedr.com/matches/{id}` |
| **Post-match analysis** | 30min after final whistle | Prediction accuracy per model | `wc2026.ehabkhedr.com/predictions` |

### Daily/Weekly Tweets

| Type | When | Content | Link |
|---|---|---|---|
| **Daily summary** | 23:00 UTC | Day's accuracy stats + best model | `wc2026.ehabkhedr.com/predictions` |
| **Weekly merch funnel** | Sun 18:00 UTC | Redbubble + AI Custom Bot | Direct links |

### Step-by-Step

| Step | Who | Action | Tool |
|---|---|---|---|
| 1 | Hermes | Read predictions.json for upcoming matches | File read |
| 2 | Hermes | Generate tweet content (human voice) | DeepSeek V4 Pro in-session |
| 3 | Hermes | Schedule tweets via OpenTweet MCP | `opentweet_create_tweet` or `opentweet_batch_schedule` |
| 4 | Hermes | Write report + update Roadmap | File write + road_sync.py |

### Tweet Content Rules

- Write like The Athletic meets a smart group chat
- No emoji bullets. No "AI predicts..." hooks.
- Match hype: hook + specific detail + quick opinion
- Links embed naturally: "Full analysis: [url]"
- Arabic: original thoughts, not translations

---

## 5. Cross-Agent Coordination Rules

### Before Starting ANY World Cup Task

1. **Read this WORKFLOW.md** — know what's scheduled and who does what
2. **Read Roadmap.csv + Roadmap.xlsx** — know current status
3. **Check existing cron jobs** — `cronjob(action='list')`
4. **Do NOT create duplicate cron jobs**

### Communication Rules

| Situation | Action |
|---|---|
| Hermes is generating predictions | Other agents: do NOT regenerate same predictions |
| Hermes queued tweets for today | Other agents: do NOT queue additional tweets for same matches |
| Ehab is running Antigravity | Hermes: wait for Ehab's response before proceeding |
| Ehab is running MiMo/Claude/Codex | Hermes: prepare next batch while waiting |
| Cairo posts daily plan at 5AM | All agents: read it, align priorities |
| Cairo posts daily report at 11PM | All agents: review, adjust next day |

### Report Requirements

Every agent task MUST:
1. Write a report to `reports/tasks/YYYY-MM-DD-agent-task-name.md`
2. Update related Roadmap rows
3. Run `python3 scripts/road_sync.py`

---

## 6. Manual Task Handoffs for Ehab

When Ehab needs to run manual predictions, Hermes will provide:

### Standard Handoff Format

```
TASK: Prediction for [Match] — [Model Name]
MATCH ID: wc2026-grp-x-n
MATCH: [Home Team] vs [Away Team] | [Date] [Time] ET

PROMPT (copy-paste this):
---
Predict the exact score for [Home Team] vs [Away Team] on [Date].

Context:
- Group: [Group]
- Stadium: [Stadium], [City]
- [Home Team] recent form: [form summary]
- [Away Team] recent form: [form summary]
- Key players: [list]
- Head-to-head: [history]

Output JSON exactly:
{
  "predicted_score": "X-Y",
  "confidence": "high|medium|low",
  "reasoning": "2-3 sentences",
  "key_factors": ["factor1", "factor2"],
  "win_probability": {"home": 0.0, "draw": 0.0, "away": 0.0}
}
---

WHERE TO RUN: [tool + command]
TIME ESTIMATE: ~2 minutes
WHAT TO REPORT BACK: Paste the JSON output
```

### Ehab's Manual Prediction Schedule

| Model | When | How |
|---|---|---|
| **MiMo v2.5** | After Hermes generates 6 automated predictions | `opencode run --model opencode-go/mimo-v2.5 "[prompt]"` |
| **Gemini/Antigravity** | After Hermes generates 6 automated predictions | Copy prompt → Antigravity 2.0 desktop app |
| **Claude Sonnet 4.6** | After Hermes generates 6 automated predictions | Copy prompt → claude.ai |
| **Codex CLI** | Optional, when Ehab wants | `codex exec` in terminal |

---

## 7. Best Agent for Specific Tasks

| Task | Best Agent | Alternative | Why |
|---|---|---|---|
| **Full-stack website build** | Antigravity (Ehab manual) | Forge via delegate_task | Visual QA + browser automation |
| **Site generator script (build.py)** | Forge | Hermes direct | Production-quality Python |
| **Data scraping script** | Swift | Hermes direct | Fast volume code |
| **Code review of build.py** | Sentinel | Archon | Security + quality focus |
| **Architecture of prediction pipeline** | Archon | Strategos | System design expertise |
| **Tweet content (human voice)** | Scribe | Hermes direct | Writing specialist |
| **Financial tracking (P&L)** | Cairo | Hermes direct | CFO role |
| **Legal audit of designs** | Lex | Hermes direct | IP/trademark expertise |
| **Research on World Cup data** | Scribe | Nexus | Research + multilingual |
| **Unconventional prediction methods** | Joker | Hermes direct | Creative approaches |
| **Bulk JSON data generation** | Swift | Hermes direct | Volume tasks |
| **Match result API design** | Archon | Forge | API architecture |

---

## 8. Quick Reference Commands

```bash
# Check all cron jobs
cronjob(action='list')

# Build website
cd "/Users/ekf/Downloads/Ehab Roadmap/projects/world-cup-2026/site" && python3 build.py

# Deploy website
cd "/Users/ekf/Downloads/Ehab Roadmap/projects/world-cup-2026/worldcup-site" && npx netlify deploy --dir=. --prod

# Sync roadmap
cd "/Users/ekf/Downloads/Ehab Roadmap" && python3 scripts/road_sync.py

# OpenCode Go predictions
opencode run --model opencode-go/qwen3.7-plus "[prompt]"
opencode run --model opencode-go/kimi-k2.6 "[prompt]"
opencode run --model opencode-go/minimax-m3 --effort max "[prompt]"
opencode run --model opencode-go/glm-5.2 "[prompt]"

# OpenClaw health check
openclaw health

# Netlify status
cd "/Users/ekf/Downloads/Ehab Roadmap/projects/world-cup-2026/worldcup-site" && npx netlify status
```

---

## 9. File Locations

| File | Path |
|---|---|
| Master Plan | `projects/world-cup-2026/site/PLAN.md` |
| This Workflow | `projects/world-cup-2026/site/WORKFLOW.md` |
| Match Data | `projects/world-cup-2026/site-data/matches.json` |
| Group Data | `projects/world-cup-2026/site-data/groups.json` |
| Predictions | `projects/world-cup-2026/site-data/predictions.json` |
| Site Builder | `projects/world-cup-2026/site/build.py` |
| Data Updater | `projects/world-cup-2026/site/update_data.py` |
| Tweet Generator | `projects/world-cup-2026/site/generate_tweets.py` |
| Built Site | `projects/world-cup-2026/worldcup-site/` |
| Roadmap | `instructions/Roadmap.csv` + `instructions/Roadmap.xlsx` |
| Reports | `reports/tasks/` |

---

## 10. Decision Log

| Date | Decision | By |
|---|---|---|
| 2026-06-18 | Static HTML generator (not dynamic app) | Hermes + Ehab |
| 2026-06-18 | 6 automated models + 4 manual models | Ehab |
| 2026-06-18 | OpenCode Go for Qwen/Kimi/Minimax/GLM/MiMo | Ehab |
| 2026-06-18 | Antigravity manual only (no SDK bridge) | Ehab |
| 2026-06-18 | Netlify for wc2026, Cloudflare for ehabkhedr.com | Ehab |
| 2026-06-18 | 3 tweets per match + daily summary + weekly merch | Hermes |

---

**End of Workflow. All agents must follow this. Questions → ask Hermes.**

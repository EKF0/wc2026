# World Cup 2026 Enhanced Site — Implementation Plan

> **For Hermes:** Lead with subagent-driven-development. Ehab executes Antigravity tasks manually.

**Goal:** Rebuild wc2026.ehabkhedr.com with real match data, AI predictions from 6 models per match, individual match pages, and automated daily updates.

**Architecture:** Static site generator — Python build script reads structured data files (JSON), generates all HTML pages, deploys to Netlify. Data files updated by agents on schedule.

**Tech Stack:** Python 3 stdlib (JSON, HTML generation), Netlify deploy, Netlify free tier. $0 budget.

---

## Research Findings

### World Cup 2026 Live State
- **Tournament window:** June 11 — July 19, 2026
- **48 teams** in **12 groups** (A-L)
- **104 total matches** (72 group stage + 32 knockout)
- **16 host cities** across USA, Canada, Mexico
- **Currently playing:** Group stage Matchday 1 complete, Matchday 2 in progress (June 18+)
- Real results available from FIFA.com, ESPN, Yahoo Sports

### Results already played (Matchday 1 complete)
| Date | Match | Score |
|---|---|---|
| Jun 11 | Korea Republic vs Czechia | 2-1 |
| Jun 12 | Canada vs Bosnia | 1-1 |
| Jun 12 | USA vs Paraguay | 4-1 |
| Jun 13 | Switzerland vs Qatar | 1-1 |
| Jun 13 | Brazil vs Morocco | 1-1 |
| Jun 13 | Scotland vs Haiti | 1-0 |
| Jun 13 | Australia vs Türkiye | 2-0 |
| Jun 14 | Germany vs Curaçao | 7-1 |
| Jun 14 | Ivory Coast vs Ecuador | 1-0 |
| Jun 14 | Netherlands vs Japan | 2-2 |
| Jun 14 | Sweden vs Tunisia | 5-1 |
| Jun 15 | Belgium vs Egypt | 1-1 |
| Jun 16 | France vs Senegal | 3-1 |
| Jun 16 | Norway vs Iraq | 4-1 |
| Jun 16 | Argentina vs Algeria | 3-0 |
| Jun 16 | Austria vs Jordan | 3-1 |
| Jun 17 | Uzbekistan vs Colombia | 1-3 |
| Jun 17 | England vs Croatia | 4-2 |
| Jun 17 | Ghana vs Panama | 1-0 |
| Jun 18 | Czechia vs South Africa | 1-1 |
| Jun 18 | Mexico vs South Africa | 2-0 (Jun 11 opener) |

### Data sources available:
- FIFA.com/scores-fixtures (official API with flags, stadiums, live scores)
- Yahoo Sports (detailed match reports)
- ESPN schedule (odds, TV info)
- Wikipedia groups (standings, qualification history)

---

## Phase 1: Data Architecture

### File: `projects/world-cup-2026/site-data/groups.json`
```json
{
  "groups": {
    "A": {
      "teams": ["Mexico", "South Africa", "South Korea", "Czechia"],
      "standings": [
        {"team": "Mexico", "MP": 1, "W": 1, "D": 0, "L": 0, "GF": 2, "GA": 0, "GD": 2, "Pts": 3}
      ]
    }
  }
}
```

### File: `projects/world-cup-2026/site-data/matches.json`
```json
{
  "matches": [
    {
      "id": "wc2026-grp-a-1",
      "date": "2026-06-11",
      "time_et": "13:00",
      "group": "A",
      "stage": "Group Stage",
      "home_team": "Mexico",
      "away_team": "South Africa",
      "home_score": 2,
      "away_score": 0,
      "status": "completed",
      "stadium": "Estadio Azteca",
      "city": "Mexico City",
      "country": "Mexico"
    }
  ]
}
```

### File: `projects/world-cup-2026/site-data/predictions.json`
```json
{
  "predictions": {
    "wc2026-grp-a-1": {
      "generated": "2026-06-11T10:00:00Z",
      "models": {
        "hermes_deepseek_v4_pro": {
          "predicted_score": "Mexico 2-1 South Africa",
          "confidence": "high",
          "reasoning": "Mexico at Azteca with home advantage...",
          "key_factors": ["Home crowd", "Altitude advantage", "Lozano form"]
        }
      }
    }
  }
}
```

---

## Phase 2: Site Structure

```
worldcup-site/
├── index.html              # Main hub — live scores, today's matches, featured
├── matches/
│   ├── index.html          # All matches grid, filterable
│   ├── wc2026-grp-a-1.html # Mexico vs South Africa
│   ├── wc2026-grp-a-2.html # South Korea vs Czechia
│   └── ... (104 total)
├── groups/
│   ├── index.html          # Group overview
│   └── group-a.html        # Individual group page
├── predictions/
│   └── index.html          # Prediction leaderboard/tracker
├── models/
│   └── index.html          # About the AI models making predictions
├── assets/
│   ├── style.css
│   ├── flags/              # Country flags (emoji or SVG)
│   └── favicon.svg
├── data/                   # Raw data files (symlinked or embedded)
│   ├── matches.json
│   ├── groups.json
│   └── predictions.json
├── build.py                # Site generator script
├── update_data.py          # Data updater (fetches results, triggers predictions)
└── netlify.toml
```

---

## Phase 3: Prediction Pipeline

### 6 AI Models Making Predictions (Direct — Hermes calls automatically)

| # | Model | Agent | Access Method | How Prediction is Generated |
|---|---|---|---|---|
| 1 | **DeepSeek V4 Pro** | Hermes | Direct (OpenRouter) | Hermes generates prediction in-session, writes JSON |
| 2 | **Qwen 3.7 Plus** | OpenCode Go | `opencode run` via terminal | Hermes calls OpenCode with `--model opencode-go/qwen3.7-plus` |
| 3 | **Kimi K2.6** | OpenCode Go | `opencode run` via terminal | Hermes calls OpenCode with `--model opencode-go/kimi-k2.6` |
| 4 | **Minimax M3** | OpenCode Go | `opencode run` via terminal | Hermes calls OpenCode with `--model opencode-go/minimax-m3 --effort max` |
| 5 | **GLM 5.2** | OpenCode Go | `opencode run` via terminal | Hermes calls OpenCode with `--model opencode-go/glm-5.2` |
| 6 | **Nemotron Ultra 550B** | OpenClaw | OpenClaw gateway at loopback:18789 | Hermes calls OpenClaw API with 1M context window |

### Manual Models (Ehab runs when needed)

| # | Model | Agent | Access Method | Notes |
|---|---|---|---|---|
| 7 | **Xiaomi MiMo v2.5** | Ehab manual | OpenCode Go or opencode web | Ehab runs manually, reports prediction back |
| 8 | **Gemini 3.5 Flash** | Antigravity | **MANUAL** — Ehab copies prompt | Ehab pastes match prompt into Antigravity desktop app → reports back |
| 9 | **Claude Sonnet 4.6** | Claude | claude.ai web | Ehab pastes match prompt into Claude.ai → copies prediction back |
| 10 | **Codex CLI** | Codex | `codex exec` via terminal | Ehab runs manually if needed |

### Prediction Format (Standardized)
```json
{
  "model": "hermes_deepseek_v4_pro",
  "model_display": "Hermes × DeepSeek V4 Pro",
  "match_id": "wc2026-grp-l-3",
  "generated": "2026-06-18T19:00:00Z",
  "predicted_score": "England 3-1 Panama",
  "confidence": "medium",
  "reasoning": "England's attacking depth with Kane and Bellingham...",
  "key_factors": ["Kane form", "Panama defensive gaps", "Set pieces"],
  "win_probability": {"home": 0.72, "draw": 0.18, "away": 0.10}
}
```

### Prediction Flow
```
1. Hermes identifies upcoming matches (next 24-48h)
2. For each match:
   a. Hermes generates prediction (DeepSeek V4 Pro) — write to predictions.json
   b. Hermes calls OpenCode Go with Qwen 3.7 Plus — parse output → write
   c. Hermes calls OpenCode Go with Kimi K2.6 — parse output → write
   d. Hermes calls OpenCode Go with Minimax M3 (Max effort) — parse output → write
   e. Hermes calls OpenCode Go with GLM 5.2 — parse output → write
   f. Hermes calls OpenClaw gateway (Nemotron Ultra) — parse output → write
   
   Optional (when Ehab has time):
   g. Ehab runs Xiaomi MiMo v2.5 via OpenCode → reports back → Hermes writes
   h. Ehab runs Antigravity (Gemini) → reports back → Hermes writes
   i. Ehab runs Claude via claude.ai → reports back → Hermes writes
   j. Ehab runs Codex CLI → reports back → Hermes writes

3. Build script regenerates match pages with all predictions
4. Deploy to Netlify
```

### OpenCode Go Command Examples

```bash
# Qwen 3.7 Plus prediction
opencode run --model opencode-go/qwen3.7-plus "Predict the score for England vs Panama on June 19, 2026. Consider: England's form, Panama's defense, key players. Output JSON: {predicted_score, confidence, reasoning, key_factors, win_probability}"

# Kimi K2.6 prediction
opencode run --model opencode-go/kimi-k2.6 "Predict the score for England vs Panama on June 19, 2026. Consider: England's form, Panama's defense, key players. Output JSON: {predicted_score, confidence, reasoning, key_factors, win_probability}"

# Minimax M3 prediction (Max effort)
opencode run --model opencode-go/minimax-m3 --effort max "Predict the score for England vs Panama on June 19, 2026. Consider: England's form, Panama's defense, key players. Output JSON: {predicted_score, confidence, reasoning, key_factors, win_probability}"

# GLM 5.2 prediction
opencode run --model opencode-go/glm-5.2 "Predict the score for England vs Panama on June 19, 2026. Consider: England's form, Panama's defense, key players. Output JSON: {predicted_score, confidence, reasoning, key_factors, win_probability}"

# Xiaomi MiMo v2.5 prediction (Ehab runs manually)
opencode run --model opencode-go/mimo-v2.5 "Predict the score for England vs Panama on June 19, 2026. Consider: England's form, Panama's defense, key players. Output JSON: {predicted_score, confidence, reasoning, key_factors, win_probability}"
```

---

## Phase 4: Automation

### Cron Jobs (Hermes managed)

| Job | Frequency | What it Does |
|---|---|---|
| `wc2026-fetch-results` | Every 2h | Scrapes FIFA.com for new results, updates matches.json |
| `wc2026-generate-predictions` | Every 6h | Generates predictions for next 48h of matches from all available models |
| `wc2026-generate-tweets` | After predictions | Auto-generates 3 tweets per match (pre-match, hype, post-match) with predictions + website links |
| `wc2026-queue-tweets` | After tweet generation | Queues tweets via OpenTweet MCP with scheduled times |
| `wc2026-daily-summary` | Daily 11:00 PM ET | Generates daily prediction accuracy summary tweet |
| `wc2026-weekly-merch` | Weekly Sunday 6 PM ET | Generates merch/service funnel tweet |
| `wc2026-rebuild-site` | After data update | Runs build.py, deploys to Netlify |

### Automation Script: `update_data.py`
- Fetches real results from FIFA.com / Yahoo Sports
- Updates matches.json with scores, status changes
- Triggers prediction generation for upcoming matches
- **Auto-generates tweets** with predictions + website links
- **Queues tweets** via OpenTweet MCP with scheduled times
- Calls build.py → deploys

---

## Phase 5: Implementation Tasks

### Task 1: Create data files (groups.json, matches.json)
Populate with real 2026 World Cup data: all 12 groups, team rosters, full match schedule, and already-played results.

### Task 2: Build the site generator (build.py)
Python script that:
- Reads groups.json, matches.json, predictions.json
- Generates index.html (live dashboard)
- Generates /matches/index.html (all matches grid)
- Generates individual /matches/wc2026-*.html (104 match pages with predictions)
- Generates /groups/index.html and /groups/group-*.html
- Generates /predictions/index.html (prediction tracker/accuracy)
- Applies consistent dark sports theme CSS

### Task 3: Generate first round of AI predictions + tweets
For the next 10 upcoming matches (June 19-22):
- Hermes generates predictions (DeepSeek V4 Pro)
- Hermes calls OpenCode Go with Qwen 3.7 Plus, Kimi K2.6, Minimax M3, GLM 5.2
- Hermes calls OpenClaw gateway (Nemotron Ultra)
- Ehab runs Xiaomi MiMo v2.5 via OpenCode (manual)
- Ehab runs Antigravity predictions (manual)
- Optional: Ehab runs Claude via claude.ai (manual)
- Write all to predictions.json
- **Auto-generate 3 tweets per match** (pre-match, hype, post-match)
- **Queue tweets via OpenTweet MCP** with scheduled times
- Each tweet includes match page link: `wc2026.ehabkhedr.com/matches/{match-id}`

### Task 4: Build and deploy site
- Run build.py → generates all HTML
- Deploy to Netlify (needs auth token or `netlify login`)

### Task 5: Setup automation cron
- Schedule result fetching every 2h
- Schedule prediction generation every 6h
- **Auto-generate tweets** when predictions are created
- **Auto-queue tweets** via OpenTweet MCP with scheduled times
- Auto-rebuild and deploy site after data updates
- Daily summary tweet at 11:00 PM ET
- Weekly merch funnel tweet (Sunday 6 PM ET)

---

## Phase 6: Social Media & Tweet Automation

### Tweet Templates (Enhanced with Predictions + Website Links)

Each match gets **3 automated tweets**:

#### Tweet 1: Pre-Match Preview (2 hours before kickoff)
```
🏆 World Cup 2026 — {Home Team} vs {Away Team}
📅 {Date} | ⏰ {Time} ET | 🏟️ {Stadium}, {City}

🤖 6 AI Models Predict:
• DeepSeek V4 Pro: {prediction}
• Qwen 3.7 Plus: {prediction}
• Kimi K2.6: {prediction}
• Minimax M3: {prediction}
• GLM 5.2: {prediction}
• Nemotron Ultra: {prediction}

📊 Consensus: {average_prediction}
🔗 Full analysis: wc2026.ehabkhedr.com/matches/{match-id}

#WorldCup2026 #{HomeTeam}#{AwayTeam}
```

#### Tweet 2: Match Hype (20 minutes before kickoff)
```
{Home Team} vs {Away Team} kicks off in 20 minutes!

Our AI models are split:
• {X}% predict {Home Team} win
• {Y}% predict draw
• {Z}% predict {Away Team} win

Most confident prediction: {model_name} → {prediction}

Watch live predictions update: wc2026.ehabkhedr.com/matches/{match-id}

#WorldCup2026
```

#### Tweet 3: Post-Match Analysis (30 minutes after final whistle)
```
Final: {Home Team} {score} {Away Team}

🤖 AI Prediction Accuracy:
• {model_1}: {prediction} — {✅ correct / ❌ wrong}
• {model_2}: {prediction} — {✅ correct / ❌ wrong}
• {model_3}: {prediction} — {✅ correct / ❌ wrong}
• {model_4}: {prediction} — {✅ correct / ❌ wrong}
• {model_5}: {prediction} — {✅ correct / ❌ wrong}
• {model_6}: {prediction} — {✅ correct / ❌ wrong}

📊 Model leaderboard: wc2026.ehabkhedr.com/predictions

#WorldCup2026
```

### Daily Summary Tweet (11:00 PM ET)
```
Today's World Cup — AI Prediction Tracker

✅ {X}/6 models predicted correctly
🏆 Best model today: {model_name} ({accuracy}%)
📈 Overall accuracy: {model_name} leads at {X}%

See full stats: wc2026.ehabkhedr.com/predictions

Follow daily predictions → wc2026.ehabkhedr.com

#WorldCup2026
```

### Merch/Service Funnel Tweet (Weekly)
```
Love the AI predictions?

Get this match on a shirt → redbubble.com/shop/pixelsilkstore
Want AI predictions for your business? → aicustombot.net

Follow for daily World Cup analysis → wc2026.ehabkhedr.com

#WorldCup2026
```

### Tweet Generation Workflow

```
1. Hermes generates predictions for upcoming matches (Phase 3)
2. For each match, Hermes auto-generates 3 tweets:
   - Pre-match preview (scheduled 2h before kickoff)
   - Match hype (scheduled 20min before kickoff)
   - Post-match analysis (scheduled 30min after final whistle)
3. Tweets include:
   - Prediction summaries from all 6 models
   - Direct link to match page: wc2026.ehabkhedr.com/matches/{match-id}
   - Direct link to predictions tracker: wc2026.ehabkhedr.com/predictions
   - Hashtags: #WorldCup2026 + team names
4. Hermes queues tweets via OpenTweet MCP
5. Daily summary tweet auto-generated at 11:00 PM ET
6. Weekly merch/service funnel tweet auto-generated
```

### Tweet Scheduling Rules

| Tweet Type | When to Post | Content |
|---|---|---|
| Pre-match preview | 2h before kickoff | All 6 predictions + match page link |
| Match hype | 20min before kickoff | Win probabilities + live predictions link |
| Post-match analysis | 30min after final whistle | Prediction accuracy + leaderboard link |
| Daily summary | 11:00 PM ET | Day's accuracy stats + predictions tracker |
| Merch funnel | Weekly (Sunday 6 PM ET) | Redbubble + AI Custom Bot links |

### Tweet Content Rules (Human Voice)

- Write like The Athletic meets a smart group chat
- No emoji bullets. No "AI predicts..." hooks. No robotic transitions.
- Match hype: hook + specific detail + quick opinion
- Predictions: casual, not salesy. "Our models are split on this one."
- Links: embed naturally, not spammy. "Full analysis: [url]"
- Arabic content: original thoughts in Arabic, not translations
- Images: sports broadcast style (1280x720), 1 image per 3-4 tweets

### Revenue Hooks in Every Tweet

- Match page link → drives traffic to wc2026.ehabkhedr.com
- Predictions tracker link → keeps users coming back
- Redbubble link → POD merchandise sales
- AI Custom Bot link → B2B service inquiries
- Social media links → follower growth

---

## Key Design Decisions

1. **Static HTML, not dynamic app** — deploy anywhere, no backend costs, fast, SEO-friendly
2. **JSON data layer** — single source of truth, easy for agents to update programmatically
3. **Python build script** — stdlib only, no dependencies, any agent can run it
4. **Multi-model prediction format** — standardized JSON, each model has equal weight on match page
5. **Dark sports theme preserved** — keep the existing `#0a0e14` / `#00d4aa` design language
6. **Mobile-first** — all match pages responsive

---

## Revenue Hooks (Built Into Every Page + Tweet)

### On Website Pages
- "Get this match on a shirt" → Redbubble POD link
- "Want AI predictions for your business?" → AI Custom Bot service
- "Follow daily predictions" → Social media links
- Bottom of every match page: funnel to merchandise + services

### In Every Tweet
- Match page link → drives traffic to wc2026.ehabkhedr.com
- Predictions tracker link → keeps users coming back daily
- Redbubble link → POD merchandise sales (weekly funnel tweet)
- AI Custom Bot link → B2B service inquiries (weekly funnel tweet)
- Social media links → follower growth → larger audience → more revenue

### Revenue Flow
```
Tweet with predictions → User clicks match page → User sees merch link → User buys shirt
Tweet with predictions → User clicks predictions tracker → User comes back daily → User follows social → User sees merch/social links
Weekly funnel tweet → Direct Redbubble/AI Custom Bot links → Direct sales/inquiries
```

---

## Files Affected

| Action | Path |
|---|---|
| CREATE | `projects/world-cup-2026/site-data/groups.json` |
| CREATE | `projects/world-cup-2026/site-data/matches.json` |
| CREATE | `projects/world-cup-2026/site-data/predictions.json` |
| CREATE | `projects/world-cup-2026/site/build.py` |
| CREATE | `projects/world-cup-2026/site/update_data.py` |
| CREATE | `projects/world-cup-2026/site/generate_tweets.py` |
| CREATE | `projects/world-cup-2026/site/netlify.toml` |
| CREATE | `projects/world-cup-2026/site/assets/style.css` |
| REPLACE | `projects/world-cup-2026/worldcup-site/index.html` |
| CREATE | `projects/world-cup-2026/worldcup-site/matches/*.html` |
| CREATE | `projects/world-cup-2026/worldcup-site/groups/*.html` |
| CREATE | `projects/world-cup-2026/worldcup-site/predictions/index.html` |
| CREATE | `projects/world-cup-2026/worldcup-site/models/index.html` |

---

## Tools Available (Verified)

| Tool | Version | Path | Status |
|---|---|---|---|
| OpenCode Go | 1.3.3 | `/usr/local/bin/opencode` | ✅ Available |
| Codex CLI | 0.137.0 | `/opt/homebrew/bin/codex` | ✅ Available |
| Netlify CLI | (needs install) | — | ⚠️ Needs `npm install netlify-cli` |
| Wrangler | 4.102.0 | (in ehab-website) | ✅ Available |

### OpenCode Go Models Available
```
opencode-go/qwen3.7-plus     ✓
opencode-go/kimi-k2.6        ✓
opencode-go/minimax-m3       ✓
opencode-go/glm-5.2          ✓
opencode-go/mimo-v2.5        ✓
opencode-go/deepseek-v4-pro  ✓
opencode-go/kimi-k2.7-code   ✓
opencode-go/qwen3.7-max      ✓
```

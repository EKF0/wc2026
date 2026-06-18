# World Cup 2026 AI Predictions

Live site: **[wc2026.ehabkhedr.com](https://wc2026.ehabkhedr.com)**

## What This Is
A static site generator that builds 100+ HTML pages for World Cup 2026 matches with AI predictions from 10 different models.

## Architecture
- `build.py` — Python 3 stdlib site generator (no dependencies)
- `site-data/` — JSON data files (matches, groups, predictions)
- `worldcup-site/` — Generated HTML output (deployed to Netlify)
- `netlify.toml` — Netlify configuration

## 10 AI Models
### Automated (via Hermes cron jobs)
1. DeepSeek V4 Pro (Hermes)
2. Qwen 3.7 Plus (OpenCode Go)
3. Kimi K2.6 (OpenCode Go)
4. Minimax M3 (OpenCode Go)
5. GLM 5.2 (OpenCode Go)
6. Nemotron Ultra 550B (OpenClaw)

### Manual (Ehab runs)
7. Xiaomi MiMo v2.5 (OpenCode Go)
8. Gemini 3.5 Flash (Antigravity)
9. Claude Sonnet 4.6 (claude.ai)
10. Codex CLI

## Build
```bash
python3 build.py
```

## Deploy
Push to `main` branch → Netlify auto-deploys.

## Owner
EKF Open AI Research — [ehabkhedr.com](https://ehabkhedr.com)

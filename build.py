#!/usr/bin/env python3
"""
World Cup 2026 AI Predictions Site Generator
Reads JSON data files and generates a complete static HTML website.
Python 3 stdlib only — no external dependencies.
"""
import json
import os
import sys
from datetime import datetime, timezone

# Paths
BASE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(BASE)
DATA_DIR = os.path.join(BASE, "site-data")
OUTPUT_DIR = os.path.join(BASE, "worldcup-site")

# Theme
BG = "#0a0e14"
ACCENT = "#00d4aa"
ACCENT2 = "#ff6b35"
WHITE = "#ffffff"
GRAY = "#a0a8b0"
DARK_CARD = "#141921"
DARK_BORDER = "#1e2530"

# Flags
FLAGS = {
    "Mexico": "🇲🇽", "South Africa": "🇿🇦", "South Korea": "🇰🇷", "Czechia": "🇨🇿",
    "Canada": "🇨🇦", "Switzerland": "🇨🇭", "Bosnia and Herzegovina": "🇧🇦", "Qatar": "🇶🇦",
    "Brazil": "🇧🇷", "Morocco": "🇲🇦", "Scotland": "🏴󠁧󠁢󠁳󠁣󠁴󠁿", "Haiti": "🇭🇹",
    "USA": "🇺🇸", "Australia": "🇦🇺", "Paraguay": "🇵🇾", "Türkiye": "🇹🇷",
    "Germany": "🇩🇪", "Curaçao": "🇨🇼", "Ivory Coast": "🇨🇮", "Ecuador": "🇪🇨",
    "Netherlands": "🇳🇱", "Japan": "🇯🇵", "Sweden": "🇸🇪", "Tunisia": "🇹🇳",
    "Iran": "🇮🇷", "New Zealand": "🇳🇿", "Belgium": "🇧🇪", "Egypt": "🇪🇬",
    "Spain": "🇪🇸", "Cape Verde": "🇨🇻", "Saudi Arabia": "🇸🇦", "Uruguay": "🇺🇾",
    "France": "🇫🇷", "Senegal": "🇸🇳", "Norway": "🇳🇴", "Iraq": "🇮🇶",
    "Argentina": "🇦🇷", "Algeria": "🇩🇿", "Austria": "🇦🇹", "Jordan": "🇯🇴",
    "Portugal": "🇵🇹", "DR Congo": "🇨🇩", "Uzbekistan": "🇺🇿", "Colombia": "🇨🇴",
    "England": "🏴󠁧󠁢󠁥󠁮󠁧󠁿", "Croatia": "🇭🇷", "Ghana": "🇬🇭", "Panama": "🇵🇦"
}

def load_data():
    """Load all JSON data files."""
    with open(os.path.join(DATA_DIR, "matches.json"), "r", encoding="utf-8") as f:
        matches = json.load(f)
    with open(os.path.join(DATA_DIR, "groups.json"), "r", encoding="utf-8") as f:
        groups = json.load(f)
    preds_path = os.path.join(DATA_DIR, "predictions.json")
    with open(preds_path, "r", encoding="utf-8") as f:
        predictions = json.load(f)
    return matches, groups, predictions

def load_reviews():
    """Load reviews data if available."""
    reviews_path = os.path.join(DATA_DIR, "reviews.json")
    if os.path.exists(reviews_path):
        with open(reviews_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"meta": {"total_reviews": 0}, "reviews": {}}

def get_flag(team):
    return FLAGS.get(team, "🏳️")

def status_class(status):
    if status == "completed": return "status-completed"
    if status == "live": return "status-live"
    return "status-upcoming"

def status_label(status):
    if status == "completed": return "FT"
    if status == "live": return "LIVE"
    return "UPCOMING"

def score_display(match):
    if match["status"] == "completed":
        return f'{match["home_score"]} - {match["away_score"]}'
    elif match["status"] == "live":
        return f'{match.get("home_score","?")} - {match.get("away_score","?")}'
    return "vs"

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def write_html(path, content):
    ensure_dir(os.path.dirname(path))
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

def css():
    return """
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#0a0e14;color:#fff;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;line-height:1.6}
a{color:#00d4aa;text-decoration:none;transition:color .2s}
a:hover{color:#ff6b35}
.container{max-width:1200px;margin:0 auto;padding:0 20px}
.header{background:#141921;border-bottom:1px solid #1e2530;padding:16px 0;position:sticky;top:0;z-index:100}
.header .container{display:flex;align-items:center;justify-content:space-between}
.logo{font-size:1.5rem;font-weight:800;color:#00d4aa}
.nav{display:flex;gap:20px}
.nav a{color:#a0a8b0;font-size:.9rem}
.nav a:hover{color:#fff}
.hero{text-align:center;padding:40px 20px}
.hero h1{font-size:2.5rem;margin-bottom:10px;background:linear-gradient(135deg,#00d4aa,#ff6b35);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.hero p{color:#a0a8b0;font-size:1.1rem}
.section{padding:30px 0}
.section h2{font-size:1.5rem;margin-bottom:20px;color:#fff;border-left:3px solid #00d4aa;padding-left:12px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:16px}
.card{background:#141921;border:1px solid #1e2530;border-radius:12px;padding:20px;transition:transform .2s,border-color .2s}
.card:hover{transform:translateY(-2px);border-color:#00d4aa}
.match-card{cursor:pointer}
.match-teams{display:flex;align-items:center;justify-content:space-between;margin:12px 0}
.team{display:flex;align-items:center;gap:8px;font-size:1.1rem;font-weight:600}
.team-flag{font-size:1.8rem}
.score{font-size:1.4rem;font-weight:800;color:#00d4aa;min-width:80px;text-align:center}
.match-meta{color:#a0a8b0;font-size:.85rem;margin-top:8px}
.status-badge{display:inline-block;padding:2px 10px;border-radius:20px;font-size:.75rem;font-weight:600}
.status-completed{background:#1a3a2a;color:#00d4aa}
.status-live{background:#3a1a1a;color:#ff6b35;animation:pulse 2s infinite}
.status-upcoming{background:#1e2530;color:#a0a8b0}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.5}}
.pred-card{background:#141921;border:1px solid #1e2530;border-radius:10px;padding:16px;margin:10px 0}
.pred-card h4{color:#00d4aa;font-size:.95rem;margin-bottom:6px}
.pred-score{font-size:1.3rem;font-weight:700;margin:4px 0}
.pred-reasoning{color:#a0a8b0;font-size:.85rem;margin-top:6px}
.pred-factors{display:flex;flex-wrap:wrap;gap:6px;margin-top:8px}
.pred-factor{background:#1e2530;padding:2px 10px;border-radius:12px;font-size:.75rem;color:#a0a8b0}
.confidence-high{color:#00d4aa}.confidence-medium{color:#ffaa00}.confidence-low{color:#ff6b35}
.prob-bar{height:8px;border-radius:4px;background:#1e2530;overflow:hidden;margin:6px 0}
.prob-fill{height:100%;transition:width .3s}
.prob-home{background:#00d4aa}.prob-draw{background:#a0a8b0}.prob-away{background:#ff6b35}
table{width:100%;border-collapse:collapse;margin:12px 0}
th,td{padding:10px 12px;text-align:left;border-bottom:1px solid #1e2530}
th{color:#00d4aa;font-size:.85rem;text-transform:uppercase}
td{font-size:.9rem}
.standings td{font-size:.9rem}
.pos{font-weight:700;color:#00d4aa}
.footer{background:#141921;border-top:1px solid #1e2530;padding:30px 0;margin-top:40px;text-align:center}
.footer-links{display:flex;gap:20px;justify-content:center;margin-bottom:12px;flex-wrap:wrap}
.footer-links a{color:#a0a8b0;font-size:.9rem}
.footer p{color:#5a6068;font-size:.8rem}
.btn{display:inline-block;padding:10px 24px;border-radius:8px;font-weight:600;transition:transform .2s}
.btn-primary{background:#00d4aa;color:#0a0e14}.btn-primary:hover{transform:translateY(-1px);color:#0a0e14}
.btn-secondary{background:transparent;border:1px solid #00d4aa;color:#00d4aa}
.match-header{text-align:center;padding:30px 0}
.match-header h1{font-size:2rem;margin:10px 0}
.match-header .teams{font-size:2.5rem;margin:16px 0}
.match-header .score{font-size:3rem;display:block;margin:10px 0}
.pred-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(350px,1fr));gap:14px}
.model-badge{display:inline-block;padding:3px 10px;border-radius:12px;font-size:.75rem;margin-bottom:6px}
.model-automated{background:#1a3a2a;color:#00d4aa}
.model-manual{background:#3a2a1a;color:#ffaa00}
.tabs{display:flex;gap:12px;margin-bottom:20px;flex-wrap:wrap}
.tab{padding:8px 18px;border-radius:8px;background:#141921;border:1px solid #1e2530;color:#a0a8b0;cursor:pointer;font-size:.85rem;transition:all .2s}
.tab.active{background:#00d4aa;color:#0a0e14;border-color:#00d4aa}
.no-pred{text-align:center;padding:30px;color:#5a6068}
@media(max-width:768px){.grid{grid-template-columns:1fr}.hero h1{font-size:1.8rem}.match-header .teams{font-size:1.8rem}.pred-grid{grid-template-columns:1fr}.nav{gap:10px}.nav a{font-size:.8rem}}
</style>
"""

def page_head(title, desc="AI-powered World Cup 2026 predictions from 10 AI models — match forecasts, live scores, and AI match reviews", canonical="", schema_type="WebSite", schema_data="", image="https://wc2026.ehabkhedr.com/og-image.jpg"):
    """Generate HTML head with complete SEO metadata."""
    safe_title = title.replace('"', '&quot;')
    safe_desc = desc.replace('"', '&quot;')[:160]
    site_name = "WC2026 AI Predictions"
    site_url = "https://wc2026.ehabkhedr.com"
    
    # Canonical URL
    canonical_url = canonical if canonical else site_url
    if canonical_url and not canonical_url.startswith("http"):
        canonical_url = site_url + canonical_url
    
    # Default schema (WebSite)
    if not schema_data:
        from datetime import datetime, timezone
        schema_data = f'''{{
      "@context": "https://schema.org",
      "@type": "WebSite",
      "name": "{site_name}",
      "url": "{site_url}",
      "description": "{safe_desc}",
      "author": {{"@type": "Organization", "name": "EKF Open AI Research", "url": "https://ehabkhedr.com"}},
      "dateModified": "{datetime.now(timezone.utc).strftime('%Y-%m-%d')}"
    }}'''
    
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<meta name="description" content="{safe_desc}">
<meta name="robots" content="index,follow,max-snippet:-1,max-image-preview:large,max-video-preview:-1">
<meta name="googlebot" content="index,follow">
<meta name="author" content="EKF Open AI Research">
<link rel="canonical" href="{canonical_url}">

<!-- OpenGraph -->
<meta property="og:title" content="{safe_title}">
<meta property="og:description" content="{safe_desc}">
<meta property="og:type" content="website">
<meta property="og:url" content="{canonical_url}">
<meta property="og:image" content="{image}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="World Cup 2026 AI Predictions">
<meta property="og:site_name" content="{site_name}">
<meta property="og:locale" content="en_US">

<!-- Twitter Card -->
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{safe_title}">
<meta name="twitter:description" content="{safe_desc}">
<meta name="twitter:image" content="{image}">
<meta name="twitter:site" content="@ehabkhedr">
<meta name="twitter:creator" content="@ehabkhedr">

<!-- Structured Data -->
<script type="application/ld+json">
{schema_data}
</script>

<!-- Preconnect to origins -->
<link rel="preconnect" href="https://wc2026-eu6.pages.dev">
<link rel="dns-prefetch" href="https://wc2026-eu6.pages.dev">

<!-- Favicon -->
<link rel="icon" type="image/svg+xml" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>⚽</text></svg>">
<link rel="apple-touch-icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>⚽</text></svg>">

{css()}
</head>
<body>
<div class="header"><div class="container">
<a href="/" class="logo">⚽ WC2026 AI</a>
<nav class="nav" aria-label="Main navigation">
<a href="/">Home</a>
<a href="/matches/">Matches</a>
<a href="/groups/">Groups</a>
<a href="/predictions/">Predictions</a>
<a href="/models/">Models</a>
<a href="/reviews/">Reviews</a>
</nav>
</div></div>
"""

def page_footer():
    return """<footer class="footer"><div class="container">
<nav class="footer-links" aria-label="Footer navigation">
<a href="/">Home</a>
<a href="/matches/">Matches</a>
<a href="/groups/">Groups</a>
<a href="/predictions/">Predictions</a>
<a href="/models/">Models</a>
<a href="/reviews/">Reviews</a>
<a href="/sitemap.xml" target="_blank">Sitemap</a>
<a href="/llms.txt" target="_blank">AI Agents</a>
<a href="https://redbubble.com/shop/pixelsilkstore" target="_blank" rel="noopener">🛍️ Merch</a>
<a href="https://ehabkhedr.com" target="_blank" rel="noopener">🌐 Ehab Khedr</a>
</nav>
<p>Powered by 10 AI Models · Built by <a href="https://ehabkhedr.com">EKF Open AI Research</a> · © 2026 · <a href="https://wc2026.ehabkhedr.com">wc2026.ehabkhedr.com</a></p>
</div></footer>
</body></html>
"""

def gen_index(matches_data, groups_data, predictions_data):
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    matches = matches_data["matches"]
    today_matches = [m for m in matches if m["date"] == today]
    live_matches = [m for m in matches if m["status"] == "live"]
    upcoming = [m for m in matches if m["status"] == "upcoming"][:6]
    completed = [m for m in matches if m["status"] == "completed"]
    
    html = page_head("World Cup 2026 AI Predictions", "Real-time AI predictions from 10 models for every World Cup 2026 match")
    html += '<div class="container">'
    html += '<div class="hero"><h1>World Cup 2026 AI Predictions</h1>'
    html += f'<p>{len(matches)} matches · 48 teams · 10 AI models · Real-time predictions</p></div>'
    
    if live_matches:
        html += '<div class="section"><h2>🔴 Live Now</h2><div class="grid">'
        for m in live_matches:
            html += match_card(m)
        html += '</div></div>'
    
    if today_matches:
        html += '<div class="section"><h2>📅 Today\'s Matches</h2><div class="grid">'
        for m in today_matches:
            html += match_card(m)
        html += '</div></div>'
    
    html += '<div class="section"><h2>⏭️ Upcoming Matches</h2><div class="grid">'
    for m in upcoming:
        html += match_card(m)
    html += '</div></div>'
    
    html += '<div class="section"><h2>✅ Recent Results</h2><div class="grid">'
    for m in completed[-6:]:
        html += match_card(m)
    html += '</div></div>'
    
    html += '<div class="section"><h2>🤖 AI Models</h2>'
    html += '<div class="grid">'
    for model in predictions_data.get("models", []):
        badge = "model-automated" if model["type"] == "automated" else "model-manual"
        html += f'<div class="card"><span class="model-badge {badge}">{model["type"].upper()}</span><h3>{model["display"]}</h3><p style="color:#a0a8b0;font-size:.85rem;margin-top:6px">Agent: {model["agent"]}</p></div>'
    html += '</div></div>'
    
    html += '</div>'
    html += page_footer()
    return html

def match_card(m):
    flag_h = get_flag(m["home_team"])
    flag_a = get_flag(m["away_team"])
    score = score_display(m)
    sl = status_label(m["status"])
    sc = status_class(m["status"])
    return f'''<a href="/matches/{m["id"]}.html" class="card match-card" style="text-decoration:none;color:inherit">
<div><span class="status-badge {sc}">{sl}</span></div>
<div class="match-teams">
<div class="team"><span class="team-flag">{flag_h}</span><span>{m["home_team"]}</span></div>
<div class="score">{score}</div>
<div class="team"><span>{m["away_team"]}</span><span class="team-flag">{flag_a}</span></div>
</div>
<div class="match-meta">📅 {m["date"]} · ⏰ {m["time_et"]} ET · 🏟️ {m["stadium"]}, {m["city"]}</div>
<div class="match-meta">Group {m["group"]}</div>
</a>'''

def gen_match_page(m, predictions_data):
    flag_h = get_flag(m["home_team"])
    flag_a = get_flag(m["away_team"])
    title = f"{m['home_team']} vs {m['away_team']} — World Cup 2026"
    desc = f"AI predictions for {m['home_team']} vs {m['away_team']} on {m['date']}, World Cup 2026 Group {m['group']}"
    
    html = page_head(title, desc)
    html += '<div class="container">'
    
    # Match header
    html += '<div class="match-header">'
    html += f'<div><span class="status-badge {status_class(m["status"])}">{status_label(m["status"])}</span></div>'
    html += f'<div class="teams">{flag_h} {m["home_team"]} <span style="color:#a0a8b0">vs</span> {m["away_team"]} {flag_a}</div>'
    if m["status"] == "completed":
        html += f'<div class="score">{m["home_score"]} - {m["away_score"]}</div>'
    elif m["status"] == "live":
        html += f'<div class="score">{m.get("home_score","?")} - {m.get("away_score","?")}</div>'
    else:
        html += '<div class="score">vs</div>'
    html += f'<div class="match-meta">📅 {m["date"]} · ⏰ {m["time_et"]} ET · 🏟️ {m["stadium"]}, {m["city"]}</div>'
    html += f'<div class="match-meta">Group {m["group"]} · {m["stage"]}</div>'
    html += '</div>'
    
    # Predictions
    match_preds = predictions_data.get("predictions", {}).get(m["id"], {})
    models_list = predictions_data.get("models", [])
    
    # Build model lookup
    model_lookup = {mod["id"]: mod for mod in models_list}
    
    # Check if we have predictions for this match
    has_predictions = bool(match_preds) and any(not k.startswith("_") for k in match_preds)
    
    if has_predictions:
        html += '<div class="section"><h2>🤖 AI Predictions</h2>'
        html += '<div class="pred-grid">'
        for model in models_list:
            pred_raw = match_preds.get(model["id"])
            if pred_raw:
                # Extract prediction from parsed sub-object (handle null)
                parsed = pred_raw.get("parsed") or {}
                pred_display = {
                    "predicted_score": parsed.get("predicted_score", "N/A"),
                    "confidence": parsed.get("confidence", 0.5),
                    "reasoning": parsed.get("reasoning", ""),
                    "key_factors": parsed.get("key_factors", []),
                    "win_probability": parsed.get("win_probability", {"home": 0.33, "draw": 0.34, "away": 0.33})
                }
                html += pred_card(model, pred_display)
        html += '</div></div>'
    else:
        html += '<div class="section"><h2>🤖 AI Predictions</h2>'
        html += '<div class="no-pred"><p>Predictions will be generated 48 hours before kickoff.</p>'
        html += '<p style="margin-top:8px">10 AI models will predict this match. Check back soon!</p></div></div>'
    
    # Revenue hooks
    html += '<div class="section" style="text-align:center">'
    html += '<a href="https://redbubble.com/shop/pixelsilkstore" class="btn btn-primary" target="_blank">🛍️ Get This Match on a Shirt</a> '
    html += '<a href="https://ehabkhedr.com" class="btn btn-secondary" target="_blank">Want AI for Your Business?</a>'
    html += '</div>'
    
    html += '</div>'
    html += page_footer()
    return html

def pred_card(model, pred):
    conf_val = pred.get("confidence", 0.5)
    if isinstance(conf_val, (int, float)):
        conf_pct = int(conf_val * 100)
        if conf_val > 0.7: conf_label = "high"
        elif conf_val > 0.4: conf_label = "medium"
        else: conf_label = "low"
    else:
        conf_label = conf_val
        conf_pct = conf_val
    conf_class = f"confidence-{conf_label}"
    factors = "".join(f'<span class="pred-factor">{f}</span>' for f in pred.get("key_factors", []))
    prob = pred.get("win_probability", {})
    h_prob = prob.get("home", 0) * 100
    d_prob = prob.get("draw", 0) * 100
    a_prob = prob.get("away", 0) * 100
    badge = "model-automated" if model["type"] == "automated" else "model-manual"
    return f'''<div class="pred-card">
<span class="model-badge {badge}">{model["type"].upper()}</span>
<h4>{model["display"]}</h4>
<div class="pred-score">{pred.get("predicted_score", "N/A")} <span class="{conf_class}" style="font-size:.8rem">({conf_pct}% confidence)</span></div>
<div class="prob-bar"><div class="prob-fill prob-home" style="width:{h_prob}%"></div></div>
<div class="prob-bar"><div class="prob-fill prob-draw" style="width:{d_prob}%"></div></div>
<div class="prob-bar"><div class="prob-fill prob-away" style="width:{a_prob}%"></div></div>
<div style="display:flex;justify-content:space-between;font-size:.75rem;color:#a0a8b0">
<span>Home {h_prob:.0f}%</span><span>Draw {d_prob:.0f}%</span><span>Away {a_prob:.0f}%</span>
</div>
<p class="pred-reasoning">{pred.get("reasoning", "")}</p>
<div class="pred-factors">{factors}</div>
</div>'''

def gen_matches_index(matches_data):
    html = page_head("All Matches — World Cup 2026", "Complete World Cup 2026 match schedule with AI predictions")
    html += '<div class="container"><div class="section"><h2>All Matches</h2>'
    html += '<div class="tabs">'
    html += '<div class="tab active" onclick="filterMatches(\'all\')">All</div>'
    html += '<div class="tab" onclick="filterMatches(\'completed\')">Completed</div>'
    html += '<div class="tab" onclick="filterMatches(\'live\')">Live</div>'
    html += '<div class="tab" onclick="filterMatches(\'upcoming\')">Upcoming</div>'
    html += '</div>'
    html += '<div class="grid" id="matches-grid">'
    for m in matches_data["matches"]:
        html += match_card(m)
    html += '</div></div></div>'
    html += '<script>'
    html += 'function filterMatches(status){'
    html += 'const cards=document.querySelectorAll("#matches-grid .match-card");'
    html += 'cards.forEach(c=>{c.style.display=(status==="all"||c.querySelector(".status-badge").classList.contains("status-"+status))?"block":"none"});'
    html += 'document.querySelectorAll(".tab").forEach(t=>t.classList.remove("active"));'
    html += 'event.target.classList.add("active")}'
    html += '</script>'
    html += page_footer()
    return html

def gen_groups_index(groups_data):
    html = page_head("Groups — World Cup 2026", "World Cup 2026 group standings and team information")
    html += '<div class="container"><div class="section"><h2>Group Standings</h2>'
    html += '<div class="grid">'
    for group_id in sorted(groups_data["groups"].keys()):
        g = groups_data["groups"][group_id]
        html += f'<div class="card"><h3 style="color:#00d4aa;margin-bottom:12px">Group {group_id}</h3>'
        html += '<table class="standings"><tr><th>#</th><th>Team</th><th>MP</th><th>W</th><th>D</th><th>L</th><th>GD</th><th>Pts</th></tr>'
        for i, s in enumerate(g["standings"], 1):
            html += f'<tr><td class="pos">{i}</td><td>{get_flag(s["team"])} {s["team"]}</td><td>{s["MP"]}</td><td>{s["W"]}</td><td>{s["D"]}</td><td>{s["L"]}</td><td>{s["GD"]:+d}</td><td><strong>{s["Pts"]}</strong></td></tr>'
        html += '</table></div>'
    html += '</div></div></div>'
    html += page_footer()
    return html

def gen_predictions_index(predictions_data, matches_data):
    html = page_head("AI Predictions — World Cup 2026", "AI predictions from 10 models for every World Cup 2026 match")
    html += '<div class="container"><div class="section"><h2>🤖 AI Predictions</h2>'
    
    predictions = predictions_data.get("predictions", {})
    match_map = {m["id"]: m for m in matches_data["matches"]}
    models_list = predictions_data.get("models", [])
    
    # Find matches with predictions
    matches_with_preds = []
    for mid in predictions:
        if mid.startswith("_"): continue
        m = match_map.get(mid)
        if m:
            pred_count = len([k for k in predictions[mid] if not k.startswith("_")])
            matches_with_preds.append((m, pred_count))
    
    # Sort by date
    matches_with_preds.sort(key=lambda x: x[0].get("date", ""))
    
    if matches_with_preds:
        html += f'<p style="color:#a0a8b0;margin-bottom:20px">{len(matches_with_preds)} matches with predictions · {sum(pc for _, pc in matches_with_preds)} total predictions from {len(models_list)} AI models</p>'
        html += '<div class="grid">'
        for m, pred_count in matches_with_preds:
            score = f'{m.get("home_score","?")}-{m.get("away_score","?")}' if m["status"] == "completed" else "vs"
            html += f'''<a href="/matches/{m["id"]}.html" class="card match-card" style="display:block;text-decoration:none;color:#fff">
                <div style="font-size:.85rem;color:#a0a8b0">{m["date"]} · {m.get("time_et","")} ET · Group {m["group"]}</div>
                <div class="match-teams">
                    <div class="team"><span class="team-flag">{get_flag(m["home_team"])}</span>{m["home_team"]}</div>
                    <div class="score">{score}</div>
                    <div class="team">{m["away_team"]}<span class="team-flag">{get_flag(m["away_team"])}</span></div>
                </div>
                <div style="color:#00d4aa;font-size:.85rem;margin-top:6px">{pred_count} model predictions available</div>
            </a>'''
        html += '</div>'
    else:
        html += '<div class="no-pred"><p>No predictions generated yet.</p><p style="margin-top:8px">Predictions will appear here as our AI models analyze upcoming matches. Check back soon!</p></div>'
    
    # Models summary
    html += '<div class="section"><h2>🔬 Prediction Models</h2><div class="grid">'
    for model in models_list:
        badge = "model-automated" if model["type"] == "automated" else "model-manual"
        # Count predictions from this model
        model_count = sum(1 for mid in predictions if not mid.startswith("_") and model["id"] in predictions[mid])
        html += f'<div class="card"><span class="model-badge {badge}">{model["type"].upper()}</span><h3>{model["display"]}</h3><p style="color:#a0a8b0;font-size:.85rem;margin-top:6px">Agent: {model["agent"]}</p><div style="margin-top:8px;font-size:.85rem;color:#00d4aa">Predictions: {model_count}</div></div>'
    html += '</div></div></div>'
    html += page_footer()
    return html

def gen_models_index(predictions_data):
    html = page_head("AI Models — World Cup 2026", "The 10 AI models making World Cup 2026 predictions")
    html += '<div class="container"><div class="section"><h2>10 AI Models Making Predictions</h2>'
    html += '<div class="grid">'
    for model in predictions_data.get("models", []):
        badge = "model-automated" if model["type"] == "automated" else "model-manual"
        html += f'<div class="card"><span class="model-badge {badge}">{model["type"].upper()}</span><h3>{model["display"]}</h3><p style="color:#a0a8b0;font-size:.85rem;margin-top:6px">Agent: {model["agent"]}</p></div>'
    html += '</div></div></div>'
    html += page_footer()
    return html

def gen_reviews_index(reviews_data, matches_data):
    """Generate the reviews index page listing all reviewed matches."""
    html = page_head("AI Match Reviews — World Cup 2026", "In-depth AI-powered analysis of every completed World Cup 2026 match")
    html += '<div class="container"><div class="section">'
    html += '<h2>🔍 AI Match Reviews</h2>'
    html += '<p style="color:#a0a8b0;margin-bottom:20px">Deep analysis combining match research, tactical breakdown, and AI prediction accuracy for every completed match.</p>'
    
    # Map match IDs to matches
    match_map = {m["id"]: m for m in matches_data["matches"]}
    reviews = reviews_data.get("reviews", {})
    
    # Sort by date (most recent first)
    reviewed_matches = []
    for mid, review in reviews.items():
        m = match_map.get(mid)
        if m and m.get("status") == "completed":
            reviewed_matches.append((m, review))
    reviewed_matches.sort(key=lambda x: x[0].get("date", ""), reverse=True)
    
    # Stats bar
    researched = sum(1 for _, r in reviewed_matches if r.get("sources"))
    html += f'<div style="display:flex;gap:20px;flex-wrap:wrap;margin-bottom:24px">'
    html += f'<div class="card" style="text-align:center;min-width:120px"><div style="font-size:2rem;color:#00d4aa;font-weight:800">{len(reviewed_matches)}</div><div style="color:#a0a8b0;font-size:.85rem">Matches Reviewed</div></div>'
    html += f'<div class="card" style="text-align:center;min-width:120px"><div style="font-size:2rem;color:#ff6b35;font-weight:800">{researched}</div><div style="color:#a0a8b0;font-size:.85rem">Deep Research</div></div>'
    html += '</div>'
    
    if not reviewed_matches:
        html += '<div class="no-pred">No reviews yet. Check back after matches are completed!</div>'
    else:
        html += '<div class="grid">'
        for m, review in reviewed_matches:
            rating = review.get("rating", "")
            headline = review.get("headline", f'{m["home_team"]} vs {m["away_team"]}')
            html += f'''<a href="/reviews/{m["id"]}.html" class="card match-card" style="display:block;text-decoration:none;color:#fff">
                <div style="font-size:.85rem;color:#a0a8b0">{m["date"]} · Group {m["group"]} · {m.get("stadium", "")}</div>
                <div class="match-teams">
                    <div class="team"><span class="team-flag">{get_flag(m["home_team"])}</span>{m["home_team"]}</div>
                    <div class="score">{m["home_score"]} - {m["away_score"]}</div>
                    <div class="team">{m["away_team"]}<span class="team-flag">{get_flag(m["away_team"])}</span></div>
                </div>
                <div style="font-weight:600;margin-top:6px;color:#fff">{headline}</div>
                <div style="color:#ffaa00;margin-top:4px;font-size:.85rem">{rating}</div>
            </a>'''
        html += '</div>'
    
    html += '</div></div>'
    html += page_footer()
    return html

def gen_review_page(m, review, matches_data, predictions_data):
    """Generate an individual match review page."""
    mid = m["id"]
    headline = review.get("headline", f'{m["home_team"]} vs {m["away_team"]}')
    
    html = page_head(f'Review: {m["home_team"]} {m["home_score"]}-{m["away_score"]} {m["away_team"]} — WC2026 AI', review.get("summary", "")[:160])
    
    # Hero section
    html += f'''<div class="container">
    <div class="match-header">
        <div style="color:#a0a8b0;font-size:.9rem">{m["date"]} · {m.get("stadium", "")}, {m.get("city", "")} · Group {m["group"]}</div>
        <div class="teams"><span class="team-flag" style="font-size:3rem">{get_flag(m["home_team"])}</span> {m["home_team"]} <span class="score">{m["home_score"]} - {m["away_score"]}</span> {m["away_team"]} <span class="team-flag" style="font-size:3rem">{get_flag(m["away_team"])}</span></div>
        <h1 style="font-size:1.5rem;max-width:700px;margin:12px auto;color:#fff">{headline}</h1>
        {f'<div style="color:#ffaa00;font-size:1.2rem">Rating: {review.get("rating", "")}</div>' if review.get("rating") else ""}
    </div>'''
    
    # Summary
    if review.get("summary"):
        html += f'<div class="section"><h2>📝 Match Summary</h2><div class="card"><p style="color:#d0d0d0;line-height:1.8;font-size:1.05rem">{review["summary"]}</p></div></div>'
    
    # Key Moments
    if review.get("key_moments"):
        html += '<div class="section"><h2>⏱️ Key Moments</h2><div class="card">'
        for km in review["key_moments"]:
            icon = km.get("icon", "")
            player_str = ""
            if km.get("player"):
                player_str = f' — <span style="color:#ff6b35">{km["player"]}</span>'
            team_str = ""
            if km.get("team"):
                team_str = f' <span style="color:#a0a8b0;font-size:.85rem">({km["team"]})</span>'
            html += f'<div style="display:flex;gap:14px;padding:12px 0;border-bottom:1px solid #1e2530;align-items:flex-start">'
            html += f'<div style="font-size:1.4rem;min-width:36px;text-align:center;color:#00d4aa;font-weight:700">{km["minute"]}</div>'
            html += f'<div style="font-size:1.3rem;min-width:28px">{icon}</div>'
            html += f'<div><strong>{km.get("type","").upper().replace("_"," ")}</strong>{player_str}{team_str}'
            html += f'<div style="color:#a0a8b0;margin-top:4px;font-size:.92rem">{km["description"]}</div></div></div>'
        html += '</div></div>'
    
    # Statistics
    if review.get("statistics"):
        stats = review["statistics"]
        html += '<div class="section"><h2>📊 Match Statistics</h2><div class="card"><table>'
        stat_labels = {"possession": "Possession %", "shots": "Shots", "shots_on_target": "Shots on Target", "red_cards": "Red Cards", "yellow_cards": "Yellow Cards"}
        for key, label in stat_labels.items():
            if key in stats:
                h_val = stats[key].get("home", "?")
                a_val = stats[key].get("away", "?")
                html += f'<tr><td>{label}</td><td style="text-align:right">{h_val}</td><td style="text-align:center;color:#5a6068">vs</td><td>{a_val}</td></tr>'
        html += '</table></div></div>'
    
    # AI Insights
    if review.get("ai_insights"):
        insights = review["ai_insights"]
        html += '<div class="section"><h2>🤖 AI Analysis</h2>'
        html += '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:16px">'
        
        if insights.get("what_to_watch"):
            html += f'<div class="card"><h3 style="color:#ff6b35;margin-bottom:10px">👀 What Caught Our Eye</h3><p style="color:#d0d0d0;line-height:1.7">{insights["what_to_watch"]}</p></div>'
        
        if insights.get("key_takeaways"):
            html += f'<div class="card"><h3 style="color:#00d4aa;margin-bottom:10px">💡 Key Takeaways</h3><p style="color:#d0d0d0;line-height:1.7">{insights["key_takeaways"]}</p></div>'
        
        if insights.get("tactical_note"):
            html += f'<div class="card"><h3 style="color:#ffaa00;margin-bottom:10px">🎯 Tactical Note</h3><p style="color:#d0d0d0;line-height:1.7">{insights["tactical_note"]}</p></div>'
        
        html += '</div></div>'
    
    # Retrospective Predictions
    retro = review.get("retrospective_predictions")
    if retro and retro.get("models"):
        html += '<div class="section"><h2>🔮 What Our Models Would Have Predicted</h2>'
        html += f'<p style="color:#a0a8b0;margin-bottom:16px;font-size:.9rem">{retro.get("note", "")}</p>'
        html += '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(350px,1fr));gap:16px">'
        
        for mp in retro["models"]:
            conf = mp.get("confidence", 0.5)
            conf_pct = int(conf * 100)
            
            html += f'<div class="card" style="border-left:3px solid #ff6b35">'
            html += f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">'
            html += f'<h4 style="color:#ff6b35;font-size:1rem">{mp["display"]}</h4>'
            html += f'<span style="font-size:.75rem;color:#a0a8b0">{conf_pct}% confidence</span>'
            html += '</div>'
            html += f'<div style="font-size:2rem;font-weight:800;margin:8px 0;color:#fff;text-align:center">{mp["predicted_score"]}</div>'
            html += f'<p style="color:#d0d0d0;line-height:1.7;font-size:.92rem;margin:10px 0">{mp["reasoning"]}</p>'
            
            if mp.get("key_factors"):
                html += '<div style="display:flex;flex-wrap:wrap;gap:6px;margin-top:8px">'
                for kf in mp["key_factors"]:
                    html += f'<span class="pred-factor">{kf}</span>'
                html += '</div>'
            
            if mp.get("player_to_watch"):
                html += f'<div style="margin:10px 0 4px;font-size:.85rem"><strong style="color:#00d4aa">⭐ {mp["player_to_watch"]}</strong></div>'
            
            if mp.get("what_we_got_right") or mp.get("what_we_missed"):
                html += '<div style="margin-top:12px;padding-top:10px;border-top:1px solid #1e2530;font-size:.82rem">'
                if mp.get("what_we_got_right"):
                    html += f'<div style="margin:4px 0"><span style="color:#00d4aa">✅</span> {mp["what_we_got_right"]}</div>'
                if mp.get("what_we_missed"):
                    html += f'<div style="margin:4px 0"><span style="color:#ff6b35">❌</span> {mp["what_we_missed"]}</div>'
                html += '</div>'
            
            html += '</div>'
        
        html += '</div></div>'
    
    # Tactical Breakdown
    if review.get("tactical_breakdown"):
        html += f'<div class="section"><h2>⚽ Tactical Breakdown</h2><div class="card"><p style="color:#d0d0d0;line-height:1.8">{review["tactical_breakdown"]}</p></div></div>'
    
    # Sources
    if review.get("sources"):
        html += '<div class="section"><h2>📚 Sources</h2><div class="card"><ul style="color:#a0a8b0;padding-left:20px">'
        for src in review["sources"]:
            html += f'<li style="margin:4px 0">{src}</li>'
        html += '</ul></div></div>'
    
    html += '</div>'
    html += page_footer()
    return html

# ═══════════════════════════════════════════
# SEO GENERATORS
# ═══════════════════════════════════════════

def gen_sitemap(matches_data, reviews_data):
    """Generate sitemap.xml with all pages."""
    site_url = "https://wc2026.ehabkhedr.com"
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    
    urls = []
    # Home
    urls.append((f"{site_url}/", "daily", "1.0"))
    # Section indexes
    urls.append((f"{site_url}/matches/", "daily", "0.9"))
    urls.append((f"{site_url}/groups/", "daily", "0.8"))
    urls.append((f"{site_url}/predictions/", "hourly", "0.9"))
    urls.append((f"{site_url}/models/", "weekly", "0.7"))
    urls.append((f"{site_url}/reviews/", "daily", "0.9"))
    
    # Individual match pages
    for m in matches_data["matches"]:
        priority = "0.8" if m["status"] == "live" else ("0.7" if m["status"] == "completed" else "0.6")
        urls.append((f"{site_url}/matches/{m['id']}.html", "daily", priority))
    
    # Review pages
    for mid in reviews_data.get("reviews", {}):
        urls.append((f"{site_url}/reviews/{mid}.html", "weekly", "0.7"))
    
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for url, freq, pri in urls:
        xml += f'  <url>\n    <loc>{url}</loc>\n    <lastmod>{today}</lastmod>\n    <changefreq>{freq}</changefreq>\n    <priority>{pri}</priority>\n  </url>\n'
    xml += '</urlset>\n'
    return xml

def gen_robots():
    """Generate robots.txt."""
    return """# WC2026 AI Predictions — robots.txt
# Allow all crawlers, point to sitemap

User-agent: *
Allow: /
Disallow: /cdn-cgi/

# AI crawlers — explicitly welcome
User-agent: GPTBot
Allow: /

User-agent: ChatGPT-User
Allow: /

User-agent: Google-Extended
Allow: /

User-agent: anthropic-ai
Allow: /

User-agent: Claude-Web
Allow: /

User-agent: PerplexityBot
Allow: /

User-agent: cohere-ai
Allow: /

# Sitemaps
Sitemap: https://wc2026.ehabkhedr.com/sitemap.xml

# Crawl-delay — be gentle
Crawl-delay: 5
"""

def gen_llms_txt(matches_data, reviews_data):
    """Generate llms.txt — AI-crawler readable site index in markdown."""
    site_url = "https://wc2026.ehabkhedr.com"
    lines = [
        f"# WC2026 AI Predictions",
        f"> Real-time World Cup 2026 predictions from 10 AI models — match forecasts, live scores, and AI-driven match reviews.",
        f"",
        f"## Site Structure",
        f"- [Home]({site_url}/): Live scores, upcoming matches, recent results, AI models overview",
        f"- [Matches]({site_url}/matches/): All 72 group stage matches with predictions",
        f"- [Groups]({site_url}/groups/): Group standings for all 12 groups (A-L)",
        f"- [Predictions]({site_url}/predictions/): Browse all AI predictions by match",
        f"- [Models]({site_url}/models/): The 10 AI models making predictions (6 automated, 4 manual)",
        f"- [Reviews]({site_url}/reviews/): In-depth AI match reviews with tactical analysis and prediction accuracy",
        f"",
        f"## Quick Links",
    ]
    
    # Add individual match links
    completed = [m for m in matches_data["matches"] if m["status"] == "completed"]
    upcoming = [m for m in matches_data["matches"] if m["status"] in ("upcoming", "live")]
    
    lines.append("### Recent Results")
    for m in completed[-10:]:
        lines.append(f"- [{m['home_team']} {m['home_score']}-{m['away_score']} {m['away_team']}]({site_url}/matches/{m['id']}.html) — {m['date']} ({m.get('stadium','')})")
    
    lines.append("")
    lines.append("### Upcoming Matches")
    for m in upcoming[:10]:
        lines.append(f"- [{m['home_team']} vs {m['away_team']}]({site_url}/matches/{m['id']}.html) — {m['date']} {m.get('time_et','')} ET ({m.get('stadium','')})")
    
    lines.append("")
    lines.append("### Match Reviews")
    for mid in list(reviews_data.get("reviews", {}).keys()):
        lines.append(f"- [Review: {mid}]({site_url}/reviews/{mid}.html)")
    
    lines.append("")
    lines.append("## For AI Agents")
    lines.append(f"- Full content dump: [{site_url}/llms-full.txt]({site_url}/llms-full.txt)")
    lines.append(f"- Sitemap: [{site_url}/sitemap.xml]({site_url}/sitemap.xml)")
    lines.append(f"- Built by EKF Open AI Research · {matches_data['meta'].get('last_updated', '2026')}")
    
    return "\n".join(lines)

def gen_llms_full(matches_data, groups_data, predictions_data, reviews_data):
    """Generate llms-full.txt — complete site content for AI training."""
    site_url = "https://wc2026.ehabkhedr.com"
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    
    lines = [
        f"# WC2026 AI Predictions — Full Content",
        f"Generated: {today}",
        f"URL: {site_url}",
        f"",
        f"## TOURNAMENT OVERVIEW",
        f"72 matches · 48 teams · 10 AI models · Group Stage (A-L)",
        f"",
    ]
    
    # All matches with results
    lines.append("## ALL MATCHES")
    for m in matches_data["matches"]:
        score = f"{m.get('home_score','?')}-{m.get('away_score','?')}" if m["status"] == "completed" else "vs"
        lines.append(f"{m['id']}: {m['home_team']} {score} {m['away_team']} | {m['date']} | Group {m['group']} | {m['status']} | {m.get('stadium','')}, {m.get('city','')}")
    
    # Group standings
    lines.append("")
    lines.append("## GROUP STANDINGS")
    groups = groups_data.get("groups", {})
    for group_id in sorted(groups.keys()):
        group = groups[group_id]
        lines.append(f"\n### Group {group_id}")
        standings = group.get("standings", group.get("teams", []))
        for team in standings:
            name = team.get("name", team.get("team", "?"))
            lines.append(f"  {team.get('position', team.get('pos', '?'))}. {name} | P:{team.get('played',0)} | W:{team.get('won',0)} | D:{team.get('drawn',0)} | L:{team.get('lost',0)} | GF:{team.get('goals_for',0)} | GA:{team.get('goals_against',0)} | Pts:{team.get('points',0)}")
    
    # Models
    lines.append("")
    lines.append("## AI MODELS")
    for model in predictions_data.get("models", []):
        lines.append(f"- {model['display']} ({model['type']}) — Agent: {model['agent']}")
    
    # Reviews
    lines.append("")
    lines.append("## MATCH REVIEWS")
    for mid, review in reviews_data.get("reviews", {}).items():
        lines.append(f"\\n### {mid}: {review.get('headline', '')}")
        lines.append(f"{review.get('summary', '')[:500]}")
        lines.append(f"Rating: {review.get('rating', 'N/A')}")
    
    return "\n".join(lines)

def gen_headers():
    """Generate _headers file for Cloudflare Pages caching rules."""
    return """# WC2026 AI — Cloudflare Pages Headers
# Cache static assets aggressively, HTML moderately

/*.html
  Cache-Control: public, max-age=300, s-maxage=600, stale-while-revalidate=3600
  X-Content-Type-Options: nosniff
  X-Frame-Options: SAMEORIGIN
  X-XSS-Protection: 1; mode=block
  Referrer-Policy: strict-origin-when-cross-origin

/sitemap.xml
  Cache-Control: public, max-age=3600

/robots.txt
  Cache-Control: public, max-age=86400

/llms.txt
  Cache-Control: public, max-age=3600

/llms-full.txt
  Cache-Control: public, max-age=3600

/*.json
  Cache-Control: public, max-age=300

/*.svg
  Cache-Control: public, max-age=2592000, immutable

/*
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
"""

def main():
    print("Loading data...")
    matches_data, groups_data, predictions_data = load_data()
    reviews_data = load_reviews()
    
    print("Generating index.html...")
    write_html(os.path.join(OUTPUT_DIR, "index.html"), gen_index(matches_data, groups_data, predictions_data))
    
    print("Generating matches/index.html...")
    write_html(os.path.join(OUTPUT_DIR, "matches", "index.html"), gen_matches_index(matches_data))
    
    print("Generating individual match pages...")
    for m in matches_data["matches"]:
        write_html(os.path.join(OUTPUT_DIR, "matches", f'{m["id"]}.html'), gen_match_page(m, predictions_data))
    
    print("Generating groups/index.html...")
    write_html(os.path.join(OUTPUT_DIR, "groups", "index.html"), gen_groups_index(groups_data))
    
    print("Generating predictions/index.html...")
    write_html(os.path.join(OUTPUT_DIR, "predictions", "index.html"), gen_predictions_index(predictions_data, matches_data))
    
    print("Generating models/index.html...")
    write_html(os.path.join(OUTPUT_DIR, "models", "index.html"), gen_models_index(predictions_data))
    
    print("Generating reviews/index.html...")
    write_html(os.path.join(OUTPUT_DIR, "reviews", "index.html"), gen_reviews_index(reviews_data, matches_data))
    
    print("Generating individual review pages...")
    match_map = {m["id"]: m for m in matches_data["matches"]}
    reviews = reviews_data.get("reviews", {})
    review_count = 0
    for mid, review in reviews.items():
        m = match_map.get(mid)
        if m and m.get("status") == "completed":
            write_html(os.path.join(OUTPUT_DIR, "reviews", f'{mid}.html'), gen_review_page(m, review, matches_data, predictions_data))
            review_count += 1
    print(f"  Generated {review_count} review pages")
    
    # ── SEO Files ──
    print("Generating sitemap.xml...")
    write_html(os.path.join(OUTPUT_DIR, "sitemap.xml"), gen_sitemap(matches_data, reviews_data))
    
    print("Generating robots.txt...")
    write_html(os.path.join(OUTPUT_DIR, "robots.txt"), gen_robots())
    
    print("Generating llms.txt...")
    write_html(os.path.join(OUTPUT_DIR, "llms.txt"), gen_llms_txt(matches_data, reviews_data))
    
    print("Generating llms-full.txt...")
    write_html(os.path.join(OUTPUT_DIR, "llms-full.txt"), gen_llms_full(matches_data, groups_data, predictions_data, reviews_data))
    
    print("Generating _headers...")
    write_html(os.path.join(OUTPUT_DIR, "_headers"), gen_headers())
    
    total_pages = 1 + 1 + len(matches_data["matches"]) + 1 + 1 + 1 + 1 + review_count
    print(f"Done! Generated {total_pages} HTML pages + 5 SEO files in {OUTPUT_DIR}")

if __name__ == "__main__":
    main()

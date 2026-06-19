#!/usr/bin/env python3
"""
World Cup 2026 AI Predictions Site Generator
Reads JSON data files and generates a complete static HTML website.
Python 3 stdlib only — no external dependencies.
"""
import json
import os
import sys
import shutil
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

def slugify(text):
    return text.lower().strip().replace(" ", "-").replace("&", "and").replace(",", "")

def canonical_path(path):
    if path == "/":
        return "/"
    return path if path.endswith("/") else path

def css():
    return """
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#0a0e14;color:#fff;font-family:'Outfit',-apple-system,BlinkMacSystemFont,sans-serif;line-height:1.6}
a{color:#00d4aa;text-decoration:none;transition:color .2s}
a:hover{color:#ff6b35}
.container{max-width:1200px;margin:0 auto;padding:0 20px}
.header{background:#141921;border-bottom:1px solid #1e2530;padding:16px 0;position:sticky;top:0;z-index:100;backdrop-filter:blur(8px);background:rgba(20,25,33,0.9)}
.header .container{display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap}
.logo{font-size:1.5rem;font-weight:800;color:#00d4aa;display:flex;align-items:center;gap:8px}
.nav{display:flex;gap:15px;align-items:center}
.nav a{color:#a0a8b0;font-size:.95rem;font-weight:500;padding:6px 10px;border-radius:6px;transition:all .2s}
.nav a:hover{color:#fff;background:rgba(255,255,255,0.05)}
.nav a.active{color:#00d4aa;background:rgba(0,212,170,0.1);font-weight:600}
.hero{text-align:center;padding:40px 20px}
.hero h1{font-size:2.8rem;margin-bottom:10px;background:linear-gradient(135deg,#00d4aa,#ff6b35);-webkit-background-clip:text;-webkit-text-fill-color:transparent;font-weight:800}
.hero p{color:#a0a8b0;font-size:1.15rem;max-width:600px;margin:0 auto}
.section{padding:30px 0}
.section h2{font-size:1.6rem;margin-bottom:20px;color:#fff;border-left:4px solid #00d4aa;padding-left:12px;font-weight:700}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:18px}
.card{background:#141921;border:1px solid #1e2530;border-radius:12px;padding:20px;transition:transform .2s,border-color .2s,box-shadow .2s;box-shadow:0 4px 6px rgba(0,0,0,0.2)}
.card:hover{transform:translateY(-3px);border-color:#00d4aa;box-shadow:0 8px 16px rgba(0,212,170,0.1)}
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
.footer{background:#141921;border-top:1px solid #1e2530;padding:30px 0;text-align:center}
.footer-links{display:flex;gap:20px;justify-content:center;margin-bottom:12px;flex-wrap:wrap}
.footer-links a{color:#a0a8b0;font-size:.9rem}
.footer p{color:#5a6068;font-size:.8rem;margin-top:8px}
.btn{display:inline-block;padding:10px 24px;border-radius:8px;font-weight:600;transition:transform .2s,background .2s;border:none;cursor:pointer}
.btn-primary{background:#00d4aa;color:#0a0e14}.btn-primary:hover{transform:translateY(-1px);background:#00b894;color:#0a0e14}
.btn-secondary{background:transparent;border:1px solid #00d4aa;color:#00d4aa}.btn-secondary:hover{background:rgba(0,212,170,0.05);transform:translateY(-1px)}
.match-header{text-align:center;padding:20px 0 30px 0}
.match-header h1{font-size:2rem;margin:10px 0}
.match-header .teams{font-size:2.5rem;margin:16px 0;font-weight:800}
.match-header .score{font-size:3rem;display:block;margin:10px 0}
.pred-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(350px,1fr));gap:14px}
.model-badge{display:inline-block;padding:3px 10px;border-radius:12px;font-size:.75rem;margin-bottom:6px}
.model-automated{background:#1a3a2a;color:#00d4aa}
.model-manual{background:#3a2a1a;color:#ffaa00}
.tabs{display:flex;gap:12px;margin-bottom:20px;flex-wrap:wrap}
.tab{padding:8px 18px;border-radius:8px;background:#141921;border:1px solid #1e2530;color:#a0a8b0;cursor:pointer;font-size:.9rem;font-weight:500;transition:all .2s;font-family:inherit}
.tab.active{background:#00d4aa;color:#0a0e14;border-color:#00d4aa;font-weight:600}
.no-pred{text-align:center;padding:30px;color:#5a6068}
.breadcrumbs{font-size:.85rem;color:#a0a8b0;margin-bottom:20px;display:flex;align-items:center;gap:8px}
.breadcrumbs a{color:#a0a8b0}
.breadcrumbs a:hover{color:#00d4aa}
.breadcrumbs .divider{color:#5a6068}
.breadcrumbs .current{color:#00d4aa;font-weight:500}
.newsletter-section{padding:50px 0;background:#0d1117;border-top:1px solid #1e2530;margin-top:40px}
.newsletter-card{background:linear-gradient(135deg,#141921,#0d1117);border:1px solid #1e2530;border-radius:16px;padding:35px;text-align:center;max-width:650px;margin:0 auto}
.newsletter-card h3{font-size:1.6rem;color:#00d4aa;margin-bottom:8px;font-weight:700}
.newsletter-card p{color:#a0a8b0;font-size:1rem;margin-bottom:24px}
.newsletter-form{display:flex;gap:10px;max-width:500px;margin:0 auto}
.newsletter-form input[type="email"]{flex:1;background:#0a0e14;border:1px solid #1e2530;padding:12px 16px;border-radius:8px;color:#fff;font-family:inherit;font-size:.95rem;transition:border-color .2s}
.newsletter-form input[type="email"]:focus{border-color:#00d4aa;outline:none}
.newsletter-message{margin-top:12px;font-size:.9rem;min-height:20px}
.newsletter-message.success{color:#00d4aa}
.newsletter-message.error{color:#ff6b35}
@media(max-width:768px){
  .grid{grid-template-columns:1fr}
  .hero h1{font-size:2rem}
  .match-header .teams{font-size:1.8rem}
  .pred-grid{grid-template-columns:1fr}
  .header .container{flex-direction:column;gap:12px;align-items:center}
  .nav{width:100%;justify-content:center;overflow-x:auto;white-space:nowrap;padding-bottom:4px;scrollbar-width:none}
  .nav::-webkit-scrollbar{display:none}
  .nav a{font-size:.9rem;padding:6px 8px;flex-shrink:0}
}
@media(max-width:480px){
  .newsletter-form{flex-direction:column;gap:8px}
}
</style>
"""

def render_nav(active_nav):
    links = [
        ("/", "Home", "home"),
        ("/matches", "Matches", "matches"),
        ("/groups", "Groups", "groups"),
        ("/predictions", "Predictions", "predictions"),
        ("/accuracy", "Accuracy", "accuracy"),
        ("/today", "Today", "today"),
        ("/reviews", "Reviews", "reviews"),
    ]
    nav_html = []
    for href, label, name in links:
        is_active = active_nav == name
        cls = ' class="active"' if is_active else ''
        nav_html.append(f'<a href="{href}"{cls}>{label}</a>')
    return "\n".join(nav_html)

def render_breadcrumbs(crumbs):
    html = ['<div class="breadcrumbs" aria-label="Breadcrumb">']
    for i, (label, href) in enumerate(crumbs):
        if i > 0:
            html.append('<span class="divider">/</span>')
        if href:
            html.append(f'<a href="{href}">{label}</a>')
        else:
            html.append(f'<span class="current">{label}</span>')
    html.append('</div>')
    return "".join(html)

def gen_breadcrumb_schema(crumbs):
    items = []
    for i, (label, href) in enumerate(crumbs):
        url = "https://wc2026.ehabkhedr.com" + href if href else "https://wc2026.ehabkhedr.com"
        items.append(f'''{{
            "@type": "ListItem",
            "position": {i+1},
            "name": "{label}",
            "item": "{url}"
        }}''')
    return f'''{{
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [{",".join(items)}]
    }}'''

def page_head(title, desc="AI-powered World Cup 2026 predictions from 10 AI models — match forecasts, live scores, and AI match reviews", canonical="", active_nav="", schema_data="", image="https://wc2026.ehabkhedr.com/og-image.jpg"):
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

<!-- Google Fonts -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">

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

<!-- Favicon -->
<link rel="icon" type="image/svg+xml" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>⚽</text></svg>">
<link rel="apple-touch-icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>⚽</text></svg>">

{css()}
</head>
<body>
<div class="header"><div class="container">
<a href="/" class="logo">⚽ WC2026 AI</a>
<nav class="nav" aria-label="Main navigation">
{render_nav(active_nav)}
</nav>
</div></div>
"""

def page_footer():
    return """
<div class="newsletter-section">
  <div class="container">
    <div class="newsletter-card">
      <h3>📬 World Cup AI Predictions Newsletter</h3>
      <p>Get daily match research, prediction audits, and tactical reviews sent to your inbox.</p>
      <form id="newsletter-form" class="newsletter-form">
        <input type="email" id="newsletter-email" name="email" placeholder="Enter your email address" required />
        <button type="submit" class="btn btn-primary">Subscribe</button>
      </form>
      <div id="newsletter-message" class="newsletter-message"></div>
    </div>
  </div>
</div>

<footer class="footer"><div class="container">
<nav class="footer-links" aria-label="Footer navigation">
<a href="/">Home</a>
<a href="/matches">Matches</a>
<a href="/groups">Groups</a>
<a href="/predictions">Predictions</a>
<a href="/accuracy">Accuracy</a>
<a href="/models">Models</a>
<a href="/reviews">Reviews</a>
<a href="/sitemap.xml" target="_blank">Sitemap</a>
<a href="/llms.txt" target="_blank">AI Agents</a>
<a href="https://redbubble.com/shop/pixelsilkstore?utm_source=wc2026site&utm_medium=footer" target="_blank" rel="noopener">🛍️ Merch</a>
<a href="https://ehabkhedr.com?utm_source=wc2026site&utm_medium=footer" target="_blank" rel="noopener">🌐 Ehab Khedr</a>
</nav>
<p>Powered by 10 AI Models · Built by <a href="https://ehabkhedr.com?utm_source=wc2026site&utm_medium=footer">EKF Open AI Research</a> · © 2026 · <a href="https://wc2026.ehabkhedr.com">wc2026.ehabkhedr.com</a></p>
</div></footer>

<script>
// Handle newsletter form submission
document.getElementById("newsletter-form")?.addEventListener("submit", async (e) => {
  e.preventDefault();
  const email = document.getElementById("newsletter-email").value;
  const msgDiv = document.getElementById("newsletter-message");
  msgDiv.textContent = "Submitting...";
  msgDiv.className = "newsletter-message";
  
  // Parse UTM parameters from URL
  const urlParams = new URLSearchParams(window.location.search);
  const utm_source = urlParams.get("utm_source") || "website_inline";
  const utm_medium = urlParams.get("utm_medium") || "organic";
  const utm_campaign = urlParams.get("utm_campaign") || "wc2026_newsletter";
  
  try {
    const res = await fetch("/api/subscribe", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, utm_source, utm_medium, utm_campaign })
    });
    const data = await res.json();
    if (res.ok && data.success) {
      msgDiv.textContent = data.message;
      msgDiv.className = "newsletter-message success";
      document.getElementById("newsletter-email").value = "";
    } else {
      msgDiv.textContent = data.error || "Subscription failed. Please try again.";
      msgDiv.className = "newsletter-message error";
    }
  } catch (err) {
    msgDiv.textContent = "An error occurred. Please try again.";
    msgDiv.className = "newsletter-message error";
  }
});
</script>
</body></html>
"""

def match_card(m):
    flag_h = get_flag(m["home_team"])
    flag_a = get_flag(m["away_team"])
    score = score_display(m)
    sl = status_label(m["status"])
    sc = status_class(m["status"])
    return f'''<a href="/matches/{m["id"]}" class="card match-card" style="text-decoration:none;color:inherit">
<div><span class="status-badge {sc}">{sl}</span></div>
<div class="match-teams">
<div class="team"><span class="team-flag">{flag_h}</span><span>{m["home_team"]}</span></div>
<div class="score">{score}</div>
<div class="team"><span>{m["away_team"]}</span><span class="team-flag">{flag_a}</span></div>
</div>
<div class="match-meta">📅 {m["date"]} · ⏰ {m["time_et"]} ET · 🏟️ {m["stadium"]}, {m["city"]}</div>
<div class="match-meta">Group {m["group"]}</div>
</a>'''

def gen_index(matches_data, groups_data, predictions_data):
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    matches = matches_data["matches"]
    today_matches = [m for m in matches if m["date"] == today]
    live_matches = [m for m in matches if m["status"] == "live"]
    upcoming = [m for m in matches if m["status"] == "upcoming"][:6]
    completed = [m for m in matches if m["status"] == "completed"]
    
    html = page_head("World Cup 2026 AI Predictions", "Real-time AI predictions from 10 models for every World Cup 2026 match", canonical="/", active_nav="home")
    html += '<div class="container">'
    html += '<div class="hero"><h1>World Cup 2026 AI Predictions</h1>'
    html += f'<p>{len(matches)} matches · 48 teams · 10 AI models · Real-time predictions</p>'
    html += '''
    <div style="text-align:center;margin:30px 0 20px 0">
        <img src="/og-image.jpg" alt="WC2026 AI Predictions Dashboard" style="max-width:100%;width:750px;border-radius:16px;border:1px solid rgba(0,212,170,0.3);box-shadow:0 15px 30px rgba(0,212,170,0.15);transition:transform 0.3s ease,box-shadow 0.3s ease;" onmouseover="this.style.transform='scale(1.015)';this.style.boxShadow='0 20px 40px rgba(0,212,170,0.25)'" onmouseout="this.style.transform='scale(1)';this.style.boxShadow='0 15px 30px rgba(0,212,170,0.15)'" />
    </div>
    '''
    html += '</div>'
    
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

def gen_match_page(m, predictions_data):
    flag_h = get_flag(m["home_team"])
    flag_a = get_flag(m["away_team"])
    title = f"{m['home_team']} vs {m['away_team']} Prediction — World Cup 2026"
    desc = f"AI predictions and statistical probability models for {m['home_team']} vs {m['away_team']} on {m['date']}, World Cup 2026 Group {m['group']}"
    
    crumbs = [("Home", "/"), ("Matches", "/matches"), (f"{m['home_team']} vs {m['away_team']}", "")]
    breadcrumb_html = render_breadcrumbs(crumbs)
    
    schema_data = gen_match_schema(m)
    
    html = page_head(title, desc, canonical=f"/matches/{m['id']}", active_nav="matches", schema_data=schema_data)
    html += '<div class="container">'
    html += breadcrumb_html
    
    # Match header
    html += '<div class="match-header">'
    html += f'<div><span class="status-badge {status_class(m["status"])}">{status_label(m["status"])}</span></div>'
    html += f'<div class="teams">{flag_h} {m["home_team"]} <span style="color:#a0a8b0">vs</span> {m["away_team"]} {flag_a}</div>'
    html += f'<h1 style="font-size:1.4rem;color:#a0a8b0;margin-top:-8px;font-weight:400">{m["home_team"]} vs {m["away_team"]} AI Match Predictions & Odds</h1>'
    if m["status"] == "completed":
        html += f'<div class="score" style="margin-top:10px">{m["home_score"]} - {m["away_score"]}</div>'
    elif m["status"] == "live":
        html += f'<div class="score" style="margin-top:10px">{m.get("home_score","?")} - {m.get("away_score","?")}</div>'
    else:
        html += '<div class="score" style="margin-top:10px">vs</div>'
    html += f'<div class="match-meta">📅 {m["date"]} · ⏰ {m["time_et"]} ET · 🏟️ {m["stadium"]}, {m["city"]}</div>'
    html += f'<div class="match-meta">Group {m["group"]} · {m["stage"]}</div>'
    
    # Links to Teams Profile Pages
    home_slug = slugify(m["home_team"])
    away_slug = slugify(m["away_team"])
    html += f'<div style="margin-top:15px;font-size:.9rem">'
    html += f'Explore Team Profile: <a href="/teams/{home_slug}">{flag_h} {m["home_team"]}</a> · '
    html += f'<a href="/teams/{away_slug}">{flag_a} {m["away_team"]}</a>'
    html += '</div>'
    html += '</div>'
    
    # Predictions
    match_preds = predictions_data.get("predictions", {}).get(m["id"], {})
    models_list = predictions_data.get("models", [])
    
    # Check if we have predictions for this match
    has_predictions = bool(match_preds) and any(not k.startswith("_") for k in match_preds)
    
    if has_predictions:
        html += '<div class="section"><h2>🤖 AI Predictions</h2>'
        html += '<div class="pred-grid">'
        for model in models_list:
            pred_raw = match_preds.get(model["id"])
            if pred_raw:
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
    
    # Merch CTA & Lead Hooks
    html += f'''<div class="section" style="text-align:center;background:rgba(20,25,33,0.5);padding:30px;border-radius:12px;border:1px solid #1e2530;margin-top:20px">
    <h3 style="margin-bottom:8px">⚽ Support Your Team</h3>
    <p style="color:#a0a8b0;margin-bottom:20px;font-size:.95rem">Get premium {m["home_team"]} and {m["away_team"]} merchandise on Pixel Silk.</p>
    <a href="https://redbubble.com/shop/pixelsilkstore?utm_source=wc2026site&utm_medium=match_{m["id"]}" class="btn btn-primary" target="_blank">🛍️ Shop World Cup Merch</a> 
    </div>'''
    
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
    html = page_head("All Matches — World Cup 2026", "Complete World Cup 2026 match schedule, groups, and AI-powered prediction list", canonical="/matches", active_nav="matches")
    html += '<div class="container"><div class="section">'
    html += '<h1>World Cup 2026 Matches</h1>'
    html += '<p style="color:#a0a8b0;margin-bottom:20px">Browse all 72 group stage matches with dynamic forecasts and live score updates.</p>'
    html += '<div class="tabs" role="tablist">'
    html += '<button type="button" class="tab active" role="tab" aria-selected="true" onclick="filterMatches(this, \'all\')">All</button>'
    html += '<button type="button" class="tab" role="tab" aria-selected="false" onclick="filterMatches(this, \'completed\')">Completed</button>'
    html += '<button type="button" class="tab" role="tab" aria-selected="false" onclick="filterMatches(this, \'live\')">Live</button>'
    html += '<button type="button" class="tab" role="tab" aria-selected="false" onclick="filterMatches(this, \'upcoming\')">Upcoming</button>'
    html += '</div>'
    html += '<div class="grid" id="matches-grid">'
    for m in matches_data["matches"]:
        html += match_card(m)
    html += '</div></div></div>'
    html += '<script>'
    html += 'function filterMatches(btn, status){'
    html += 'const cards=document.querySelectorAll("#matches-grid .match-card");'
    html += 'cards.forEach(c=>{c.style.display=(status==="all"||c.querySelector(".status-badge").classList.contains("status-"+status))?"block":"none"});'
    html += 'document.querySelectorAll(".tab").forEach(t=>{t.classList.remove("active"); t.setAttribute("aria-selected", "false");});'
    html += 'btn.classList.add("active"); btn.setAttribute("aria-selected", "true");}'
    html += '</script>'
    html += page_footer()
    return html

def gen_groups_index(groups_data):
    html = page_head("Groups Standings — World Cup 2026", "World Cup 2026 group standings, live points, and team profiles for all 12 groups", canonical="/groups", active_nav="groups")
    html += '<div class="container"><div class="section">'
    html += '<h1>World Cup 2026 Group Standings</h1>'
    html += '<p style="color:#a0a8b0;margin-bottom:20px">Check standings for Groups A-L and click on any team to explore their custom AI profile.</p>'
    html += '<div class="grid">'
    for group_id in sorted(groups_data["groups"].keys()):
        g = groups_data["groups"][group_id]
        html += f'<div class="card">'
        html += f'<h3 style="color:#00d4aa;margin-bottom:12px;display:flex;justify-content:space-between;align-items:center">'
        html += f'<span>Group {group_id}</span>'
        html += f'<a href="/groups/group-{group_id.lower()}" style="font-size:.8rem;font-weight:400">View Details &rarr;</a>'
        html += '</h3>'
        html += '<table class="standings"><tr><th>#</th><th>Team</th><th>MP</th><th>GD</th><th>Pts</th></tr>'
        for i, s in enumerate(g["standings"], 1):
            team_slug = slugify(s["team"])
            html += f'<tr><td class="pos">{i}</td><td><a href="/teams/{team_slug}">{get_flag(s["team"])} {s["team"]}</a></td><td>{s["MP"]}</td><td>{s["GD"]:+d}</td><td><strong>{s["Pts"]}</strong></td></tr>'
        html += '</table></div>'
    html += '</div></div></div>'
    html += page_footer()
    return html

def gen_predictions_index(predictions_data, matches_data):
    html = page_head("AI Predictions List — World Cup 2026", "Browse 10 model predictions for every upcoming and finished World Cup match", canonical="/predictions", active_nav="predictions")
    html += '<div class="container"><div class="section">'
    html += '<h1>🤖 AI Predictions Dashboard</h1>'
    
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
        html += f'<p style="color:#a0a8b0;margin-bottom:20px">{len(matches_with_preds)} matches with active predictions · {sum(pc for _, pc in matches_with_preds)} forecasts generated from {len(models_list)} AI agents</p>'
        html += '<div class="grid">'
        for m, pred_count in matches_with_preds:
            score = f'{m.get("home_score","?")}-{m.get("away_score","?")}' if m["status"] == "completed" else "vs"
            html += f'''<a href="/matches/{m["id"]}" class="card match-card" style="display:block;text-decoration:none;color:#fff">
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
        model_count = sum(1 for mid in predictions if not mid.startswith("_") and model["id"] in predictions[mid])
        html += f'<div class="card"><span class="model-badge {badge}">{model["type"].upper()}</span><h3>{model["display"]}</h3><p style="color:#a0a8b0;font-size:.85rem;margin-top:6px">Agent: {model["agent"]}</p><div style="margin-top:8px;font-size:.85rem;color:#00d4aa">Total Predictions: {model_count}</div></div>'
    html += '</div></div></div>'
    html += page_footer()
    return html

def gen_models_index(predictions_data):
    html = page_head("AI Models Directory — World Cup 2026", "Meet the 10 AI models making World Cup predictions", canonical="/models", active_nav="models")
    html += '<div class="container"><div class="section">'
    html += '<h1>10 AI Models Making Predictions</h1>'
    html += '<p style="color:#a0a8b0;margin-bottom:20px">Our suite merges automated, real-time agent models with human-curated strategic predictions.</p>'
    html += '<div class="grid">'
    for model in predictions_data.get("models", []):
        badge = "model-automated" if model["type"] == "automated" else "model-manual"
        html += f'<div class="card"><span class="model-badge {badge}">{model["type"].upper()}</span><h3>{model["display"]}</h3><p style="color:#a0a8b0;font-size:.85rem;margin-top:6px">Agent: {model["agent"]}</p></div>'
    html += '</div></div></div>'
    html += page_footer()
    return html

def gen_reviews_index(reviews_data, matches_data):
    html = page_head("AI Match Reviews — World Cup 2026", "In-depth AI-powered analysis and tactical breakdown of every completed match", canonical="/reviews", active_nav="reviews")
    html += '<div class="container"><div class="section">'
    html += '<h1>🔍 AI Match Reviews</h1>'
    html += '<p style="color:#a0a8b0;margin-bottom:20px">Deep analysis combining match research, tactical breakdown, and AI prediction accuracy audit for completed matches.</p>'
    
    match_map = {m["id"]: m for m in matches_data["matches"]}
    reviews = reviews_data.get("reviews", {})
    
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
    html += f'<div class="card" style="text-align:center;min-width:120px"><div style="font-size:2rem;color:#ff6b35;font-weight:800">{researched}</div><div style="color:#a0a8b0;font-size:.85rem">Deep Research Reviews</div></div>'
    html += '</div>'
    
    if not reviewed_matches:
        html += '<div class="no-pred">No reviews yet. Check back after matches are completed!</div>'
    else:
        html += '<div class="grid">'
        for m, review in reviewed_matches:
            rating = review.get("rating", "")
            headline = review.get("headline", f'{m["home_team"]} vs {m["away_team"]}')
            html += f'''<a href="/reviews/{m["id"]}" class="card match-card" style="display:block;text-decoration:none;color:#fff">
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
    mid = m["id"]
    headline = review.get("headline", f'{m["home_team"]} vs {m["away_team"]}')
    
    crumbs = [("Home", "/"), ("Reviews", "/reviews"), (f"{m['home_team']} vs {m['away_team']}", "")]
    breadcrumb_html = render_breadcrumbs(crumbs)
    
    schema_data = gen_review_schema(m, review)
    
    html = page_head(f'Review: {m["home_team"]} {m["home_score"]}-{m["away_score"]} {m["away_team"]} — WC2026 AI', review.get("summary", "")[:160], canonical=f"/reviews/{mid}", active_nav="reviews", schema_data=schema_data)
    
    html += f'''<div class="container">
    {breadcrumb_html}
    <div class="match-header">
        <div style="color:#a0a8b0;font-size:.9rem">{m["date"]} · {m.get("stadium", "")}, {m.get("city", "")} · Group {m["group"]}</div>
        <div class="teams"><span class="team-flag" style="font-size:3rem">{get_flag(m["home_team"])}</span> {m["home_team"]} <span class="score">{m["home_score"]} - {m["away_score"]}</span> {m["away_team"]} <span class="team-flag" style="font-size:3rem">{get_flag(m["away_team"])}</span></div>
        <h1 style="font-size:1.5rem;max-width:700px;margin:12px auto;color:#fff">{headline}</h1>
        {f'<div style="color:#ffaa00;font-size:1.2rem">Rating: {review.get("rating", "")}</div>' if review.get("rating") else ""}
    </div>'''
    
    if review.get("summary"):
        html += f'<div class="section"><h2>📝 Match Summary</h2><div class="card"><p style="color:#d0d0d0;line-height:1.8;font-size:1.05rem">{review["summary"]}</p></div></div>'
    
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
    
    if review.get("tactical_breakdown"):
        html += f'<div class="section"><h2>⚽ Tactical Breakdown</h2><div class="card"><p style="color:#d0d0d0;line-height:1.8">{review["tactical_breakdown"]}</p></div></div>'
    
    if review.get("sources"):
        html += '<div class="section"><h2>📚 Sources</h2><div class="card"><ul style="color:#a0a8b0;padding-left:20px">'
        for src in review["sources"]:
            html += f'<li style="margin:4px 0">{src}</li>'
        html += '</ul></div></div>'
    
    html += '</div>'
    html += page_footer()
    return html

# ═══════════════════════════════════════════
# NEW GENERATORS & HELPERS
# ═══════════════════════════════════════════

def gen_match_schema(m):
    home_team = m["home_team"]
    away_team = m["away_team"]
    start_date = f'{m["date"]}T{m.get("time_et","12:00")}:00-04:00'
    stadium = m.get("stadium", "World Cup Stadium")
    city = m.get("city", "USA")
    
    score_data = ""
    if m["status"] == "completed":
        score_data = f''',
        "sportEventOutputs": {{
          "@type": "SportEventModel",
          "homeTeamScore": {m["home_score"]},
          "awayTeamScore": {m["away_score"]}
        }}'''
        
    return f'''{{
      "@context": "https://schema.org",
      "@type": "SportsEvent",
      "name": "{home_team} vs {away_team} — World Cup 2026",
      "startDate": "{start_date}",
      "location": {{
        "@type": "Place",
        "name": "{stadium}",
        "address": {{
          "@type": "PostalAddress",
          "addressLocality": "{city}",
          "addressCountry": "{m.get("country", "USA")}"
        }}
      }},
      "competitor": [
        {{
          "@type": "SportsTeam",
          "name": "{home_team}",
          "logo": "https://wc2026.ehabkhedr.com/og-image.jpg"
        }},
        {{
          "@type": "SportsTeam",
          "name": "{away_team}",
          "logo": "https://wc2026.ehabkhedr.com/og-image.jpg"
        }}
      ]{score_data}
    }}'''

def gen_review_schema(m, review):
    headline = review.get("headline", "").replace('"', '\\"')
    summary = review.get("summary", "").replace('"', '\\"')
    rating_val = 3.5
    rating_str = review.get("rating", "")
    if rating_str:
        rating_val = rating_str.count("⭐") + (0.5 if "½" in rating_str else 0)
        
    return f'''{{
      "@context": "https://schema.org",
      "@type": "Review",
      "headline": "{headline}",
      "description": "{summary}",
      "itemReviewed": {{
        "@type": "SportsEvent",
        "name": "{m["home_team"]} vs {m["away_team"]} — World Cup 2026",
        "startDate": "{m["date"]}"
      }},
      "reviewRating": {{
        "@type": "Rating",
        "ratingValue": {rating_val},
        "bestRating": 5,
        "worstRating": 1
      }},
      "author": {{
        "@type": "Organization",
        "name": "EKF Open AI Research",
        "url": "https://ehabkhedr.com"
      }}
    }}'''

def compute_model_accuracy(matches_data, predictions_data):
    models_stats = {}
    models_list = predictions_data.get("models", [])
    predictions = predictions_data.get("predictions", {})
    
    # Initialize
    for model in models_list:
        models_stats[model["id"]] = {
            "id": model["id"],
            "display": model["display"],
            "type": model["type"],
            "agent": model["agent"],
            "total_predicted": 0,
            "correct_outcome": 0,
            "exact_scores": 0,
            "sum_goal_diff_error": 0.0,
            "sum_goals_error": 0.0,
        }
    
    match_map = {m["id"]: m for m in matches_data["matches"]}
    
    for mid, match_preds in predictions.items():
        if mid.startswith("_"):
            continue
        match = match_map.get(mid)
        if not match or match["status"] != "completed":
            continue
        
        try:
            act_h = int(match["home_score"])
            act_a = int(match["away_score"])
        except (TypeError, ValueError):
            continue
            
        act_diff = act_h - act_a
        if act_diff > 0:
            act_outcome = "home"
        elif act_diff < 0:
            act_outcome = "away"
        else:
            act_outcome = "draw"
            
        for model_id, pred_raw in match_preds.items():
            if model_id not in models_stats:
                continue
            parsed = pred_raw.get("parsed") or {}
            pred_score_str = parsed.get("predicted_score")
            if not pred_score_str or "-" not in pred_score_str:
                continue
                
            try:
                pred_h, pred_a = map(int, pred_score_str.split("-"))
              # If pred_score is parsed incorrectly but we have values
            except (ValueError, TypeError):
                continue
                
            stats = models_stats[model_id]
            stats["total_predicted"] += 1
            
            # Exact score check
            if pred_h == act_h and pred_a == act_a:
                stats["exact_scores"] += 1
                
            # Outcome check
            pred_diff = pred_h - pred_a
            if pred_diff > 0:
                pred_outcome = "home"
            elif pred_diff < 0:
                pred_outcome = "away"
            else:
                pred_outcome = "draw"
                
            if pred_outcome == act_outcome:
                stats["correct_outcome"] += 1
                
            # Errors
            stats["sum_goal_diff_error"] += abs(pred_diff - act_diff)
            stats["sum_goals_error"] += abs(pred_h - act_h) + abs(pred_a - act_a)
            
    leaderboard = []
    for m_id, stats in models_stats.items():
        tot = stats["total_predicted"]
        if tot > 0:
            stats["outcome_accuracy_pct"] = (stats["correct_outcome"] / tot) * 100
            stats["exact_score_accuracy_pct"] = (stats["exact_scores"] / tot) * 100
            stats["avg_goal_diff_error"] = stats["sum_goal_diff_error"] / tot
            stats["avg_goals_error"] = stats["sum_goals_error"] / tot
        else:
            stats["outcome_accuracy_pct"] = 0.0
            stats["exact_score_accuracy_pct"] = 0.0
            stats["avg_goal_diff_error"] = 0.0
            stats["avg_goals_error"] = 0.0
        leaderboard.append(stats)
        
    leaderboard.sort(key=lambda x: (x["outcome_accuracy_pct"], x["exact_score_accuracy_pct"]), reverse=True)
    return leaderboard

def gen_accuracy_page(leaderboard, predictions_data):
    html = page_head("AI Models Accuracy Leaderboard — World Cup 2026", "Compare the prediction accuracy of 10 AI models for the World Cup 2026 matches", canonical="/accuracy", active_nav="accuracy")
    html += '<div class="container"><div class="section">'
    html += '<h1>AI Prediction Models Leaderboard</h1>'
    html += '<p style="color:#a0a8b0;margin-bottom:20px">Real-time auditing of model accuracy. Leaderboard dynamically tracks and ranks all 10 models based on completed match predictions.</p>'
    
    html += '<div class="card" style="overflow-x:auto"><table>'
    html += '<tr><th>Rank</th><th>Model Persona</th><th>Type</th><th>Predicted</th><th>Outcome Accuracy</th><th>Exact Scores</th><th>Avg Goal Diff Error</th></tr>'
    
    for i, stats in enumerate(leaderboard, 1):
        badge = "model-automated" if stats["type"] == "automated" else "model-manual"
        html += f'''<tr>
            <td class="pos">{i}</td>
            <td><strong>{stats["display"]}</strong><br><span style="font-size:.75rem;color:#a0a8b0">Agent: {stats["agent"]}</span></td>
            <td><span class="model-badge {badge}">{stats["type"].upper()}</span></td>
            <td>{stats["total_predicted"]}</td>
            <td style="color:#00d4aa;font-weight:700">{stats["outcome_accuracy_pct"]:.1f}%</td>
            <td>{stats["exact_score_accuracy_pct"]:.1f}% ({stats["exact_scores"]} matches)</td>
            <td>{stats["avg_goal_diff_error"]:.2f} goals</td>
        </tr>'''
        
    html += '</table></div></div></div>'
    html += page_footer()
    return html

def gen_team_pages(matches_data, groups_data, predictions_data):
    teams = set()
    for m in matches_data["matches"]:
        teams.add(m["home_team"])
        teams.add(m["away_team"])
        
    match_map = {m["id"]: m for m in matches_data["matches"]}
    
    for team in sorted(list(teams)):
        team_slug = slugify(team)
        title = f"{team} World Cup 2026 Standings, Predictions & Schedule"
        desc = f"AI predictions, match schedule, and group standings for the {team} national soccer team in the FIFA World Cup 2026"
        
        crumbs = [("Home", "/"), ("Groups", "/groups"), (team, "")]
        breadcrumb_html = render_breadcrumbs(crumbs)
        
        # Find group
        team_group = "N/A"
        team_standings = []
        for g_id, g in groups_data["groups"].items():
            if team in g["teams"]:
                team_group = g_id
                team_standings = g["standings"]
                break
                
        # Find team matches
        team_matches = [m for m in matches_data["matches"] if m["home_team"] == team or m["away_team"] == team]
        
        # Schema
        schema_data = f'''{{
          "@context": "https://schema.org",
          "@type": "SportsTeam",
          "name": "{team}",
          "memberOf": {{
            "@type": "SportsOrganization",
            "name": "FIFA"
          }}
        }}'''
        
        html = page_head(title, desc, canonical=f"/teams/{team_slug}", active_nav="groups", schema_data=schema_data)
        html += '<div class="container">'
        html += breadcrumb_html
        
        html += f'''<div class="match-header">
            <span style="font-size:4rem;display:block">{get_flag(team)}</span>
            <h1>{team} National Team</h1>
            <p style="color:#a0a8b0">World Cup 2026 · Group {team_group}</p>
        </div>'''
        
        # Standings
        html += f'<div class="grid"><div class="card"><h3 style="color:#00d4aa;margin-bottom:12px">Group {team_group} Standings</h3>'
        html += '<table class="standings"><tr><th>#</th><th>Team</th><th>MP</th><th>GD</th><th>Pts</th></tr>'
        for i, s in enumerate(team_standings, 1):
            is_current = "background:rgba(0,212,170,0.1);" if s["team"] == team else ""
            html += f'<tr style="{is_current}"><td class="pos">{i}</td><td>{get_flag(s["team"])} {s["team"]}</td><td>{s["MP"]}</td><td>{s["GD"]:+d}</td><td><strong>{s["Pts"]}</strong></td></tr>'
        html += '</table></div>'
        
        # Matches
        html += f'<div class="card"><h3 style="color:#00d4aa;margin-bottom:12px">{team} Match Schedule</h3>'
        for m in team_matches:
            flag_h = get_flag(m["home_team"])
            flag_a = get_flag(m["away_team"])
            score = score_display(m)
            sc = status_class(m["status"])
            sl = status_label(m["status"])
            
            html += f'''<a href="/matches/{m["id"]}" style="display:block;padding:10px 0;border-bottom:1px solid #1e2530;text-decoration:none;color:#fff">
                <div style="display:flex;justify-content:space-between;align-items:center">
                    <span style="font-size:.8rem;color:#a0a8b0">{m["date"]}</span>
                    <span class="status-badge {sc}" style="font-size:.7rem;padding:1px 6px">{sl}</span>
                </div>
                <div style="display:flex;justify-content:space-between;align-items:center;margin-top:6px">
                    <span>{flag_h} {m["home_team"]}</span>
                    <strong>{score}</strong>
                    <span>{m["away_team"]} {flag_a}</span>
                </div>
            </a>'''
        html += '</div></div></div>'
        html += page_footer()
        
        write_html(os.path.join(OUTPUT_DIR, "teams", f"{team_slug}.html"), html)

def gen_group_pages(matches_data, groups_data):
    for g_id in sorted(groups_data["groups"].keys()):
        g = groups_data["groups"][g_id]
        title = f"Group {g_id} Standings, Matches & Predictions — World Cup 2026"
        desc = f"Complete standings table, schedules, and AI score predictions for World Cup 2026 Group {g_id}"
        
        crumbs = [("Home", "/"), ("Groups", "/groups"), (f"Group {g_id}", "")]
        breadcrumb_html = render_breadcrumbs(crumbs)
        
        # Matches in this group
        group_matches = [m for m in matches_data["matches"] if m["group"] == g_id]
        
        html = page_head(title, desc, canonical=f"/groups/group-{g_id.lower()}", active_nav="groups")
        html += '<div class="container">'
        html += breadcrumb_html
        
        html += f'<div class="match-header"><h1>Group {g_id} Overview</h1></div>'
        
        html += '<div class="grid">'
        # Table
        html += f'<div class="card"><h3 style="color:#00d4aa;margin-bottom:12px">Standings Table</h3>'
        html += '<table class="standings"><tr><th>#</th><th>Team</th><th>MP</th><th>W</th><th>D</th><th>L</th><th>GD</th><th>Pts</th></tr>'
        for i, s in enumerate(g["standings"], 1):
            team_slug = slugify(s["team"])
            html += f'<tr><td class="pos">{i}</td><td><a href="/teams/{team_slug}">{get_flag(s["team"])} {s["team"]}</a></td><td>{s["MP"]}</td><td>{s["W"]}</td><td>{s["D"]}</td><td>{s["L"]}</td><td>{s["GD"]:+d}</td><td><strong>{s["Pts"]}</strong></td></tr>'
        html += '</table></div>'
        
        # Matches
        html += f'<div class="card"><h3 style="color:#00d4aa;margin-bottom:12px">Group Matches</h3>'
        for m in group_matches:
            flag_h = get_flag(m["home_team"])
            flag_a = get_flag(m["away_team"])
            score = score_display(m)
            sc = status_class(m["status"])
            sl = status_label(m["status"])
            
            html += f'''<a href="/matches/{m["id"]}" style="display:block;padding:12px 0;border-bottom:1px solid #1e2530;text-decoration:none;color:#fff">
                <div style="display:flex;justify-content:space-between;align-items:center">
                    <span style="font-size:.8rem;color:#a0a8b0">{m["date"]} · {m["time_et"]} ET</span>
                    <span class="status-badge {sc}" style="font-size:.7rem;padding:1px 6px">{sl}</span>
                </div>
                <div style="display:flex;justify-content:space-between;align-items:center;margin-top:6px">
                    <span>{flag_h} {m["home_team"]}</span>
                    <strong>{score}</strong>
                    <span>{m["away_team"]} {flag_a}</span>
                </div>
            </a>'''
        html += '</div></div></div>'
        html += page_footer()
        
        write_html(os.path.join(OUTPUT_DIR, "groups", f"group-{g_id.lower()}.html"), html)

def gen_today_page(matches_data, reviews_data, predictions_data):
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    matches = matches_data["matches"]
    today_matches = [m for m in matches if m["date"] == today]
    live_matches = [m for m in matches if m["status"] == "live"]
    
    # Map match IDs to matches
    match_map = {m["id"]: m for m in matches}
    reviews = reviews_data.get("reviews", {})
    reviewed_matches = []
    for mid, review in reviews.items():
        m = match_map.get(mid)
        if m and m.get("status") == "completed":
            reviewed_matches.append((m, review))
    reviewed_matches.sort(key=lambda x: x[0].get("date", ""), reverse=True)
    
    html = page_head("Today's World Cup 2026 AI Predictions & Live Scores", "Live scores, match research, and model prediction summaries for matches scheduled today", canonical="/today", active_nav="today")
    html += '<div class="container"><div class="section">'
    html += '<h1>⚽ Today\'s Matchday Hub</h1>'
    html += f'<p style="color:#a0a8b0;margin-bottom:20px">Date: {today} · Tracking live games and AI forecasting updates</p>'
    
    if live_matches:
        html += '<h2>🔴 Live Now</h2><div class="grid" style="margin-bottom:30px">'
        for m in live_matches:
            html += match_card(m)
        html += '</div>'
        
    if today_matches:
        html += '<h2>📅 Today\'s Fixtures</h2><div class="grid" style="margin-bottom:30px">'
        for m in today_matches:
            html += match_card(m)
        html += '</div>'
    else:
        html += '<div class="card" style="text-align:center;padding:30px;color:#a0a8b0;margin-bottom:30px">No matches scheduled for today. Check out the <a href="/tomorrow">Tomorrow</a> tab or browse finished <a href="/reviews">Reviews</a>.</div>'
        
    if reviewed_matches:
        html += '<h2>🔍 Latest Match Reviews</h2><div class="grid">'
        for m, review in reviewed_matches[:3]:
            headline = review.get("headline", f'{m["home_team"]} vs {m["away_team"]}')
            html += f'''<a href="/reviews/{m["id"]}" class="card match-card" style="display:block;text-decoration:none;color:#fff">
                <div style="font-size:.85rem;color:#a0a8b0">{m["date"]} · Group {m["group"]}</div>
                <div class="match-teams">
                    <div class="team"><span class="team-flag">{get_flag(m["home_team"])}</span>{m["home_team"]}</div>
                    <div class="score">{m["home_score"]} - {m["away_score"]}</div>
                    <div class="team">{m["away_team"]}<span class="team-flag">{get_flag(m["away_team"])}</span></div>
                </div>
                <div style="font-weight:600;margin-top:6px;color:#fff">{headline}</div>
            </a>'''
        html += '</div>'
        
    html += '</div></div>'
    html += page_footer()
    return html

def gen_tomorrow_page(matches_data):
    # Calculate tomorrow date
    import datetime as dt
    tomorrow = (datetime.now(timezone.utc) + dt.timedelta(days=1)).strftime("%Y-%m-%d")
    matches = matches_data["matches"]
    tomorrow_matches = [m for m in matches if m["date"] == tomorrow]
    
    html = page_head("Tomorrow's World Cup 2026 AI Predictions & Schedule", "Preview upcoming match schedules and AI prediction percentages for matches tomorrow", canonical="/tomorrow", active_nav="today")
    html += '<div class="container"><div class="section">'
    html += '<h1>📅 Tomorrow\'s Match Previews</h1>'
    html += f'<p style="color:#a0a8b0;margin-bottom:20px">Date: {tomorrow} · AI model consensus forecasting</p>'
    
    if tomorrow_matches:
        html += '<div class="grid">'
        for m in tomorrow_matches:
            html += match_card(m)
        html += '</div>'
    else:
        # Show next 3 upcoming matches instead if none for exactly tomorrow
        upcoming = [m for m in matches if m["status"] == "upcoming"][:3]
        html += '<div class="card" style="text-align:center;padding:30px;color:#a0a8b0;margin-bottom:30px">No matches scheduled for exactly tomorrow. Showing next upcoming matches:</div>'
        html += '<div class="grid">'
        for m in upcoming:
            html += match_card(m)
        html += '</div>'
        
    html += '</div></div>'
    html += page_footer()
    return html

# ═══════════════════════════════════════════
# SEO GENERATORS
# ═══════════════════════════════════════════

def gen_sitemap(matches_data, reviews_data):
    """Generate sitemap.xml with all pages using clean extensionless URLs."""
    site_url = "https://wc2026.ehabkhedr.com"
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    
    urls = []
    # Core pages
    urls.append((f"{site_url}/", "daily", "1.0"))
    urls.append((f"{site_url}/matches", "daily", "0.9"))
    urls.append((f"{site_url}/groups", "daily", "0.8"))
    urls.append((f"{site_url}/predictions", "hourly", "0.9"))
    urls.append((f"{site_url}/models", "weekly", "0.7"))
    urls.append((f"{site_url}/reviews", "daily", "0.9"))
    urls.append((f"{site_url}/accuracy", "hourly", "0.9"))
    urls.append((f"{site_url}/today", "hourly", "0.9"))
    urls.append((f"{site_url}/tomorrow", "daily", "0.8"))
    
    # Teams
    teams = set()
    for m in matches_data["matches"]:
        teams.add(m["home_team"])
        teams.add(m["away_team"])
    for team in sorted(list(teams)):
        urls.append((f"{site_url}/teams/{slugify(team)}", "daily", "0.7"))
        
    # Group detail pages
    for g_id in sorted(groups_data_glob["groups"].keys()):
        urls.append((f"{site_url}/groups/group-{g_id.lower()}", "daily", "0.7"))
    
    # Individual match pages (clean URL)
    for m in matches_data["matches"]:
        priority = "0.8" if m["status"] == "live" else ("0.7" if m["status"] == "completed" else "0.6")
        urls.append((f"{site_url}/matches/{m['id']}", "daily", priority))
    
    # Review pages (clean URL)
    for mid in reviews_data.get("reviews", {}):
        urls.append((f"{site_url}/reviews/{mid}", "weekly", "0.7"))
    
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
        f"- [Matches]({site_url}/matches): All 72 group stage matches with predictions",
        f"- [Groups]({site_url}/groups): Group standings for all 12 groups (A-L) and team profiles",
        f"- [Predictions]({site_url}/predictions): Browse all AI predictions by match",
        f"- [Accuracy]({site_url}/accuracy): Real-time AI prediction accuracy leaderboard",
        f"- [Today]({site_url}/today): Today's live matchday hub",
        f"- [Tomorrow]({site_url}/tomorrow): Tomorrow's fixtures and previews",
        f"- [Models]({site_url}/models): The 10 AI models making predictions (6 automated, 4 manual)",
        f"- [Reviews]({site_url}/reviews): In-depth AI match reviews with tactical analysis and prediction accuracy",
        f"",
        f"## Quick Links",
    ]
    
    # Add individual match links
    completed = [m for m in matches_data["matches"] if m["status"] == "completed"]
    upcoming = [m for m in matches_data["matches"] if m["status"] in ("upcoming", "live")]
    
    lines.append("### Recent Results")
    for m in completed[-10:]:
        lines.append(f"- [{m['home_team']} {m['home_score']}-{m['away_score']} {m['away_team']}]({site_url}/matches/{m['id']}) — {m['date']} ({m.get('stadium','')})")
    
    lines.append("")
    lines.append("### Upcoming Matches")
    for m in upcoming[:10]:
        lines.append(f"- [{m['home_team']} vs {m['away_team']}]({site_url}/matches/{m['id']}) — {m['date']} {m.get('time_et','')} ET ({m.get('stadium','')})")
    
    lines.append("")
    lines.append("### Match Reviews")
    for mid in list(reviews_data.get("reviews", {}).keys()):
        lines.append(f"- [Review: {mid}]({site_url}/reviews/{mid})")
    
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
        lines.append(f"\n### {mid}: {review.get('headline', '')}")
        lines.append(f"{review.get('summary', '')[:500]}")
        lines.append(f"Rating: {review.get('rating', 'N/A')}")
    
    return "\n".join(lines)

def gen_headers():
    """Generate _headers file for Cloudflare Pages caching rules matching extensionless paths."""
    return """# WC2026 AI — Cloudflare Pages Headers
# Cache static assets aggressively, HTML moderately

# Clean / extensionless routes matches
/matches/*
  Cache-Control: public, max-age=300, s-maxage=600, stale-while-revalidate=3600
  X-Content-Type-Options: nosniff
  X-Frame-Options: SAMEORIGIN
  X-XSS-Protection: 1; mode=block
  Referrer-Policy: strict-origin-when-cross-origin

/reviews/*
  Cache-Control: public, max-age=300, s-maxage=600, stale-while-revalidate=3600
  X-Content-Type-Options: nosniff
  X-Frame-Options: SAMEORIGIN
  X-XSS-Protection: 1; mode=block
  Referrer-Policy: strict-origin-when-cross-origin

/teams/*
  Cache-Control: public, max-age=600, s-maxage=1200, stale-while-revalidate=3600
  X-Content-Type-Options: nosniff
  X-Frame-Options: SAMEORIGIN
  X-XSS-Protection: 1; mode=block
  Referrer-Policy: strict-origin-when-cross-origin

/groups/*
  Cache-Control: public, max-age=300, s-maxage=600, stale-while-revalidate=3600
  X-Content-Type-Options: nosniff
  X-Frame-Options: SAMEORIGIN
  X-XSS-Protection: 1; mode=block
  Referrer-Policy: strict-origin-when-cross-origin

/predictions
  Cache-Control: public, max-age=300, s-maxage=600, stale-while-revalidate=3600

/accuracy
  Cache-Control: public, max-age=300, s-maxage=600, stale-while-revalidate=3600

/today
  Cache-Control: public, max-age=300, s-maxage=600, stale-while-revalidate=3600

/tomorrow
  Cache-Control: public, max-age=1800, s-maxage=3600, stale-while-revalidate=7200

# Legacy HTML routes
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

/*.jpg
  Cache-Control: public, max-age=2592000, immutable

/*.png
  Cache-Control: public, max-age=2592000, immutable

/*.svg
  Cache-Control: public, max-age=2592000, immutable

/*
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
"""

# Global storage for sitemap tracking
groups_data_glob = {}

def main():
    global groups_data_glob
    
    print("Loading data...")
    matches_data, groups_data, predictions_data = load_data()
    groups_data_glob = groups_data
    reviews_data = load_reviews()
    
    print("Computing AI prediction models accuracy leaderboard...")
    leaderboard = compute_model_accuracy(matches_data, predictions_data)
    
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
    
    # ── New Pages ──
    print("Generating accuracy leaderboard page...")
    write_html(os.path.join(OUTPUT_DIR, "accuracy.html"), gen_accuracy_page(leaderboard, predictions_data))
    
    print("Generating team profile pages...")
    gen_team_pages(matches_data, groups_data, predictions_data)
    
    print("Generating group detail pages...")
    gen_group_pages(matches_data, groups_data)
    
    print("Generating today's matchday hub...")
    write_html(os.path.join(OUTPUT_DIR, "today.html"), gen_today_page(matches_data, reviews_data, predictions_data))
    
    print("Generating tomorrow's match previews...")
    write_html(os.path.join(OUTPUT_DIR, "tomorrow.html"), gen_tomorrow_page(matches_data))
    
    # Copy default og-image.jpg to output directory
    src_og = os.path.join(BASE, "og-image.jpg")
    dest_og = os.path.join(OUTPUT_DIR, "og-image.jpg")
    if os.path.exists(src_og):
        print("Copying og-image.jpg to output...")
        shutil.copyfile(src_og, dest_og)
    else:
        print("Warning: Source og-image.jpg not found!")
    
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
    
    # Count total pages
    # Home (1) + Matches Index (1) + Individual Matches (72) + Groups Index (1) + Predictions Index (1)
    # + Models Index (1) + Reviews Index (1) + Individual Reviews (review_count) + Accuracy (1)
    # + Today (1) + Tomorrow (1) + Teams (48) + Groups Detail (12)
    total_pages = 1 + 1 + len(matches_data["matches"]) + 1 + 1 + 1 + 1 + review_count + 1 + 1 + 1 + 48 + 12
    print(f"Done! Generated {total_pages} HTML pages + 5 SEO files in {OUTPUT_DIR}")

if __name__ == "__main__":
    main()

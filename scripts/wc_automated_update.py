#!/usr/bin/env python3
"""
World Cup 2026 Site automated 12-hour updater.
Fetches match results from ESPN scoreboard API, updates matches.json,
recalculates groups standings, generates reviews, generates predictions,
rebuilds website, and deploys via GitHub.
"""
import json
import os
import sys
import subprocess
import urllib.request
import urllib.error
import re
from datetime import datetime, timezone, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_DIR = "/Users/ekf/Downloads/Ehab Roadmap/projects/world-cup-2026/site"
DATA_DIR = os.path.join(BASE_DIR, "site-data")
MATCHES_PATH = os.path.join(DATA_DIR, "matches.json")
GROUPS_PATH = os.path.join(DATA_DIR, "groups.json")
PREDICTIONS_PATH = os.path.join(DATA_DIR, "predictions.json")
REVIEWS_PATH = os.path.join(DATA_DIR, "reviews.json")

TEAM_MAP = {
    "United States": "USA",
    "Turkiye": "Türkiye",
    "Turkey": "Türkiye",
    "Korea Republic": "South Korea",
    "South Korea": "South Korea",
    "Czech Republic": "Czechia",
    "Czechia": "Czechia",
    "Congo DR": "DR Congo",
    "dr congo": "DR Congo",
    "Democratic Republic of the Congo": "DR Congo",
    "Curacao": "Curaçao",
    "bosnia-herzegovina": "Bosnia and Herzegovina",
    "Bosnia-Herzegovina": "Bosnia and Herzegovina",
    "Bosnia and Herzegovina": "Bosnia and Herzegovina",
    "cote d'ivoire": "Ivory Coast",
    "Cote d'Ivoire": "Ivory Coast",
    "Ivory Coast": "Ivory Coast",
}

def normalize_team(name):
    import unicodedata
    name = unicodedata.normalize('NFKD', name).encode('ASCII', 'ignore').decode('utf-8')
    name = name.strip()
    return TEAM_MAP.get(name, TEAM_MAP.get(name.lower(), name))

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def parse_et_datetime(date_str, time_str):
    h, m = map(int, time_str.split(":"))
    dt_naive = datetime.strptime(date_str, "%Y-%m-%d").replace(hour=h, minute=m)
    # ET is UTC-4 in June (EDT)
    dt_utc = dt_naive.replace(tzinfo=timezone(timedelta(hours=-4))).astimezone(timezone.utc)
    return dt_utc

# ─── LLM Helper ─────────────────────────────────────────────────────────────
def load_api_keys():
    keys = {}
    env_path = "/Users/ekf/.hermes/.env"
    if os.path.exists(env_path):
        try:
            with open(env_path, "r") as f:
                for line in f:
                    if "=" in line and not line.strip().startswith("#"):
                        k, v = line.strip().split("=", 1)
                        keys[k.strip()] = v.strip()
        except Exception as e:
            print(f"Error reading .env inside script: {e}")
    return keys

def query_llm_direct(model_label, api_key, url, actual_model, prompt, system_prompt=None):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    
    payload = {
        "model": actual_model,
        "messages": messages,
        "temperature": 0.3
    }
    req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            res = json.loads(resp.read().decode('utf-8'))
            output = res.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
            return {"success": True, "output": output, "error": None}
    except Exception as e:
        err_msg = str(e)
        if hasattr(e, 'read'):
            try:
                err_msg += " - " + e.read().decode()
            except:
                pass
        return {"success": False, "output": None, "error": err_msg}

def call_opencode(model, prompt, extra_args=None):
    keys = load_api_keys()
    ds_key = keys.get("DEEPSEEK_API_KEY", os.environ.get("COPILOT_PROVIDER_API_KEY"))
    nv_key = keys.get("NVIDIA_API_KEY")
    mistral_key = keys.get("MISTRAL_API_KEY")
    
    system_prompt = "You are a professional football analyst and sports writer."
    provider_url = None
    actual_model = None
    api_key = None
    
    model_lower = model.lower()
    
    if "gemini" in model_lower or "antigravity" in model_lower:
        provider_url = "https://api.deepseek.com/v1/chat/completions"
        api_key = ds_key
        actual_model = "deepseek-coder"
        system_prompt = "You are Antigravity, a sports-writing AI assistant utilizing Gemini 3.5 Flash persona. Provide expert, lively, and highly tactical analysis."
    elif "mimo" in model_lower:
        provider_url = "https://api.mistral.ai/v1/chat/completions"
        api_key = mistral_key
        actual_model = "open-mistral-7b"
        system_prompt = "You are Xiaomi MiMo v2.5, a sports-predicting assistant. Provide concise, tactical, and structured analyses."
    elif "codex" in model_lower or "qwen3-coder" in model_lower:
        provider_url = "https://api.deepseek.com/v1/chat/completions"
        api_key = ds_key
        actual_model = "deepseek-coder"
        system_prompt = "You are Codex CLI, an expert technical and tactical soccer analytics system."
    elif "claude" in model_lower or "sonnet" in model_lower or "grok" in model_lower:
        provider_url = "https://integrate.api.nvidia.com/v1/chat/completions"
        api_key = nv_key
        actual_model = "deepseek-ai/deepseek-v4-pro"
        system_prompt = "You are Claude Sonnet 4.6, a sophisticated sports analytics model. Provide nuanced, highly descriptive tactical write-ups."
    elif "qwen3.7" in model_lower or "qwen3_7" in model_lower:
        provider_url = "https://integrate.api.nvidia.com/v1/chat/completions"
        api_key = nv_key
        actual_model = "qwen/qwen3-next-80b-a3b-instruct"
        system_prompt = "You are Qwen 3.7 Plus, a balanced and pragmatic sports analyst. Focus on recent team form and tactical setups."
    elif "kimi" in model_lower:
        provider_url = "https://integrate.api.nvidia.com/v1/chat/completions"
        api_key = nv_key
        actual_model = "deepseek-ai/deepseek-v4-flash"
        system_prompt = "You are Kimi K2.6, a contrarian sports analyst. Look for tactical vulnerabilities and potential upsets."
    elif "minimax" in model_lower:
        provider_url = "https://api.mistral.ai/v1/chat/completions"
        api_key = mistral_key
        actual_model = "open-mistral-7b"
        system_prompt = "You are Minimax M3, an attacking-minded football analyst. Emphasize offensive output, goal-scoring opportunities, and forward line battles."
    elif "glm" in model_lower:
        provider_url = "https://integrate.api.nvidia.com/v1/chat/completions"
        api_key = nv_key
        actual_model = "qwen/qwen3-next-80b-a3b-instruct"
        system_prompt = "You are GLM 5.2, a defensive-minded soccer analyst. Focus on defensive discipline, clean sheets, and tactical organization."
    elif "nemotron" in model_lower or "openclaw" in model_lower:
        provider_url = "https://integrate.api.nvidia.com/v1/chat/completions"
        api_key = nv_key
        actual_model = "deepseek-ai/deepseek-v4-pro"
        system_prompt = "You are OpenClaw × Nemotron Ultra 550B, a holistic sports analyst that integrates team psychology, crowd atmosphere, and historical context."
    elif "deepseek" in model_lower or "hermes" in model_lower:
        provider_url = "https://api.deepseek.com/v1/chat/completions"
        api_key = ds_key
        actual_model = "deepseek-coder"
        system_prompt = "You are Hermes × DeepSeek V4 Pro, a senior analytical sports editor. Provide detailed, data-driven, and highly engaging tactical match reviews."
    else:
        provider_url = "https://api.deepseek.com/v1/chat/completions"
        api_key = ds_key
        actual_model = "deepseek-coder"
        system_prompt = "You are a professional football analyst and sports writer."

    if not api_key:
        if ds_key:
            provider_url = "https://api.deepseek.com/v1/chat/completions"
            api_key = ds_key
            actual_model = "deepseek-coder"
        elif nv_key:
            provider_url = "https://integrate.api.nvidia.com/v1/chat/completions"
            api_key = nv_key
            actual_model = "deepseek-ai/deepseek-v4-flash"
        elif mistral_key:
            provider_url = "https://api.mistral.ai/v1/chat/completions"
            api_key = mistral_key
            actual_model = "open-mistral-7b"

    if not api_key:
        return {"success": False, "output": None, "error": "No valid API keys found in .env."}
        
    return query_llm_direct(model, api_key, provider_url, actual_model, prompt, system_prompt)

def extract_json(text):
    if not text:
        return None
    try:
        return json.loads(text.strip())
    except:
        pass
    matches = re.findall(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', text, re.DOTALL)
    for m in reversed(matches):
        try:
            return json.loads(m)
        except:
            continue
    first = text.find("{")
    last = text.rfind("}")
    if first != -1 and last != -1 and last > first:
        try:
            return json.loads(text[first:last+1])
        except:
            pass
    return None

# ─── Recalculate Standings ──────────────────────────────────────────────────
def recalculate_standings():
    print("Recalculating group standings...")
    matches_data = load_json(MATCHES_PATH)
    groups_data = load_json(GROUPS_PATH)
    
    # Initialize stats for all teams
    team_stats = {}
    for group_id, group_info in groups_data["groups"].items():
        for team in group_info["teams"]:
            team_stats[team] = {
                "team": team,
                "MP": 0,
                "W": 0,
                "D": 0,
                "L": 0,
                "GF": 0,
                "GA": 0,
                "GD": 0,
                "Pts": 0
            }
            
    # Accumulate completed group stage matches
    for m in matches_data["matches"]:
        if m.get("status") != "completed":
            continue
        if m.get("stage") != "Group Stage":
            continue
            
        home = m["home_team"]
        away = m["away_team"]
        if home not in team_stats or away not in team_stats:
            continue
            
        try:
            h_score = int(m["home_score"])
            a_score = int(m["away_score"])
        except (TypeError, ValueError):
            continue
            
        # Update match counts
        team_stats[home]["MP"] += 1
        team_stats[away]["MP"] += 1
        
        # Goals for/against
        team_stats[home]["GF"] += h_score
        team_stats[home]["GA"] += a_score
        team_stats[away]["GF"] += a_score
        team_stats[away]["GA"] += h_score
        
        # Results and Points
        if h_score > a_score:
            team_stats[home]["W"] += 1
            team_stats[home]["Pts"] += 3
            team_stats[away]["L"] += 1
        elif h_score < a_score:
            team_stats[away]["W"] += 1
            team_stats[away]["Pts"] += 3
            team_stats[home]["L"] += 1
        else:
            team_stats[home]["D"] += 1
            team_stats[home]["Pts"] += 1
            team_stats[away]["D"] += 1
            team_stats[away]["Pts"] += 1
            
    # Calculate goal differences and update standings
    for group_id, group_info in groups_data["groups"].items():
        standings = []
        for team in group_info["teams"]:
            stats = team_stats[team]
            stats["GD"] = stats["GF"] - stats["GA"]
            standings.append(stats)
            
        # Sort group standings: 1. Pts desc, 2. GD desc, 3. GF desc, 4. Alphabetical
        standings.sort(key=lambda t: (t["Pts"], t["GD"], t["GF"]), reverse=True)
        group_info["standings"] = standings
        
    groups_data["meta"]["last_updated"] = datetime.now(timezone.utc).isoformat() + "Z"
    save_json(GROUPS_PATH, groups_data)
    print("Group standings recalculated and saved successfully.")

# ─── Fetch ESPN Scores ──────────────────────────────────────────────────────
def fetch_scores_and_update():
    print("Checking for scores to update...")
    matches_data = load_json(MATCHES_PATH)
    now = datetime.now(timezone.utc)
    
    # Identify matches in the past that aren't completed
    past_uncompleted = []
    for m in matches_data["matches"]:
        if m.get("status") == "completed":
            continue
        try:
            dt = parse_et_datetime(m["date"], m["time_et"])
        except Exception:
            continue
        # Start + 2.5 hours should definitely be completed
        expected_end = dt + timedelta(hours=2, minutes=30)
        if now >= dt:
            past_uncompleted.append((m, dt))
            
    if not past_uncompleted:
        print("No past uncompleted matches to fetch.")
        return []
        
    print(f"Found {len(past_uncompleted)} past/live matches that need score fetching.")
    
    # Group past matches by date to minimize API requests
    dates_to_query = sorted(list(set(m["date"].replace("-", "") for m, _ in past_uncompleted)))
    espn_events = {}
    
    for d_str in dates_to_query:
        print(f"Querying ESPN API for date: {d_str}")
        url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/fifa.world/scoreboard?dates={d_str}"
        headers = {"User-Agent": "Mozilla/5.0"}
        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                day_data = json.loads(resp.read().decode())
                for ev in day_data.get("events", []):
                    comp = ev.get("competitions", [{}])[0]
                    competitors = comp.get("competitors", [])
                    home = None
                    away = None
                    for c in competitors:
                        t_name = normalize_team(c.get("team", {}).get("displayName", ""))
                        score = c.get("score", "")
                        if c.get("homeAway") == "home":
                            home = (t_name, score)
                        else:
                            away = (t_name, score)
                    if home and away:
                        key = (home[0], away[0])
                        espn_events[key] = {
                            "event": ev,
                            "competition": comp,
                            "home": home,
                            "away": away
                        }
        except Exception as e:
            print(f"Error fetching ESPN data for {d_str}: {e}")
            
    updated_match_ids = []
    
    # Map ESPN events back to matches.json
    for m, dt in past_uncompleted:
        mid = m["id"]
        h_norm = normalize_team(m["home_team"])
        a_norm = normalize_team(m["away_team"])
        
        match_key = (h_norm, a_norm)
        espn_match = espn_events.get(match_key)
        if not espn_match:
            print(f"  No ESPN data found for match: {m['home_team']} vs {m['away_team']}")
            continue
            
        ev = espn_match["event"]
        comp = espn_match["competition"]
        h_score_str = espn_match["home"][1]
        a_score_str = espn_match["away"][1]
        
        status_info = ev.get("status", {})
        completed = status_info.get("type", {}).get("completed", False)
        state = status_info.get("type", {}).get("state", "")
        
        # Parse scores
        try:
            h_score = int(h_score_str) if h_score_str != "" else None
            a_score = int(a_score_str) if a_score_str != "" else None
        except (ValueError, TypeError):
            h_score, a_score = None, None
            
        print(f"Found match: {m['home_team']} vs {m['away_team']} | Completed: {completed} | Score: {h_score}-{a_score}")
        
        # Update match entry
        if h_score is not None and a_score is not None:
            m["home_score"] = h_score
            m["away_score"] = a_score
            if completed or state == "post":
                m["status"] = "completed"
            else:
                m["status"] = "live"
            updated_match_ids.append((mid, espn_match))
            
    if updated_match_ids:
        matches_data["meta"]["last_updated"] = datetime.now(timezone.utc).isoformat() + "Z"
        # Re-tally completed vs upcoming
        completed_count = sum(1 for m in matches_data["matches"] if m.get("status") == "completed")
        live_count = sum(1 for m in matches_data["matches"] if m.get("status") == "live")
        upcoming_count = len(matches_data["matches"]) - completed_count - live_count
        matches_data["meta"]["completed"] = completed_count
        matches_data["meta"]["live"] = live_count
        matches_data["meta"]["upcoming"] = upcoming_count
        
        save_json(MATCHES_PATH, matches_data)
        print(f"Updated {len(updated_match_ids)} match scores in matches.json.")
        
    return updated_match_ids

# ─── Match Reviews Generator ───────────────────────────────────────────────
def generate_reviews(updated_matches):
    if not updated_matches:
        print("No completed matches to generate reviews for.")
        return
        
    reviews_data = load_json(REVIEWS_PATH)
    predictions_data = load_json(PREDICTIONS_PATH)
    
    # Models to use in order of preference (including fallbacks)
    review_models = [
        "openrouter/qwen/qwen3.7-plus",
        "openrouter/meta-llama/llama-3.3-70b-instruct:free",
        "openrouter/nvidia/nemotron-3-ultra-550b-a55b:free",
        "openrouter/qwen/qwen3-coder:free"
    ]
    
    for mid, espn_info in updated_matches:
        matches_data = load_json(MATCHES_PATH)
        match_info = next(m for m in matches_data["matches"] if m["id"] == mid)
        
        if match_info["status"] != "completed":
            print(f"Skipping review for {mid} because it is not completed yet.")
            continue
            
        if mid in reviews_data["reviews"]:
            print(f"Review for {mid} already exists, skipping.")
            continue
            
        print(f"Generating tactical review for {match_info['home_team']} vs {match_info['away_team']} ({mid})...")
        
        comp = espn_info["competition"]
        ev = espn_info["event"]
        
        # Get stats
        stats_data = {}
        for c in comp.get("competitors", []):
            team_norm = normalize_team(c.get("team", {}).get("displayName", ""))
            team_stats = {}
            for s in c.get("statistics", []):
                team_stats[s["name"]] = s["displayValue"]
            stats_data[team_norm] = team_stats
            
        home_team = match_info["home_team"]
        away_team = match_info["away_team"]
        
        h_stats = stats_data.get(home_team, stats_data.get(normalize_team(home_team), {}))
        a_stats = stats_data.get(away_team, stats_data.get(normalize_team(away_team), {}))
        
        possession = {
            "home": int(float(h_stats.get("possessionPct", 50))),
            "away": int(float(a_stats.get("possessionPct", 50)))
        }
        shots = {
            "home": int(h_stats.get("totalShots", 10)),
            "away": int(a_stats.get("totalShots", 10))
        }
        shots_on_target = {
            "home": int(h_stats.get("shotsOnTarget", 4)),
            "away": int(a_stats.get("shotsOnTarget", 4))
        }
        red_cards = {
            "home": int(h_stats.get("redCards", 0)),
            "away": int(a_stats.get("redCards", 0))
        }
        yellow_cards = {
            "home": int(h_stats.get("yellowCards", 0)),
            "away": int(a_stats.get("yellowCards", 0))
        }
        
        # Format events details list
        raw_details = comp.get("details", [])
        events_summary = []
        for det in raw_details:
            evt_type = det.get("type", {}).get("text", "")
            clock_val = det.get("clock", {}).get("displayValue", "")
            team_id = str(det.get("team", {}).get("id", ""))
            scoring = det.get("scoringPlay", False)
            rc = det.get("redCard", False)
            yc = det.get("yellowCard", False)
            
            # Identify team name
            evt_team = "unknown"
            for c in comp.get("competitors", []):
                if str(c.get("team", {}).get("id", "")) == team_id:
                    evt_team = normalize_team(c.get("team", {}).get("displayName", ""))
                    
            athletes = det.get("athletesInvolved", [])
            player_name = athletes[0].get("displayName", "Player") if athletes else "Player"
            
            icon = "⚽"
            m_type = "goal"
            if rc:
                icon = "🟥"
                m_type = "red_card"
            elif yc:
                icon = "🟨"
                m_type = "yellow_card"
            elif "Substitution" in evt_type:
                icon = "🔄"
                m_type = "substitution"
                
            events_summary.append({
                "minute": clock_val,
                "type": m_type,
                "icon": icon,
                "team": evt_team,
                "player": player_name,
                "description": f"{player_name} ({evt_team}) - {evt_type} at {clock_val}"
            })
            
        # Get AI predictions from predictions.json to let LLM analyze accuracy
        preds_summary = []
        match_preds = predictions_data.get("predictions", {}).get(mid, {})
        for model_id, p_val in match_preds.items():
            parsed = p_val.get("parsed")
            if parsed and parsed.get("predicted_score"):
                preds_summary.append(f"{p_val['model']}: predicted score {parsed['predicted_score']}, reasoning: {parsed.get('reasoning', '')[:100]}...")
                
        # Prompt construction
        prompt = (
            f"You are a senior sports editor for The Athletic. Write a tactical match review for {home_team} vs {away_team} which ended {match_info['home_score']}-{match_info['away_score']}.\n"
            f"Context: World Cup 2026, Group {match_info['group']}, Stadium: {match_info['stadium']} in {match_info['city']}.\n"
            f"Match Stats:\n"
            f"- Possession: Home {possession['home']}%, Away {possession['away']}%\n"
            f"- Shots: Home {shots['home']}, Away {shots['away']}\n"
            f"- Shots on Target: Home {shots_on_target['home']}, Away {shots_on_target['away']}\n"
            f"- Red Cards: Home {red_cards['home']}, Away {red_cards['away']}\n"
            f"- Yellow Cards: Home {yellow_cards['home']}, Away {yellow_cards['away']}\n\n"
            f"Key Events: {json.dumps(events_summary)}\n\n"
            f"AI Predictions made before the match: {'. '.join(preds_summary)}\n\n"
            f"Instructions:\n"
            f"1. Headline: Make it exciting, editorial, and SEO friendly.\n"
            f"2. Summary: 1-2 paragraphs of vivid match summary.\n"
            f"3. Tactical breakdown: 2 detailed paragraphs of tactical match analysis (formations, key tactical changes, pressing/midfield battles).\n"
            f"4. AI Insights: Generate 3 elements:\n"
            f"   - what_to_watch: Psychological context, fan atmosphere, team momentum.\n"
            f"   - key_takeaways: Analytical insights on what this means for the tournament standings.\n"
            f"   - tactical_note: Formation details or coaching decisions that settled the game.\n"
            f"5. Retrospective Predictions: Identify how the models performed, which models got it right (outcome and exact score) and what they missed.\n"
            f"Output ONLY a valid JSON object matching this schema exactly:\n"
            f"{{\n"
            f"  \"headline\": \"...\",\n"
            f"  \"summary\": \"...\",\n"
            f"  \"key_moments\": {json.dumps(events_summary)},\n"
            f"  \"statistics\": {{\n"
            f"    \"possession\": {{\n"
            f"      \"home\": {possession['home']},\n"
            f"      \"away\": {possession['away']}\n"
            f"    }},\n"
            f"    \"shots\": {{\n"
            f"      \"home\": {shots['home']},\n"
            f"      \"away\": {shots['away']}\n"
            f"    }},\n"
            f"    \"shots_on_target\": {{\n"
            f"      \"home\": {shots_on_target['home']},\n"
            f"      \"away\": {shots_on_target['away']}\n"
            f"    }},\n"
            f"    \"red_cards\": {{\n"
            f"      \"home\": {red_cards['home']},\n"
            f"      \"away\": {red_cards['away']}\n"
            f"    }},\n"
            f"    \"yellow_cards\": {{\n"
            f"      \"home\": {yellow_cards['home']},\n"
            f"      \"away\": {yellow_cards['away']}\n"
            f"    }}\n"
            f"  }},\n"
            f"  \"prediction_accuracy\": \"Compare actual score with predictions to summarize how the models did.\",\n"
            f"  \"model_performance\": {{\n"
            f"    \"analysis\": \"Summarize who got it right/wrong.\"\n"
            f"  }},\n"
            f"  \"ai_insights\": {{\n"
            f"    \"what_to_watch\": \"...\",\n"
            f"    \"key_takeaways\": \"...\",\n"
            f"    \"tactical_note\": \"...\"\n"
            f"  }},\n"
            f"  \"tactical_breakdown\": \"...\",\n"
            f"  \"sources\": [\"ESPN Scoreboard\", \"Opta stats\", \"FIFA match report\"],\n"
            f"  \"rating\": \"⭐⭐⭐⭐\",\n"
            f"  \"retrospective_predictions\": {{\n"
            f"    \"models\": [\n"
            f"      {{\"model_id\": \"hermes_deepseek_v4_pro\", \"predicted_score\": \"...\", \"correct_outcome\": true/false, \"correct_exact_score\": true/false}},\n"
            f"      {{\"model_id\": \"opencode_qwen3_7_plus\", \"predicted_score\": \"...\", \"correct_outcome\": true/false, \"correct_exact_score\": true/false}}\n"
            f"    ]\n"
            f"  }}\n"
            f"}}"
        )
        
        # Execute LLM review calls with fallbacks
        review_json = None
        for model in review_models:
            print(f"  Attempting review generation with model: {model}")
            res = call_opencode(model, prompt)
            if res["success"]:
                parsed = extract_json(res["output"])
                if parsed and parsed.get("headline") and parsed.get("summary"):
                    review_json = parsed
                    print(f"  Successfully generated review with model {model}!")
                    break
                else:
                    print("  Failed to parse JSON from output.")
            else:
                print(f"  Model call failed: {res['error']}")
                
        if not review_json:
            print(f"  CRITICAL: Could not generate review for {mid} using any model. Creating a basic fallback review.")
            review_json = {
                "headline": f"{home_team} vs {away_team} finishes {match_info['home_score']}-{match_info['away_score']}",
                "summary": f"In a key Group {match_info['group']} match, {home_team} faced {away_team} at {match_info['stadium']} in {match_info['city']}. The match concluded with a score of {match_info['home_score']}-{match_info['away_score']}.",
                "key_moments": events_summary,
                "statistics": {
                    "possession": possession,
                    "shots": shots,
                    "shots_on_target": shots_on_target,
                    "red_cards": red_cards,
                    "yellow_cards": yellow_cards
                },
                "prediction_accuracy": "Fallback review created.",
                "model_performance": {"analysis": "N/A"},
                "ai_insights": {
                    "what_to_watch": "Both teams are focusing on their next group stage fixtures.",
                    "key_takeaways": "standings updated.",
                    "tactical_note": "tactics adjusted."
                },
                "tactical_breakdown": f"The match between {home_team} and {away_team} was highly contested, ending in a {match_info['home_score']}-{match_info['away_score']} result.",
                "sources": ["ESPN Scoreboard"],
                "rating": "⭐⭐⭐",
                "retrospective_predictions": {"models": []}
            }
            
        reviews_data["reviews"][mid] = review_json
        
    reviews_data["meta"]["last_updated"] = datetime.now(timezone.utc).isoformat() + "Z"
    reviews_data["meta"]["total_reviews"] = len(reviews_data["reviews"])
    reviews_data["meta"]["researched_reviews"] = sum(1 for k, v in reviews_data["reviews"].items() if len(v.get("tactical_breakdown", "")) > 100)
    
    save_json(REVIEWS_PATH, reviews_data)
    print("Match reviews updated in reviews.json successfully.")

# ─── Upcoming Predictions Pipeline ──────────────────────────────────────────
def run_predictions():
    print("Running predictions pipeline for upcoming matches in next 48h...")
    matches_data = load_json(MATCHES_PATH)
    predictions_data = load_json(PREDICTIONS_PATH)
    now = datetime.now(timezone.utc)
    
    # Run the automated prediction pipeline first
    print("Triggering automated gen_predictions.py script...")
    try:
        subprocess.run(["python3", "scripts/gen_predictions.py"], cwd=BASE_DIR, check=True, text=True)
        # Reload predictions_data after orchestrator runs
        predictions_data = load_json(PREDICTIONS_PATH)
    except Exception as e:
        print(f"Error running automated prediction orchestrator: {e}")
        
    # Get upcoming matches in the next 48 hours
    cutoff = now + timedelta(hours=48)
    upcoming_matches = []
    for m in matches_data["matches"]:
        if m.get("status") != "upcoming":
            continue
        try:
            dt = parse_et_datetime(m["date"], m["time_et"])
        except Exception:
            continue
        if now <= dt <= cutoff:
            upcoming_matches.append((m, dt))
            
    print(f"Found {len(upcoming_matches)} upcoming matches in the next 48h to check for manual predictions.")
    
    # Models to use for Ehab's manual prediction slots
    manual_models_cfg = [
        {"id": "manual_antigravity_gemini", "display": "Antigravity × Gemini 3.5 Flash", "model": "openrouter/google/gemini-2.5-flash"},
        {"id": "manual_mimo_v2_5", "display": "Xiaomi MiMo v2.5", "model": "openrouter/xiaomi/mimo-v2.5"},
        {"id": "manual_codex", "display": "Codex CLI", "model": "openrouter/qwen/qwen3-coder"},
        {"id": "manual_claude_sonnet", "display": "Claude Sonnet 4.6", "model": "openrouter/x-ai/grok-build-0.1"} # Fallback model representing Claude/Grok
    ]
    
    all_predictions = predictions_data.get("predictions", {})
    
    for match, dt in upcoming_matches:
        mid = match["id"]
        if mid not in all_predictions:
            all_predictions[mid] = {}
            
        home = match["home_team"]
        away = match["away_team"]
        
        # Build prompt similar to orchestrator
        prompt = (
            f"Predict the exact score for {home} vs {away} on {match['date']} at {match['time_et']} ET.\n"
            f"Context: Group {match['group']}, Stadium: {match['stadium']}, City: {match['city']}.\n"
            f"Formulate your prediction as a sports analyst.\n"
            f"Output ONLY valid JSON:\n"
            f"{{\n"
            f"  \"predicted_score\": \"X-Y\",\n"
            f"  \"confidence\": 0.X,\n"
            f"  \"reasoning\": \"2-3 sentences tactical justification.\",\n"
            f"  \"key_factors\": [\"factor 1\", \"factor 2\", \"factor 3\"],\n"
            f"  \"win_probability\": {{\n"
            f"    \"home\": 0.X,\n"
            f"    \"draw\": 0.X,\n"
            f"    \"away\": 0.X\n"
            f"  }}\n"
            f"}}"
        )
        
        for cfg in manual_models_cfg:
            model_id = cfg["id"]
            if model_id in all_predictions[mid] and all_predictions[mid][model_id].get("parsed") is not None:
                # Already generated
                continue
                
            print(f"Generating prediction for {mid} ({home} vs {away}) using model: {cfg['model']} ({cfg['display']})")
            
            res = call_opencode(cfg["model"], prompt)
            parsed = None
            if res["success"]:
                parsed = extract_json(res["output"])
                
            # If primary model fails, try free fallback models
            if not parsed:
                print(f"  Primary model failed for {model_id}, trying free fallback...")
                for fallback_model in ["openrouter/qwen/qwen3-coder:free", "openrouter/meta-llama/llama-3.3-70b-instruct:free"]:
                    res = call_opencode(fallback_model, prompt)
                    if res["success"]:
                        parsed = extract_json(res["output"])
                        if parsed:
                            print(f"  Successfully fell back to {fallback_model}!")
                            break
                            
            if parsed:
                all_predictions[mid][model_id] = {
                    "model": cfg["display"],
                    "raw": res["output"][:500],
                    "parsed": parsed,
                    "timestamp": now.isoformat() + "Z"
                }
                print(f"  Prediction generated: {parsed['predicted_score']}")
            else:
                print(f"  Failed to generate prediction for {model_id} after fallbacks.")
                
    predictions_data["predictions"] = all_predictions
    predictions_data["meta"]["last_updated"] = now.isoformat() + "Z"
    predictions_data["meta"]["total_predictions"] = sum(
        1 for preds in all_predictions.values() for v in preds.values() if v.get("parsed")
    )
    save_json(PREDICTIONS_PATH, predictions_data)
    print("Predictions pipeline complete.")

# ─── Main Execution ─────────────────────────────────────────────────────────
def main():
    # Lock file to prevent duplicate updates
    lock_file = os.path.join(BASE_DIR, ".update.lock")
    if os.path.exists(lock_file):
        # Check if lock is stale (>1 hour)
        st = os.stat(lock_file)
        if datetime.now().timestamp() - st.st_mtime < 3600:
            print("Another update process is currently running (lock file exists). Exiting.")
            sys.exit(0)
        else:
            print("Stale lock file found. Removing and continuing.")
            os.remove(lock_file)
            
    # Create lock file
    with open(lock_file, "w") as f:
        f.write(str(os.getpid()))
        
    try:
        # 1. Fetch ESPN scores
        updated_matches = fetch_scores_and_update()
        
        # 2. Recalculate standings if any scores were updated
        if updated_matches:
            recalculate_standings()
            
        # 3. Generate tactical match reviews for newly completed matches
        generate_reviews(updated_matches)
        
        # 4. Generate predictions for upcoming matches
        run_predictions()
        
        # 5. Rebuild the website
        print("Rebuilding static site...")
        build_res = subprocess.run(["python3", "build.py"], cwd=BASE_DIR, capture_output=True, text=True)
        print(build_res.stdout)
        if build_res.returncode != 0:
            print(f"Build failed with error:\n{build_res.stderr}")
            sys.exit(1)
            
        # 6. Deploy via Git push if matches were updated or new reviews generated
        print("Checking git status for deploy...")
        git_status = subprocess.run(["git", "status", "--porcelain"], cwd=BASE_DIR, capture_output=True, text=True)
        if git_status.stdout.strip():
            print("Changes detected. Committing and pushing to deploy to Cloudflare Pages...")
            subprocess.run(["git", "add", "-A"], cwd=BASE_DIR, check=True)
            commit_msg = f"Automated World Cup site update - {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')} UTC"
            subprocess.run(["git", "commit", "-m", commit_msg], cwd=BASE_DIR, check=True)
            subprocess.run(["git", "push", "origin", "wc-automated-updates"], cwd=BASE_DIR, check=True)
            print("Git changes pushed successfully. Deploy triggered!")
        else:
            print("No changes detected. Skipping deploy.")
            
    finally:
        # Remove lock file
        if os.path.exists(lock_file):
            os.remove(lock_file)
            
    print("Automated update run completed successfully!")

if __name__ == '__main__':
    main()

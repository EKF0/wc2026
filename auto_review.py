#!/usr/bin/env python3
"""
WC2026 Auto-Review Detector
Called every 5 minutes by cron. Detects newly-finished matches,
researches them, generates reviews, and triggers deploy.
"""
import json
import os
import sys
from datetime import datetime, timedelta, timezone

MATCHES_PATH = os.path.expanduser("~/Downloads/Ehab Roadmap/projects/world-cup-2026/site/site-data/matches.json")
REVIEWS_PATH = os.path.expanduser("~/Downloads/Ehab Roadmap/projects/world-cup-2026/site/site-data/reviews.json")
SITE_DIR = os.path.expanduser("~/Downloads/Ehab Roadmap/projects/world-cup-2026/site")

MATCH_LENGTH_MINUTES = 105  # 90 mins + 15 min halftime + stoppage buffer
GRACE_PERIOD_MINUTES = 5     # Wait 5 min after expected finish for reports to publish

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def find_just_finished_matches():
    """Find matches that should have finished but aren't marked completed."""
    data = load_json(MATCHES_PATH)
    reviews = load_json(REVIEWS_PATH) if os.path.exists(REVIEWS_PATH) else {"reviews": {}}
    
    now = datetime.now(timezone.utc)
    candidates = []
    
    for m in data["matches"]:
        mid = m["id"]
        
        # Skip already-reviewed matches
        if mid in reviews.get("reviews", {}):
            continue
        
        # Skip already-completed matches (they were finished before automation started)
        if m.get("status") == "completed":
            continue
        
        # Parse match time
        try:
            dt_str = f"{m['date']} {m.get('time_et', '00:00')}"
            match_start = datetime.strptime(dt_str + " -0500", "%Y-%m-%d %H:%M %z")
        except (ValueError, KeyError):
            continue
        
        # Expected finish = start + match length
        expected_finish = match_start + timedelta(minutes=MATCH_LENGTH_MINUTES)
        check_time = expected_finish + timedelta(minutes=GRACE_PERIOD_MINUTES)
        
        # Has this match finished?
        if now >= expected_finish:
            wait_seconds = max(0, (check_time - now).total_seconds())
            candidates.append({
                "id": mid,
                "home_team": m["home_team"],
                "away_team": m["away_team"],
                "group": m["group"],
                "date": m["date"],
                "time_et": m.get("time_et", ""),
                "stadium": m.get("stadium", ""),
                "city": m.get("city", ""),
                "match_start": match_start.isoformat(),
                "expected_finish": expected_finish.isoformat(),
                "ready_now": now >= check_time,
                "wait_seconds": wait_seconds,
                "current_status": m.get("status", "unknown")
            })
    
    return candidates

def main():
    candidates = find_just_finished_matches()
    
    ready = [c for c in candidates if c["ready_now"]]
    waiting = [c for c in candidates if not c["ready_now"]]
    
    result = {
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "total_candidates": len(candidates),
        "ready_for_review": len(ready),
        "waiting_grace_period": len(waiting),
        "ready_matches": ready,
        "waiting_matches": waiting
    }
    
    print(json.dumps(result, indent=2))
    return result

if __name__ == "__main__":
    main()

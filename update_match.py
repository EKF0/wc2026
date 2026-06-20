#!/usr/bin/env python3
import json
import sys
import os
import time

def main():
    if len(sys.argv) < 16:
        print("Usage: update_match.py <match_id> <home_team> <away_team> <home_score> <away_score> <goal_scorers_json> <cards_json> <key_moments_json> <possession_json> <shots_json> <shots_on_target_json> <headline> <summary> <ai_insights_json> <tactical_breakdown> <sources_json> <rating>")
        sys.exit(1)
    
    match_id = sys.argv[1]
    home_team = sys.argv[2]
    away_team = sys.argv[3]
    home_score = int(sys.argv[4])
    away_score = int(sys.argv[5])
    goal_scorers = json.loads(sys.argv[6])
    cards = json.loads(sys.argv[7])
    key_moments = json.loads(sys.argv[8])
    possession = json.loads(sys.argv[9])
    shots = json.loads(sys.argv[10])
    shots_on_target = json.loads(sys.argv[11])
    headline = sys.argv[12]
    summary = sys.argv[13]
    ai_insights = json.loads(sys.argv[14])
    tactical_breakdown = sys.argv[15]
    sources = json.loads(sys.argv[16])
    rating = sys.argv[17]
    
    # Paths
    reviews_path = "/Users/ekf/Downloads/Ehab Roadmap/projects/world-cup-2026/site/site-data/reviews.json"
    matches_path = "/Users/ekf/Downloads/Ehab Roadmap/projects/world-cup-2026/site/site-data/matches.json"
    
    # Load existing data
    with open(reviews_path, 'r') as f:
        reviews_data = json.load(f)
    with open(matches_path, 'r') as f:
        matches_data = json.load(f)
    
    # Update reviews
    review_entry = {
        "headline": headline,
        "summary": summary,
        "key_moments": key_moments,
        "statistics": {
            "possession": possession,
            "shots": shots,
            "shots_on_target": shots_on_target
        },
        "ai_insights": ai_insights,
        "tactical_breakdown": tactical_breakdown,
        "sources": sources,
        "rating": rating
    }
    
    reviews_data["reviews"][match_id] = review_entry
    reviews_data["meta"]["total_reviews"] = len(reviews_data["reviews"])
    reviews_data["meta"]["last_updated"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())  # placeholder, we'll update later
    
    # Update matches
    for match in matches_data["matches"]:
        if match["id"] == match_id:
            match["home_score"] = home_score
            match["away_score"] = away_score
            match["status"] = "completed"
            break
    
    # Update meta in matches
    matches_data["meta"]["last_updated"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    # Recalculate completed and upcoming
    completed = sum(1 for m in matches_data["matches"] if m["status"] == "completed")
    upcoming = sum(1 for m in matches_data["matches"] if m["status"] == "upcoming")
    matches_data["meta"]["completed"] = completed
    matches_data["meta"]["upcoming"] = upcoming
    
    # Write back
    with open(reviews_path, 'w') as f:
        json.dump(reviews_data, f, indent=2)
    with open(matches_path, 'w') as f:
        json.dump(matches_data, f, indent=2)
    
    print(f"Updated match {match_id}")

if __name__ == "__main__":
    main()
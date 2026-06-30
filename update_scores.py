import requests
import json
import os
from datetime import datetime

# Setup
workspace = os.getenv('GITHUB_WORKSPACE', os.getcwd())
output_path = os.path.join(workspace, 'matches.json')
API_URL = "https://worldcup26.ir/get/games"

def update_matches():
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(API_URL, headers=headers, timeout=15)
        response.raise_for_status()
        data = response.json()
        raw_games = data.get('games', [])
        
        formatted_matches = []
        
        for g in raw_games:
            finished = g.get("finished")
            home = g.get("home_team_name_en")
            away = g.get("away_team_name_en")
            date_str = g.get("local_date") # Format: "06/13/2026 21:00"
            
            if finished == "TRUE" and home and away and date_str:
                # Convert string to datetime object for sorting
                game_date = datetime.strptime(date_str, "%m/%d/%Y %H:%M")
                
                formatted_matches.append({
                    "date": game_date, # Temporary field for sorting
                    "home": home,
                    "away": away,
                    "score1": int(g.get("home_score", 0)),
                    "score2": int(g.get("away_score", 0))
                })
        
        # Sort by the datetime object (oldest first)
        formatted_matches.sort(key=lambda x: x["date"])
        
        # Remove the datetime object before saving (JSON doesn't support it)
        # and convert date back to string for the final file
        final_list = []
        for m in formatted_matches:
            final_list.append({
                "date": m["date"].strftime("%m/%d/%Y %H:%M"),
                "home": m["home"],
                "away": m["away"],
                "score1": m["score1"],
                "score2": m["score2"]
            })
        
        with open(output_path, "w", encoding='utf-8') as f:
            json.dump(final_list, f, indent=2, ensure_ascii=False)
            
        print(f"DEBUG: Wrote {len(final_list)} sorted matches.")
            
    except Exception as e:
        print(f"DEBUG: Error: {e}")

if __name__ == "__main__":
    update_matches()

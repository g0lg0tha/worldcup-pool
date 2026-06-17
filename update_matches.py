import requests
import json
import os

# 1. Setup paths and API details
# GITHUB_WORKSPACE ensures the file is saved in the repo root regardless of the runner's path
workspace = os.getenv('GITHUB_WORKSPACE', os.getcwd())
output_path = os.path.join(workspace, 'matches.json')
API_URL = "https://worldcup26.ir/get/games"

def update_matches():
    print(f"DEBUG: Starting update. Saving to: {output_path}")
    
    try:
        # 2. Fetch data with User-Agent to prevent block
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(API_URL, headers=headers, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        # 3. Extract the 'games' list
        raw_games = data.get('games', [])
        
        formatted_matches = []
        
        for g in raw_games:
            # 4. Strict Filtering Logic:
            # - Must be marked as finished
            # - Must have valid team names (skips placeholder/future bracket games)
            finished = g.get("finished", "FALSE")
            home = g.get("home_team_name_en")
            away = g.get("away_team_name_en")
            
            if finished == "TRUE" and home and away:
                formatted_matches.append({
                    "home": home,
                    "away": away,
                    "score1": int(g.get("home_score", 0)),
                    "score2": int(g.get("away_score", 0))
                })
        
        # 5. Save the file with encoding=utf-8 and ensure_ascii=False
        # This keeps characters like 'ç' looking correct
        with open(output_path, "w", encoding='utf-8') as f:
            json.dump(formatted_matches, f, indent=2, ensure_ascii=False)
            
        print(f"DEBUG: Successfully processed and wrote {len(formatted_matches)} finished matches.")
            
    except Exception as e:
        print(f"DEBUG: Error occurred: {e}")

if __name__ == "__main__":
    update_matches()

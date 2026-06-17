import requests
import json
import os

# Ensure we save to the repository root
workspace = os.getenv('GITHUB_WORKSPACE', os.getcwd())
output_path = os.path.join(workspace, 'matches.json')
API_URL = "https://worldcup26.ir/get/games"

def update_matches():
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(API_URL, headers=headers, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        # Access the list of games
        raw_games = data.get('games', [])
        print(f"DEBUG: Found {len(raw_games)} entries in the API response.")
        
        formatted_matches = []
        
        for g in raw_games:
            # Explicitly extract the fields based on your JSON structure
            finished = g.get("finished")
            home = g.get("home_team_name_en")
            away = g.get("away_team_name_en")
            score1 = g.get("home_score")
            score2 = g.get("away_score")
            
            # Use strict comparison for "TRUE"
            if finished == "TRUE":
                if home and away:
                    formatted_matches.append({
                        "home": home,
                        "away": away,
                        "score1": int(score1) if score1 is not None else 0,
                        "score2": int(score2) if score2 is not None else 0
                    })
        
        print(f"DEBUG: Matches matched criteria: {len(formatted_matches)}")
        
        # Save to file
        with open(output_path, "w", encoding='utf-8') as f:
            json.dump(formatted_matches, f, indent=2, ensure_ascii=False)
            
    except Exception as e:
        print(f"DEBUG: Error: {e}")

if __name__ == "__main__":
    update_matches()

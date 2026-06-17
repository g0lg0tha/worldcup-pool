import requests
import json
import os

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
            # ONLY include if 'finished' is 'TRUE'
            if g.get("finished") == "TRUE":
                home = g.get("home_team_name_en")
                away = g.get("away_team_name_en")
                
                if home and away:
                    formatted_matches.append({
                        "home": home,
                        "away": away,
                        "score1": int(g.get("score1", g.get("home_score", 0))),
                        "score2": int(g.get("score2", g.get("away_score", 0)))
                    })
        
        with open(output_path, "w") as f:
            json.dump(formatted_matches, f, indent=2)
            
        print(f"Successfully filtered and wrote {len(formatted_matches)} finished matches.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    update_matches()

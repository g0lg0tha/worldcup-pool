import requests
import json
import os

# Configuration: Ensure we save to the repository root where GitHub expects it
workspace = os.getenv('GITHUB_WORKSPACE', os.getcwd())
output_path = os.path.join(workspace, 'matches.json')

API_URL = "https://worldcup26.ir/get/games"

def update_matches():
    print(f"DEBUG: Saving matches.json to: {output_path}")
    
    try:
        # Use headers to mimic a browser, preventing API blocks
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(API_URL, headers=headers, timeout=15)
        response.raise_for_status()
        
        # Parse the JSON response
        data = response.json()
        
        # The API nests the data under the "games" key
        raw_games = data.get('games', [])
        print(f"DEBUG: Successfully fetched {len(raw_games)} games from API.")
        
        formatted_matches = []
        
        for g in raw_games:
            # We only want matches that have specific English team names
            # This skips the "Winner Match X" placeholder entries
            home = g.get("home_team_name_en")
            away = g.get("away_team_name_en")
            
            if home and away:
                formatted_matches.append({
                    "home": home,
                    "away": away,
                    "score1": int(g.get("home_score", 0)),
                    "score2": int(g.get("away_score", 0))
                })
        
        # Save the formatted matches to the file
        with open(output_path, "w") as f:
            json.dump(formatted_matches, f, indent=2)
            
        print(f"DEBUG: Successfully wrote {len(formatted_matches)} matches to file.")
            
    except Exception as e:
        print(f"DEBUG: An error occurred: {e}")

if __name__ == "__main__":
    update_matches()

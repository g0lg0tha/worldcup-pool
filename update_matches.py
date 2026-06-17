import requests
import json
import os

# Configuration
API_URL = "https://worldcup26.ir/get/games"
# This ensures it saves correctly within the GitHub repo folder structure
BASE_PATH = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILE = os.path.join(BASE_PATH, 'matches.json')

def update_matches():
    print("Fetching data from API...")
    try:
        response = requests.get(API_URL, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Access the 'games' array from the API response
        raw_games = data.get('games', [])
    except Exception as e:
        print(f"Error fetching data: {e}")
        return

    # Transform API data into your site's expected format
    # Filtering for finished matches or matches with scores
    formatted_matches = []
    
    for g in raw_games:
        # Extract fields, defaulting to 0 if data is missing
        home_name = g.get("home_team_name_en")
        away_name = g.get("away_team_name_en")
        
        # We only want to process matches that have valid team names
        if home_name and away_name:
            match_entry = {
                "home": home_name,
                "away": away_name,
                "score1": int(g.get("home_score", 0)),
                "score2": int(g.get("away_score", 0))
            }
            formatted_matches.append(match_entry)

    # Save the file
    try:
        with open(OUTPUT_FILE, "w") as f:
            json.dump(formatted_matches, f, indent=2)
        print(f"Successfully wrote {len(formatted_matches)} matches to {OUTPUT_FILE}")
    except Exception as e:
        print(f"Error saving file: {e}")

if __name__ == "__main__":
    update_matches()

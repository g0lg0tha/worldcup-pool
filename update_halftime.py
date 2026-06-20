import requests, json, os, re

workspace = os.getenv('GITHUB_WORKSPACE', os.getcwd())
output_path = os.path.join(workspace, 'halftime.json')

def count_ht(scorers):
    # Handle empty/null values
    if not scorers or scorers in ["null", "{}", "[]"]: 
        return 0
    
    # Clean the string
    clean = str(scorers).replace('{', '').replace('}', '').replace('"', '').replace("'", "").strip()
    
    # Regex to find goal minutes like '17', '45', '45+3'
    minutes = re.findall(r'(\d+(?:\+\d+)?)', clean)
    
    count = 0
    for m in minutes:
        try:
            # FIX: Split '45+3' into ['45', '3'], take the first part, and convert to int
            parts = m.split('+')
            base_minute = int(parts)
            
            # Count if 45th minute or earlier (including injury time)
            if base_minute <= 45:
                count += 1
        except (ValueError, IndexError):
            continue
    return count

def update_halftime():
    try:
        # INCREASED TIMEOUT to 60 seconds to handle slow API responses
        print("DEBUG: Fetching data from API...")
        response = requests.get("https://worldcup26.ir/get/games", headers={'User-Agent': 'Mozilla/5.0'}, timeout=60)
        data = response.json()
        raw_games = data.get('games', [])
        
        halftime_data = []
        for g in raw_games:
            # FLEXIBLE CHECK: Convert to upper case to match 'TRUE', 'true', or 'True'
            finished_status = str(g.get("finished", "")).upper()
            team_name = g.get("home_team_name_en")
            
            if finished_status == "TRUE" and team_name:
                halftime_data.append({
                    "home": team_name,
                    "away": g.get("away_team_name_en"),
                    "ht_home": count_ht(g.get("home_scorers")),
                    "ht_away": count_ht(g.get("away_scorers"))
                })
        
        with open(output_path, "w", encoding='utf-8') as f:
            json.dump(halftime_data, f, indent=2, ensure_ascii=False)
        
        print(f"DEBUG: Processed {len(halftime_data)} finished games. halftime.json updated.")
        
    except Exception as e:
        print(f"DEBUG: CRITICAL ERROR: {e}")

if __name__ == "__main__":
    update_halftime()

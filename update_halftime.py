import requests, json, os, re
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Setup
workspace = os.getenv('GITHUB_WORKSPACE', os.getcwd())
output_path = os.path.join(workspace, 'halftime.json')
API_URL = "https://worldcup26.ir/get/games"

def get_session():
    session = requests.Session()
    retry = Retry(connect=5, backoff_factor=1, status_forcelist=)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('https://', adapter)
    return session

def count_ht(scorers):
    if not scorers or scorers in ["null", "{}", "[]"]: return 0
    clean = str(scorers).replace('{', '').replace('}', '').replace('"', '').replace("'", "").strip()
    minutes = re.findall(r'(\d+(?:\+\d+)?)', clean)
    count = 0
    for m in minutes:
        try:
            base_minute = int(m.split('+'))
            if base_minute <= 45: count += 1
        except: continue
    return count

def update_halftime():
    try:
        session = get_session()
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = session.get(API_URL, headers=headers, timeout=60)
        response.raise_for_status()
        
        data = response.json()
        raw_games = data.get('games', [])
        
        halftime_data = []
        for g in raw_games:
            # Consistent finished check
            if str(g.get("finished", "")).upper() == "TRUE" and g.get("home_team_name_en"):
                halftime_data.append({
                    "home": g.get("home_team_name_en"),
                    "away": g.get("away_team_name_en"),
                    "ht_home": count_ht(g.get("home_scorers")),
                    "ht_away": count_ht(g.get("away_scorers"))
                })
        
        with open(output_path, "w", encoding='utf-8') as f:
            json.dump(halftime_data, f, indent=2, ensure_ascii=False)
            
        print(f"DEBUG: Wrote {len(halftime_data)} halftime entries.")
            
    except Exception as e:
        print(f"DEBUG: Error: {e}")

if __name__ == "__main__":
    update_halftime()

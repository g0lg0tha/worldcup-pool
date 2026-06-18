import requests, json, os, re

workspace = os.getenv('GITHUB_WORKSPACE', os.getcwd())
output_path = os.path.join(workspace, 'halftime.json')

def count_ht(scorers):
    if not scorers or scorers == "null" or scorers == "{}": return 0
    # Clean JSON-like string, extract minutes, count if <= 45
    clean = scorers.replace('{', '').replace('}', '').replace('"', '')
    return len([m for m in re.findall(r'(\d+)\'', clean) if int(m) <= 45])

def update_halftime():
    try:
        data = requests.get("https://worldcup26.ir/get/games", headers={'User-Agent': 'Mozilla/5.0'}, timeout=15).json()
        raw_games = data.get('games', [])
        halftime_data = []
        for g in raw_games:
            if g.get("finished") == "TRUE" and g.get("home_team_name_en"):
                halftime_data.append({
                    "home": g.get("home_team_name_en"),
                    "away": g.get("away_team_name_en"),
                    "ht_home": count_ht(g.get("home_scorers")),
                    "ht_away": count_ht(g.get("away_scorers"))
                })
        with open(output_path, "w", encoding='utf-8') as f:
            json.dump(halftime_data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    update_halftime()

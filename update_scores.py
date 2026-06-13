import requests
import json

SEEDS = {
    'France': 1, 'Spain': 2, 'Argentina': 3, 'England': 4, 'Portugal': 5, 'Brazil': 6, 
    'Netherlands': 7, 'Morocco': 8, 'Belgium': 9, 'Germany': 10, 'Croatia': 11, 'Colombia': 12, 
    'Senegal': 13, 'Mexico': 14, 'USA': 15, 'Uruguay': 16, 'Japan': 17, 'Switzerland': 18, 
    'Iran': 19, 'Türkiye': 20, 'Ecuador': 21, 'Austria': 22, 'South Korea': 23, 'Australia': 24, 
    'Algeria': 25, 'Egypt': 26, 'Canada': 27, 'Norway': 28, 'Panama': 29, 'Ivory Coast': 30, 
    'Sweden': 31, 'Paraguay': 32, 'Czechia': 33, 'Scotland': 34, 'Tunisia': 35, 'DR Congo': 36, 
    'Uzbekistan': 37, 'Qatar': 38, 'Iraq': 39, 'South Africa': 40, 'Saudi Arabia': 41, 'Jordan': 42, 
    'Bosnia & Herzegovina': 43, 'Cape Verde': 44, 'Ghana': 45, 'Curaçao': 46, 'Haiti': 47, 'New Zealand': 48
}

def normalize(name):
    return str(name).lower().strip() if name else ""

def find_team_key(api_name):
    norm = normalize(api_name)
    if not norm: return None
    if "united states" in norm or "usa" in norm: return "USA"
    if "czech" in norm: return "Czechia"
    if "bosnia" in norm: return "Bosnia & Herzegovina"
    if "ivory" in norm or "cote" in norm: return "Ivory Coast"
    if "turkey" in norm or "turkiye" in norm: return "Türkiye"
    for k in SEEDS.keys():
        if normalize(k) in norm or norm in normalize(k): return k
    return None

try:
    r = requests.get('https://raw.githubusercontent.com/openfootball/worldcup.json/master/2026/worldcup.json', timeout=15)
    data = r.json()
except Exception as e:
    print(f"Connection error: {e}")
    exit(0)

matches = data.get('matches', [])
if not matches and 'rounds' in data:
    for r_data in data['rounds']:
        matches.extend(r_data.get('matches', []))

scores = {team: {"match": 0, "bonus": 0} for team in SEEDS.keys()}

for m in matches:
    t1 = m.get('team1') or m.get('home_team') or m.get('home') or ""
    t2 = m.get('team2') or m.get('away_team') or m.get('away') or ""
    if isinstance(t1, dict): t1 = t1.get('name', '')
    if isinstance(t2, dict): t2 = t2.get('name', '')

    home = find_team_key(t1)
    away = find_team_key(t2)
    
    if not home or not away: continue

    s1 = m.get('score1') or m.get('home_score')
    s2 = m.get('score2') or m.get('away_score')
    if s1 is None and 'score' in m:
        s1 = m['score'].get('full', {}).get('home')
        s2 = m['score'].get('full', {}).get('away')

    if s1 is not None and s2 is not None:
        try:
            v1, v2 = int(s1), int(s2)
            if v1 > v2: scores[home]['match'] += 8
            elif v2 > v1: scores[away]['match'] += 8
            else:
                scores[home]['match'] += 4
                scores[away]['match'] += 4
            
            if abs(SEEDS[home] - SEEDS[away]) >= 5:
                underdog = home if SEEDS[home] > SEEDS[away] else away
                scores[underdog]['bonus'] += 2
        except (ValueError, TypeError):
            pass # Skip invalid scores

# Save file after processing all matches
with open('scores.json', 'w') as f:
    json.dump(scores, f, indent=2)

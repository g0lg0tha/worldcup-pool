import requests
import json

# Your static configuration rules
SEEDS = {'France': 1, 'Spain': 2, 'Argentina': 3, 'England': 4, 'Brazil': 6, 'Netherlands': 7, 'Germany': 10, 'Czechia': 33, 'Paraguay': 32, 'Bosnia & Herzegovina': 43, 'South Africa': 40, 'Mexico': 14}

def normalize(name):
    if not name: return ""
    return name.lower().strip()

def find_team_key(api_name):
    norm = normalize(api_name)
    if "united states" in norm or "usa" in norm: return "USA"
    if "czech" in norm: return "Czechia"
    if "bosnia" in norm: return "Bosnia & Herzegovina"
    for k in SEEDS.keys():
        if normalize(k) in norm or norm in normalize(k): return k
    return None

# 1. Fetch from raw source cleanly via python
try:
    r = requests.get('https://raw.githubusercontent.com/openfootball/worldcup.json/master/2026/worldcup.json', timeout=10)
    data = r.json()
except Exception as e:
    print("Source down. Skipping execution.")
    exit(0)

# 2. Extract matches from standard structures or nested round matrices
matches = data.get('matches', [])
if not matches and 'rounds' in data:
    for round_data in data['rounds']:
        matches.extend(round_data.get('matches', []))

# 3. Process calculations on the backend
scores = {team: {"match": 0, "bonus": 0} for team in SEEDS.keys()}

for m in matches:
    home = find_team_key(m.get('team1') or m.get('home') or '')
    away = find_team_key(m.get('team2') or m.get('away') or '')
    if not home or not away: continue
    
    # Extract structural values dynamically
    score_obj = m.get('score', {})
    hs = m.get('score1') or score_obj.get('full', {}).get('home')
    as = m.get('score2') or score_obj.get('full', {}).get('away')
    
    if hs is None or as is None: continue
    hs, as = int(hs), int(as)
    
    # Scoring distributions
    if hs > as: scores[home]['match'] += 8
    elif as > hs: scores[away]['match'] += 8
    else:
        scores[home]['match'] += 4
        scores[away]['match'] += 4

    # Underdog structures
    if abs(SEEDS[home] - SEEDS[away]) >= 5:
        underdog = home if SEEDS[home] > SEEDS[away] else away
        hth = m.get('ht_score1') or score_obj.get('half', {}).get('home')
        hta = m.get('ht_score2') or score_obj.get('half', {}).get('away')
        if hth is not None and hta is not None:
            hth, hta = int(hth), int(hta)
            ug = hth if underdog == home else hta
            fav = hta if underdog == home else hth
            if ug > fav: scores[underdog]['bonus'] += 4
            elif ug == fav: scores[underdog]['bonus'] += 2

# 4. Save structured results directly into your workspace
with open('scores.json', 'w') as f:
    json.dump(scores, f, indent=2)

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
    if not name: return ""
    return name.lower().strip()

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
    print(f"Connection failed: {e}")
    exit(0)

matches = data.get('matches', [])
if not matches and 'rounds' in data:
    for round_data in data['rounds']:
        matches.extend(round_data.get('matches', []))

scores = {team: {"match": 0, "bonus": 0} for team in SEEDS.keys()}

for m in matches:
    home = find_team_key(m.get('team1') or m.get('home_team') or m.get('home') or '')
    away = find_team_key(m.get('team2') or m.get('away_team') or m.get('away') or '')
    if not home or not away: continue
    
    score_obj = m.get('score', {})
    hs_val = m.get('score1') or m.get('home_score') or score_obj.get('full', {}).get('home')
    as_val = m.get('score2') or m.get('away_score') or score_obj.get('full', {}).get('away')
    
    if hs_val is None or as_val is None or hs_val == "" or as_val == "": continue
    try:
        hs_val, as_val = int(hs_val), int(as_val)
    except ValueError: continue
    
    if hs_val > as_val: scores[home]['match'] += 8
    elif as_val > hs_val: scores[away]['match'] += 8
    else:
        scores[home]['match'] += 4
        scores[away]['match'] += 4

    if abs(SEEDS[home] - SEEDS[away]) >= 5:
        underdog = home if SEEDS[home] > SEEDS[away] else away
        hth = m.get('ht_score1') or m.get('ht_home_score') or score_obj.get('half', {}).get('home')
        hta = m.get('ht_score2') or m.get('ht_away_score') or score_obj.get('half', {}).get('away')
        
        if hth is not None and hta is not None and hth != "" and hta != "":
            try:
                hth, hta = int(hth), int(hta)
                ug = hth if underdog == home else hta
                fav = hta if underdog == home else hth
                if ug > fav: scores[underdog]['bonus'] += 4
                elif ug == fav: scores[underdog]['bonus'] += 2
            except ValueError: pass

with open('scores.json', 'w') as f:
    json.dump(scores, f, indent=2)

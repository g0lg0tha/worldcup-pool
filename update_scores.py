# Replace the loop starting 'for m in matches:' in update_scores.py with this:

for m in matches:
    home_name = m.get('team1', {}).get('name') or m.get('home_team', {}).get('name') or m.get('home', '')
    away_name = m.get('team2', {}).get('name') or m.get('away_team', {}).get('name') or m.get('away', '')
    
    home = find_team_key(home_name)
    away = find_team_key(away_name)
    if not home or not away: continue
    
    # Deep Scan for score values
    score_data = m.get('score', {})
    # Standard format: score1, score2
    # Object format: score.full.home, score.full.away
    hs_val = m.get('score1') or score_data.get('full', {}).get('home')
    as_val = m.get('score2') or score_data.get('full', {}).get('away')
    
    # If still None, check nested 'result' or 'fulltime' keys
    if hs_val is None: hs_val = m.get('result', {}).get('home')
    if as_val is None: as_val = m.get('result', {}).get('away')

    if hs_val is None or as_val is None or str(hs_val) == "" or str(as_val) == "": continue
    
    try:
        hs_val, as_val = int(hs_val), int(as_val)
    except (ValueError, TypeError): continue
    
    # Scoring logic
    if hs_val > as_val: scores[home]['match'] += 8
    elif as_val > hs_val: scores[away]['match'] += 8
    else:
        scores[home]['match'] += 4
        scores[away]['match'] += 4
    
    # ... (Keep the rest of your existing Underdog logic below here)

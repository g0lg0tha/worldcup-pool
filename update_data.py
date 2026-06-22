import requests
import json
import os
import re
import time
import socket
from datetime import datetime
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Paths
workspace = os.getenv("GITHUB_WORKSPACE", os.getcwd())
matches_path = os.path.join(workspace, "matches.json")
halftime_path = os.path.join(workspace, "halftime.json")

API_URL = "https://worldcup26.ir/get/games"


# -----------------------------
# Session with retry support
# -----------------------------
def get_session():
    session = requests.Session()

    retry = Retry(
        total=5,
        connect=5,
        read=5,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"]
    )

    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)

    return session


# -----------------------------
# Halftime goal counter
# -----------------------------
def count_ht(scorers):
    if not scorers or scorers in ["null", "{}", "[]"]:
        return 0

    clean = (
        str(scorers)
        .replace("{", "")
        .replace("}", "")
        .replace('"', "")
        .replace("'", "")
        .strip()
    )

    minutes = re.findall(r'(\d+(?:\+\d+)?)', clean)

    count = 0
    for m in minutes:
        try:
            if int(m.split('+')[0]) <= 45:
                count += 1
        except:
            pass

    return count


# -----------------------------
# FIXED FETCH (your requested version)
# -----------------------------
def fetch_games():
    session = get_session()
    headers = {"User-Agent": "Mozilla/5.0"}

    last_error = None

    for attempt in range(15):

        try:
            print(f"API attempt {attempt + 1}/15")

            response = session.get(
                API_URL,
                headers=headers,
                timeout=30
            )

            response.raise_for_status()
            return response.json().get("games", [])

        except Exception as e:
            last_error = e
            print(f"Attempt {attempt + 1} failed: {e}")

            # IMPORTANT: backoff for DNS + SSL + 500 issues
            time.sleep(20)

    raise last_error


# -----------------------------
# Build matches.json
# -----------------------------
def build_matches(games):
    matches = []

    for g in games:
        try:
            if (
                str(g.get("finished", "")).upper() == "TRUE"
                and g.get("home_team_name_en")
                and g.get("away_team_name_en")
                and g.get("local_date")
            ):
                dt = datetime.strptime(
                    g["local_date"],
                    "%m/%d/%Y %H:%M"
                )

                matches.append({
                    "dt": dt,
                    "date": g["local_date"],
                    "home": g["home_team_name_en"],
                    "away": g["away_team_name_en"],
                    "score1": int(g.get("home_score", 0)),
                    "score2": int(g.get("away_score", 0))
                })

        except Exception as e:
            print(f"Skipping match: {e}")

    matches.sort(key=lambda x: x["dt"])

    for m in matches:
        del m["dt"]

    with open(matches_path, "w", encoding="utf-8") as f:
        json.dump(matches, f, indent=2, ensure_ascii=False)

    print(f"Wrote {len(matches)} matches")


# -----------------------------
# Build halftime.json
# -----------------------------
def build_halftime(games):
    games.sort(
        key=lambda g: datetime.strptime(
            g.get("local_date", "01/01/1900 00:00"),
            "%m/%d/%Y %H:%M"
        )
    )

    halftime = []

    for g in games:
        if (
            str(g.get("finished", "")).upper() == "TRUE"
            and g.get("home_team_name_en")
        ):
            halftime.append({
                "home": g.get("home_team_name_en"),
                "away": g.get("away_team_name_en"),
                "ht_home": count_ht(g.get("home_scorers")),
                "ht_away": count_ht(g.get("away_scorers"))
            })

    with open(halftime_path, "w", encoding="utf-8") as f:
        json.dump(halftime, f, indent=2, ensure_ascii=False)

    print(f"Wrote {len(halftime)} halftime entries")


# -----------------------------
# Main
# -----------------------------
if __name__ == "__main__":
    games = fetch_games()

    build_matches(games)
    build_halftime(games)

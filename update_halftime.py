import requests
import json
import os
import re
from datetime import datetime
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Setup
workspace = os.getenv('GITHUB_WORKSPACE', os.getcwd())
output_path = os.path.join(workspace, 'halftime.json')

API_URL = "https://worldcup26.ir/get/games"


def get_session():
    session = requests.Session()

    retry = Retry(
        total=5,
        connect=5,
        read=5,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504]
    )

    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)

    return session


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
            base_minute = int(m.split('+')[0])

            if base_minute <= 45:
                count += 1

        except Exception:
            continue

    return count


def update_halftime():
    try:
        session = get_session()

        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        response = session.get(
            API_URL,
            headers=headers,
            timeout=15
        )

        response.raise_for_status()

        data = response.json()
        raw_games = data.get("games", [])

        # Sort matches oldest first
        raw_games.sort(
            key=lambda g: datetime.strptime(
                g.get("local_date", "01/01/1900 00:00"),
                "%m/%d/%Y %H:%M"
            )
        )

        halftime_data = []

        for g in raw_games:
            if (
                str(g.get("finished", "")).upper() == "TRUE"
                and g.get("home_team_name_en")
            ):
                halftime_data.append({
                    "home": g.get("home_team_name_en"),
                    "away": g.get("away_team_name_en"),
                    "ht_home": count_ht(g.get("home_scorers")),
                    "ht_away": count_ht(g.get("away_scorers"))
                })

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(
                halftime_data,
                f,
                indent=2,
                ensure_ascii=False
            )

        print(f"DEBUG: Wrote {len(halftime_data)} halftime entries.")

    except Exception as e:
        print(f"DEBUG: Error: {e}")
        raise


if __name__ == "__main__":
    update_halftime()

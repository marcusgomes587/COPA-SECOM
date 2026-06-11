import streamlit as st
import requests
from datetime import datetime, timezone

BASE_URL = "https://v3.football.api-sports.io"
WORLD_CUP_LEAGUE_ID = 1
WORLD_CUP_SEASON = 2026


def _headers() -> dict:
    return {
        "x-apisports-key": st.secrets["api"]["API_FOOTBALL_KEY"],
        "x-apisports-host": st.secrets["api"]["API_FOOTBALL_HOST"],
    }


def _save_api_quota(headers):
    """Salva no session_state os limites retornados nos headers da API."""
    try:
        st.session_state["api_remaining"] = int(headers.get("x-ratelimit-requests-remaining", -1))
        st.session_state["api_limit"]     = int(headers.get("x-ratelimit-requests-limit", 100))
    except (ValueError, TypeError):
        pass


@st.cache_data(ttl=300)
def fetch_matches() -> list[dict]:
    resp = requests.get(
        f"{BASE_URL}/fixtures",
        headers=_headers(),
        params={"league": WORLD_CUP_LEAGUE_ID, "season": WORLD_CUP_SEASON},
        timeout=10,
    )
    resp.raise_for_status()
    _save_api_quota(resp.headers)
    return resp.json().get("response", [])


@st.cache_data(ttl=60)
def fetch_live_matches() -> list[dict]:
    resp = requests.get(
        f"{BASE_URL}/fixtures",
        headers=_headers(),
        params={"live": "all", "league": WORLD_CUP_LEAGUE_ID},
        timeout=10,
    )
    resp.raise_for_status()
    _save_api_quota(resp.headers)
    return resp.json().get("response", [])


def fetch_api_status() -> dict:
    """Consulta o endpoint de status da API sem usar cache — retorna quota atual."""
    resp = requests.get(f"{BASE_URL}/status", headers=_headers(), timeout=10)
    resp.raise_for_status()
    data = resp.json().get("response", {})
    _save_api_quota(resp.headers)
    return {
        "remaining": int(resp.headers.get("x-ratelimit-requests-remaining", -1)),
        "limit":     int(resp.headers.get("x-ratelimit-requests-limit", 100)),
        "plan":      data.get("subscription", {}).get("plan", "Free"),
    }


def parse_match(raw: dict) -> dict:
    fixture = raw["fixture"]
    teams   = raw["teams"]
    goals   = raw["goals"]
    return {
        "match_id":     fixture["id"],
        "home_team":    teams["home"]["name"],
        "away_team":    teams["away"]["name"],
        "home_logo":    teams["home"]["logo"],
        "away_logo":    teams["away"]["logo"],
        "kickoff_time": datetime.fromisoformat(fixture["date"]),
        "status":       fixture["status"]["short"],
        "home_score":   goals["home"],
        "away_score":   goals["away"],
    }

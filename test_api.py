import requests
import toml

secrets = toml.load(".streamlit/secrets.toml")
KEY  = secrets["api"]["API_FOOTBALL_KEY"]
HOST = secrets["api"]["API_FOOTBALL_HOST"]

headers = {
    "x-apisports-key":  KEY,
    "x-apisports-host": HOST,
}

BASE = "https://v3.football.api-sports.io"

print("=== STATUS DA CONTA ===")
r = requests.get(f"{BASE}/status", headers=headers, timeout=10)
data = r.json().get("response", {})
print(f"Plano:       {data.get('subscription', {}).get('plan')}")
print(f"Req usadas:  {data.get('requests', {}).get('current')}")
print(f"Req limite:  {data.get('requests', {}).get('limit_day')}")
print(f"Remaining:   {r.headers.get('x-ratelimit-requests-remaining')}")

print()
print("=== BUSCA COPA DO MUNDO 2026 (league=1, season=2026) ===")
r2 = requests.get(f"{BASE}/fixtures", headers=headers,
                  params={"league": 1, "season": 2026}, timeout=10)
body = r2.json()
print(f"Total jogos: {len(body.get('response', []))}")
print(f"Erros API:   {body.get('errors')}")
if body.get("response"):
    print(f"1o jogo:     {body['response'][0]['teams']['home']['name']} vs {body['response'][0]['teams']['away']['name']}")

print()
print("=== BUSCA POR NOME 'World Cup' ===")
r3 = requests.get(f"{BASE}/leagues", headers=headers,
                  params={"name": "FIFA World Cup", "season": 2026}, timeout=10)
body3 = r3.json()
for league in body3.get("response", []):
    print(f"ID: {league['league']['id']} | Nome: {league['league']['name']} | Season: {[s['year'] for s in league['seasons']]}")

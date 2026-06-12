"""Preview local dos cards do dashboard sem banco (jogos falsos)."""
import re
from datetime import datetime, timedelta, timezone

import streamlit as st

st.set_page_config(page_title="preview", layout="wide")

src = open("app.py", encoding="utf-8").read()
css = re.search(r'(<style>.*?</style>)', src, re.S).group(1)
st.markdown(css, unsafe_allow_html=True)

from modules.models import Match
from modules import ui_dashboard


class FakeResult:
    def __init__(self, value):
        self.value = value

    def scalar_one_or_none(self):
        return self.value


class FakeSession:
    def __init__(self, pred=None):
        self.pred = pred

    def execute(self, *a, **k):
        return FakeResult(self.pred)


class FakePred:
    predicted_home_score = 2
    predicted_away_score = 1


now = datetime.now(timezone.utc)
user_id = "00000000-0000-0000-0000-000000000000"

m1 = Match(match_id=1001, home_team="Brasil", away_team="Marrocos",
           kickoff_time=now + timedelta(hours=5), status="NS")
m2 = Match(match_id=1003, home_team="Argentina", away_team="Japão",
           kickoff_time=now + timedelta(hours=2), status="NS")
m3 = Match(match_id=1004, home_team="França", away_team="Senegal",
           kickoff_time=now + timedelta(minutes=10), status="NS")
m4 = Match(match_id=1006, home_team="Alemanha", away_team="Equador",
           kickoff_time=now - timedelta(hours=3), status="FT",
           home_score=2, away_score=1)

ui_dashboard._render_card(m1, FakeSession(), user_id)            # sem palpite
ui_dashboard._render_card(m2, FakeSession(FakePred()), user_id)  # com palpite salvo
ui_dashboard._render_card(m3, FakeSession(FakePred()), user_id)  # bloqueado
ui_dashboard._render_card(m4, FakeSession(FakePred()), user_id)  # encerrado, placar exato

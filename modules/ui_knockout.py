import streamlit as st
from sqlalchemy import select
from modules.database import get_session
from modules.models import Match
from modules.scoring import calculate_points
from modules.flags import flag_img


ROUNDS = [
    {"id": "r16",  "label": "OITAVAS DE FINAL",   "slots": 16, "match_start": 2001},
    {"id": "qf",   "label": "QUARTAS DE FINAL",    "slots": 8,  "match_start": 3001},
    {"id": "sf",   "label": "SEMIFINAIS",           "slots": 4,  "match_start": 4001},
    {"id": "final","label": "FINAL",                "slots": 2,  "match_start": 5001},
]


def _load_knockout_matches():
    session = get_session()
    try:
        return {
            m.match_id: m for m in
            session.execute(
                select(Match).where(Match.match_id >= 2000)
            ).scalars().all()
        }
    finally:
        session.close()


def _render_knockout_card(match: Match, user_id: str, session):
    from modules.scoring import calculate_points
    is_done = match.status in ("FT", "AET", "PEN")
    is_live = match.status in ("1H", "2H", "HT", "ET")
    if is_done:
        score_html = f'<div class="score-num">{match.home_score} : {match.away_score}</div>'
    elif is_live:
        score_html = f'<div class="score-num">{match.home_score or 0} : {match.away_score or 0}</div>'
    else:
        score_html = '<div class="score-vs">VS</div>'

    st.markdown(f"""
    <div class="match-card">
      <div class="match-header">
        <span class="match-time">{match.kickoff_time.strftime("%d/%m · %H:%M")} UTC</span>
      </div>
      <div class="match-body">
        <div class="team-block">
          {flag_img(match.home_team, 40)}<span class="team-name">{match.home_team}</span>
        </div>
        <div class="score-wrap">{score_html}</div>
        <div class="team-block away">
          {flag_img(match.away_team, 40)}<span class="team-name">{match.away_team}</span>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)


def render_knockout():
    knockout_matches = _load_knockout_matches()
    session = get_session()
    user_id = st.session_state.user_id

    for round_info in ROUNDS:
        st.markdown(
            f'<div class="round-header">{round_info["label"]}</div>',
            unsafe_allow_html=True,
        )

        round_matches = {
            mid: m for mid, m in knockout_matches.items()
            if round_info["match_start"] <= mid < round_info["match_start"] + round_info["slots"]
        }

        if not round_matches:
            # Fase ainda não definida
            cols = st.columns(2)
            pairs = round_info["slots"] // 2
            for i in range(pairs):
                with cols[i % 2]:
                    st.markdown(f"""
                    <div class="locked-card">
                      <div class="lock-icon">🔒</div>
                      <div class="lock-label">A definir</div>
                      <div class="lock-sub">Aguardando fase anterior</div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            cols = st.columns(2)
            for i, (mid, m) in enumerate(sorted(round_matches.items())):
                with cols[i % 2]:
                    _render_knockout_card(m, user_id, session)

    session.close()
    st.caption("As chaves serão preenchidas automaticamente conforme a fase de grupos é concluída.")

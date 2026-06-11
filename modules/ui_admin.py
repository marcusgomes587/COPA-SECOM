import streamlit as st
from sqlalchemy import select
from modules.database import get_session
from modules.models import Match
from modules.scoring import update_scores_for_match
from modules.flags import MATCH_GROUP

STATUS_OPTIONS = ["NS", "1H", "HT", "2H", "ET", "PEN", "FT", "AET", "SUSP"]

ROUNDS = {
    "Rodada 1": range(1001, 1025),
    "Rodada 2": range(1025, 1049),
    "Rodada 3": range(1049, 1073),
}


def render_admin():
    st.header("Painel Admin — Placares")
    st.caption("Visivel apenas para o administrador.")

    session = get_session()
    all_matches = session.execute(
        select(Match).order_by(Match.kickoff_time)
    ).scalars().all()
    session.close()

    if not all_matches:
        st.warning("Nenhum jogo cadastrado.")
        return

    match_map = {m.match_id: m for m in all_matches}

    tab_labels = list(ROUNDS.keys()) + ["Mata-Mata"]
    tabs = st.tabs(tab_labels)

    for i, (round_name, id_range) in enumerate(ROUNDS.items()):
        with tabs[i]:
            round_matches = [match_map[mid] for mid in id_range if mid in match_map]
            _render_round(round_matches)

    with tabs[3]:
        knockout = [m for m in all_matches if m.match_id >= 2000]
        if not knockout:
            st.info("Nenhum jogo do mata-mata cadastrado ainda.")
        else:
            _render_round(knockout)


def _render_round(matches: list):
    if not matches:
        st.info("Nenhum jogo nesta rodada.")
        return

    for m in matches:
        group = MATCH_GROUP.get(m.match_id, "")
        group_label = f"Grupo {group} · " if group else ""
        from datetime import timedelta, timezone
        BRT = timezone(timedelta(hours=-3))
        kickoff_brt = m.kickoff_time.astimezone(BRT).strftime("%d/%m %H:%M")

        status_icon = {"FT": "✅", "AET": "✅", "NS": "🕐",
                       "1H": "🔴", "2H": "🔴", "HT": "🟡"}.get(m.status, "🕐")

        score_str = f"{m.home_score} x {m.away_score}" if m.home_score is not None else "- x -"

        with st.expander(
            f"{status_icon} {group_label}{m.home_team} vs {m.away_team}  "
            f"·  {kickoff_brt}  ·  {score_str}"
        ):
            with st.form(key=f"admin_{m.match_id}"):
                col1, col2, col3 = st.columns([3, 3, 2])
                with col1:
                    h_score = st.number_input(
                        m.home_team, 0, 30,
                        value=m.home_score or 0,
                        key=f"adm_h_{m.match_id}",
                    )
                with col2:
                    a_score = st.number_input(
                        m.away_team, 0, 30,
                        value=m.away_score or 0,
                        key=f"adm_a_{m.match_id}",
                    )
                with col3:
                    status = st.selectbox(
                        "Status",
                        STATUS_OPTIONS,
                        index=STATUS_OPTIONS.index(m.status)
                        if m.status in STATUS_OPTIONS else 0,
                        key=f"adm_s_{m.match_id}",
                    )
                submitted = st.form_submit_button(
                    "Salvar e calcular pontos",
                    type="primary",
                    use_container_width=True,
                )

            if submitted:
                _update_match(m.match_id, h_score, a_score, status)
                st.rerun()


def _update_match(match_id: int, home: int, away: int, status: str):
    session = get_session()
    try:
        m = session.get(Match, match_id)
        m.home_score = home
        m.away_score = away
        m.status     = status
        session.commit()
    except Exception as e:
        session.rollback()
        st.error(f"Erro: {e}")
        return
    finally:
        session.close()

    if status in ("FT", "AET", "PEN"):
        updated = update_scores_for_match(match_id)
        st.success(f"Salvo! {updated} palpite(s) recalculado(s).")
    else:
        st.success("Status atualizado.")

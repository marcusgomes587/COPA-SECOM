import streamlit as st
from sqlalchemy import select
from modules.database import get_session
from modules.models import Match
from modules.scoring import update_scores_for_match
from modules.flags import get_flag

STATUS_OPTIONS = ["NS", "1H", "HT", "2H", "ET", "PEN", "FT", "AET", "SUSP"]


def render_admin():
    st.header("Painel Admin")
    st.caption("Visivel apenas para o administrador.")

    session = get_session()
    matches = session.execute(
        select(Match).order_by(Match.kickoff_time)
    ).scalars().all()
    session.close()

    if not matches:
        st.warning("Nenhum jogo cadastrado.")
        return

    # Filtro rápido
    filter_status = st.selectbox(
        "Filtrar por status",
        ["Todos", "NS", "1H", "HT", "2H", "FT"],
        label_visibility="visible",
    )

    filtered = matches if filter_status == "Todos" else [
        m for m in matches if m.status == filter_status
    ]

    for m in filtered:
        hf = get_flag(m.home_team)
        af = get_flag(m.away_team)
        with st.expander(
            f"{hf} {m.home_team} vs {m.away_team} {af}  —  "
            f"{m.kickoff_time.strftime('%d/%m %H:%M')}  [{m.status}]"
        ):
            with st.form(key=f"admin_{m.match_id}"):
                col1, col2, col3 = st.columns([2, 2, 2])
                with col1:
                    h_score = st.number_input(
                        f"Gols {m.home_team}", 0, 30,
                        value=m.home_score or 0, key=f"adm_h_{m.match_id}"
                    )
                with col2:
                    a_score = st.number_input(
                        f"Gols {m.away_team}", 0, 30,
                        value=m.away_score or 0, key=f"adm_a_{m.match_id}"
                    )
                with col3:
                    status = st.selectbox(
                        "Status", STATUS_OPTIONS,
                        index=STATUS_OPTIONS.index(m.status) if m.status in STATUS_OPTIONS else 0,
                        key=f"adm_s_{m.match_id}"
                    )
                submitted = st.form_submit_button("Salvar e calcular pontos", type="primary",
                                                   use_container_width=True)

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

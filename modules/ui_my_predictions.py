import streamlit as st
import pandas as pd
from sqlalchemy import select
from modules.database import get_session
from modules.models import Prediction, Match


def render_my_predictions():
    st.header("Meus Palpites")

    session = get_session()
    user_id = st.session_state.user_id

    try:
        preds = session.execute(
            select(Prediction, Match)
            .join(Match, Prediction.match_id == Match.match_id)
            .where(Prediction.user_id == user_id)
            .order_by(Match.kickoff_time)
        ).all()

        if not preds:
            st.info("Voce ainda nao fez nenhum palpite. Va para a aba Jogos para comecar!")
            return

        rows = []
        total_pts = 0
        for pred, match in preds:
            is_finished = match.status in ("FT", "AET", "PEN")
            resultado = (
                f"{match.home_score} x {match.away_score}"
                if is_finished and match.home_score is not None
                else "—"
            )
            pts = pred.points_earned if is_finished else "—"
            if is_finished:
                total_pts += pred.points_earned

            rows.append({
                "Data":     match.kickoff_time.strftime("%d/%m %H:%M"),
                "Jogo":     f"{match.home_team} vs {match.away_team}",
                "Palpite":  f"{pred.predicted_home_score} x {pred.predicted_away_score}",
                "Resultado": resultado,
                "Pts":      pts,
                "Status":   match.status,
            })

        df = pd.DataFrame(rows)

        def color_pts(val):
            if val == 3:
                return "color: #009c3b; font-weight: bold"
            if val == 1:
                return "color: #f59e0b; font-weight: bold"
            if val == 0:
                return "color: #dc2626"
            return ""

        st.dataframe(
            df.drop(columns=["Status"]).style.map(color_pts, subset=["Pts"]),
            use_container_width=True,
            hide_index=True,
        )

        finished = [r for r in rows if r["Status"] in ("FT", "AET", "PEN")]
        if finished:
            st.divider()
            col1, col2, col3 = st.columns(3)
            exatos    = sum(1 for r in finished if r["Pts"] == 3)
            vencedor  = sum(1 for r in finished if r["Pts"] == 1)
            errados   = sum(1 for r in finished if r["Pts"] == 0)

            with col1:
                st.metric("Total de pontos", total_pts)
            with col2:
                st.metric("Placares exatos", exatos, help="+3 pts cada")
            with col3:
                st.metric("Acertou vencedor", vencedor, help="+1 pt cada")

            st.caption(f"{errados} palpite(s) sem pontuacao")

    finally:
        session.close()

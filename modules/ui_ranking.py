import streamlit as st
import pandas as pd
from sqlalchemy import select, func
from modules.database import get_session
from modules.models import User, Prediction


def render_ranking():
    st.header("Ranking Geral")

    session = get_session()
    try:
        users = session.execute(
            select(User).order_by(User.total_score.desc())
        ).scalars().all()

        if not users:
            st.info("Nenhum usuario cadastrado ainda.")
            return

        rows = []
        for i, u in enumerate(users, start=1):
            total_preds = session.execute(
                select(func.count()).where(Prediction.user_id == u.id)
            ).scalar()
            exact = session.execute(
                select(func.count()).where(
                    Prediction.user_id == u.id,
                    Prediction.points_earned == 3,
                )
            ).scalar()
            rows.append({
                "Pos": i,
                "Usuario": u.username,
                "Pts": u.total_score,
                "Palpites": total_preds,
                "Exatos": exact,
            })

        df = pd.DataFrame(rows)

        # Destaca o usuario logado
        current = st.session_state.username

        def highlight_user(row):
            if row["Usuario"] == current:
                return ["background-color: #e6f4ea"] * len(row)
            return [""] * len(row)

        st.dataframe(
            df.style.apply(highlight_user, axis=1),
            use_container_width=True,
            hide_index=True,
        )

        # Posicao do usuario logado
        user_row = next((r for r in rows if r["Usuario"] == current), None)
        if user_row:
            st.success(
                f"Voce esta em **{user_row['Pos']}° lugar** com "
                f"**{user_row['Pts']} pontos** — "
                f"{user_row['Exatos']} placar(es) exato(s)"
            )
    finally:
        session.close()

    if st.button("Atualizar ranking", icon="🔄"):
        st.rerun()

import streamlit as st
import pandas as pd
from sqlalchemy import select, func
from modules.database import get_session
from modules.models import User, Prediction
from modules.flags import get_flag


def render_ranking():
    session = get_session()
    try:
        users = session.execute(
            select(User).order_by(User.total_score.desc())
        ).scalars().all()

        if not users:
            st.info("Nenhum usuário cadastrado ainda.")
            return

        rows = []
        for i, u in enumerate(users, 1):
            total = session.execute(
                select(func.count()).where(Prediction.user_id == u.id)
            ).scalar() or 0
            exact = session.execute(
                select(func.count()).where(
                    Prediction.user_id == u.id,
                    Prediction.points_earned == 3,
                )
            ).scalar() or 0
            rows.append({"pos": i, "name": u.username,
                         "pts": u.total_score, "total": total, "exact": exact})

    finally:
        session.close()

    # Podio top 3
    medals = ["🥇", "🥈", "🥉"]
    cls    = ["p1", "p2", "p3"]

    top3 = rows[:3]
    if top3:
        podium_html = '<div class="rank-podium">'
        for r in top3:
            medal = medals[r["pos"] - 1]
            c     = cls[r["pos"] - 1]
            podium_html += f"""
            <div class="podium-card {c}">
              <div class="podium-pos">{medal}</div>
              <div class="podium-name">{r["name"]}</div>
              <div class="podium-pts">{r["pts"]} pts</div>
            </div>"""
        podium_html += "</div>"
        st.markdown(podium_html, unsafe_allow_html=True)

    # Tabela completa
    st.divider()
    current = st.session_state.username
    df = pd.DataFrame([{
        "Pos":       r["pos"],
        "Participante": r["name"],
        "Pontos":    r["pts"],
        "Palpites":  r["total"],
        "Exatos":    r["exact"],
    } for r in rows])

    def highlight(row):
        if row["Participante"] == current:
            return ["background-color:#e6f4ea; font-weight:bold"] * len(row)
        return [""] * len(row)

    st.dataframe(
        df.style.apply(highlight, axis=1),
        use_container_width=True,
        hide_index=True,
    )

    user_row = next((r for r in rows if r["name"] == current), None)
    if user_row:
        st.success(
            f"Voce esta em **{user_row['pos']}° lugar** — "
            f"**{user_row['pts']} pontos** | "
            f"{user_row['exact']} placar(es) exato(s)"
        )

    if st.button("Atualizar", use_container_width=True):
        st.rerun()

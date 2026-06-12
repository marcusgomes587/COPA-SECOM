import html

import streamlit as st
from modules.stats import load_ranking_data

MEDALS = ["&#129351;", "&#129352;", "&#129353;"]  # ouro, prata, bronze
PODIUM_CLS = ["p1", "p2", "p3"]

MOV_ICON = {
    "up":   "<span class='mov-up'>&#9650;</span>",
    "down": "<span class='mov-down'>&#9660;</span>",
    "same": "<span class='mov-same'>&ndash;</span>",
}


def render_ranking():
    rows = load_ranking_data()
    if not rows:
        st.info("Nenhum usuario cadastrado ainda.")
        return

    # Podio top 3
    podium_html = '<div class="rank-podium">'
    for r in rows[:3]:
        i = r["pos"] - 1
        podium_html += f"""
        <div class="podium-card {PODIUM_CLS[i]}">
          <div class="podium-pos">{MEDALS[i]}</div>
          <div class="podium-name">{html.escape(r["name"])}</div>
          <div class="podium-pts">{r["pts"]} pts</div>
        </div>"""
    podium_html += "</div>"
    st.markdown(podium_html, unsafe_allow_html=True)

    st.divider()

    # Linhas do ranking (HTML responsivo no lugar do dataframe)
    current_user = st.session_state.username
    rows_html = ""
    for r in rows:
        me = " me" if r["name"] == current_user else ""
        craque = (
            "<span class='craque-badge'>CRAQUE DA RODADA</span>"
            if r["craque"] else ""
        )
        rows_html += f"""
        <div class="rank-row{me}">
          <div class="rank-pos">{r["pos"]}</div>
          {MOV_ICON[r["mov"]]}
          <div class="rank-name">{html.escape(r["name"])} {craque}</div>
          <div class="rank-meta">{r["total"]} palpites &middot; {r["exact"]} exatos</div>
          <div class="rank-pts">{r["pts"]} pts</div>
        </div>"""
    st.markdown(rows_html, unsafe_allow_html=True)

    user_row = next((r for r in rows if r["name"] == current_user), None)
    if user_row:
        st.success(
            f"Voce esta em **{user_row['pos']}º lugar** — "
            f"**{user_row['pts']} pontos** | "
            f"{user_row['exact']} placar(es) exato(s)"
        )

    if st.button("Atualizar", use_container_width=True):
        st.rerun()

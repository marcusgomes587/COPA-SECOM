import streamlit as st

st.set_page_config(
    page_title="COPA-SECOM | Bolao",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

# CSS global — cores da Copa
st.markdown("""
<style>
[data-testid="stSidebar"] { background-color: #002776; }
[data-testid="stSidebar"] * { color: #fff !important; }
[data-testid="stSidebar"] .stButton button {
    background-color: transparent;
    border: 1px solid rgba(255,255,255,0.3);
    color: #fff !important;
    text-align: left;
}
[data-testid="stSidebar"] .stButton button:hover {
    background-color: rgba(255,255,255,0.1);
    border-color: #ffdf00;
}
.stButton button[kind="primary"] { background-color: #009c3b; border-color: #009c3b; }
</style>
""", unsafe_allow_html=True)

# Inicializa session state
for key, default in {
    "logged_in": False,
    "user_id":   None,
    "username":  None,
    "total_score": 0,
    "page": "Jogos",
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# --- Autenticacao ---
if not st.session_state.logged_in:
    from modules.ui_auth import render_login_page
    render_login_page()
    st.stop()

# --- Sidebar de navegacao ---
from modules.auth import logout

with st.sidebar:
    st.markdown("## COPA-SECOM")
    st.markdown(f"**{st.session_state.username}**")
    st.caption(f"{st.session_state.total_score} pts")
    st.divider()

    pages = ["Jogos", "Meus Palpites", "Ranking", "Apostas Especiais"]
    icons  = ["⚽", "📝", "🏆", "⭐"]

    for page, icon in zip(pages, icons):
        active = st.session_state.page == page
        if st.button(
            f"{icon}  {page}",
            key=f"nav_{page}",
            use_container_width=True,
            type="primary" if active else "secondary",
        ):
            st.session_state.page = page
            st.rerun()

    st.divider()
    if st.button("Sair", use_container_width=True):
        logout()

from modules.monitor import render_sidebar_monitor
render_sidebar_monitor()

# --- Renderiza a pagina ativa ---
page = st.session_state.page

if page == "Jogos":
    from modules.ui_dashboard import render_dashboard
    render_dashboard()

elif page == "Meus Palpites":
    from modules.ui_my_predictions import render_my_predictions
    render_my_predictions()

elif page == "Ranking":
    from modules.ui_ranking import render_ranking
    render_ranking()

elif page == "Apostas Especiais":
    from modules.ui_special_bets import render_special_bets
    render_special_bets()

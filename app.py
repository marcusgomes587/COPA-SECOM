import streamlit as st

st.set_page_config(
    page_title="COPA-SECOM 2026",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;900&family=Rajdhani:wght@600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* ── Fundo estadio: refletores + faixas de gramado (CSS-only) ── */
.stApp {
    background:
        radial-gradient(ellipse 55% 38% at 12% -6%, rgba(0,255,135,0.10), transparent 62%),
        radial-gradient(ellipse 55% 38% at 88% -6%, rgba(34,211,238,0.09), transparent 62%),
        radial-gradient(ellipse 85% 55% at 50% 112%, rgba(0,61,181,0.20), transparent 65%),
        repeating-linear-gradient(90deg, rgba(255,255,255,0.014) 0 90px, transparent 90px 180px),
        #0a0f1e;
    background-attachment: fixed;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0a0f1e 0%, #0d1426 100%);
    border-right: 1px solid rgba(0,255,135,0.35);
    box-shadow: 8px 0 32px rgba(0,255,135,0.05);
}
[data-testid="stSidebar"] * { color: #e7ecf5 !important; }
[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.10) !important; }
[data-testid="stSidebar"] .stButton > button {
    background: transparent;
    border: 1px solid rgba(255,255,255,0.14);
    border-radius: 12px;
    color: #e7ecf5 !important;
    text-align: left;
    font-weight: 600;
    transition: all 0.2s;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(0,255,135,0.10);
    border-color: rgba(0,255,135,0.6);
    box-shadow: 0 0 14px rgba(0,255,135,0.25);
    transform: translateX(4px);
}
[data-testid="stSidebar"] .stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #00ff87, #00d96f) !important;
    color: #06281a !important;
    border-color: transparent !important;
    box-shadow: 0 0 18px rgba(0,255,135,0.35);
}

/* ── Fundo geral ── */
.main .block-container { max-width: 860px; padding: 1.5rem 1rem; }

/* ── Botoes (area principal) ── */
.main .stButton > button { border-radius: 12px; font-weight: 700; }
.main .stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #00ff87, #00d96f);
    color: #06281a;
    border: none;
    box-shadow: 0 0 16px rgba(0,255,135,0.30);
    transition: all 0.2s;
}
.main .stButton > button[kind="primary"]:hover {
    box-shadow: 0 0 28px rgba(0,255,135,0.55);
    transform: translateY(-1px);
}
.main .stButton > button[kind="secondary"] {
    background: #121a2e;
    border: 1px solid rgba(255,255,255,0.14);
    color: #e7ecf5;
}

/* ── Hero header ── */
.copa-hero {
    background: linear-gradient(135deg, #0d1f3c 0%, #0a2e1f 100%);
    border: 1px solid rgba(0,255,135,0.25);
    border-radius: 18px;
    padding: 24px 28px;
    margin-bottom: 24px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: 0 0 40px rgba(0,255,135,0.10), inset 0 1px 0 rgba(255,255,255,0.05);
}
.copa-hero-title {
    font-family: 'Rajdhani', sans-serif;
    color: #ffe600;
    font-size: 30px;
    font-weight: 700;
    letter-spacing: 1px;
    margin: 0;
    text-shadow: 0 0 18px rgba(255,230,0,0.35);
}
.copa-hero-sub { color: #8b96ad; font-size: 13px; margin-top: 4px; }
.copa-hero-ball { font-size: 52px; line-height: 1; filter: drop-shadow(0 0 14px rgba(255,230,0,0.35)); }

/* ── Match Card ── */
.match-card {
    background: #121a2e;
    border-radius: 16px;
    margin-bottom: 14px;
    box-shadow: 0 4px 18px rgba(0,0,0,0.35);
    border: 1px solid rgba(255,255,255,0.08);
    overflow: hidden;
    transition: transform 0.18s, box-shadow 0.18s, border-color 0.18s;
}
.match-card:hover {
    transform: translateY(-3px);
    border-color: rgba(0,255,135,0.45);
    box-shadow: 0 0 24px rgba(0,255,135,0.16);
}

.match-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 8px 16px;
    background: #0d1426;
    border-bottom: 1px solid rgba(255,255,255,0.06);
}
.group-badge {
    background: rgba(0,255,135,0.10);
    color: #00ff87;
    border: 1px solid rgba(0,255,135,0.35);
    font-size: 10px;
    font-weight: 800;
    padding: 3px 9px;
    border-radius: 20px;
    letter-spacing: 0.8px;
    text-transform: uppercase;
}
.match-time { color: #8b96ad; font-size: 12px; font-weight: 600; }
.status-ns  { color: #8b96ad; font-size: 11px; }
.status-live {
    color: #ff4d6d; font-size: 11px; font-weight: 700;
    text-shadow: 0 0 10px rgba(255,77,109,0.5);
    animation: pulse 1.5s infinite;
}
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.5} }
.status-ft { color: #00ff87; font-size: 11px; font-weight: 700; }

.match-body {
    display: flex;
    align-items: center;
    padding: 18px 16px;
    gap: 8px;
}
.team-block { flex: 1; display: flex; align-items: center; gap: 10px; }
.team-block.away { flex-direction: row-reverse; justify-content: flex-start; }
.team-block img {
    width: 40px; height: 40px;
    border-radius: 6px;
    filter: drop-shadow(0 2px 6px rgba(0,0,0,0.6));
}
.team-flag { font-size: 30px; line-height: 1; }
.team-name { font-size: 15px; font-weight: 800; color: #e7ecf5; }
.team-block.away .team-name { text-align: right; }

/* ── Placar estilo painel eletronico ── */
.score-wrap {
    background: #060a14;
    border: 1px solid rgba(255,230,0,0.25);
    border-radius: 12px;
    padding: 10px 18px;
    text-align: center;
    min-width: 88px;
    box-shadow: inset 0 0 18px rgba(0,0,0,0.8), 0 0 14px rgba(255,230,0,0.08);
}
.score-num {
    font-family: 'Rajdhani', sans-serif;
    font-size: 28px; font-weight: 700; color: #ffe600;
    letter-spacing: 4px;
    text-shadow: 0 0 12px rgba(255,230,0,0.45);
}
.score-vs {
    font-family: 'Rajdhani', sans-serif;
    font-size: 14px; font-weight: 700;
    color: rgba(231,236,245,0.35); letter-spacing: 2px;
}

/* ── Pontuacao palpite ── */
.pts-badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 700;
}
.pts-5 { background: rgba(34,211,238,0.12); color: #22d3ee; border: 1px solid rgba(34,211,238,0.35); }
.pts-3 { background: rgba(0,255,135,0.12); color: #00ff87; border: 1px solid rgba(0,255,135,0.35); }
.pts-1 { background: rgba(255,230,0,0.12); color: #ffe600; border: 1px solid rgba(255,230,0,0.35); }
.pts-0 { background: rgba(139,150,173,0.12); color: #8b96ad; border: 1px solid rgba(139,150,173,0.30); }

/* ── Secao Mata-Mata ── */
.round-header {
    font-family: 'Rajdhani', sans-serif;
    background: linear-gradient(90deg, rgba(0,255,135,0.14), rgba(34,211,238,0.08));
    border: 1px solid rgba(0,255,135,0.30);
    color: #ffe600;
    font-weight: 700;
    font-size: 16px;
    letter-spacing: 2px;
    padding: 10px 18px;
    border-radius: 12px;
    margin: 20px 0 12px 0;
    text-transform: uppercase;
    text-shadow: 0 0 12px rgba(255,230,0,0.30);
}
.locked-card {
    background: rgba(255,255,255,0.03);
    border: 2px dashed rgba(139,150,173,0.35);
    border-radius: 14px;
    padding: 18px;
    text-align: center;
    color: #8b96ad;
    margin-bottom: 10px;
}
.locked-card .lock-icon { font-size: 22px; margin-bottom: 6px; }
.locked-card .lock-label { font-size: 13px; font-weight: 600; color: #8b96ad; }
.locked-card .lock-sub { font-size: 11px; color: #5d6880; }

/* ── Ranking ── */
.rank-podium { display: flex; justify-content: center; gap: 16px; margin-bottom: 20px; }
.podium-card {
    background: #121a2e;
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 18px 24px;
    text-align: center;
    box-shadow: 0 4px 18px rgba(0,0,0,0.35);
    min-width: 120px;
}
.podium-card.p1 {
    border-top: 3px solid #ffe600;
    box-shadow: 0 0 26px rgba(255,230,0,0.18);
}
.podium-card.p2 { border-top: 3px solid #9ca3af; }
.podium-card.p3 { border-top: 3px solid #cd7c3a; }
.podium-pos { font-size: 28px; }
.podium-name { font-size: 13px; font-weight: 700; color: #e7ecf5; margin-top: 6px; }
.podium-pts  { font-family: 'Rajdhani', sans-serif; font-size: 22px; font-weight: 700; color: #00ff87; text-shadow: 0 0 12px rgba(0,255,135,0.35); }

/* ── Countdown ── */
.countdown-pill {
    display: inline-block;
    background: rgba(255,230,0,0.08);
    border: 1px solid rgba(255,230,0,0.30);
    color: #ffe600;
    font-size: 11px;
    font-weight: 700;
    padding: 2px 10px;
    border-radius: 20px;
}

/* ── Card footer (palpite salvo + countdown) ── */
.card-footer {
    padding: 6px 16px 12px;
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
}
.saved-badge {
    display: inline-block;
    background: rgba(0,255,135,0.10);
    color: #00ff87;
    font-size: 11px;
    font-weight: 700;
    padding: 3px 10px;
    border-radius: 20px;
    border: 1px solid rgba(0,255,135,0.35);
}

/* ── Resultado do palpite (jogo encerrado) ── */
.pred-result {
    padding: 6px 16px 12px;
    font-size: 13px;
    color: #aab4c8;
}

/* ── Animacao de entrada ── */
@keyframes cardIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: none; } }
.match-card, .podium-card, .stats-card, .rank-row { animation: cardIn 0.35s ease both; }

/* Hover so em dispositivos com mouse */
@media (hover: none) {
  .match-card:hover { transform: none; border-color: rgba(255,255,255,0.08); box-shadow: 0 4px 18px rgba(0,0,0,0.35); }
}

/* ── Card de estatisticas pessoais ── */
.stats-card {
  display: flex; gap: 10px;
  background: #121a2e;
  border: 1px solid rgba(0,255,135,0.25);
  border-radius: 16px; padding: 16px; margin-bottom: 18px;
  box-shadow: 0 0 24px rgba(0,255,135,0.08);
}
.stat-box { flex: 1; text-align: center; }
.stat-val {
  font-family: 'Rajdhani', sans-serif;
  font-size: 24px; font-weight: 700; color: #ffe600;
  text-shadow: 0 0 12px rgba(255,230,0,0.35);
}
.stat-lbl {
  font-size: 10px; font-weight: 700; letter-spacing: 0.8px;
  text-transform: uppercase; color: #8b96ad; margin-top: 2px;
}

/* ── Linhas do ranking ── */
.rank-row {
  display: flex; align-items: center; gap: 10px;
  background: #121a2e; border: 1px solid rgba(255,255,255,0.08); border-radius: 12px;
  padding: 10px 14px; margin-bottom: 8px;
}
.rank-row.me {
  background: rgba(0,255,135,0.07);
  border-color: rgba(0,255,135,0.45);
  box-shadow: 0 0 16px rgba(0,255,135,0.12);
}
.rank-pos { font-family: 'Rajdhani', sans-serif; width: 34px; font-size: 17px; font-weight: 700; color: #22d3ee; text-align: center; }
.rank-name { flex: 1; font-size: 14px; font-weight: 700; color: #e7ecf5; display: flex; align-items: center; gap: 6px; flex-wrap: wrap; }
.rank-pts { font-family: 'Rajdhani', sans-serif; font-size: 18px; font-weight: 700; color: #00ff87; min-width: 64px; text-align: right; }
.rank-meta { font-size: 11px; color: #8b96ad; min-width: 110px; text-align: right; }
.mov-up { color: #00ff87; font-size: 12px; font-weight: 900; }
.mov-down { color: #ff4d6d; font-size: 12px; font-weight: 900; }
.mov-same { color: #5d6880; font-size: 12px; }
.craque-badge {
  background: linear-gradient(135deg, #ffe600, #fbbf24);
  color: #4a3203; font-size: 10px; font-weight: 800;
  padding: 2px 8px; border-radius: 20px; letter-spacing: 0.5px;
  box-shadow: 0 0 10px rgba(255,230,0,0.35);
}

/* ── Inputs com foco neon ── */
.stNumberInput input, .stTextInput input { border-radius: 10px; }
[data-baseweb="input"]:focus-within {
  border-color: #00ff87 !important;
  box-shadow: 0 0 0 1px rgba(0,255,135,0.6), 0 0 12px rgba(0,255,135,0.25);
}

/* ── Mobile (ate 640px) ── */
@media (max-width: 640px) {
  .stApp { background-attachment: scroll; }
  .main .block-container { padding: 0.8rem 0.6rem; }
  .copa-hero { padding: 16px 18px; border-radius: 14px; }
  .copa-hero-title { font-size: 21px; }
  .copa-hero-ball { font-size: 36px; }
  .match-body { padding: 12px 10px; gap: 6px; }
  .team-block img { width: 30px; height: 30px; }
  .team-name { font-size: 13px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; max-width: 96px; }
  .score-wrap { min-width: 64px; padding: 8px 10px; }
  .score-num { font-size: 21px; letter-spacing: 2px; }
  .stats-card { padding: 12px 8px; gap: 4px; }
  .stat-val { font-size: 18px; }
  .rank-podium { flex-direction: column; align-items: stretch; gap: 8px; }
  .podium-card { display: flex; align-items: center; justify-content: space-between; padding: 12px 16px; min-width: 0; }
  .podium-card.p1 { order: -1; padding: 16px; }
  .podium-pos { font-size: 22px; }
  .rank-meta { display: none; }
  .stButton > button { min-height: 44px; }
  .stNumberInput input { min-height: 44px; }
}
</style>
""", unsafe_allow_html=True)

# Session state
for key, default in {
    "logged_in": False, "user_id": None,
    "username": None, "total_score": 0, "page": "Grupos",
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

if not st.session_state.logged_in:
    from modules.ui_auth import render_login_page
    render_login_page()
    st.stop()

from modules.auth import logout
from modules.monitor import render_sidebar_monitor, is_admin

with st.sidebar:
    st.markdown("""
    <div style='text-align:center;padding:12px 0 4px'>
      <div style='font-size:32px;filter:drop-shadow(0 0 10px rgba(0,255,135,0.5))'>⚽</div>
      <div style='font-family:Rajdhani,sans-serif;font-size:18px;font-weight:700;color:#ffe600;letter-spacing:1px;text-shadow:0 0 12px rgba(255,230,0,0.4)'>COPA-SECOM</div>
      <div style='font-size:11px;color:#8b96ad'>Bolão Oficial 2026</div>
    </div>
    """, unsafe_allow_html=True)
    st.divider()
    st.markdown(f"**{st.session_state.username}**")
    st.caption(f"{st.session_state.total_score} pontos")
    st.divider()

    nav_items = [
        ("Grupos",   "Fase de Grupos"),
        ("Mata-Mata","Mata-Mata"),
        ("Palpites", "Meus Palpites"),
        ("Ranking",  "Ranking"),
        ("Especiais","Apostas Especiais"),
        ("Conta",    "Minha Conta"),
    ]
    for key, label in nav_items:
        active = st.session_state.page == key
        if st.button(label, key=f"nav_{key}", use_container_width=True,
                     type="primary" if active else "secondary"):
            st.session_state.page = key
            st.rerun()

    st.divider()
    if is_admin():
        if st.button("Painel Admin", use_container_width=True, key="nav_admin"):
            st.session_state.page = "Admin"
            st.rerun()

    if st.button("Sair", use_container_width=True, key="nav_sair"):
        logout()

render_sidebar_monitor()

# Hero header
from modules.stats import load_phase


@st.cache_data(ttl=300, show_spinner=False)
def _cached_phase():
    try:
        return load_phase()
    except Exception:
        return "Fase de Grupos"


phase = _cached_phase()
st.markdown(f"""
<div class="copa-hero">
  <div>
    <div class="copa-hero-title">COPA DO MUNDO 2026</div>
    <div class="copa-hero-sub">Bolão Oficial da SECOM · {phase}</div>
  </div>
  <div class="copa-hero-ball">🏆</div>
</div>
""", unsafe_allow_html=True)

page = st.session_state.page

if page == "Grupos":
    from modules.ui_dashboard import render_dashboard
    render_dashboard()
elif page == "Mata-Mata":
    from modules.ui_knockout import render_knockout
    render_knockout()
elif page == "Palpites":
    from modules.ui_my_predictions import render_my_predictions
    render_my_predictions()
elif page == "Ranking":
    from modules.ui_ranking import render_ranking
    render_ranking()
elif page == "Especiais":
    from modules.ui_special_bets import render_special_bets
    render_special_bets()
elif page == "Conta":
    from modules.ui_account import render_account
    render_account()
elif page == "Admin":
    from modules.ui_admin import render_admin
    render_admin()

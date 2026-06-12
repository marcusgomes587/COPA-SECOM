import streamlit as st

st.set_page_config(
    page_title="COPA-SECOM 2026",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;900&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #001a5e 0%, #002776 60%, #003399 100%);
    border-right: 3px solid #ffdf00;
}
[data-testid="stSidebar"] * { color: #fff !important; }
[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.15) !important; }
[data-testid="stSidebar"] .stButton > button {
    background: transparent;
    border: 1px solid rgba(255,255,255,0.2);
    border-radius: 8px;
    color: #fff !important;
    text-align: left;
    font-weight: 600;
    transition: all 0.2s;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(255,223,0,0.15);
    border-color: #ffdf00;
    transform: translateX(4px);
}
[data-testid="stSidebar"] .stButton > button[kind="primary"] {
    background: #ffdf00 !important;
    color: #002776 !important;
    border-color: #ffdf00 !important;
}

/* ── Fundo geral ── */
.main .block-container { max-width: 860px; padding: 1.5rem 1rem; }

/* ── Hero header ── */
.copa-hero {
    background: linear-gradient(135deg, #002776 0%, #009c3b 100%);
    border-radius: 16px;
    padding: 24px 28px;
    margin-bottom: 24px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: 0 8px 32px rgba(0,39,118,0.25);
}
.copa-hero-title { color: #ffdf00; font-size: 26px; font-weight: 900; letter-spacing: -0.5px; margin: 0; }
.copa-hero-sub { color: rgba(255,255,255,0.8); font-size: 13px; margin-top: 4px; }
.copa-hero-ball { font-size: 52px; line-height: 1; }

/* ── Match Card ── */
.match-card {
    background: #fff;
    border-radius: 14px;
    margin-bottom: 14px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.07);
    border: 1px solid #eaecf0;
    overflow: hidden;
    transition: transform 0.18s, box-shadow 0.18s;
}
.match-card:hover { transform: translateY(-3px); box-shadow: 0 8px 24px rgba(0,0,0,0.12); }

.match-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 8px 16px;
    background: #f7f8fa;
    border-bottom: 1px solid #eaecf0;
}
.group-badge {
    background: #002776;
    color: #ffdf00;
    font-size: 10px;
    font-weight: 800;
    padding: 3px 9px;
    border-radius: 20px;
    letter-spacing: 0.8px;
    text-transform: uppercase;
}
.match-time { color: #6b7280; font-size: 12px; font-weight: 600; }
.status-ns  { color: #6b7280; font-size: 11px; }
.status-live {
    color: #ef4444; font-size: 11px; font-weight: 700;
    animation: pulse 1.5s infinite;
}
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.5} }
.status-ft { color: #009c3b; font-size: 11px; font-weight: 700; }

.match-body {
    display: flex;
    align-items: center;
    padding: 18px 16px;
    gap: 8px;
}
.team-block { flex: 1; display: flex; align-items: center; gap: 10px; }
.team-block.away { flex-direction: row-reverse; justify-content: flex-start; }
.team-flag { font-size: 30px; line-height: 1; }
.team-name { font-size: 15px; font-weight: 800; color: #111827; }
.team-block.away .team-name { text-align: right; }

.score-wrap {
    background: linear-gradient(135deg, #002776, #003db5);
    border-radius: 12px;
    padding: 10px 18px;
    text-align: center;
    min-width: 88px;
    box-shadow: 0 4px 12px rgba(0,39,118,0.3);
}
.score-num { font-size: 26px; font-weight: 900; color: #fff; letter-spacing: 4px; }
.score-vs  { font-size: 13px; font-weight: 700; color: rgba(255,255,255,0.5); letter-spacing: 2px; }

/* ── Pontuação palpite ── */
.pts-badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 700;
}
.pts-5 { background: #dbeafe; color: #1d4ed8; }
.pts-3 { background: #dcfce7; color: #15803d; }
.pts-1 { background: #fef9c3; color: #92400e; }
.pts-0 { background: #f3f4f6; color: #9ca3af; }

/* ── Secao Mata-Mata ── */
.round-header {
    background: linear-gradient(90deg, #002776, #009c3b);
    color: #ffdf00;
    font-weight: 900;
    font-size: 14px;
    letter-spacing: 1px;
    padding: 10px 18px;
    border-radius: 10px;
    margin: 20px 0 12px 0;
    text-transform: uppercase;
}
.locked-card {
    background: #f9fafb;
    border: 2px dashed #d1d5db;
    border-radius: 12px;
    padding: 18px;
    text-align: center;
    color: #9ca3af;
    margin-bottom: 10px;
}
.locked-card .lock-icon { font-size: 22px; margin-bottom: 6px; }
.locked-card .lock-label { font-size: 13px; font-weight: 600; color: #6b7280; }
.locked-card .lock-sub { font-size: 11px; color: #9ca3af; }

/* ── Ranking ── */
.rank-podium { display: flex; justify-content: center; gap: 16px; margin-bottom: 20px; }
.podium-card {
    background: #fff;
    border-radius: 14px;
    padding: 18px 24px;
    text-align: center;
    box-shadow: 0 4px 16px rgba(0,0,0,0.08);
    min-width: 120px;
}
.podium-card.p1 { border-top: 4px solid #ffdf00; }
.podium-card.p2 { border-top: 4px solid #9ca3af; }
.podium-card.p3 { border-top: 4px solid #cd7c3a; }
.podium-pos { font-size: 28px; }
.podium-name { font-size: 13px; font-weight: 700; color: #111827; margin-top: 6px; }
.podium-pts  { font-size: 20px; font-weight: 900; color: #009c3b; }

/* ── Countdown ── */
.countdown-pill {
    display: inline-block;
    background: #fff7ed;
    border: 1px solid #fed7aa;
    color: #c2410c;
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
    background: #dcfce7;
    color: #15803d;
    font-size: 11px;
    font-weight: 700;
    padding: 3px 10px;
    border-radius: 20px;
    border: 1px solid #bbf7d0;
}

/* ── Resultado do palpite (jogo encerrado) ── */
.pred-result {
    padding: 6px 16px 12px;
    font-size: 13px;
    color: #374151;
}

/* ── Animacao de entrada ── */
@keyframes cardIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: none; } }
.match-card, .podium-card, .stats-card, .rank-row { animation: cardIn 0.35s ease both; }

/* Hover so em dispositivos com mouse */
@media (hover: none) {
  .match-card:hover { transform: none; box-shadow: 0 2px 12px rgba(0,0,0,0.07); }
}

/* ── Card de estatisticas pessoais ── */
.stats-card {
  display: flex; gap: 10px;
  background: linear-gradient(135deg, #001a5e 0%, #002776 60%, #003399 100%);
  border-radius: 16px; padding: 16px; margin-bottom: 18px;
  box-shadow: 0 8px 24px rgba(0,39,118,0.25);
}
.stat-box { flex: 1; text-align: center; }
.stat-val { font-size: 22px; font-weight: 900; color: #ffdf00; }
.stat-lbl {
  font-size: 10px; font-weight: 700; letter-spacing: 0.8px;
  text-transform: uppercase; color: rgba(255,255,255,0.7); margin-top: 2px;
}

/* ── Linhas do ranking ── */
.rank-row {
  display: flex; align-items: center; gap: 10px;
  background: #fff; border: 1px solid #eaecf0; border-radius: 12px;
  padding: 10px 14px; margin-bottom: 8px;
  box-shadow: 0 1px 6px rgba(0,0,0,0.05);
}
.rank-row.me { background: #e6f4ea; border-color: #86efac; }
.rank-pos { width: 34px; font-size: 15px; font-weight: 900; color: #002776; text-align: center; }
.rank-name { flex: 1; font-size: 14px; font-weight: 700; color: #111827; display: flex; align-items: center; gap: 6px; flex-wrap: wrap; }
.rank-pts { font-size: 16px; font-weight: 900; color: #009c3b; min-width: 64px; text-align: right; }
.rank-meta { font-size: 11px; color: #6b7280; min-width: 110px; text-align: right; }
.mov-up { color: #16a34a; font-size: 12px; font-weight: 900; }
.mov-down { color: #dc2626; font-size: 12px; font-weight: 900; }
.mov-same { color: #9ca3af; font-size: 12px; }
.craque-badge {
  background: linear-gradient(135deg, #ffdf00, #fbbf24);
  color: #78350f; font-size: 10px; font-weight: 800;
  padding: 2px 8px; border-radius: 20px; letter-spacing: 0.5px;
}

/* ── Mobile (ate 640px) ── */
@media (max-width: 640px) {
  .main .block-container { padding: 0.8rem 0.6rem; }
  .copa-hero { padding: 16px 18px; border-radius: 12px; }
  .copa-hero-title { font-size: 19px; }
  .copa-hero-ball { font-size: 36px; }
  .match-body { padding: 12px 10px; gap: 6px; }
  .team-name { font-size: 13px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; max-width: 110px; }
  .score-wrap { min-width: 64px; padding: 8px 10px; }
  .score-num { font-size: 20px; letter-spacing: 2px; }
  .stats-card { padding: 12px 8px; gap: 4px; }
  .stat-val { font-size: 17px; }
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
      <div style='font-size:32px'>⚽</div>
      <div style='font-size:17px;font-weight:900;color:#ffdf00;letter-spacing:-0.5px'>COPA-SECOM</div>
      <div style='font-size:11px;color:rgba(255,255,255,0.6)'>Bolão Oficial 2026</div>
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
elif page == "Admin":
    from modules.ui_admin import render_admin
    render_admin()

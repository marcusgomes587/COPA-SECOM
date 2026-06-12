# Dark Mode Neon + Gestao de Senhas — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Adicionar troca/reset de senha e aplicar o redesign dark mode neon ao COPA-SECOM.

**Architecture:** Funcoes de senha entram em `modules/auth.py` (puras testaveis + funcoes com banco), com UI em nova pagina `modules/ui_account.py` e nova secao no `modules/ui_admin.py`. O redesign e CSS-only: troca do bloco `<style>` em `app.py`, tema dark em `.streamlit/config.toml`, bandeiras Twemoji (funcao `flag_img` existente) nos cards.

**Tech Stack:** Streamlit, SQLAlchemy 2 + psycopg3, bcrypt, pytest. Spec: `docs/superpowers/specs/2026-06-12-dark-neon-e-senhas-design.md`.

**Restricao de ambiente:** rede do escritorio bloqueia porta 5432 (Neon). Testes pytest nao tocam banco; verificacao visual completa so em producao apos push.

---

### Task 1: Funcoes de senha em `modules/auth.py` (TDD)

**Files:**
- Test: `tests/test_auth.py` (criar)
- Modify: `modules/auth.py`

- [ ] **Step 1: Escrever os testes que devem falhar**

Criar `tests/test_auth.py`:

```python
from modules.auth import (
    TEMP_ALPHABET,
    generate_temp_password,
    hash_password,
    validate_new_password,
    verify_password,
)


def test_hash_e_verify_roundtrip():
    h = hash_password("minha-senha-123")
    assert h != "minha-senha-123"
    assert verify_password("minha-senha-123", h)


def test_senha_errada_rejeitada():
    h = hash_password("minha-senha-123")
    assert not verify_password("outra-senha", h)


def test_senha_temporaria_formato():
    temp = generate_temp_password()
    assert temp.startswith("copa-")
    sufixo = temp.removeprefix("copa-")
    assert len(sufixo) == 4
    assert all(c in TEMP_ALPHABET for c in sufixo)


def test_senha_temporaria_varia():
    geradas = {generate_temp_password() for _ in range(10)}
    assert len(geradas) > 1


def test_validate_nova_senha_curta():
    assert validate_new_password("abc", "abc") == "Senha deve ter pelo menos 6 caracteres."


def test_validate_confirmacao_diferente():
    assert validate_new_password("abcdef", "abcdeg") == "As senhas nao coincidem."


def test_validate_senha_ok():
    assert validate_new_password("abcdef", "abcdef") is None
```

- [ ] **Step 2: Rodar e confirmar que falham**

Run: `python -m pytest tests/test_auth.py -v`
Expected: FAIL/ERROR com `ImportError: cannot import name 'TEMP_ALPHABET'`

- [ ] **Step 3: Implementar em `modules/auth.py`**

Adicionar aos imports do topo:

```python
import secrets
import uuid
```

Adicionar ao final do arquivo:

```python
TEMP_ALPHABET = "abcdefghjkmnpqrstuvwxyz23456789"


def generate_temp_password() -> str:
    """Senha temporaria legivel, sem caracteres ambiguos (0/O, 1/l/i)."""
    return "copa-" + "".join(secrets.choice(TEMP_ALPHABET) for _ in range(4))


def validate_new_password(new: str, confirm: str) -> str | None:
    """Retorna mensagem de erro ou None se a nova senha e valida."""
    if len(new) < 6:
        return "Senha deve ter pelo menos 6 caracteres."
    if new != confirm:
        return "As senhas nao coincidem."
    return None


def change_password(user_id: str, current_password: str, new_password: str) -> tuple[bool, str]:
    session = get_session()
    try:
        user = session.get(User, uuid.UUID(user_id))
        if not user:
            return False, "Usuario nao encontrado."
        if not verify_password(current_password, user.password_hash):
            return False, "Senha atual incorreta."
        user.password_hash = hash_password(new_password)
        session.commit()
        return True, "Senha alterada com sucesso!"
    except Exception as e:
        session.rollback()
        return False, f"Erro ao alterar senha: {str(e)}"
    finally:
        session.close()


def admin_reset_password(username: str) -> tuple[bool, str]:
    """Gera senha temporaria para o usuario. Retorna (True, senha_em_claro) ou (False, erro)."""
    temp = generate_temp_password()
    session = get_session()
    try:
        user = session.execute(
            select(User).where(User.username == username)
        ).scalar_one_or_none()
        if not user:
            return False, "Usuario nao encontrado."
        user.password_hash = hash_password(temp)
        session.commit()
        return True, temp
    except Exception as e:
        session.rollback()
        return False, f"Erro ao redefinir senha: {str(e)}"
    finally:
        session.close()
```

- [ ] **Step 4: Rodar todos os testes**

Run: `python -m pytest -v`
Expected: 22 antigos + 7 novos = 29 PASS

- [ ] **Step 5: Commit**

```bash
git add tests/test_auth.py modules/auth.py
git commit -m "feat: troca de senha e reset por senha temporaria em auth"
```

---

### Task 2: Pagina "Conta" (trocar minha senha)

**Files:**
- Create: `modules/ui_account.py`
- Modify: `app.py` (nav_items e roteamento)

- [ ] **Step 1: Criar `modules/ui_account.py`**

```python
import streamlit as st
from modules.auth import change_password, validate_new_password


def render_account():
    st.subheader("Minha Conta")
    st.caption(f"Usuario: {st.session_state.username}")

    with st.form("form_change_password", clear_on_submit=True):
        st.markdown("**Trocar senha**")
        current = st.text_input("Senha atual", type="password")
        new = st.text_input("Nova senha", type="password", placeholder="minimo 6 caracteres")
        confirm = st.text_input("Confirmar nova senha", type="password")
        submitted = st.form_submit_button("Alterar senha", type="primary", use_container_width=True)

    if submitted:
        if not current or not new or not confirm:
            st.error("Preencha todos os campos.")
            return
        error = validate_new_password(new, confirm)
        if error:
            st.error(error)
            return
        ok, msg = change_password(st.session_state.user_id, current, new)
        if ok:
            st.success(msg)
        else:
            st.error(msg)
```

- [ ] **Step 2: Registrar na navegacao em `app.py`**

Em `nav_items`, acrescentar ao final da lista:

```python
        ("Conta",    "Minha Conta"),
```

No roteamento (cadeia de `elif page == ...`), antes do bloco `elif page == "Admin":`, acrescentar:

```python
elif page == "Conta":
    from modules.ui_account import render_account
    render_account()
```

- [ ] **Step 3: Smoke test de import**

Run: `python -c "import ast; ast.parse(open('app.py', encoding='utf-8').read()); import modules.ui_account; print('ok')"`
Expected: `ok`

- [ ] **Step 4: Commit**

```bash
git add modules/ui_account.py app.py
git commit -m "feat: pagina Conta com troca de senha"
```

---

### Task 3: Secao "Usuarios" no Painel Admin (reset de senha)

**Files:**
- Modify: `modules/ui_admin.py`

- [ ] **Step 1: Adicionar imports**

No topo de `modules/ui_admin.py`, trocar:

```python
from modules.models import Match
```

por:

```python
from modules.models import Match, User
```

- [ ] **Step 2: Adicionar a secao logo apos o caption inicial**

Em `render_admin()`, imediatamente apos `st.caption("Visivel apenas para o administrador.")`, inserir:

```python
    with st.expander("Usuarios — redefinir senha"):
        st.caption("Para quem esqueceu a senha: gere uma temporaria e repasse. A pessoa troca depois em 'Minha Conta'.")
        session = get_session()
        usernames = [u for (u,) in session.execute(
            select(User.username).order_by(User.username)
        ).all()]
        session.close()
        if not usernames:
            st.info("Nenhum usuario cadastrado.")
        else:
            sel = st.selectbox("Usuario", usernames, key="reset_pw_user")
            if st.button("Gerar senha temporaria", key="btn_reset_pw", type="primary"):
                from modules.auth import admin_reset_password
                ok, result = admin_reset_password(sel)
                if ok:
                    st.success("Senha temporaria gerada — copie agora, ela nao sera mostrada de novo:")
                    st.code(result)
                else:
                    st.error(result)
```

- [ ] **Step 3: Smoke test + pytest**

Run: `python -c "import modules.ui_admin; print('ok')" && python -m pytest -q`
Expected: `ok` e 29 PASS

- [ ] **Step 4: Commit**

```bash
git add modules/ui_admin.py
git commit -m "feat: admin redefine senha de usuario com senha temporaria"
```

---

### Task 4: Tema dark no `.streamlit/config.toml`

**Files:**
- Modify: `.streamlit/config.toml`

- [ ] **Step 1: Substituir a secao `[theme]`**

Conteudo completo novo do arquivo:

```toml
[theme]
base = "dark"
primaryColor = "#00ff87"
backgroundColor = "#0a0f1e"
secondaryBackgroundColor = "#121a2e"
textColor = "#e7ecf5"
font = "sans serif"

[server]
headless = true
enableCORS = false

[browser]
gatherUsageStats = false
```

- [ ] **Step 2: Commit**

```bash
git add .streamlit/config.toml
git commit -m "feat: tema dark nativo do Streamlit (inputs, tabs, expanders)"
```

---

### Task 5: CSS dark neon em `app.py`

**Files:**
- Modify: `app.py` (bloco `<style>` completo + brand da sidebar)

- [ ] **Step 1: Substituir o bloco `st.markdown("""<style> ... </style>""")` inteiro (linhas 10-281) por:**

```python
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
```

- [ ] **Step 2: Atualizar brand da sidebar em `app.py`**

Trocar o bloco do brand (dentro de `with st.sidebar:`):

```python
    st.markdown("""
    <div style='text-align:center;padding:12px 0 4px'>
      <div style='font-size:32px;filter:drop-shadow(0 0 10px rgba(0,255,135,0.5))'>⚽</div>
      <div style='font-family:Rajdhani,sans-serif;font-size:18px;font-weight:700;color:#ffe600;letter-spacing:1px;text-shadow:0 0 12px rgba(255,230,0,0.4)'>COPA-SECOM</div>
      <div style='font-size:11px;color:#8b96ad'>Bolão Oficial 2026</div>
    </div>
    """, unsafe_allow_html=True)
```

- [ ] **Step 3: Smoke test de sintaxe**

Run: `python -c "import ast; ast.parse(open('app.py', encoding='utf-8').read()); print('ok')"`
Expected: `ok`

- [ ] **Step 4: Commit**

```bash
git add app.py
git commit -m "feat: dark mode neon - fundo estadio, glow, Rajdhani, cards escuros"
```

---

### Task 6: Bandeiras grandes nos cards + estilos inline dark

**Files:**
- Modify: `modules/ui_dashboard.py`
- Modify: `modules/ui_knockout.py`

- [ ] **Step 1: Bandeiras no card da fase de grupos**

Em `modules/ui_dashboard.py`, trocar o import:

```python
from modules.flags import MATCH_GROUP
```

por:

```python
from modules.flags import MATCH_GROUP, flag_img
```

Em `_render_card`, no HTML do card, trocar os dois `team-block`:

```python
        <div class="team-block">
          {flag_img(m.home_team, 40)}<span class="team-name">{m.home_team}</span>
        </div>
        <div class="score-wrap">{score_html}</div>
        <div class="team-block away">
          {flag_img(m.away_team, 40)}<span class="team-name">{m.away_team}</span>
        </div>
```

- [ ] **Step 2: Pill "Palpites encerrados" em dark**

Na linha 149 de `modules/ui_dashboard.py`, trocar por:

```python
        extra = '<span class="countdown-pill" style="background:rgba(255,77,109,0.10);border-color:rgba(255,77,109,0.40);color:#ff4d6d">Palpites encerrados</span>'
```

- [ ] **Step 3: Bandeiras no card do mata-mata**

Em `modules/ui_knockout.py`, adicionar ao import do topo:

```python
from modules.flags import flag_img
```

Em `_render_knockout_card`, trocar os dois `team-block` no HTML:

```python
        <div class="team-block">
          {flag_img(match.home_team, 40)}<span class="team-name">{match.home_team}</span>
        </div>
        <div class="score-wrap">{score_html}</div>
        <div class="team-block away">
          {flag_img(match.away_team, 40)}<span class="team-name">{match.away_team}</span>
        </div>
```

(`flag_img` retorna string vazia para time desconhecido — placeholders tipo "A definir" ficam sem bandeira, sem erro.)

- [ ] **Step 4: Smoke test + pytest**

Run: `python -c "import modules.ui_dashboard, modules.ui_knockout; print('ok')" && python -m pytest -q`
Expected: `ok` e 29 PASS

- [ ] **Step 5: Commit**

```bash
git add modules/ui_dashboard.py modules/ui_knockout.py
git commit -m "feat: bandeiras Twemoji grandes nos cards de jogo"
```

---

### Task 7: Tela de login em dark

**Files:**
- Modify: `modules/ui_auth.py`

- [ ] **Step 1: Atualizar o header**

Trocar o bloco `st.markdown` do inicio de `render_login_page()` por:

```python
    st.markdown("""
        <style>
        .auth-header {
            text-align: center;
            padding: 2rem 0 1rem 0;
        }
        .auth-header h1 {
            font-family: 'Rajdhani', sans-serif;
            font-size: 2.6rem;
            color: #ffe600;
            margin: 0;
            letter-spacing: 2px;
            text-shadow: 0 0 20px rgba(255,230,0,0.35);
        }
        .auth-header p  { color: #8b96ad; margin-top: .4rem; }
        </style>
        <div class="auth-header">
            <h1>COPA-SECOM 2026</h1>
            <p>Bolao exclusivo para a equipe</p>
        </div>
    """, unsafe_allow_html=True)
```

- [ ] **Step 2: Smoke test**

Run: `python -c "import modules.ui_auth; print('ok')"`
Expected: `ok`

- [ ] **Step 3: Commit**

```bash
git add modules/ui_auth.py
git commit -m "feat: tela de login no tema dark neon"
```

---

### Task 8: Verificacao final e deploy

**Files:** nenhum (verificacao)

- [ ] **Step 1: Suite completa**

Run: `python -m pytest -v`
Expected: 29 PASS

- [ ] **Step 2: Compilacao de todos os modulos**

Run: `python -m compileall -q app.py modules && echo OK`
Expected: `OK`

- [ ] **Step 3: Screenshot local da tela de login (unica tela sem banco)**

Subir `streamlit run app.py --server.port 8511` em background e capturar screenshot da tela de login com Playwright (skill webapp-testing), desktop (1280x800) e mobile (390x844). Conferir: fundo escuro com brilho de refletores, titulo amarelo neon Rajdhani, inputs dark com foco verde.
Se o Streamlit nao subir por qualquer motivo de ambiente, registrar e seguir (verificacao final sera em producao).

- [ ] **Step 4: Push (deploy automatico)**

```bash
git push origin main
```

- [ ] **Step 5: Usuario revisa em producao**

Avisar o usuario para conferir https://copa-secom-3ymwcweyz5wwujfbjlc7za.streamlit.app/ (forcar reload/limpar cache do app no Streamlit Cloud se necessario) e testar: login, dashboard com bandeiras, ranking, pagina Conta (trocar senha), admin (reset de senha).

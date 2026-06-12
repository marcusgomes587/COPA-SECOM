# Redesign Visual + Responsividade Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Upgrade visual do bolao COPA-SECOM com responsividade mobile, card de estatisticas pessoais, ranking com setas de movimento e craque da rodada, correcao do bug dos Exatos e polimento do admin — sem nenhuma mudanca de schema ou escrita nova no banco.

**Architecture:** Toda logica nova de calculo (aproveitamento, sequencia, posicoes, movimento, craque) vive em `modules/stats.py` como funcoes puras testaveis com pytest, mais loaders finos que consultam o banco e delegam para as funcoes puras. CSS continua centralizado no bloco unico de `app.py`. Spec: `docs/superpowers/specs/2026-06-12-redesign-responsivo-design.md`.

**Tech Stack:** Streamlit 1.58+, SQLAlchemy 2.0 + psycopg3 (Neon PostgreSQL), pytest (somente dev local, NAO adicionar ao requirements.txt).

**Restricao critica:** Nenhuma migracao, nenhuma tabela nova, nenhum UPDATE/DELETE novo. Os unicos caminhos de escrita continuam sendo os existentes (salvar palpite, salvar placar no admin).

---

### Task 1: Funcoes puras de estatistica (`modules/stats.py`) — TDD

**Files:**
- Create: `modules/stats.py`
- Test: `tests/test_stats.py`
- Create: `tests/__init__.py` (vazio)

- [ ] **Step 1: Instalar pytest (somente local)**

Run: `pip install pytest`
NAO adicionar pytest ao `requirements.txt` (o Streamlit Cloud nao precisa dele).

- [ ] **Step 2: Criar `tests/__init__.py` vazio e escrever os testes que devem falhar**

Conteudo completo de `tests/test_stats.py`:

```python
from modules.stats import (
    aproveitamento,
    current_streak,
    ranking_positions,
    movement,
    round_top_scorers,
)


# ── aproveitamento ──

def test_aproveitamento_sem_palpites_retorna_none():
    assert aproveitamento([]) is None


def test_aproveitamento_todos_pontuaram():
    assert aproveitamento([5, 3, 1]) == 100


def test_aproveitamento_metade_pontuou():
    assert aproveitamento([5, 0, 3, 0]) == 50


def test_aproveitamento_arredonda():
    # 2 de 3 = 66.67 -> 67
    assert aproveitamento([3, 1, 0]) == 67


# ── current_streak ──

def test_streak_vazia():
    assert current_streak([]) == 0


def test_streak_conta_consecutivos_do_mais_recente():
    # mais recente primeiro: pontuou, pontuou, errou, pontuou
    assert current_streak([3, 5, 0, 3]) == 2


def test_streak_zero_se_errou_o_ultimo():
    assert current_streak([0, 5, 3]) == 0


def test_streak_none_quebra_sequencia():
    # None = nao palpitou naquele jogo
    assert current_streak([3, None, 5]) == 1


# ── ranking_positions ──

def test_ranking_ordena_por_pontos_desc():
    pos = ranking_positions([("ana", 10), ("bia", 30), ("caio", 20)])
    assert pos == {"bia": 1, "caio": 2, "ana": 3}


def test_ranking_vazio():
    assert ranking_positions([]) == {}


# ── movement ──

def test_movement_subiu_desceu_manteve():
    current = {"ana": 1, "bia": 2, "caio": 3}
    previous = {"ana": 2, "bia": 1, "caio": 3}
    mov = movement(current, previous)
    assert mov == {"ana": "up", "bia": "down", "caio": "same"}


def test_movement_usuario_novo_e_same():
    mov = movement({"ana": 1}, {})
    assert mov == {"ana": "same"}


# ── round_top_scorers ──

def test_craque_unico():
    assert round_top_scorers({"ana": 8, "bia": 5}) == ["ana"]


def test_craque_empate_retorna_todos():
    result = round_top_scorers({"ana": 8, "bia": 8, "caio": 3})
    assert sorted(result) == ["ana", "bia"]


def test_craque_ninguem_pontuou_retorna_vazio():
    assert round_top_scorers({"ana": 0, "bia": 0}) == []


def test_craque_dict_vazio():
    assert round_top_scorers({}) == []
```

- [ ] **Step 3: Rodar os testes e confirmar que falham**

Run: `python -m pytest tests/test_stats.py -v`
Expected: FAIL com `ModuleNotFoundError: No module named 'modules.stats'`

- [ ] **Step 4: Implementar as funcoes puras**

Conteudo de `modules/stats.py` (parte 1 — funcoes puras; os loaders entram nas Tasks 3 e 4):

```python
from datetime import timedelta, timezone

BRT = timezone(timedelta(hours=-3))
FINISHED = ("FT", "AET", "PEN")


def aproveitamento(points_list):
    """points_list: points_earned do usuario em jogos encerrados onde palpitou.
    Retorna percentual inteiro 0-100, ou None se nao ha palpites encerrados."""
    if not points_list:
        return None
    scored = sum(1 for p in points_list if p > 0)
    return round(100 * scored / len(points_list))


def current_streak(points_desc):
    """points_desc: pontos por jogo encerrado, do mais recente para o mais antigo.
    None = usuario nao palpitou naquele jogo (quebra a sequencia)."""
    streak = 0
    for p in points_desc:
        if p is not None and p > 0:
            streak += 1
        else:
            break
    return streak


def ranking_positions(scores):
    """scores: lista de (username, pontos). Retorna dict username -> posicao 1-based."""
    ordered = sorted(scores, key=lambda s: s[1], reverse=True)
    return {name: i + 1 for i, (name, _) in enumerate(ordered)}


def movement(current_pos, previous_pos):
    """Compara posicoes. Retorna dict username -> 'up' | 'down' | 'same'."""
    result = {}
    for name, pos in current_pos.items():
        prev = previous_pos.get(name)
        if prev is None or prev == pos:
            result[name] = "same"
        elif pos < prev:
            result[name] = "up"
        else:
            result[name] = "down"
    return result


def round_top_scorers(points_by_user):
    """points_by_user: dict username -> pontos na ultima rodada.
    Retorna usernames com a maior pontuacao (se > 0); lista vazia caso contrario."""
    if not points_by_user:
        return []
    best = max(points_by_user.values())
    if best <= 0:
        return []
    return [u for u, p in points_by_user.items() if p == best]


def last_finished_day(matches):
    """matches: iteravel de Match. Retorna a date BRT do ultimo dia com jogo
    encerrado, ou None se nenhum jogo encerrou ainda."""
    days = [
        m.kickoff_time.astimezone(BRT).date()
        for m in matches if m.status in FINISHED
    ]
    return max(days) if days else None


def current_phase(matches):
    """Fase atual do torneio derivada dos jogos: 'Mata-Mata' quando toda a fase
    de grupos (match_id 1001-1072) encerrou, senao 'Fase de Grupos'."""
    group = [m for m in matches if 1001 <= m.match_id <= 1072]
    if group and all(m.status in FINISHED for m in group):
        return "Mata-Mata"
    return "Fase de Grupos"
```

- [ ] **Step 5: Rodar os testes e confirmar que passam**

Run: `python -m pytest tests/test_stats.py -v`
Expected: 16 passed

- [ ] **Step 6: Commit**

```bash
git add modules/stats.py tests/__init__.py tests/test_stats.py
git commit -m "feat: funcoes puras de estatistica (aproveitamento, streak, ranking, craque)"
```

---

### Task 2: CSS global responsivo + hero dinamico (`app.py`)

**Files:**
- Modify: `app.py` (bloco `<style>` linhas 10-216 e hero linhas 272-281)

- [ ] **Step 1: Acrescentar o CSS novo ao final do bloco `<style>` existente**

Em `app.py`, inserir ANTES do `</style>` (linha 215) o bloco abaixo. Nao remover nenhuma regra existente.

```css
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
```

- [ ] **Step 2: Tornar o subtitulo do hero dinamico**

Em `app.py`, substituir o bloco do hero (linhas 272-281):

```python
# Hero header
from modules.stats import load_phase
phase = load_phase()
st.markdown(f"""
<div class="copa-hero">
  <div>
    <div class="copa-hero-title">COPA DO MUNDO 2026</div>
    <div class="copa-hero-sub">Bolao Oficial da SECOM &middot; {phase}</div>
  </div>
  <div class="copa-hero-ball">&#127942;</div>
</div>
""", unsafe_allow_html=True)
```

E acrescentar o loader ao FINAL de `modules/stats.py`:

```python
def load_phase():
    """Loader: fase atual do torneio a partir do banco."""
    from sqlalchemy import select
    from modules.database import get_session
    from modules.models import Match

    session = get_session()
    try:
        matches = session.execute(select(Match)).scalars().all()
    finally:
        session.close()
    return current_phase(matches)
```

(Imports dentro da funcao para manter as funcoes puras importaveis nos testes sem precisar de banco/secrets.)

- [ ] **Step 3: Smoke test local**

Run: `streamlit run app.py` e abrir http://localhost:8501
Expected: app carrega sem erro, hero mostra "Bolao Oficial da SECOM · Fase de Grupos", visual existente intacto. Encerrar com Ctrl+C.

- [ ] **Step 4: Commit**

```bash
git add app.py modules/stats.py
git commit -m "feat: CSS responsivo mobile, animacoes e hero com fase dinamica"
```

---

### Task 3: Card de estatisticas pessoais no dashboard

**Files:**
- Modify: `modules/stats.py` (adicionar loader)
- Modify: `modules/ui_dashboard.py` (render do card em `render_dashboard`)

- [ ] **Step 1: Adicionar o loader de estatisticas ao final de `modules/stats.py`**

```python
def load_user_stats(user_id, username):
    """Loader: estatisticas pessoais do usuario para o card do dashboard."""
    from sqlalchemy import select
    from modules.database import get_session
    from modules.models import Match, Prediction, User

    session = get_session()
    try:
        users = session.execute(select(User.username, User.total_score)).all()
        finished = session.execute(
            select(Match)
            .where(Match.status.in_(FINISHED))
            .order_by(Match.kickoff_time.desc())
        ).scalars().all()
        preds = {
            p.match_id: p.points_earned
            for p in session.execute(
                select(Prediction).where(Prediction.user_id == user_id)
            ).scalars().all()
        }
    finally:
        session.close()

    positions = ranking_positions([(u, s) for u, s in users])
    pts_finished = [preds[m.match_id] for m in finished if m.match_id in preds]
    return {
        "pontos": dict(users).get(username, 0),
        "posicao": positions.get(username, 0),
        "total_users": len(positions),
        "aproveitamento": aproveitamento(pts_finished),
        "sequencia": current_streak([preds.get(m.match_id) for m in finished]),
    }
```

- [ ] **Step 2: Renderizar o card no topo do dashboard**

Em `modules/ui_dashboard.py`, dentro de `render_dashboard()`, logo APOS `if not matches: ... return` e ANTES do calculo de `dates`, inserir:

```python
    from modules.stats import load_user_stats
    stats = load_user_stats(st.session_state.user_id, st.session_state.username)
    ap = f"{stats['aproveitamento']}%" if stats["aproveitamento"] is not None else "&mdash;"
    st.markdown(f"""
    <div class="stats-card">
      <div class="stat-box"><div class="stat-val">{stats['pontos']}</div><div class="stat-lbl">Pontos</div></div>
      <div class="stat-box"><div class="stat-val">{stats['posicao']}&ordm;</div><div class="stat-lbl">de {stats['total_users']}</div></div>
      <div class="stat-box"><div class="stat-val">{ap}</div><div class="stat-lbl">Aproveitamento</div></div>
      <div class="stat-box"><div class="stat-val">{stats['sequencia']}</div><div class="stat-lbl">Sequencia</div></div>
    </div>
    """, unsafe_allow_html=True)
```

- [ ] **Step 3: Verificar local**

Run: `streamlit run app.py`, logar e abrir a pagina Grupos.
Expected: card azul com 4 metricas acima do seletor de data. Sem jogos encerrados no banco, Aproveitamento mostra travessao e Sequencia mostra 0.

- [ ] **Step 4: Rodar os testes para garantir que nada quebrou**

Run: `python -m pytest tests/ -v`
Expected: 16 passed

- [ ] **Step 5: Commit**

```bash
git add modules/stats.py modules/ui_dashboard.py
git commit -m "feat: card de estatisticas pessoais no dashboard"
```

---

### Task 4: Ranking — correcao do bug Exatos, setas de movimento, craque da rodada, layout responsivo

**Files:**
- Modify: `modules/stats.py` (adicionar loader do ranking)
- Modify: `modules/ui_ranking.py` (reescrever `render_ranking`)

**Contexto do bug:** `ui_ranking.py:28` conta `Prediction.points_earned == 3` como "Exatos", mas placar exato vale 5 pontos desde a mudanca de pontuacao. 3 pontos = acertou o vencedor. A correcao e apenas na consulta de exibicao — nenhum ponto gravado muda.

- [ ] **Step 1: Adicionar o loader do ranking ao final de `modules/stats.py`**

```python
def load_ranking_data():
    """Loader: linhas do ranking com movimento de posicao e craque da rodada.

    'Ultima rodada' = ultimo dia-calendario BRT com pelo menos um jogo encerrado.
    Posicao anterior = ranking recalculado subtraindo os pontos desse dia
    (derivavel porque total_score e a soma de points_earned).
    """
    from sqlalchemy import select
    from modules.database import get_session
    from modules.models import Match, Prediction, User

    session = get_session()
    try:
        users = session.execute(
            select(User).order_by(User.total_score.desc())
        ).scalars().all()
        finished = session.execute(
            select(Match).where(Match.status.in_(FINISHED))
        ).scalars().all()
        preds = session.execute(select(Prediction)).scalars().all()
        user_rows = [(u.id, u.username, u.total_score) for u in users]
    finally:
        session.close()

    last_day = last_finished_day(finished)
    last_ids = {
        m.match_id for m in finished
        if last_day and m.kickoff_time.astimezone(BRT).date() == last_day
    }

    rows = []
    last_round_pts = {}
    for uid, name, score in user_rows:
        user_preds = [p for p in preds if p.user_id == uid]
        last_pts = sum(p.points_earned for p in user_preds if p.match_id in last_ids)
        last_round_pts[name] = last_pts
        rows.append({
            "name": name,
            "pts": score,
            "total": len(user_preds),
            "exact": sum(1 for p in user_preds if p.points_earned == 5),
            "last_pts": last_pts,
        })

    current = ranking_positions([(r["name"], r["pts"]) for r in rows])
    previous = ranking_positions([(r["name"], r["pts"] - r["last_pts"]) for r in rows])
    mov = movement(current, previous)
    craques = round_top_scorers(last_round_pts)

    rows.sort(key=lambda r: r["pts"], reverse=True)
    for i, r in enumerate(rows, 1):
        r["pos"] = i
        r["mov"] = mov[r["name"]] if last_day else "same"
        r["craque"] = r["name"] in craques
    return rows
```

- [ ] **Step 2: Reescrever `modules/ui_ranking.py` por completo**

Conteudo integral do arquivo apos a reescrita:

```python
import streamlit as st
from modules.stats import load_ranking_data

MEDALS = ["&#129351;", "&#129352;", "&#129353;"]  # ouro, prata, bronze (entidades HTML)
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
          <div class="podium-name">{r["name"]}</div>
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
          <div class="rank-name">{r["name"]} {craque}</div>
          <div class="rank-meta">{r["total"]} palpites &middot; {r["exact"]} exatos</div>
          <div class="rank-pts">{r["pts"]} pts</div>
        </div>"""
    st.markdown(rows_html, unsafe_allow_html=True)

    user_row = next((r for r in rows if r["name"] == current_user), None)
    if user_row:
        st.success(
            f"Voce esta em **{user_row['pos']}&ordm; lugar** &mdash; "
            f"**{user_row['pts']} pontos** | "
            f"{user_row['exact']} placar(es) exato(s)"
        )

    if st.button("Atualizar", use_container_width=True):
        st.rerun()
```

Observacoes:
- `pandas` deixa de ser usado aqui (era so para o dataframe). NAO remover do `requirements.txt` — outros modulos podem usar.
- O import de `get_flag` foi removido junto (nao era usado).
- As medalhas continuam as mesmas do visual atual, agora como entidades HTML.

- [ ] **Step 3: Verificar local**

Run: `streamlit run app.py`, logar e abrir Ranking.
Expected: podio + linhas estilizadas; linha do usuario logado com fundo verde; coluna de exatos contando apenas placares exatos (5 pts). Sem jogos encerrados, todas as setas ficam neutras e ninguem tem badge de craque.

- [ ] **Step 4: Rodar os testes**

Run: `python -m pytest tests/ -v`
Expected: 16 passed

- [ ] **Step 5: Commit**

```bash
git add modules/stats.py modules/ui_ranking.py
git commit -m "feat: ranking com setas de movimento e craque da rodada; corrige contagem de exatos (5 pts)"
```

---

### Task 5: Polimento do Painel Admin

**Files:**
- Modify: `modules/ui_admin.py`

- [ ] **Step 1: Adicionar contador de progresso no topo**

Em `render_admin()`, logo apos obter `all_matches` (e o early-return de lista vazia), inserir:

```python
    FINISHED_ST = ("FT", "AET", "PEN")
    group = [m for m in all_matches if 1001 <= m.match_id <= 1072]
    done = sum(1 for m in group if m.status in FINISHED_ST)
    if group:
        st.progress(done / len(group))
        st.caption(f"{done} de {len(group)} jogos da fase de grupos com placar lancado")
    knockout_all = [m for m in all_matches if m.match_id >= 2000]
    if knockout_all:
        ko_done = sum(1 for m in knockout_all if m.status in FINISHED_ST)
        st.caption(f"Mata-mata: {ko_done} de {len(knockout_all)} jogos encerrados")
```

- [ ] **Step 2: Trocar os emojis de status por indicador de cor**

Em `_render_round()`, substituir o bloco do `status_icon` (linhas 72-73):

```python
        status_dot = {
            "FT": ":green[&#9679;]", "AET": ":green[&#9679;]", "PEN": ":green[&#9679;]",
            "1H": ":red[&#9679;]", "2H": ":red[&#9679;]", "ET": ":red[&#9679;]",
            "HT": ":orange[&#9679;]",
        }.get(m.status, ":gray[&#9679;]")
```

E na chamada do `st.expander`, trocar `{status_icon}` por `{status_dot}`.

Nota: se a sintaxe de cor `:green[...]` nao renderizar no rotulo do expander nesta versao do Streamlit, usar texto simples no lugar do dot: `{"FT": "Encerrado", "AET": "Encerrado", "PEN": "Encerrado", "NS": "Agendado"}.get(m.status, "Ao vivo")`.

- [ ] **Step 3: Verificar local**

Run: `streamlit run app.py`, logar como admin (Marcus Gabriel) e abrir Painel Admin.
Expected: barra de progresso "0 de 72" (ou contagem real), expanders com indicador colorido de status, fluxo de salvar placar intacto.

- [ ] **Step 4: Commit**

```bash
git add modules/ui_admin.py
git commit -m "feat: painel admin com progresso de placares e status por cor"
```

---

### Task 6: Verificacao visual mobile + desktop (Playwright)

**Files:** nenhum (verificacao)

- [ ] **Step 1: Subir o app local**

Run: `streamlit run app.py` (em background, porta 8501)

- [ ] **Step 2: Capturar screenshots com Playwright (usar a skill webapp-testing)**

Para cada viewport — mobile 390x844 e desktop 1280x800 — logar e capturar as paginas: Grupos, Ranking, Mata-Mata e Painel Admin. As credenciais de login devem ser pedidas ao usuario na hora (nao estao no repositorio).

Checklist do que verificar nas capturas:
- Mobile: hero compacto; nomes de times sem estourar o card; placar central reduzido; podio empilhado com 1o lugar no topo; coluna "palpites/exatos" oculta nas linhas do ranking; botoes com altura confortavel de toque.
- Desktop: hover dos cards funcionando; podio lado a lado; linhas do ranking com todas as colunas.
- Ambos: card de estatisticas com 4 metricas; nenhum erro no console do Streamlit.

- [ ] **Step 3: Conferir que nenhum dado mudou**

No Ranking, conferir que os pontos totais exibidos de cada usuario sao os mesmos de antes do redesign (a correcao dos Exatos muda contagem exibida, nao pontos). Em caso de duvida, comparar com a aba Ranking do app em producao.

- [ ] **Step 4: Encerrar o app e commit final (se houve ajustes)**

```bash
git add -A
git commit -m "fix: ajustes visuais pos-verificacao mobile/desktop"
```

(So commitar se a verificacao gerou ajustes.)

---

## Pos-implementacao

- O push para o GitHub (que dispara o deploy no Streamlit Cloud) e feito pelo usuario apos validar localmente.
- Lembrete ja existente da spec: nenhuma mudanca de schema foi feita; nao ha passo de migracao no deploy.

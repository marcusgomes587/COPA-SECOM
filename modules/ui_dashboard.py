from datetime import datetime, timezone
import streamlit as st
from sqlalchemy import select
from modules.database import get_session
from modules.models import Match, Prediction
from modules.flags import get_flag, MATCH_GROUP
from modules.scoring import calculate_points

LOCK_MINUTES = 30

STATUS_LABEL = {
    "NS": "Agendado", "1H": "1° Tempo", "HT": "Intervalo",
    "2H": "2° Tempo", "ET": "Prorrogação", "PEN": "Pênaltis",
    "FT": "Encerrado", "AET": "Encerrado", "SUSP": "Suspenso",
}
STATUS_CLASS = {
    "NS": "status-ns", "FT": "status-ft", "AET": "status-ft",
    "1H": "status-live", "2H": "status-live", "HT": "status-live",
    "ET": "status-live", "PEN": "status-live",
}


def _minutes_left(kickoff: datetime) -> float:
    return (kickoff - datetime.now(timezone.utc)).total_seconds() / 60


def _countdown(minutes: float) -> str:
    if minutes <= 0:
        return "Iniciado"
    h, m = divmod(int(minutes), 60)
    return f"{h}h {m:02d}min" if h else f"{m}min"


def _load_matches():
    session = get_session()
    try:
        return session.execute(select(Match).order_by(Match.kickoff_time)).scalars().all()
    finally:
        session.close()


def _get_pred(session, user_id, match_id):
    p = session.execute(
        select(Prediction).where(
            Prediction.user_id == user_id,
            Prediction.match_id == match_id,
        )
    ).scalar_one_or_none()
    return (p.predicted_home_score, p.predicted_away_score) if p else None


def _save_pred(user_id, match_id, home, away):
    session = get_session()
    try:
        p = session.execute(
            select(Prediction).where(
                Prediction.user_id == user_id,
                Prediction.match_id == match_id,
            )
        ).scalar_one_or_none()
        if p:
            p.predicted_home_score = home
            p.predicted_away_score = away
        else:
            session.add(Prediction(
                user_id=user_id, match_id=match_id,
                predicted_home_score=home, predicted_away_score=away,
            ))
        session.commit()
        st.toast("Palpite salvo!")
    except Exception as e:
        session.rollback()
        st.error(f"Erro: {e}")
    finally:
        session.close()


def render_dashboard():
    matches = _load_matches()
    if not matches:
        st.info("Nenhum jogo cadastrado ainda.")
        return

    dates = sorted({m.kickoff_time.date() for m in matches})
    today = datetime.now(timezone.utc).date()
    idx   = next((i for i, d in enumerate(dates) if d >= today), 0)

    selected = st.selectbox(
        "Data",
        dates,
        index=idx,
        format_func=lambda d: d.strftime("%d/%m/%Y"),
        label_visibility="collapsed",
    )

    day_matches = [m for m in matches if m.kickoff_time.date() == selected]
    session     = get_session()
    user_id     = st.session_state.user_id

    for m in day_matches:
        _render_card(m, session, user_id)

    session.close()
    st.caption("Palpites bloqueados 30 minutos antes do início da partida.")


def _render_card(m: Match, session, user_id: str):
    mins    = _minutes_left(m.kickoff_time)
    locked  = mins <= LOCK_MINUTES
    is_live = m.status in ("1H", "2H", "HT", "ET", "PEN")
    is_done = m.status in ("FT", "AET")
    group   = MATCH_GROUP.get(m.match_id, "")
    label   = STATUS_LABEL.get(m.status, m.status)
    cls     = STATUS_CLASS.get(m.status, "status-ns")

    hf = get_flag(m.home_team)
    af = get_flag(m.away_team)

    if is_done:
        score_html = f'<div class="score-num">{m.home_score} : {m.away_score}</div>'
    elif is_live:
        h = m.home_score if m.home_score is not None else 0
        a = m.away_score if m.away_score is not None else 0
        score_html = f'<div class="score-num">{h} : {a}</div>'
    else:
        score_html = '<div class="score-vs">VS</div>'

    if m.status == "NS" and not locked:
        time_extra = f'<span class="countdown-pill">Fecha em {_countdown(mins)}</span>'
    elif m.status == "NS" and locked:
        time_extra = '<span class="countdown-pill" style="background:#fee2e2;border-color:#fca5a5;color:#dc2626">Fechado</span>'
    else:
        time_extra = ""

    st.markdown(f"""
    <div class="match-card">
      <div class="match-header">
        <span class="group-badge">GRUPO {group}</span>
        <span class="match-time">{m.kickoff_time.strftime("%d/%m · %H:%M")} UTC</span>
        <span class="{cls}">{label}</span>
      </div>
      <div class="match-body">
        <div class="team-block">
          <span class="team-flag">{hf}</span>
          <span class="team-name">{m.home_team}</span>
        </div>
        <div class="score-wrap">{score_html}</div>
        <div class="team-block away">
          <span class="team-flag">{af}</span>
          <span class="team-name">{m.away_team}</span>
        </div>
      </div>
      {"<div style='text-align:center;padding-bottom:10px'>" + time_extra + "</div>" if time_extra else ""}
    </div>
    """, unsafe_allow_html=True)

    # Palpite
    existing = _get_pred(session, user_id, m.match_id)
    ph = existing[0] if existing else 0
    pa = existing[1] if existing else 0

    if is_done:
        if existing:
            pts = calculate_points(ph, pa, m.home_score or 0, m.away_score or 0)
            labels = {3: "Placar exato!", 1: "Acertou o vencedor", 0: "Sem pontos"}
            cls_map = {3: "pts-3", 1: "pts-1", 0: "pts-0"}
            st.markdown(
                f"<div style='padding:6px 16px 12px'>"
                f"Seu palpite: <b>{ph} x {pa}</b> &nbsp;"
                f"<span class='pts-badge {cls_map[pts]}'>{labels[pts]} +{pts} pts</span>"
                f"</div>",
                unsafe_allow_html=True,
            )
        return

    label_exp = "Meu palpite" + (" ✓ salvo" if existing else "")
    with st.expander(label_exp, expanded=False):
        if locked:
            if existing:
                st.info(f"Seu palpite: **{ph} x {pa}** (bloqueado)")
            else:
                st.warning("Palpites encerrados para esta partida.")
        else:
            c1, c2, c3 = st.columns([3, 1, 3])
            with c1:
                g_home = st.number_input(m.home_team, 0, 20, ph, key=f"h_{m.match_id}")
            with c2:
                st.markdown("<p style='text-align:center;padding-top:28px;font-weight:700'>x</p>",
                            unsafe_allow_html=True)
            with c3:
                g_away = st.number_input(m.away_team, 0, 20, pa, key=f"a_{m.match_id}")
            if st.button("Salvar palpite", key=f"btn_{m.match_id}",
                         use_container_width=True, type="primary"):
                _save_pred(user_id, m.match_id, g_home, g_away)
                st.rerun()

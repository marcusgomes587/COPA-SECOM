from datetime import datetime, timezone, timedelta
import streamlit as st
from sqlalchemy import select
from modules.database import get_session
from modules.models import Match, Prediction
from modules.api_football import fetch_matches, parse_match


_STATUS_LABEL = {
    "NS": "Agendado", "1H": "1° Tempo", "HT": "Intervalo",
    "2H": "2° Tempo", "ET": "Prorrogacao", "PEN": "Penaltis",
    "FT": "Encerrado", "AET": "Encerrado", "SUSP": "Suspenso",
}
LOCK_MINUTES = 30


def _minutes_to_kickoff(kickoff: datetime) -> float:
    now = datetime.now(timezone.utc)
    return (kickoff - now).total_seconds() / 60


def _countdown_str(minutes: float) -> str:
    if minutes <= 0:
        return "Iniciado"
    h, m = divmod(int(minutes), 60)
    if h:
        return f"{h}h {m:02d}min"
    return f"{m}min"


def _get_user_prediction(session, user_id: str, match_id: int) -> tuple[int, int] | None:
    pred = session.execute(
        select(Prediction).where(
            Prediction.user_id == user_id,
            Prediction.match_id == match_id,
        )
    ).scalar_one_or_none()
    if pred:
        return pred.predicted_home_score, pred.predicted_away_score
    return None


def _save_prediction(user_id: str, match_id: int, home: int, away: int):
    session = get_session()
    try:
        pred = session.execute(
            select(Prediction).where(
                Prediction.user_id == user_id,
                Prediction.match_id == match_id,
            )
        ).scalar_one_or_none()

        if pred:
            pred.predicted_home_score = home
            pred.predicted_away_score = away
        else:
            session.add(Prediction(
                user_id=user_id,
                match_id=match_id,
                predicted_home_score=home,
                predicted_away_score=away,
            ))
        session.commit()
        st.toast("Palpite salvo!", icon="✅")
    except Exception as e:
        session.rollback()
        st.error(f"Erro ao salvar: {e}")
    finally:
        session.close()


def _sync_matches_to_db(raw_list: list[dict]):
    """Sincroniza fixtures da API com a tabela matches."""
    session = get_session()
    try:
        for raw in raw_list:
            m = parse_match(raw)
            existing = session.get(Match, m["match_id"])
            if existing:
                existing.status     = m["status"]
                existing.home_score = m["home_score"]
                existing.away_score = m["away_score"]
            else:
                session.add(Match(
                    match_id    = m["match_id"],
                    home_team   = m["home_team"],
                    away_team   = m["away_team"],
                    kickoff_time= m["kickoff_time"],
                    status      = m["status"],
                    home_score  = m["home_score"],
                    away_score  = m["away_score"],
                ))
        session.commit()
    except Exception:
        session.rollback()
    finally:
        session.close()


def render_dashboard():
    st.header("Jogos da Copa 2026")

    with st.spinner("Carregando jogos..."):
        try:
            raw_matches = fetch_matches()
            _sync_matches_to_db(raw_matches)
            matches = [parse_match(r) for r in raw_matches]
        except Exception as e:
            st.error(f"Erro ao buscar jogos: {e}")
            return

    if not matches:
        st.info("Nenhum jogo encontrado. A fase de grupos ainda nao foi sorteada ou a API nao retornou dados.")
        return

    # Filtra por data selecionada
    dates = sorted({m["kickoff_time"].date() for m in matches})
    today = datetime.now(timezone.utc).date()
    default_idx = next((i for i, d in enumerate(dates) if d >= today), 0)

    selected_date = st.selectbox(
        "Data",
        dates,
        index=default_idx,
        format_func=lambda d: d.strftime("%d/%m/%Y (%A)"),
    )

    day_matches = [m for m in matches if m["kickoff_time"].date() == selected_date]

    session = get_session()
    user_id = st.session_state.user_id

    for match in sorted(day_matches, key=lambda x: x["kickoff_time"]):
        _render_match_card(match, session, user_id)

    session.close()

    st.caption("Palpites bloqueados 30 minutos antes do inicio da partida.")
    if st.button("Atualizar placar", icon="🔄"):
        st.cache_data.clear()
        st.rerun()


def _render_match_card(match: dict, session, user_id: str):
    minutes_left = _minutes_to_kickoff(match["kickoff_time"])
    locked = minutes_left <= LOCK_MINUTES
    status = _STATUS_LABEL.get(match["status"], match["status"])
    is_finished = match["status"] in ("FT", "AET", "PEN")

    with st.container(border=True):
        # Header da partida
        col_time, col_status = st.columns([1, 1])
        with col_time:
            st.caption(match["kickoff_time"].strftime("%H:%M UTC"))
        with col_status:
            if match["status"] == "NS" and not locked:
                st.caption(f"Fecha em: **{_countdown_str(minutes_left)}**")
            elif match["status"] == "NS" and locked:
                st.caption(":red[Palpites encerrados]")
            else:
                st.caption(f"**{status}**")

        # Times e placar
        col_home, col_score, col_away = st.columns([3, 2, 3])
        with col_home:
            st.markdown(f"**{match['home_team']}**")
        with col_score:
            if is_finished or match["status"] not in ("NS",):
                h = match["home_score"] if match["home_score"] is not None else "-"
                a = match["away_score"] if match["away_score"] is not None else "-"
                st.markdown(f"<h3 style='text-align:center;margin:0'>{h} x {a}</h3>", unsafe_allow_html=True)
            else:
                st.markdown("<h3 style='text-align:center;margin:0;color:#ccc'>vs</h3>", unsafe_allow_html=True)
        with col_away:
            st.markdown(f"<div style='text-align:right'><b>{match['away_team']}</b></div>", unsafe_allow_html=True)

        # Palpite
        if not is_finished:
            existing = _get_user_prediction(session, user_id, match["match_id"])
            ph = existing[0] if existing else 0
            pa = existing[1] if existing else 0

            with st.expander("Meu palpite" + (" (salvo)" if existing else ""), expanded=not locked):
                if locked:
                    if existing:
                        st.info(f"Seu palpite: **{ph} x {pa}** (bloqueado)")
                    else:
                        st.warning("Palpites encerrados para esta partida.")
                else:
                    c1, c2, c3 = st.columns([2, 1, 2])
                    with c1:
                        g_home = st.number_input(
                            match["home_team"], min_value=0, max_value=20,
                            value=ph, key=f"h_{match['match_id']}", label_visibility="visible"
                        )
                    with c2:
                        st.markdown("<p style='text-align:center;padding-top:28px'>x</p>", unsafe_allow_html=True)
                    with c3:
                        g_away = st.number_input(
                            match["away_team"], min_value=0, max_value=20,
                            value=pa, key=f"a_{match['match_id']}", label_visibility="visible"
                        )
                    if st.button("Salvar palpite", key=f"btn_{match['match_id']}", use_container_width=True):
                        _save_prediction(user_id, match["match_id"], g_home, g_away)
                        st.rerun()
        else:
            # Jogo finalizado — mostra palpite e pontos ganhos
            existing = _get_user_prediction(session, user_id, match["match_id"])
            if existing:
                from modules.scoring import calculate_points
                pts = calculate_points(
                    existing[0], existing[1],
                    match["home_score"] or 0, match["away_score"] or 0,
                )
                label = {3: "Placar exato!", 1: "Acertou o vencedor", 0: "Nao pontuou"}[pts]
                color = {3: "green", 1: "orange", 0: "gray"}[pts]
                st.markdown(
                    f"Seu palpite: **{existing[0]} x {existing[1]}** — "
                    f"<span style='color:{color}'>{label} (+{pts} pts)</span>",
                    unsafe_allow_html=True,
                )

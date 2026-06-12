import streamlit as st
from sqlalchemy import select
from modules.database import get_session
from modules.models import Match, User
from modules.scoring import update_scores_for_match, recalculate_all_finished
from modules.flags import MATCH_GROUP

STATUS_OPTIONS = ["NS", "1H", "HT", "2H", "ET", "PEN", "FT", "AET", "SUSP"]

ROUNDS = {
    "Rodada 1": range(1001, 1025),
    "Rodada 2": range(1025, 1049),
    "Rodada 3": range(1049, 1073),
}


def render_admin():
    st.header("Painel Admin — Placares")
    st.caption("Visivel apenas para o administrador.")

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

    st.divider()
    st.markdown("**Recalcular todos os pontos**")
    st.caption("Use apos trocar a metodologia de pontuacao. Reprocessa todos os jogos encerrados.")
    if st.button("Recalcular todos os palpites", type="primary", use_container_width=True):
        try:
            updated = recalculate_all_finished()
            st.success(f"Recalculo concluido! {updated} palpite(s) atualizados.")
        except Exception as e:
            st.error(f"Erro: {e}")
    st.divider()

    session = get_session()
    all_matches = session.execute(
        select(Match).order_by(Match.kickoff_time)
    ).scalars().all()
    session.close()

    if not all_matches:
        st.warning("Nenhum jogo cadastrado.")
        return

    from modules.stats import FINISHED, GROUP_STAGE_MIN, GROUP_STAGE_MAX

    group = [m for m in all_matches if GROUP_STAGE_MIN <= m.match_id <= GROUP_STAGE_MAX]
    done = sum(1 for m in group if m.status in FINISHED)
    if group:
        st.progress(done / len(group))
        st.caption(f"{done} de {len(group)} jogos da fase de grupos com placar lancado")
    knockout_all = [m for m in all_matches if m.match_id >= 2000]
    if knockout_all:
        ko_done = sum(1 for m in knockout_all if m.status in FINISHED)
        st.caption(f"Mata-mata: {ko_done} de {len(knockout_all)} jogos encerrados")

    match_map = {m.match_id: m for m in all_matches}

    tab_labels = list(ROUNDS.keys()) + ["Mata-Mata"]
    tabs = st.tabs(tab_labels)

    for i, (round_name, id_range) in enumerate(ROUNDS.items()):
        with tabs[i]:
            round_matches = [match_map[mid] for mid in id_range if mid in match_map]
            _render_round(round_matches)

    with tabs[3]:
        knockout = [m for m in all_matches if m.match_id >= 2000]
        if not knockout:
            st.info("Nenhum jogo do mata-mata cadastrado ainda.")
        else:
            _render_round(knockout)


def _render_round(matches: list):
    if not matches:
        st.info("Nenhum jogo nesta rodada.")
        return

    for m in matches:
        group = MATCH_GROUP.get(m.match_id, "")
        group_label = f"Grupo {group} · " if group else ""
        from datetime import timedelta, timezone
        BRT = timezone(timedelta(hours=-3))
        kickoff_brt = m.kickoff_time.astimezone(BRT).strftime("%d/%m %H:%M")

        status_dot = {
            "FT": ":green[●]", "AET": ":green[●]", "PEN": ":green[●]",
            "1H": ":red[●]", "2H": ":red[●]", "ET": ":red[●]",
            "HT": ":orange[●]",
        }.get(m.status, ":gray[●]")

        score_str = f"{m.home_score} x {m.away_score}" if m.home_score is not None else "- x -"

        with st.expander(
            f"{status_dot} {group_label}{m.home_team} vs {m.away_team}  "
            f"·  {kickoff_brt}  ·  {score_str}"
        ):
            with st.form(key=f"admin_{m.match_id}"):
                col1, col2, col3 = st.columns([3, 3, 2])
                with col1:
                    h_score = st.number_input(
                        m.home_team, 0, 30,
                        value=m.home_score or 0,
                        key=f"adm_h_{m.match_id}",
                    )
                with col2:
                    a_score = st.number_input(
                        m.away_team, 0, 30,
                        value=m.away_score or 0,
                        key=f"adm_a_{m.match_id}",
                    )
                with col3:
                    status = st.selectbox(
                        "Status",
                        STATUS_OPTIONS,
                        index=STATUS_OPTIONS.index(m.status)
                        if m.status in STATUS_OPTIONS else 0,
                        key=f"adm_s_{m.match_id}",
                    )
                submitted = st.form_submit_button(
                    "Salvar e calcular pontos",
                    type="primary",
                    use_container_width=True,
                )

            if submitted:
                _update_match(m.match_id, h_score, a_score, status)
                st.rerun()


def _update_match(match_id: int, home: int, away: int, status: str):
    session = get_session()
    try:
        m = session.get(Match, match_id)
        m.home_score = home
        m.away_score = away
        m.status     = status
        session.commit()
    except Exception as e:
        session.rollback()
        st.error(f"Erro: {e}")
        return
    finally:
        session.close()

    if status in ("FT", "AET", "PEN"):
        updated = update_scores_for_match(match_id)
        st.success(f"Salvo! {updated} palpite(s) recalculado(s).")
    else:
        st.success("Status atualizado.")

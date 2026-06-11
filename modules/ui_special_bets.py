import streamlit as st
from sqlalchemy import select
from modules.database import get_session
from modules.models import SpecialBet

# Selecao das selecoes participantes da Copa 2026
TEAMS = [
    "Argentina", "Brasil", "Franca", "Inglaterra", "Alemanha", "Espanha",
    "Portugal", "Holanda", "Belgica", "Italia", "Croacia", "Uruguai",
    "Mexico", "EUA", "Canada", "Japao", "Coreia do Sul", "Marrocos",
    "Senegal", "Nigeria", "Egito", "Australia", "Colombia", "Chile",
    "Peru", "Equador", "Venezuela", "Bolivia", "Paraguai", "Costa Rica",
    "Panama", "Honduras", "Jamaica", "Arabia Saudita", "Ira", "Catar",
    "Polonia", "Serbia", "Suica", "Dinamarca", "Noruega", "Austria",
    "Turquia", "Ucrania", "Eslovaquia", "Eslovania", "Albania", "Georgia",
]


def render_special_bets():
    st.header("Apostas Especiais")
    st.caption("Esses palpites podem ser alterados ate o inicio da Copa.")

    user_id = st.session_state.user_id
    session = get_session()

    try:
        bet = session.execute(
            select(SpecialBet).where(SpecialBet.user_id == user_id)
        ).scalar_one_or_none()

        current_champion  = bet.champion_team if bet else None
        current_scorer    = bet.top_scorer    if bet else ""
        current_best      = bet.best_player   if bet else ""

        with st.form("form_special_bets"):
            st.subheader("Selecao Campeã")
            champion = st.selectbox(
                "Quem vai ganhar a Copa 2026?",
                options=[""] + sorted(TEAMS),
                index=([""] + sorted(TEAMS)).index(current_champion) if current_champion in TEAMS else 0,
            )

            st.divider()
            st.subheader("Artilheiro do Torneio")
            scorer = st.text_input(
                "Nome do jogador",
                value=current_scorer,
                placeholder="Ex: Vinicius Jr.",
            )

            st.divider()
            st.subheader("Melhor Jogador (Bola de Ouro)")
            best = st.text_input(
                "Nome do jogador",
                value=current_best,
                placeholder="Ex: Mbappe",
                key="best_player_input",
            )

            submitted = st.form_submit_button("Salvar apostas especiais", use_container_width=True, type="primary")

        if submitted:
            _save_special_bet(session, user_id, bet, champion or None, scorer or None, best or None)
            st.rerun()

        # Resumo atual
        if bet and any([bet.champion_team, bet.top_scorer, bet.best_player]):
            st.divider()
            st.subheader("Suas apostas atuais")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Campeã", bet.champion_team or "—")
            with col2:
                st.metric("Artilheiro", bet.top_scorer or "—")
            with col3:
                st.metric("Melhor Jogador", bet.best_player or "—")
    finally:
        session.close()


def _save_special_bet(session, user_id, existing, champion, scorer, best):
    try:
        if existing:
            existing.champion_team = champion
            existing.top_scorer    = scorer
            existing.best_player   = best
        else:
            session.add(SpecialBet(
                user_id       = user_id,
                champion_team = champion,
                top_scorer    = scorer,
                best_player   = best,
            ))
        session.commit()
        st.success("Apostas especiais salvas!")
    except Exception as e:
        session.rollback()
        st.error(f"Erro ao salvar: {e}")


def render_special_bets_summary():
    """Resumo das apostas de todos os usuarios — visivel no ranking."""
    session = get_session()
    try:
        bets = session.execute(select(SpecialBet)).scalars().all()
        if not bets:
            st.info("Nenhuma aposta especial registrada ainda.")
            return

        from modules.models import User
        from sqlalchemy import select as sel
        rows = []
        for b in bets:
            u = session.get(User, b.user_id)
            rows.append({
                "Usuario":    u.username if u else "?",
                "Campea":     b.champion_team or "—",
                "Artilheiro": b.top_scorer    or "—",
                "Melhor Jog": b.best_player   or "—",
            })

        import pandas as pd
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    finally:
        session.close()

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

import streamlit as st
from modules.auth import login_user, register_user


def render_login_page():
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

    tab_login, tab_register = st.tabs(["Entrar", "Cadastrar"])

    with tab_login:
        _render_login_form()

    with tab_register:
        _render_register_form()


def _render_login_form():
    with st.form("form_login", clear_on_submit=False):
        st.subheader("Entrar")
        username = st.text_input("Nome de usuario", placeholder="seu.nome")
        password = st.text_input("Senha", type="password", placeholder="••••••")
        submitted = st.form_submit_button("Entrar", use_container_width=True, type="primary")

    if submitted:
        if not username or not password:
            st.error("Preencha todos os campos.")
            return
        ok, msg = login_user(username, password)
        if ok:
            st.success(msg)
            st.rerun()
        else:
            st.error(msg)


def _render_register_form():
    with st.form("form_register", clear_on_submit=True):
        st.subheader("Criar conta")
        username = st.text_input("Escolha um nome de usuario", placeholder="seu.nome")
        password = st.text_input("Senha", type="password", placeholder="minimo 6 caracteres")
        confirm  = st.text_input("Confirmar senha", type="password", placeholder="repita a senha")
        submitted = st.form_submit_button("Cadastrar", use_container_width=True, type="primary")

    if submitted:
        if not username or not password or not confirm:
            st.error("Preencha todos os campos.")
            return
        if password != confirm:
            st.error("As senhas nao coincidem.")
            return
        ok, msg = register_user(username, password)
        if ok:
            st.success(msg + " Agora faca o login.")
        else:
            st.error(msg)

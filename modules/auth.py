import secrets
import uuid

import bcrypt
import streamlit as st
from sqlalchemy import select
from modules.database import get_session
from modules.models import User


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


def register_user(username: str, password: str) -> tuple[bool, str]:
    if len(username.strip()) < 3:
        return False, "Nome de usuario deve ter pelo menos 3 caracteres."
    if len(password) < 6:
        return False, "Senha deve ter pelo menos 6 caracteres."

    session = get_session()
    try:
        existing = session.execute(
            select(User).where(User.username == username.strip())
        ).scalar_one_or_none()

        if existing:
            return False, "Nome de usuario ja esta em uso."

        user = User(username=username.strip(), password_hash=hash_password(password))
        session.add(user)
        session.commit()
        return True, "Cadastro realizado com sucesso!"
    except Exception as e:
        session.rollback()
        return False, f"Erro ao cadastrar: {str(e)}"
    finally:
        session.close()


def login_user(username: str, password: str) -> tuple[bool, str]:
    session = get_session()
    try:
        user = session.execute(
            select(User).where(User.username == username.strip())
        ).scalar_one_or_none()

        if not user or not verify_password(password, user.password_hash):
            return False, "Usuario ou senha incorretos."

        st.session_state.logged_in = True
        st.session_state.user_id = str(user.id)
        st.session_state.username = user.username
        st.session_state.total_score = user.total_score
        return True, "Login realizado!"
    except Exception as e:
        return False, f"Erro ao fazer login: {str(e)}"
    finally:
        session.close()


def logout():
    for key in ["logged_in", "user_id", "username", "total_score"]:
        st.session_state.pop(key, None)
    st.rerun()


def require_login():
    """Redireciona para login se o usuario nao estiver autenticado."""
    if not st.session_state.get("logged_in"):
        st.warning("Faca login para continuar.")
        st.stop()


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

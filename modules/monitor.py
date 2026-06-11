import streamlit as st
from sqlalchemy import text
from modules.database import get_session


def get_db_size() -> dict:
    """Retorna tamanho atual do banco Neon e percentual do limite free (512 MB)."""
    session = get_session()
    try:
        result = session.execute(text("""
            SELECT
                pg_size_pretty(pg_database_size(current_database())) AS size_pretty,
                pg_database_size(current_database()) AS size_bytes
        """)).fetchone()
        size_bytes = result.size_bytes
        size_mb    = size_bytes / (1024 * 1024)
        limit_mb   = 512
        pct        = (size_mb / limit_mb) * 100
        return {
            "size_pretty": result.size_pretty,
            "size_mb":     round(size_mb, 2),
            "limit_mb":    limit_mb,
            "pct":         round(pct, 1),
        }
    except Exception:
        return {"size_pretty": "—", "size_mb": 0, "limit_mb": 512, "pct": 0}
    finally:
        session.close()


def render_sidebar_monitor():
    """Bloco de monitoramento exibido na sidebar para o usuario logado."""
    st.sidebar.divider()
    st.sidebar.caption("Monitor de limites")

    # --- Banco de dados ---
    db = get_db_size()
    db_color = "normal"
    if db["pct"] >= 80:
        db_color = "inverse"
    elif db["pct"] >= 50:
        db_color = "off"

    st.sidebar.metric(
        label="Banco Neon (512 MB free)",
        value=db["size_pretty"],
        delta=f"{db['pct']}% usado",
        delta_color=db_color,
    )

    # Barra de progresso do banco
    st.sidebar.progress(
        min(db["pct"] / 100, 1.0),
        text=f"{db['size_mb']} MB / {db['limit_mb']} MB",
    )

    # --- API-Football ---
    remaining = st.session_state.get("api_remaining", -1)
    limit     = st.session_state.get("api_limit", 100)

    if remaining >= 0:
        used    = limit - remaining
        api_pct = used / limit if limit > 0 else 0
        api_color = "normal"
        if api_pct >= 0.8:
            api_color = "inverse"
        elif api_pct >= 0.5:
            api_color = "off"

        st.sidebar.metric(
            label="API-Football (100 req/dia)",
            value=f"{remaining} restantes",
            delta=f"{used} usadas hoje",
            delta_color=api_color,
        )
        st.sidebar.progress(
            min(api_pct, 1.0),
            text=f"{used} / {limit} requisicoes",
        )
    else:
        st.sidebar.caption("API: sem dados ainda — acesse a aba Jogos")

    # Botao para consultar quota manualmente
    if st.sidebar.button("Verificar quota API", use_container_width=True):
        try:
            from modules.api_football import fetch_api_status
            status = fetch_api_status()
            st.sidebar.success(
                f"Plano: {status['plan']} | "
                f"{status['remaining']}/{status['limit']} req restantes"
            )
        except Exception as e:
            st.sidebar.error(f"Erro: {e}")

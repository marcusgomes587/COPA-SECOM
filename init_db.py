"""
Executa uma vez para criar as 4 tabelas no Neon.
Uso: python init_db.py
"""
import sys
import os
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode

sys.path.insert(0, os.path.dirname(__file__))

import toml
secrets = toml.load(".streamlit/secrets.toml")
raw_url = secrets["database"]["DATABASE_URL"]

# Troca driver para psycopg3
url = raw_url.replace("postgresql://", "postgresql+psycopg://", 1)

# Remove channel_binding que pode bloquear psycopg3 no Windows
parsed = urlparse(url)
params = parse_qs(parsed.query, keep_blank_values=True)
params.pop("channel_binding", None)
clean_query = urlencode({k: v[0] for k, v in params.items()})
url = urlunparse(parsed._replace(query=clean_query))

from sqlalchemy import create_engine, text
from modules.models import Base

def main():
    engine = create_engine(
        url,
        pool_pre_ping=True,
        connect_args={"connect_timeout": 15},
    )

    print("Conectando ao Neon...")
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version()"))
        print(f"Conexao OK. {result.scalar()[:40]}")

    print("Criando tabelas...")
    Base.metadata.create_all(engine)
    print("Tabelas criadas com sucesso:")
    for table in Base.metadata.sorted_tables:
        print(f"  - {table.name}")

if __name__ == "__main__":
    main()

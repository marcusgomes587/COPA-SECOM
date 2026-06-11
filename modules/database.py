import streamlit as st
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

_engine = None
_SessionLocal = None


def get_engine():
    global _engine
    if _engine is None:
        url = st.secrets["database"]["DATABASE_URL"]
        # psycopg3 requer o prefixo postgresql+psycopg://
        url = url.replace("postgresql://", "postgresql+psycopg://", 1)
        _engine = create_engine(url, pool_pre_ping=True)
    return _engine


def get_session():
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(bind=get_engine(), autocommit=False, autoflush=False)
    return _SessionLocal()


class Base(DeclarativeBase):
    pass

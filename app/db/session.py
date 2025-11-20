from sqlmodel import SQLModel, create_engine, Session
from app.core.config import settings

# check_same_thread=False es necesario solo para SQLite, pero aquí usamos Postgres
# echo=True nos mostrará en la terminal las consultas SQL que Python genera (genial para aprender)
engine = create_engine(settings.DATABASE_URL, echo=True)

def get_session():
    with Session(engine) as session:
        yield session

def create_db_and_tables():
    """Crea las tablas en la BD si no existen"""
    SQLModel.metadata.create_all(engine)
import os
from sqlmodel import create_engine, Session, SQLModel

# DATABASE_URL viene preso dal file docker-compose.yml
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@db:5432/fantacalcio_db")

engine = create_engine(DATABASE_URL, echo=True)

def init_db():
    # Questa riga crea fisicamente le tabelle nel DB se non esistono
    SQLModel.metadata.create_all(engine)

def get_session():
    # Funzione per ottenere una sessione di lavoro con il DB
    with Session(engine) as session:
        yield session
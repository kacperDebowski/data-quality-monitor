from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Adres do naszej bazy PostgreSQL odpalonej w Dockerze
# Format: postgresql://użytkownik:hasło@host:port/nazwa_bazy
SQLALCHEMY_DATABASE_URL = "postgresql://admin:adminpassword@localhost:5432/data_quality_db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Funkcja pomocnicza do pobierania sesji bazy danych w endpointach FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

import models
import schemas
from database import engine, get_db

# Ta linijka automatycznie tworzy tabele w bazie PostgreSQL na podstawie models.py
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Data Quality Monitor API",
    description="API do zarządzania regułami jakości danych (Praca Inżynierska)",
    version="1.0.0"
)

# ---------------------------------------------------------
# ENDPOINTY: ZARZĄDZANIE POŁĄCZENIAMI (DATABASE CONNECTIONS)
# ---------------------------------------------------------

@app.post("/connections/", response_model=schemas.DatabaseConnectionResponse, tags=["Connections"])
def create_connection(connection: schemas.DatabaseConnectionCreate, db: Session = Depends(get_db)):
    """Dodaje nowe połączenie do bazy danych."""
    # Tworzymy obiekt modelu na podstawie danych z Pydantica
    db_connection = models.DatabaseConnection(**connection.model_dump())
    db.add(db_connection)
    db.commit()
    db.refresh(db_connection)
    return db_connection

@app.get("/connections/", response_model=List[schemas.DatabaseConnectionResponse], tags=["Connections"])
def read_connections(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Zwraca listę wszystkich zapisanych połączeń."""
    connections = db.query(models.DatabaseConnection).offset(skip).limit(limit).all()
    return connections

@app.delete("/connections/{connection_id}", tags=["Connections"])
def delete_connection(connection_id: int, db: Session = Depends(get_db)):
    """Usuwa połączenie (kaskadowo usunie też przypisane do niego reguły!)."""
    db_connection = db.query(models.DatabaseConnection).filter(models.DatabaseConnection.id == connection_id).first()
    if not db_connection:
        raise HTTPException(status_code=404, detail="Nie znaleziono takiego połączenia")
    
    db.delete(db_connection)
    db.commit()
    return {"status": "success", "message": f"Połączenie {connection_id} usunięte"}


# ---------------------------------------------------------
# ENDPOINTY: ZARZĄDZANIE REGUŁAMI (VALIDATION RULES)
# ---------------------------------------------------------

@app.post("/rules/", response_model=schemas.ValidationRuleResponse, tags=["Rules"])
def create_rule(rule: schemas.ValidationRuleCreate, db: Session = Depends(get_db)):
    """Dodaje nową regułę walidacyjną."""
    # Sprawdzamy najpierw, czy baza danych o podanym ID w ogóle istnieje
    db_connection = db.query(models.DatabaseConnection).filter(models.DatabaseConnection.id == rule.database_id).first()
    if not db_connection:
        raise HTTPException(status_code=404, detail="Baza danych o podanym ID nie istnieje")

    db_rule = models.ValidationRule(**rule.model_dump())
    db.add(db_rule)
    db.commit()
    db.refresh(db_rule)
    return db_rule

@app.get("/rules/", response_model=List[schemas.ValidationRuleResponse], tags=["Rules"])
def read_rules(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Zwraca listę wszystkich skonfigurowanych reguł."""
    rules = db.query(models.ValidationRule).offset(skip).limit(limit).all()
    return rules

@app.delete("/rules/{rule_id}", tags=["Rules"])
def delete_rule(rule_id: int, db: Session = Depends(get_db)):
    """Usuwa regułę sprawdzającą i historię jej wykonań."""
    db_rule = db.query(models.ValidationRule).filter(models.ValidationRule.id == rule_id).first()
    if not db_rule:
        raise HTTPException(status_code=404, detail="Nie znaleziono takiej reguły")
    
    db.delete(db_rule)
    db.commit()
    return {"status": "success", "message": f"Reguła {rule_id} usunięta"}

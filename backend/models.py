from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

# Importujemy Base z naszego pliku database.py
from database import Base

# --- Enumy (Typy wyliczeniowe dla ułatwienia i bezpieczeństwa) ---
class RuleType(enum.Enum):
    BUILT_IN = "built_in"
    CUSTOM_SQL = "custom_sql"

class ExecutionStatus(enum.Enum):
    SUCCESS = "success"  # Test przeszedł poprawnie (znaleziono wyniki/brak błędów)
    FAILED = "failed"    # Jakość danych poniżej oczekiwań (np. test znalazł nulle)
    ERROR = "error"      # Błąd samego zapytania (np. zła składnia SQL)


# --- Modele ---

class DatabaseConnection(Base):
    """Tabela przechowująca konfiguracje podłączonych baz danych klientów"""
    __tablename__ = "database_connections"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False) # Np. "Baza Produkcyjna - ERP"
    connection_uri = Column(String(255), nullable=False) # Np. postgresql://user:pass@host/db
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relacja: Jedna baza może mieć wiele podpiętych reguł sprawdzających
    rules = relationship("ValidationRule", back_populates="database", cascade="all, delete-orphan")


class ValidationRule(Base):
    """Tabela przechowująca reguły walidacyjne zdefiniowane przez użytkownika"""
    __tablename__ = "validation_rules"

    id = Column(Integer, primary_key=True, index=True)
    database_id = Column(Integer, ForeignKey("database_connections.id"), nullable=False)
    
    name = Column(String(100), nullable=False) # Np. "Brakujące numery PESEL"
    description = Column(Text, nullable=True)
    rule_type = Column(Enum(RuleType), nullable=False, default=RuleType.BUILT_IN)
    
    # Gdzie odpalamy test?
    target_table = Column(String(100), nullable=False)
    target_column = Column(String(100), nullable=True)
    
    # Zarezerwowane dla własnego kodu SQL
    custom_sql = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relacje
    database = relationship("DatabaseConnection", back_populates="rules")
    executions = relationship("RuleExecutionHistory", back_populates="rule", cascade="all, delete-orphan")


class RuleExecutionHistory(Base):
    """Tabela archiwizująca wyniki każdego wykonania reguły (historia do wykresów)"""
    __tablename__ = "rule_execution_history"

    id = Column(Integer, primary_key=True, index=True)
    rule_id = Column(Integer, ForeignKey("validation_rules.id"), nullable=False)
    
    execution_time = Column(DateTime, default=datetime.utcnow)
    status = Column(Enum(ExecutionStatus), nullable=False)
    
    # Konkretny wynik, np. liczba znalezionych błędnych rekordów (pomaga wyliczyć Score na froncie)
    result_value = Column(Integer, nullable=True) 
    error_message = Column(Text, nullable=True) # Wypełniane tylko, gdy status to ERROR

    # Relacja
    rule = relationship("ValidationRule", back_populates="executions")
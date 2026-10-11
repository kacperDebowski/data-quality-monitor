from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from models import RuleType # Importujemy naszego Enuma

# --- Schematy dla Połączeń z Bazą (Database Connection) ---

class DatabaseConnectionBase(BaseModel):
    name: str = Field(..., example="Hurtownia Produkcyjna - Snowflake")
    connection_uri: str = Field(..., example="postgresql://user:pass@localhost:5432/db")

class DatabaseConnectionCreate(DatabaseConnectionBase):
    pass # Klasa używana przy tworzeniu (POST) - dziedziczy wszystko z Base

class DatabaseConnectionResponse(DatabaseConnectionBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True # Ważne: pozwala Pydanticowi czytać dane z modeli SQLAlchemy


# --- Schematy dla Reguł Walidacyjnych (Validation Rule) ---

class ValidationRuleBase(BaseModel):
    database_id: int
    name: str = Field(..., example="Sprawdzenie pustych NIP-ów")
    description: Optional[str] = None
    rule_type: RuleType = RuleType.BUILT_IN
    target_table: str
    target_column: Optional[str] = None
    custom_sql: Optional[str] = None

class ValidationRuleCreate(ValidationRuleBase):
    pass # Klasa używana przy tworzeniu (POST)

class ValidationRuleResponse(ValidationRuleBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
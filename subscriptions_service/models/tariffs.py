from typing import Optional

from pydantic import BaseModel
from sqlmodel import Field, SQLModel


class Tariff(SQLModel, table=True):
    """Таблица tariff: тарифы абонементов (table=True - класс становится таблицей)."""
    id: Optional[int] = Field(default=None, primary_key=True)  # первичный ключ
    name: str
    price: float
    duration_days: int


class TariffCreate(BaseModel):
    """Тело запроса при создании тарифа."""
    name: str
    price: float
    duration_days: int

    model_config = {
        "json_schema_extra": {
            "example": {"name": "Полугодие", "price": 12000, "duration_days": 180}
        }
    }


class TariffUpdate(BaseModel):
    """Тело запроса при обновлении: передаются только изменяемые поля."""
    name: Optional[str] = None
    price: Optional[float] = None
    duration_days: Optional[int] = None

    model_config = {"json_schema_extra": {"example": {"price": 2700}}}

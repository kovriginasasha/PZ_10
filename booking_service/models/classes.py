from datetime import datetime
from typing import Optional

from pydantic import BaseModel, NaiveDatetime
from sqlmodel import Field, SQLModel


class FitClass(SQLModel, table=True):
    """Таблица fitclass: занятия в расписании."""
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    trainer: str
    starts_at: NaiveDatetime
    capacity: int


class FitClassCreate(BaseModel):
    """Тело запроса при создании занятия."""
    title: str
    trainer: str
    starts_at: datetime
    capacity: int

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "Пилатес", "trainer": "Орлова Е.",
                "starts_at": "2026-12-01T18:00:00", "capacity": 12,
            }
        }
    }


class FitClassUpdate(BaseModel):
    """Тело запроса при обновлении: передаются только изменяемые поля."""
    title: Optional[str] = None
    trainer: Optional[str] = None
    starts_at: Optional[datetime] = None
    capacity: Optional[int] = None

    model_config = {"json_schema_extra": {"example": {"capacity": 15}}}


class FitClassPublic(BaseModel):
    """Занятие с вычисляемым числом свободных мест (в БД не хранится)."""
    id: int
    title: str
    trainer: str
    starts_at: datetime
    capacity: int
    free_places: int

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, NaiveDatetime
from sqlmodel import Field, SQLModel


class Booking(SQLModel, table=True):
    """Таблица booking: записи клиентов на занятия."""
    id: Optional[int] = Field(default=None, primary_key=True)
    class_id: int = Field(foreign_key="fitclass.id")
    client_id: int = Field(index=True)
    status: str = Field(default="active")  # active / cancelled
    created_at: NaiveDatetime


class BookingRequest(BaseModel):
    """Тело запроса на запись (в БД не хранится)."""
    client_id: int  # номер клиента, который записывается
    class_id: int

    model_config = {"json_schema_extra": {"example": {"client_id": 1, "class_id": 1}}}

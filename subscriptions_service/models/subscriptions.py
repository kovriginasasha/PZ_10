from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, NaiveDatetime
from sqlmodel import Field, SQLModel


class Subscription(SQLModel, table=True):
    """Таблица subscription: абонементы клиентов."""
    id: Optional[int] = Field(default=None, primary_key=True)
    client_id: int = Field(index=True)
    tariff_id: int = Field(foreign_key="tariff.id")
    start_date: date
    end_date: date
    status: str = Field(default="active")  # active / expired


class Payment(SQLModel, table=True):
    """Таблица payment: платежи (в том числе отклонённые)."""
    id: Optional[int] = Field(default=None, primary_key=True)
    client_id: int = Field(index=True)
    tariff_id: int = Field(foreign_key="tariff.id")
    subscription_id: Optional[int] = Field(default=None, foreign_key="subscription.id")
    amount: float
    status: str  # approved / declined
    created_at: NaiveDatetime

class PurchaseRequest(BaseModel):
    """Тело запроса на покупку (в БД не хранится)."""
    client_id: int  # номер клиента, который покупает абонемент
    tariff_id: int
    card_token: str

    model_config = {
        "json_schema_extra": {"example": {"client_id": 1, "tariff_id": 1, "card_token": "tok_visa_4242"}}
    }

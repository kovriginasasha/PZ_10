from datetime import date, datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import desc
from sqlmodel import Session, select

from database.connection import get_session
from models.subscriptions import Payment, PurchaseRequest, Subscription
from models.tariffs import Tariff
from services.payment_gateway import charge

subscription_router = APIRouter(tags=["Subscriptions"])


@subscription_router.post("/buy", status_code=status.HTTP_201_CREATED)
def buy_subscription(
    data: PurchaseRequest,
    session: Session = Depends(get_session),
) -> dict:
    """Вариант использования 1: оформить и оплатить абонемент."""
    client_id = data.client_id
    tariff = session.get(Tariff, data.tariff_id)
    if tariff is None:  # А1: тариф не выбран / не существует
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tariff with supplied ID does not exist",
        )

    if not charge(tariff.price, data.card_token):  # А2: платёж отклонён
        session.add(Payment(client_id=client_id, tariff_id=tariff.id, amount=tariff.price,
                            status="declined", created_at=datetime.now()))
        session.commit()  # отказ тоже записываем в историю платежей
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Payment declined, subscription not activated",
        )

    start = date.today()
    end = start + timedelta(days=tariff.duration_days)  # срок действия по тарифу
    sub = Subscription(client_id=client_id, tariff_id=tariff.id,
                       start_date=start, end_date=end, status="active")
    session.add(sub)
    session.flush()  # получаем id абонемента, транзакция ещё не завершена
    session.add(Payment(client_id=client_id, tariff_id=tariff.id, subscription_id=sub.id,
                        amount=tariff.price, status="approved", created_at=datetime.now()))
    session.commit()  # абонемент и платёж сохраняются вместе
    return {
        "message": "Payment processed, subscription activated",
        "subscription_id": sub.id,
        "valid_until": end.isoformat(),
    }


@subscription_router.get("/active", response_model=Subscription)
def retrieve_active_subscription(
    client_id: int = 1,  # номер клиента
    on_date: Optional[date] = None,  # на какую дату проверить (по умолчанию сегодня)
    session: Session = Depends(get_session),
) -> Subscription:
    """Действующий абонемент клиента на дату. Им пользуется сервис записи:
    он передаёт дату занятия, чтобы абонемент не истёк раньше тренировки.
    Срок проверяется по датам прямо в запросе, поэтому просроченный абонемент
    не найдётся, даже если статус ещё не сменили на expired."""
    check_date = on_date or date.today()
    statement = (
        select(Subscription)
        .where(
            Subscription.client_id == client_id,
            Subscription.status == "active",
            Subscription.start_date <= check_date,
            Subscription.end_date >= check_date,
        )
        .order_by(desc(Subscription.end_date))
    )
    sub = session.exec(statement).first()
    if sub is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client has no active subscription on " + check_date.isoformat(),
        )
    return sub


@subscription_router.get("/my", response_model=List[Subscription])
def retrieve_client_subscriptions(
    client_id: int = 1,  # номер клиента
    session: Session = Depends(get_session),
) -> List[Subscription]:
    """Все абонементы клиента (история), в том числе истёкшие."""
    return session.exec(
        select(Subscription).where(Subscription.client_id == client_id)
        .order_by(Subscription.id)
    ).all()


@subscription_router.post("/expire")
def run_expiration(session: Session = Depends(get_session)) -> dict:
    """Закрывает абонементы, срок которых вышел: статус active -> expired."""
    subs = session.exec(
        select(Subscription).where(
            Subscription.status == "active", Subscription.end_date < date.today()
        )
    ).all()
    ids = [s.id for s in subs]
    for s in subs:
        s.status = "expired"
        session.add(s)
    session.commit()
    return {"message": "Expiration completed", "expired": len(ids), "subscription_ids": ids}

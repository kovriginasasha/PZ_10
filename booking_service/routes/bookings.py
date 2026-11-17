from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from database.connection import get_session
from models.bookings import Booking, BookingRequest
from models.classes import FitClass
from routes.classes import free_places
from services.subscriptions_client import (
    SubscriptionServiceUnavailable,
    has_active_subscription,
)

booking_router = APIRouter(tags=["Bookings"])


@booking_router.post("/", status_code=status.HTTP_201_CREATED)
def create_booking(
    data: BookingRequest,
    session: Session = Depends(get_session),
) -> dict:
    """Вариант использования 2: записаться на тренировку."""
    client_id = data.client_id
    fit_class = session.get(FitClass, data.class_id)
    if fit_class is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Class with supplied ID does not exist",
        )

    already = session.exec(
        select(Booking).where(
            Booking.class_id == data.class_id,
            Booking.client_id == client_id,
            Booking.status == "active",
        )
    ).first()
    if already is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Client is already booked on this class",
        )

    if free_places(session, fit_class) <= 0:  # А1: нет свободных мест
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No free places on this class",
        )

    try:  # проверка абонемента в другом микросервисе - на ДАТУ ЗАНЯТИЯ
        has_subscription = has_active_subscription(client_id, fit_class.starts_at.date())
    except SubscriptionServiceUnavailable:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Subscription service is unavailable, try again later",
        )
    if not has_subscription:  # А2: абонемента нет, он истёк или истечёт до занятия
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No subscription valid on the class date: buy or renew it first",
        )

    booking = Booking(class_id=data.class_id, client_id=client_id,
                      status="active", created_at=datetime.now())
    session.add(booking)
    session.commit()
    session.refresh(booking)
    return {"message": "Booking created successfully", "booking_id": booking.id}


@booking_router.get("/my", response_model=List[Booking])
def retrieve_my_bookings(
    client_id: int = 1,  # номер клиента
    session: Session = Depends(get_session),
) -> List[Booking]:
    return session.exec(
        select(Booking).where(Booking.client_id == client_id).order_by(Booking.id)
    ).all()

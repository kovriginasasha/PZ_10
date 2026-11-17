from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlmodel import Session, select

from database.connection import get_session
from models.bookings import Booking
from models.classes import FitClass, FitClassCreate, FitClassPublic, FitClassUpdate

class_router = APIRouter(tags=["Classes"])


def booked_count(session: Session, class_id: int) -> int:
    return session.exec(
        select(func.count(Booking.id)).where(
            Booking.class_id == class_id, Booking.status == "active"
        )
    ).one()


def free_places(session: Session, fit_class: FitClass) -> int:
    return fit_class.capacity - booked_count(session, fit_class.id)


def to_public(session: Session, c: FitClass) -> dict:
    return {
        "id": c.id, "title": c.title, "trainer": c.trainer,
        "starts_at": c.starts_at, "capacity": c.capacity,
        "free_places": free_places(session, c),
    }


def get_class_or_404(session: Session, id: int) -> FitClass:
    fit_class = session.get(FitClass, id)
    if fit_class is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Class with supplied ID does not exist",
        )
    return fit_class


# READ: все записи
@class_router.get("/", response_model=List[FitClassPublic])
def retrieve_all_classes(session: Session = Depends(get_session)) -> List[FitClassPublic]:
    fit_classes = session.exec(select(FitClass).order_by(FitClass.starts_at)).all()
    return [to_public(session, c) for c in fit_classes]


# READ: одна запись по первичному ключу
@class_router.get("/{id}", response_model=FitClassPublic)
def retrieve_class(id: int, session: Session = Depends(get_session)) -> FitClassPublic:
    return to_public(session, get_class_or_404(session, id))


# CREATE
@class_router.post("/new", status_code=status.HTTP_201_CREATED)
def create_class(data: FitClassCreate, session: Session = Depends(get_session)) -> dict:
    new_class = FitClass(**data.model_dump())
    session.add(new_class)
    session.commit()
    session.refresh(new_class)
    return {"message": "Class created successfully", "id": new_class.id}


# UPDATE
@class_router.put("/edit/{id}", response_model=FitClassPublic)
def update_class(
    id: int, new_data: FitClassUpdate, session: Session = Depends(get_session)
) -> FitClassPublic:
    fit_class = get_class_or_404(session, id)
    changes = new_data.model_dump(exclude_unset=True)
    # нельзя уменьшить вместимость ниже числа уже записанных клиентов
    if "capacity" in changes and changes["capacity"] < booked_count(session, id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Capacity is less than the number of booked clients",
        )
    for key, value in changes.items():
        setattr(fit_class, key, value)
    session.add(fit_class)
    session.commit()
    session.refresh(fit_class)
    return to_public(session, fit_class)


# DELETE
@class_router.delete("/delete/{id}")
def delete_class(id: int, session: Session = Depends(get_session)) -> dict:
    fit_class = get_class_or_404(session, id)
    has_bookings = session.exec(select(Booking).where(Booking.class_id == id)).first()
    if has_bookings is not None:  # нельзя удалять занятие, на которое есть записи
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Class has bookings and cannot be deleted",
        )
    session.delete(fit_class)
    session.commit()
    return {"message": "Class deleted successfully"}

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from database.connection import get_session
from models.subscriptions import Subscription
from models.tariffs import Tariff, TariffCreate, TariffUpdate

tariff_router = APIRouter(tags=["Tariffs"])


# READ: все записи
@tariff_router.get("/", response_model=List[Tariff])
def retrieve_all_tariffs(session: Session = Depends(get_session)) -> List[Tariff]:
    statement = select(Tariff).order_by(Tariff.price)
    return session.exec(statement).all()


# READ: одна запись по первичному ключу
@tariff_router.get("/{id}", response_model=Tariff)
def retrieve_tariff(id: int, session: Session = Depends(get_session)) -> Tariff:
    tariff = session.get(Tariff, id)
    if tariff:
        return tariff
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Tariff with supplied ID does not exist",
    )


# CREATE
@tariff_router.post("/new", status_code=status.HTTP_201_CREATED)
def create_tariff(data: TariffCreate, session: Session = Depends(get_session)) -> dict:
    new_tariff = Tariff(**data.model_dump())
    session.add(new_tariff)       # объект в памяти сессии
    session.commit()              # транзакция фиксируется в БД
    session.refresh(new_tariff)   # подтягиваем из БД присвоенный id
    return {"message": "Tariff created successfully", "id": new_tariff.id}


# UPDATE
@tariff_router.put("/edit/{id}", response_model=Tariff)
def update_tariff(
    id: int, new_data: TariffUpdate, session: Session = Depends(get_session)
) -> Tariff:
    tariff = session.get(Tariff, id)
    if not tariff:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tariff with supplied ID does not exist",
        )
    # exclude_unset: меняем только те поля, которые прислал клиент
    for key, value in new_data.model_dump(exclude_unset=True).items():
        setattr(tariff, key, value)
    session.add(tariff)
    session.commit()
    session.refresh(tariff)
    return tariff


# DELETE
@tariff_router.delete("/delete/{id}")
def delete_tariff(id: int, session: Session = Depends(get_session)) -> dict:
    tariff = session.get(Tariff, id)
    if not tariff:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tariff with supplied ID does not exist",
        )
    # нельзя удалить тариф, по которому уже оформлены абонементы (целостность данных)
    used = session.exec(select(Subscription).where(Subscription.tariff_id == id)).first()
    if used is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Tariff is used by existing subscriptions and cannot be deleted",
        )
    session.delete(tariff)
    session.commit()
    return {"message": "Tariff deleted successfully"}

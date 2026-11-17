"""Подключение к базе данных (SQLite через SQLModel).
Файл БД booking.db создаётся автоматически рядом с сервисом."""
from datetime import datetime, timedelta
from pathlib import Path

from sqlmodel import Session, SQLModel, create_engine, select

from models.bookings import Booking  # noqa: F401  (нужно для создания таблицы)
from models.classes import FitClass

DB_FILE = Path(__file__).resolve().parent.parent / "booking.db"
DATABASE_URL = f"sqlite:///{DB_FILE}"

# echo=True: в терминале видны SQL-команды (CREATE TABLE, INSERT, SELECT ...)
engine = create_engine(DATABASE_URL, echo=True, connect_args={"check_same_thread": False})


def get_session():
    """Зависимость FastAPI: одна сессия на запрос, закрывается автоматически."""
    with Session(engine) as session:
        yield session


def conn() -> None:
    """Создаёт файл БД и таблицы (create_all), при первом запуске заполняет расписание."""
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        if session.exec(select(FitClass)).first() is not None:
            return
        base = datetime.now().replace(minute=0, second=0, microsecond=0) + timedelta(days=1)
        session.add_all([
            FitClass(title="Йога", trainer="Иванова А.", starts_at=base, capacity=10),
            FitClass(title="Силовая тренировка", trainer="Петров С.",
                     starts_at=base + timedelta(hours=2), capacity=2),  # всего 2 места
            FitClass(title="Кроссфит", trainer="Сидоров Д.",
                     starts_at=base + timedelta(hours=4), capacity=8),
            FitClass(title="Йога (через 60 дней)", trainer="Иванова А.",
                     starts_at=base + timedelta(days=60), capacity=10),  # позже срока месячного абонемента
        ])
        session.commit()

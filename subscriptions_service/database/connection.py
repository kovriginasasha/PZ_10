"""Подключение к базе данных (SQLite через SQLModel).
Файл БД subscriptions.db создаётся автоматически рядом с сервисом."""
from datetime import date, datetime, timedelta
from pathlib import Path

from sqlmodel import Session, SQLModel, create_engine, select

from models.subscriptions import Payment, Subscription
from models.tariffs import Tariff

DB_FILE = Path(__file__).resolve().parent.parent / "subscriptions.db"
DATABASE_URL = f"sqlite:///{DB_FILE}"

# check_same_thread=False: FastAPI обрабатывает запросы в разных потоках
# echo=True: в терминале видны SQL-команды (CREATE TABLE, INSERT, SELECT ...)
engine = create_engine(DATABASE_URL, echo=True, connect_args={"check_same_thread": False})


def get_session():
    """Зависимость FastAPI: одна сессия на запрос, закрывается автоматически."""
    with Session(engine) as session:
        yield session


def conn() -> None:
    """Создаёт файл БД и таблицы (create_all), при первом запуске заполняет их начальными данными."""
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        if session.exec(select(Tariff)).first() is not None:
            return
        session.add_all([
            Tariff(name="Месяц", price=2500, duration_days=30),
            Tariff(name="Квартал", price=6500, duration_days=90),
            Tariff(name="Год", price=21000, duration_days=365),
        ])
        session.commit()

        # Демо: у клиента 99 абонемент уже просрочен (закончился 10 дней назад),
        # но статус ещё 'active' - проверка сроков давно не запускалась.
        today = date.today()
        old = Subscription(client_id=99, tariff_id=1,
                           start_date=today - timedelta(days=40),
                           end_date=today - timedelta(days=10), status="active")
        session.add(old)
        session.flush()  # получаем id абонемента до commit
        session.add(Payment(client_id=99, tariff_id=1, subscription_id=old.id,
                            amount=2500, status="approved",
                            created_at=datetime.now() - timedelta(days=40)))
        session.commit()

from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from database.connection import conn
from routes.bookings import booking_router
from routes.classes import class_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    conn()  # при запуске создаём БД и таблицы
    yield


app = FastAPI(title="FitLife: сервис записи на тренировки", lifespan=lifespan)

# CORS: разрешаем странице интерфейса (другой адрес/порт) обращаться к этому сервису
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(class_router, prefix="/classes")
app.include_router(booking_router, prefix="/bookings")


@app.get("/", include_in_schema=False)
async def home():
    return RedirectResponse(url="/classes/")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8002, reload=True)

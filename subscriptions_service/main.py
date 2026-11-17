from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from database.connection import conn
from routes.subscriptions import subscription_router
from routes.tariffs import tariff_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    conn()  # при запуске создаём БД и таблицы
    yield


app = FastAPI(title="FitLife: сервис абонементов и оплаты", lifespan=lifespan)

# CORS: разрешаем странице интерфейса (другой адрес/порт) обращаться к этому сервису
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(tariff_router, prefix="/tariffs")
app.include_router(subscription_router, prefix="/subscriptions")


@app.get("/", include_in_schema=False)
async def home():
    return RedirectResponse(url="/tariffs/")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)

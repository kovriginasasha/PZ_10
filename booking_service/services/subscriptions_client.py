import os
from datetime import date

import httpx

SUBSCRIPTIONS_URL = os.getenv("SUBSCRIPTIONS_URL", "http://127.0.0.1:8001")


class SubscriptionServiceUnavailable(Exception):
    pass


def has_active_subscription(client_id: int, on_date: date) -> bool:
    """HTTP-запрос к сервису абонементов (межсервисное взаимодействие).
    Спрашиваем: действует ли абонемент клиента именно на дату занятия."""
    try:
        resp = httpx.get(
            f"{SUBSCRIPTIONS_URL}/subscriptions/active",
            params={"client_id": client_id, "on_date": on_date.isoformat()},
            timeout=3,
        )
    except httpx.RequestError:
        raise SubscriptionServiceUnavailable
    if resp.status_code == 200:
        return True
    if resp.status_code == 404:
        return False
    raise SubscriptionServiceUnavailable

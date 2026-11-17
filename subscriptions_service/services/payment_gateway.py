def charge(amount: float, card_token: str) -> bool:
    """Заглушка внешнего платёжного шлюза.
    Токен "declined" имитирует отказ в оплате (альтернативный сценарий А2)."""
    return card_token != "declined"

# Два набора команд для работы с записями в БД (ЛР №3)

Номер клиента (client_id) передаётся в теле запроса или параметром адреса (?client_id=1).
Сервисы должны быть запущены (порты 8001 и 8002).

## Набор 1. Сервис абонементов и оплаты (БД subscriptions.db), таблица tariff

    # READ: все тарифы
    curl -X GET 'http://127.0.0.1:8001/tariffs/' -H 'accept: application/json'

    # READ: тариф по первичному ключу
    curl -X GET 'http://127.0.0.1:8001/tariffs/1' -H 'accept: application/json'

    # CREATE: новый тариф (в ответе придёт id, при первом запуске это 4)
    curl -X POST 'http://127.0.0.1:8001/tariffs/new' -H 'accept: application/json' -H 'Content-Type: application/json' -d '{"name":"Полугодие","price":12000,"duration_days":180}'

    # UPDATE: изменить только цену
    curl -X PUT 'http://127.0.0.1:8001/tariffs/edit/4' -H 'accept: application/json' -H 'Content-Type: application/json' -d '{"price":11500}'

    # DELETE: удалить тариф
    curl -X DELETE 'http://127.0.0.1:8001/tariffs/delete/4' -H 'accept: application/json'

    # DELETE тарифа 1 -> 409: по нему оформлены абонементы (целостность данных)
    curl -X DELETE 'http://127.0.0.1:8001/tariffs/delete/1' -H 'accept: application/json'

    # Оплата абонемента: записи в таблицах subscription и payment
    curl -X POST 'http://127.0.0.1:8001/subscriptions/buy' -H 'accept: application/json' -H 'Content-Type: application/json' -d '{"client_id":1,"tariff_id":1,"card_token":"tok_visa_4242"}'

    # Действующий абонемент и вся история клиента
    curl -X GET 'http://127.0.0.1:8001/subscriptions/active?client_id=1'
    curl -X GET 'http://127.0.0.1:8001/subscriptions/my?client_id=1'

    # UPDATE массовый: просроченные абонементы -> status = expired
    curl -X POST 'http://127.0.0.1:8001/subscriptions/expire'

## Набор 2. Сервис записи на тренировки (БД booking.db), таблицы fitclass и booking

    # READ: расписание со свободными местами
    curl -X GET 'http://127.0.0.1:8002/classes/' -H 'accept: application/json'

    # READ: занятие по первичному ключу
    curl -X GET 'http://127.0.0.1:8002/classes/1' -H 'accept: application/json'

    # CREATE: новое занятие (при первом запуске id = 5)
    curl -X POST 'http://127.0.0.1:8002/classes/new' -H 'accept: application/json' -H 'Content-Type: application/json' -d '{"title":"Пилатес","trainer":"Орлова Е.","starts_at":"2026-12-01T18:00:00","capacity":12}'

    # UPDATE: изменить вместимость
    curl -X PUT 'http://127.0.0.1:8002/classes/edit/5' -H 'accept: application/json' -H 'Content-Type: application/json' -d '{"capacity":15}'

    # DELETE: удалить занятие
    curl -X DELETE 'http://127.0.0.1:8002/classes/delete/5' -H 'accept: application/json'

    # Запись на тренировку (нужен действующий абонемент): запись в таблице booking
    curl -X POST 'http://127.0.0.1:8002/bookings/' -H 'accept: application/json' -H 'Content-Type: application/json' -d '{"client_id":1,"class_id":1}'

    # Мои записи
    curl -X GET 'http://127.0.0.1:8002/bookings/my?client_id=1'

    # DELETE занятия 1 после записи -> 409: на него есть записи
    curl -X DELETE 'http://127.0.0.1:8002/classes/delete/1'

## Проверка содержимого БД напрямую (SQLite)

    cd subscriptions_service && sqlite3 subscriptions.db
    .tables
    SELECT * FROM tariff;
    SELECT * FROM subscription;
    SELECT * FROM payment;
    .quit

    cd booking_service && sqlite3 booking.db
    SELECT * FROM fitclass;
    SELECT * FROM booking;

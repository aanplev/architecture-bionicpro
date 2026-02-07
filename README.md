# Reports Platform (Airflow + ClickHouse + Keycloak + PKCE)

Учебный проект, демонстрирующий работу распределенной аналитической системы:

- сбор и агрегация данных через Apache Airflow
- хранение витрины в ClickHouse
- доступ к отчетам через Backend API
- аутентификация и авторизация через Keycloak (Authorization Code + PKCE)
- получение отчета через Web UI

Отчет может получить **только авторизованный пользователь** и **только для самого себя**  
(`user_id` берётся из `sub` JWT-токена).

---

## Запуск проекта (чистый старт, без кэшей)

Выполнить последовательно:

docker compose build --no-cache  
docker compose up -d

---

## Доступные сервисы

| Сервис       | URL |
|-------------|-----|
| Frontend    | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| Keycloak    | http://localhost:8080 |
| Airflow     | http://localhost:8082 |
| ClickHouse  | http://localhost:8123 |

---

## Keycloak

- Realm импортируется автоматически при старте контейнера
- Используется Authorization Code Flow с PKCE
- Frontend-клиент: `reports-frontend`

Тестовые пользователи находятся в `realm-export.json`.

---

## Airflow

- DAG: `crm_telemetry_daily_report`
- Расписание: `@daily`
- При первом старте ClickHouse пустой
- После выполнения DAG:
    - создается таблица `report_mart`
    - загружаются агрегированные данные

Проверка в ClickHouse:

SELECT * FROM report_mart;

---

## Backend API

### Healthcheck

GET /health

### Получение отчета

GET /reports  
Authorization: Bearer <access_token>

Особенности:
- `user_id` берется из `sub`
- данные возвращаются только для текущего пользователя
- тестовый пользователь - user1
- если данных нет - возвращается пустой список
- смотреть network

---

## Frontend

1. Открыть http://localhost:3000
2. Нажать Login
3. Авторизоваться в Keycloak
4. Нажать Download Report
5. Получить отчет текущего пользователя в network

---

## Как проверить

1. Запустить проект
2. Зайти в Airflow и убедиться, что DAG отработал
3. Проверить, что данные появились в ClickHouse
4. Авторизоваться во Frontend
5. Скачать отчет - доступ только к своим данным

---

## Примечания

- Все сервисы поднимаются автоматически
- Ручных действий в ClickHouse делать не требуется
- Проект проверяется как единая система (Frontend + Backend + Keycloak + Airflow)

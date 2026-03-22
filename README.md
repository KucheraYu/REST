# Лабораторна робота №2 — REST API

## Мета
Створення серверної частини застосунку з чіткою структурою API.

## Опис
REST API з CRUD-операціями, пагінацією, сортуванням та фільтрацією.
Три зв'язані сутності з вкладеними відповідями.

## Сутності та зв'язки

User (id, name, email)
  │ 1:N
  ▼
Post (id, title, content, user_id)
  │ 1:N
  ▼
Comment (id, text, post_id, user_id)

## Ендпоінти

### Users
| Метод | URL | Код | Опис |
|-------|-----|-----|------|
| GET | /users | 200 | Список |
| GET | /users/{id} | 200/404 | Один (з постами та коментарями) |
| POST | /users | 201 | Створити |
| PUT | /users/{id} | 200/404 | Оновити |
| DELETE | /users/{id} | 204/404 | Видалити |

### Posts
| Метод | URL | Код | Опис |
|-------|-----|-----|------|
| GET | /posts | 200 | Список |
| GET | /posts/{id} | 200/404 | Один (з коментарями) |
| POST | /posts | 201/400 | Створити |
| PUT | /posts/{id} | 200/404 | Оновити |
| DELETE | /posts/{id} | 204/404 | Видалити |

### Comments
| Метод | URL | Код | Опис |
|-------|-----|-----|------|
| GET | /comments | 200 | Список |
| GET | /comments/{id} | 200/404 | Один |
| POST | /comments | 201/400 | Створити |
| PUT | /comments/{id} | 200/404 | Оновити |
| DELETE | /comments/{id} | 204/404 | Видалити |

## Пагінація, сортування, фільтрація

| Параметр | Де | Приклад |
|----------|-----|---------|
| page | скрізь | ?page=1 |
| limit | скрізь | ?limit=10 |
| sort | скрізь | ?sort=name або ?sort=-name |
| name | /users | ?name=Іван |
| user_id | /posts, /comments | ?user_id=3 |
| title | /posts | ?title=python |
| post_id | /comments | ?post_id=1 |

Відповідь на GET-списки містить:
- data — масив записів
- total — загальна кількість
- page — поточна сторінка
- limit — записів на сторінку

## Запуск

pip install fastapi uvicorn sqlalchemy "pydantic[email]"
uvicorn main:app --reload

Swagger UI: http://127.0.0.1:8000/docs

## Стек
Python 3, FastAPI, SQLAlchemy, SQLite, Pydantic v2

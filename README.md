# Лабораторна робота №2 — REST API

## Мета

Створення серверної частини застосунку з чіткою структурою API.

## Стек

Python 3, FastAPI, SQLAlchemy, SQLite, Pydantic v2, JWT, bcrypt

## Сутності та зв'язки

```
User (id, name, email, password_hash)
  │ 1:N
  ▼
Post (id, title, content, user_id)
  │ 1:N
  ▼
Comment (id, text, post_id, user_id)
```

## Ендпоінти

### Auth

| Метод  | URL             | Код       | Опис                  |
|--------|-----------------|-----------|----------------------|
| POST   | /auth/register  | 201       | Реєстрація           |
| POST   | /auth/login     | 200 / 401 | Вхід                 |
| GET    | /auth/me        | 200       | Поточний користувач  |

### Users

| Метод  | URL          | Код       | Опис     |
|--------|--------------|-----------|----------|
| GET    | /users       | 200       | Список   |
| GET    | /users/{id}  | 200 / 404 | Один     |
| POST   | /users       | 201       | Створити |
| PUT    | /users/{id}  | 200 / 404 | Оновити  |
| DELETE | /users/{id}  | 204 / 404 | Видалити |

### Posts

| Метод  | URL         | Код       | Опис     |
|--------|-------------|-----------|----------|
| GET    | /posts      | 200       | Список   |
| GET    | /posts/{id} | 200 / 404 | Один     |
| POST   | /posts      | 201 / 400 | Створити |
| PUT    | /posts/{id} | 200 / 404 | Оновити  |
| DELETE | /posts/{id} | 204 / 404 | Видалити |

### Comments

| Метод  | URL             | Код       | Опис     |
|--------|-----------------|-----------|----------|
| GET    | /comments       | 200       | Список   |
| GET    | /comments/{id}  | 200 / 404 | Один     |
| POST   | /comments       | 201 / 400 | Створити |
| PUT    | /comments/{id}  | 200 / 404 | Оновити  |
| DELETE | /comments/{id}  | 204 / 404 | Видалити |

## Пагінація, сортування, фільтрація

| Параметр | Де                  | Приклад              |
|----------|---------------------|----------------------|
| page     | всі маршрути        | `?page=1`            |
| limit    | всі маршрути        | `?limit=10`          |
| sort     | всі маршрути        | `?sort=name`, `?sort=-name` |
| name     | /users              | `?name=Іван`         |
| user_id  | /posts, /comments   | `?user_id=3`         |
| title    | /posts              | `?title=python`      |
| post_id  | /comments           | `?post_id=1`         |

## Запуск

```bash
pip install fastapi uvicorn sqlalchemy "pydantic[email]" bcrypt pyjwt
uvicorn main:app --reload
```

Swagger UI: http://127.0.0.1:8000/docs

---

# Лабораторна робота №3 — Frontend-застосунок

## Мета

Створити клієнтський застосунок із базовою архітектурою, підключений до API.

## Стек

React 18, React Router, Axios, Context API, CSS

## Сторінки

| Сторінка | URL     | Опис                        |
|----------|---------|-----------------------------|
| Login    | /login  | Вхід та реєстрація          |
| Users    | /users  | CRUD користувачів           |
| Posts    | /posts  | CRUD постів та коментарів   |

## Функціональність

- Авторизація через JWT-токен
- Глобальний стан (React Context API)
- Захищені маршрути (ProtectedRoute)
- Обробка помилок (axios interceptor)
- Збереження токена в localStorage
- Навігація (React Router)

## Структура проєкту

```
REST/
├── main.py                   # бекенд (FastAPI + JWT)
└── frontend/
    └── src/
        ├── App.js             # маршрутизація
        ├── App.css            # стилі
        ├── context/
        │   └── AuthContext.js # глобальний стан авторизації
        ├── api/
        │   └── api.js         # axios-клієнт із токеном
        ├── components/
        │   └── Navbar.js      # навігаційна панель
        └── pages/
            ├── LoginPage.js   # логін / реєстрація
            ├── UsersPage.js   # CRUD користувачів
            └── PostsPage.js   # CRUD постів + коментарі
```

## Запуск

```bash
cd frontend
npm install
npm start
```

Відкриється: http://localhost:3000
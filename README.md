![Python](https://img.shields.io/badge/Python-3-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-✓-009688)
![React](https://img.shields.io/badge/React-18-61dafb)
![Coverage](https://img.shields.io/badge/Coverage-88%25-brightgreen)

# REST API + Frontend + Testing

## Зміст

- [Лабораторна робота №2 — REST API](#лабораторна-робота-2--rest-api)
- [Лабораторна робота №3 — Frontend-застосунок](#лабораторна-робота-3--frontend-застосунок)
- [Лабораторна робота №4 — Тестування](#лабораторна-робота-4--тестування)
- [Структура проєкту](#структура-проєкту)

---

## Лабораторна робота №2 — REST API

### Мета

Створення серверної частини застосунку з чіткою структурою API.

### Стек

Python 3, FastAPI, SQLAlchemy, SQLite, Pydantic v2, JWT, bcrypt

### Сутності та зв'язки

```
┌─────────────────────────────┐
│  User                       │
│  id, name, email,           │
│  password_hash              │
└──────────────┬──────────────┘
               │ 1:N
               ▼
┌─────────────────────────────┐
│  Post                       │
│  id, title, content,        │
│  user_id                    │
└──────────────┬──────────────┘
               │ 1:N
               ▼
┌─────────────────────────────┐
│  Comment                    │
│  id, text, post_id,         │
│  user_id                    │
└─────────────────────────────┘
```

### Ендпоінти

#### Auth

| Метод | URL            | Код       | Опис                 |
|-------|----------------|-----------|----------------------|
| POST  | /auth/register | 201       | Реєстрація           |
| POST  | /auth/login    | 200 / 401 | Вхід                 |
| GET   | /auth/me       | 200       | Поточний користувач  |

#### Users

| Метод  | URL          | Код       | Опис     |
|--------|--------------|-----------|----------|
| GET    | /users       | 200       | Список   |
| GET    | /users/{id}  | 200 / 404 | Один     |
| POST   | /users       | 201       | Створити |
| PUT    | /users/{id}  | 200 / 404 | Оновити  |
| DELETE | /users/{id}  | 204 / 404 | Видалити |

#### Posts

| Метод  | URL          | Код       | Опис     |
|--------|--------------|-----------|----------|
| GET    | /posts       | 200       | Список   |
| GET    | /posts/{id}  | 200 / 404 | Один     |
| POST   | /posts       | 201 / 400 | Створити |
| PUT    | /posts/{id}  | 200 / 404 | Оновити  |
| DELETE | /posts/{id}  | 204 / 404 | Видалити |

#### Comments

| Метод  | URL             | Код       | Опис     |
|--------|-----------------|-----------|----------|
| GET    | /comments       | 200       | Список   |
| GET    | /comments/{id}  | 200 / 404 | Один     |
| POST   | /comments       | 201 / 400 | Створити |
| PUT    | /comments/{id}  | 200 / 404 | Оновити  |
| DELETE | /comments/{id}  | 204 / 404 | Видалити |

### Пагінація, сортування, фільтрація

| Параметр | Де                  | Приклад               |
|----------|---------------------|-----------------------|
| page     | всі маршрути        | `?page=1`             |
| limit    | всі маршрути        | `?limit=10`           |
| sort     | всі маршрути        | `?sort=name`, `?sort=-name` |
| name     | /users              | `?name=Іван`          |
| user_id  | /posts, /comments   | `?user_id=3`          |
| title    | /posts              | `?title=python`       |
| post_id  | /comments           | `?post_id=1`          |

### Запуск

```bash
pip install fastapi uvicorn sqlalchemy "pydantic[email]" bcrypt pyjwt
uvicorn main:app --reload
```

Swagger UI: http://127.0.0.1:8000/docs

---

## Лабораторна робота №3 — Frontend-застосунок

### Мета

Створити клієнтський застосунок із базовою архітектурою, підключений до API.

### Стек

React 18, React Router, Axios, Context API, CSS

### Сторінки

| Сторінка | URL     | Опис                       |
|----------|---------|----------------------------|
| Login    | /login  | Вхід та реєстрація         |
| Users    | /users  | CRUD користувачів          |
| Posts    | /posts  | CRUD постів та коментарів  |

### Функціональність

- Авторизація через JWT-токен
- Глобальний стан (React Context API)
- Захищені маршрути (ProtectedRoute)
- Обробка помилок (axios interceptor)
- Збереження токена в localStorage
- Навігація (React Router)

### Запуск

```bash
cd frontend
npm install
npm start
```

Відкриється: http://localhost:3000

---

## Лабораторна робота №4 — Тестування

### Мета

Покрити серверну частину unit- та інтеграційними тестами, провести навантажувальне тестування та скрапінг фронтенду.

### Code Coverage

| Модуль  | Покриття |
|---------|----------|
| main.py | 88%      |

Команда для запуску тестів із генерацією звіту покриття:

```bash
pytest tests/test_api.py -v --cov=main --cov-report=html
```

HTML-звіт генерується в папку `htmlcov/`.

---

### Unit-тести

Файл: `tests/test_api.py`

| Клас              | К-сть | Що перевіряє                                                                                      |
|-------------------|-------|---------------------------------------------------------------------------------------------------|
| TestAuth          | 6     | Реєстрація, дублікат email, логін, невірний пароль, `/auth/me` з токеном і без                    |
| TestUsersCRUD     | 7     | Створення, пагінація, сортування, фільтрація, вкладені дані (пости + коментарі), оновлення, видалення |
| TestPostsCRUD     | 4     | Створення, отримання з коментарями, оновлення, видалення                                          |
| TestCommentsCRUD  | 4     | Створення, помилка при неіснуючому пості, фільтрація за post_id, видалення                       |
| **Разом**         | **21**|                                                                                                   |

---

### Інтеграційний тест

Клас `TestComplexScenario`, метод `test_full_workflow`.

Сценарій виконується як єдиний ланцюжок викликів, де результат кожного є вхідними даними для наступного:

1. `POST /auth/register` — реєстрація нового користувача
2. `GET /auth/me` — отримання `user_id` поточного користувача
3. `POST /posts` — створення поста з отриманим `user_id`
4. `POST /comments` — створення коментаря з отриманим `post_id`
5. `GET /users/{id}` — перевірка, що пост і коментар відображаються у вкладеній відповіді

**Ключовий акцент:** результат одного виклику API використовується як вхідні дані для наступного.

---

### Performance-тестування (Locust)

Файл: `tests/performance/locustfile.py`

| Сценарій                                                        | Вага |
|-----------------------------------------------------------------|------|
| `GET /users`                                                    | 3    |
| `GET /posts`                                                    | 3    |
| `GET /auth/me`                                                  | 2    |
| `POST /posts` → `POST /comments` → `DELETE /posts` (складний)  | 1    |

- `on_start`: автоматична реєстрація користувача перед початком тесту
- Складний сценарій використовує `id` щойно створеного поста для наступних запитів

Команда запуску:

```bash
locust -f tests/performance/locustfile.py --host=http://localhost:8000
```

Веб-інтерфейс Locust: http://localhost:8089

---

### Скрапінг (Selenium)

Файл: `tests/scraper/scraper.py`

Сценарій по кроках:

1. Відкрити `http://localhost:3000/login`
2. Клікнути кнопку «Register»
3. Заповнити поля: ім'я, email, пароль
4. Натиснути Submit → авторизація
5. Зчитати всі рядки таблиці Users (id, name, email)
6. Клікнути вкладку Posts
7. Порахувати кількість постів

Результат виводиться в консоль. Використовується headless Chrome.

Команда запуску:

```bash
python tests/scraper/scraper.py
```

---

## Структура проєкту

```
REST/
├── main.py                        # бекенд (FastAPI + JWT)
├── frontend/
│   └── src/
│       ├── App.js                 # маршрутизація
│       ├── App.css                # стилі
│       ├── context/
│       │   └── AuthContext.js     # глобальний стан авторизації
│       ├── api/
│       │   └── api.js             # axios-клієнт із токеном
│       ├── components/
│       │   └── Navbar.js          # навігаційна панель
│       └── pages/
│           ├── LoginPage.js       # логін / реєстрація
│           ├── UsersPage.js       # CRUD користувачів
│           └── PostsPage.js       # CRUD постів + коментарі
├── tests/
│   ├── __init__.py
│   ├── test_api.py                # unit + інтеграційні тести (22 тест)
│   ├── performance/
│   │   ├── __init__.py
│   │   └── locustfile.py          # навантажувальне тестування
│   └── scraper/
│       ├── __init__.py
│       └── scraper.py             # Selenium-скрапінг фронтенду
├── htmlcov/                       # звіт покриття (HTML)
└── venv/                          # віртуальне середовище Python
```
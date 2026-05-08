# Bible Study Circle — Web App

Веб-приложение для управления и публикации контента библейского кружка: курсы по книгам Библии, тематические лекции, справочные материалы.

## Стек

- **FastAPI** — backend + API
- **SQLite** — база данных
- **Jinja2** — серверный рендеринг шаблонов
- **Docker** + **Traefik** — деплой

## Структура

```
bible-app/
├── app/
│   ├── main.py              # FastAPI app
│   ├── config.py            # Env-based config
│   ├── database.py          # SQLAlchemy models
│   ├── schemas.py           # Pydantic validation
│   ├── deps.py              # Dependencies (auth, templates)
│   ├── routers/
│   │   ├── api_courses.py   # Course CRUD
│   │   ├── api_lectures.py  # Lecture CRUD
│   │   ├── api_reference.py # Reference page CRUD
│   │   ├── api_images.py    # Image upload
│   │   └── web.py           # Web page routes
│   └── templates/           # Jinja2 templates
├── static/
│   ├── style.css
│   └── app.js
├── data/                    # SQLite DB + images (gitignored)
├── Dockerfile
├── docker-compose.yml
├── Jenkinsfile
├── migrate.py               # Import existing content
└── requirements.txt
```

## Быстрый старт (локально)

```bash
# Установить зависимости
pip install -r requirements.txt

# Задать API-ключ
export API_KEY=my-secret-key

# Запустить
uvicorn app.main:app --reload

# Открыть:
#   http://localhost:8000          — сайт
#   http://localhost:8000/docs     — Swagger UI
```

## API

Все write-операции требуют заголовок `X-API-Key`.

### Курсы

| Метод | Путь | Описание |
|-------|------|----------|
| `GET` | `/api/courses/` | Список курсов |
| `POST` | `/api/courses/` | Создать курс |
| `GET` | `/api/courses/{slug}` | Получить курс |
| `PUT` | `/api/courses/{slug}` | Обновить курс |
| `DELETE` | `/api/courses/{slug}` | Удалить курс |

### Лекции

| Метод | Путь | Описание |
|-------|------|----------|
| `GET` | `/api/courses/{course}/lectures/` | Список лекций |
| `POST` | `/api/courses/{course}/lectures/` | Создать лекцию |
| `GET` | `/api/courses/{course}/lectures/{slug}` | Получить лекцию |
| `PUT` | `/api/courses/{course}/lectures/{slug}` | Обновить лекцию |
| `DELETE` | `/api/courses/{course}/lectures/{slug}` | Удалить лекцию |

### Справочные страницы

| Метод | Путь | Описание |
|-------|------|----------|
| `GET` | `/api/courses/{course}/reference/` | Список |
| `POST` | `/api/courses/{course}/reference/` | Создать |
| `GET` | `/api/courses/{course}/reference/{slug}` | Получить |
| `PUT` | `/api/courses/{course}/reference/{slug}` | Обновить |
| `DELETE` | `/api/courses/{course}/reference/{slug}` | Удалить |

### Изображения

| Метод | Путь | Описание |
|-------|------|----------|
| `POST` | `/api/images/` | Загрузить (`multipart/form-data`, поле `file`) |
| `GET` | `/api/images/` | Список |
| `DELETE` | `/api/images/{filename}` | Удалить |

### Пример: добавить лекцию

```bash
curl -X POST http://localhost:8000/api/courses/luke/lectures/ \
  -H "X-API-Key: my-secret-key" \
  -H "Content-Type: application/json" \
  -d '{
    "slug": "9-10",
    "title": "Лк 9–10",
    "subtitle": "Преображение · Послание семидесяти",
    "chapter_start": 9,
    "chapter_end": 10,
    "content": "<div class=\"section-header\">Лк 9:1–6</div>...",
    "sort_order": 5
  }'
```

### Пример: обновить контент лекции

```bash
curl -X PUT http://localhost:8000/api/courses/luke/lectures/9-10 \
  -H "X-API-Key: my-secret-key" \
  -H "Content-Type: application/json" \
  -d '{"content": "<div class=\"section-header\">Лк 9:1–6</div>...обновлённый контент..."}'
```

## Деплой

### Docker Compose

```bash
# Создать .env
cp .env.example .env
# Отредактировать .env: задать API_KEY, DOMAIN

# Запустить
docker compose up -d --build
```

Traefik маршрутизирует трафик по домену из `DOMAIN` env var.

### Jenkins

Jenkinsfile:
1. Собирает Docker-образ
2. Запускает `docker compose up -d --build --force-recreate`

Требуется Jenkins credential `bible-study-domain` с доменом.

## Миграция существующего контента

```bash
# Запустить приложение
uvicorn app.main:app &

# Импортировать лекции Луки
python migrate.py --api-url http://localhost:8000 --api-key my-secret-key --source-dir /path/to/outputs
```

## Добавление нового курса

```bash
# Создать курс
curl -X POST http://localhost:8000/api/courses/ \
  -H "X-API-Key: my-secret-key" \
  -H "Content-Type: application/json" \
  -d '{
    "slug": "genesis",
    "title": "Бытие",
    "subtitle": "Книга начал",
    "course_type": "book",
    "sort_order": 2
  }'

# Добавить лекции
curl -X POST http://localhost:8000/api/courses/genesis/lectures/ \
  -H "X-API-Key: my-secret-key" \
  -H "Content-Type: application/json" \
  -d '{
    "slug": "1-2",
    "title": "Быт 1–2",
    "subtitle": "Творение",
    "chapter_start": 1,
    "chapter_end": 2,
    "content": "...",
    "sort_order": 1
  }'
```

## Переменные окружения

| Переменная | По умолчанию               | Описание |
|------------|----------------------------|----------|
| `API_KEY` | `dev-key-change-me`        | Ключ для write-API |
| `SITE_TITLE` | `Библейский кружок`        | Заголовок сайта |
| `SITE_SUBTITLE` | `Комментарий для XXI века` | Подзаголовок |
| `DATABASE_URL` | `sqlite:///data/bible.db`  | Путь к SQLite |
| `DOMAIN` | —                          | Домен для Traefik (в .env) |

# Recommendation Engine API

Микросервис для рекомендации объектов недвижимости на основе векторного поиска.

## Стек технологий
- Python 3.10
- FastAPI
- Qdrant (векторная БД)
- Redis (кэширование)
- Prometheus + Grafana (мониторинг)
- Docker

## Запуск
```bash
docker-compose up --build
```

## Доступные сервисы
- API: http://localhost:8000/docs
- Qdrant Dashboard: http://localhost:6333/dashboard
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (логин: admin, пароль: admin)

## Пример запроса
```bash
GET /recommend?query=квартира+москва&min_price=10000000&max_price=20000000&rooms=2
```

## Запуск тестов
```bash
pytest
```

## Автор
Илья Гуриков
```

### 11. .gitignore
```
__pycache__/
*.pyc
.env
.venv
qdrant_storage/
*.log
```

### Структура проекта:
```
.
├── .github
│   └── workflows
│       └── test.yml
├── app
│   ├── __init__.py
│   ├── healthcheck.py
│   ├── main.py
│   └── qdrant_utils.py
├── data
│   └── sample_data.json
├── tests
│   └── test_api.py
├── .env
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── prometheus.yml
├── README.md
└── requirements.txt
```
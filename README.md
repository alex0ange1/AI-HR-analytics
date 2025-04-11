# AI-HR-analytics
Project for GazpromNeft

## 🚀 Quick Start

To launch the application containers, run the following command:

```bash
docker compose --env-file ./backend/.env up
```

## Setting

To start the migration, run the following command:

```bash
docker-compose exec backend alembic revision --autogenerate -m 'name'
```
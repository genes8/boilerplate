# Backend - Enterprise Boilerplate

FastAPI backend aplikacija za enterprise boilerplate.

## Development Setup

### Prerequisites

- Python 3.11+
- Poetry

### Installation

```bash
# Install Poetry (if not already installed)
pip3 install poetry

# Install dependencies
poetry install

# Activate virtual environment
poetry shell
```

### Environment Configuration

```bash
# Copy environment template
cp ../.env.example .env

# Edit with your configuration
nano .env
```

### Database Setup

```bash
# Generate initial migration
alembic revision --autogenerate -m "Initial migration"

# Apply migrations
alembic upgrade head
```

### Running the Application

```bash
# Development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or with Poetry
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app instance
│   ├── config.py            # Configuration
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       └── endpoints.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── security.py      # JWT, password hashing
│   │   └── database.py      # Database connection
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py          # Base model
│   │   └── user.py          # User model
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── user.py          # Pydantic schemas
│   ├── services/
│   │   ├── __init__.py
│   │   └── auth.py          # Business logic
│   └── utils/
│       ├── __init__.py
│       └── helpers.py       # Utility functions
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Test configuration
│   └── test_auth.py         # Auth tests
├── alembic/
│   ├── versions/
│   ├── env.py
│   └── alembic.ini
├── pyproject.toml
└── poetry.lock
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test
pytest tests/test_auth.py
```

## Code Quality

```bash
# Format code
black .
isort .

# Lint
ruff check .

# Type check
mypy .
```

## Environment Variables

Key variables for development:

- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string
- `JWT_SECRET` - JWT signing secret
- `ENVIRONMENT` - development/production

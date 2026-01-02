.PHONY: help install dev-setup lint format test test-coverage docker-up docker-down clean build deploy

# Default target
help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Backend commands
install: ## Install all dependencies (backend + frontend)
	@echo "Installing backend dependencies..."
	cd backend && poetry install --with dev
	@echo "Installing frontend dependencies..."
	cd frontend && npm install

dev-setup: ## Set up development environment
	@echo "Setting up development environment..."
	@echo "Installing backend dependencies..."
	cd backend && poetry install --with dev
	@echo "Installing frontend dependencies..."
	cd frontend && npm install
	@echo "Setting up pre-commit hooks..."
	cd backend && poetry run pre-commit install
	@echo "Starting Docker services..."
	docker compose -f docker-compose.dev.yml up -d
	@echo "Waiting for services to be ready..."
	sleep 10
	@echo "Testing database connection..."
	cd backend && poetry run python scripts/test_db_connection.py
	@echo "Testing Redis connection..."
	cd backend && poetry run python scripts/test_redis_connection.py
	@echo "Development environment ready!"

lint: ## Run linting for both backend and frontend
	@echo "Linting backend..."
	cd backend && poetry run ruff check .
	@echo "Linting frontend..."
	cd frontend && npm run lint

format: ## Run formatting for both backend and frontend
	@echo "Formatting backend..."
	cd backend && poetry run ruff format .
	@echo "Formatting frontend..."
	cd frontend && npm run format

format-check: ## Check formatting without changing files
	@echo "Checking backend formatting..."
	cd backend && poetry run ruff format --check .
	@echo "Checking frontend formatting..."
	cd frontend && npm run format:check

type-check: ## Run type checking for both backend and frontend
	@echo "Type checking backend..."
	cd backend && poetry run mypy app/ --ignore-missing-imports
	@echo "Type checking frontend..."
	cd frontend && npm run type-check

test: ## Run all tests
	@echo "Running backend tests..."
	cd backend && poetry run pytest tests/ -v
	@echo "Running frontend tests..."
	cd frontend && npm run test:unit

test-coverage: ## Run tests with coverage
	@echo "Running backend tests with coverage..."
	cd backend && poetry run pytest tests/ -v --cov=app --cov-report=term-missing --cov-report=html
	@echo "Running frontend tests with coverage..."
	cd frontend && npm run test:coverage

test-watch: ## Run tests in watch mode
	@echo "Running backend tests in watch mode..."
	cd backend && poetry run pytest tests/ -v -f

# Database commands
db-up: ## Start database services
	docker compose -f docker-compose.dev.yml up -d postgres redis

db-down: ## Stop database services
	docker compose -f docker-compose.dev.yml down

db-reset: ## Reset database (delete volumes and restart)
	docker compose -f docker-compose.dev.yml down -v
	docker compose -f docker-compose.dev.yml up -d postgres redis

db-test: ## Test database connection
	cd backend && poetry run python scripts/test_db_connection.py

redis-test: ## Test Redis connection
	cd backend && poetry run python scripts/test_redis_connection.py

# Migration commands
db-migrate: ## Run database migrations
	cd backend && poetry run alembic upgrade head

db-migrate-create: ## Create new migration (use MSG="migration message")
	@if [ -z "$(MSG)" ]; then echo "Usage: make db-migrate-create MSG='migration message'"; exit 1; fi
	cd backend && poetry run alembic revision --autogenerate -m "$(MSG)"

db-migrate-down: ## Rollback last migration
	cd backend && poetry run alembic downgrade -1

# Development server commands
dev-backend: ## Start backend development server
	cd backend && poetry run uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload

dev-frontend: ## Start frontend development server
	cd frontend && npm run dev

dev: ## Start both backend and frontend servers
	@echo "Starting backend server..."
	cd backend && poetry run uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload &
	@echo "Starting frontend server..."
	cd frontend && npm run dev &
	@echo "Both servers started. Press Ctrl+C to stop."
	@wait

# Docker commands
docker-up: ## Start all Docker services
	docker compose -f docker-compose.dev.yml up -d

docker-down: ## Stop all Docker services
	docker compose -f docker-compose.dev.yml down

docker-logs: ## Show Docker logs
	docker compose -f docker-compose.dev.yml logs -f

docker-clean: ## Clean Docker images and volumes
	docker system prune -f
	docker volume prune -f

# Build commands
build-backend: ## Build backend Docker image
	docker build -t enterprise-boilerplate-backend:latest ./backend

build-frontend: ## Build frontend Docker image
	docker build -t enterprise-boilerplate-frontend:latest ./frontend

build: ## Build all Docker images
	$(MAKE) build-backend
	$(MAKE) build-frontend

# Production commands
prod-up: ## Start production environment
	docker compose -f docker-compose.yml up -d

prod-down: ## Stop production environment
	docker compose -f docker-compose.yml down

prod-logs: ## Show production logs
	docker compose -f docker-compose.yml logs -f

# Security commands
security-scan: ## Run security scan
	@echo "Running security scan on backend..."
	cd backend && poetry run safety check
	@echo "Running security scan on dependencies..."
	cd backend && poetry run pip-audit

security-update: ## Update dependencies for security
	@echo "Updating backend dependencies..."
	cd backend && poetry update
	@echo "Updating frontend dependencies..."
	cd frontend && npm audit fix

# Cleanup commands
clean: ## Clean up generated files
	@echo "Cleaning backend..."
	cd backend && find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	cd backend && find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	cd backend && find . -type f -name "*.pyc" -delete 2>/dev/null || true
	cd backend && rm -rf .coverage htmlcov/ .pytest_cache/ 2>/dev/null || true
	@echo "Cleaning frontend..."
	cd frontend && rm -rf dist/ build/ .nyc_output/ coverage/ 2>/dev/null || true
	cd frontend && rm -rf node_modules/.cache 2>/dev/null || true

clean-all: clean ## Clean everything including Docker
	$(MAKE) docker-clean
	$(MAKE) clean

# Deployment commands (placeholder for future CI/CD)
deploy-staging: ## Deploy to staging (placeholder)
	@echo "Deploy to staging - not implemented yet"

deploy-prod: ## Deploy to production (placeholder)
	@echo "Deploy to production - not implemented yet"

# Pre-commit commands
pre-commit-run: ## Run pre-commit hooks manually
	cd backend && poetry run pre-commit run --all-files

pre-commit-update: ## Update pre-commit hooks
	cd backend && poetry run pre-commit autoupdate

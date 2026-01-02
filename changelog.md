# Changelog

All notable changes to this project will be documented in this file.

---

## [1.9.0] - 2026-01-02

### Added - Phase 0.7: CI/CD Pipeline - Basic

- **GitHub Actions CI** - Kompletnan CI pipeline:
  - `.github/workflows/ci.yml` sa backend i frontend jobovima
  - PostgreSQL i Redis services za testiranje
  - Ruff linting i formatting za Python
  - MyPy type checking za Python
  - ESLint i Prettier za TypeScript/JavaScript
  - Unit tests sa coverage reporting
  - Security scanning sa Trivy
  - Docker image building i testing
- **Makefile** - 40+ development komandi:
  - `make dev-setup` - kompletna postavka okruženja
  - `make lint` - linting za backend/frontend
  - `make test` - unit tests sa coverage
  - `make docker-up/down` - Docker management
  - `make db-*` - database migracije i testiranje
  - `make clean` - cleanup utilities
- **Pre-commit Hooks** - Automatski code quality:
  - Ruff (lint + format) za Python
  - MyPy type checking
  - Black formatting
  - ESLint/Prettier za frontend
  - YAML/JSON/Markdown linting
  - Security scanning (Bandit, Safety)
  - Docker file linting (Hadolint)
- **Development Tools** - Additional dependencies:
  - `safety` - dependency vulnerability scanning
  - `bandit` - security linting
  - `pip-audit` - audit installed packages
- **Code Quality** - Standardizovani workflow:
  - Automatsko formatiranje na svakom commit-u
  - Type checking pre push-a
  - Security scanning u CI/CD
  - Coverage reporting na Codecov

### Task Status
- [x] Task 0.7 - CI/CD Pipeline - Basic (COMPLETED)

---

## [1.8.0] - 2026-01-02

### Added - Phase 0.6: Redis Connection Setup

- **Redis Connection Pool** - Kompletna Redis integracija:
  - `app/core/redis.py` sa async connection pool (max_connections=20)
  - Connection health check svakih 30 sekundi
  - Retry on timeout sa socket timeout od 5 sekundi
  - `get_redis()` dependency za FastAPI injection
- **RedisCache Class** - High-level cache operations:
  - String, JSON, numeric operations (increment/decrement)
  - TTL management, key existence checks
  - Pattern-based key deletion (`delete_pattern`)
  - JSON serialization/deserialization automatski
- **Cache Key Utilities** - Organizovani cache keys:
  - `cache_key()` - generički key builder
  - `session_cache_key()` - session-specifični keys
  - `user_cache_key()` - user-specifični keys
  - `generate_session_id()` - UUID-based session IDs
- **Application Lifecycle** - Redis integration:
  - `init_redis()` test konekcije na startup
  - `close_redis()` pravilno gašenje konekcija
  - Status logging za Redis konekciju
- **Test Endpoints** - `/test/redis/*` API endpoints:
  - Ping, GET/SET/DELETE cache operations
  - JSON cache operations
  - Session management endpoints
  - Key listing sa pattern matching
- **Test Script** - `scripts/test_redis_connection.py` za verifikaciju
- **Docker Integration** - Redis radi na portu 6380 (zbog konflikta)

### Task Status
- [x] Task 0.6 - Redis Connection Setup (COMPLETED)

---

## [1.7.0] - 2026-01-02

### Added - Phase 0.5: Database Connection & Alembic Setup

- **SQLAlchemy Async Engine** - Kompletna database konfiguracija:
  - `app/core/database.py` sa async engine i session management
  - Connection pooling (pool_size=10, max_overflow=20)
  - Pool pre-ping za connection validation
  - Pool recycle nakon 1 sata
  - `get_db` dependency za FastAPI injection
  - `DbSession` type alias za čistiji kod
  - `init_db()` i `close_db()` lifecycle funkcije
- **Base Model Classes** - Reusable model mixins:
  - `app/models/base.py` sa BaseModel, UUIDMixin, TimestampMixin
  - UUID primary key (auto-generated)
  - `created_at` i `updated_at` timestamps (server-side defaults)
  - `to_dict()` helper metoda
- **Alembic Setup** - Async migration support:
  - Inicijalizovan Alembic sa `alembic init`
  - `alembic/env.py` konfigurisan za async SQLAlchemy
  - Koristi `create_async_engine` sa asyncpg driver
  - `compare_type=True` i `compare_server_default=True` za preciznije migracije
  - Auto-import modela za autogenerate support
- **Application Lifecycle** - Database integration:
  - Ažuriran `main.py` sa database connection test na startup
  - Proper shutdown sa `close_db()` 
  - Status logging za database konekciju
- **Dependencies** - Dodat psycopg2-binary za Alembic kompatibilnost
- **Test Script** - `scripts/test_db_connection.py` za verifikaciju konekcije
- **Environment** - `backend/.env` kreiran sa development konfiguracijom

### Task Status
- [x] Task 0.5 - Database Connection & Alembic Setup (COMPLETED)

---

## [1.3.0] - 2026-01-02

### Added - Phase 0.1: Repository & Project Structure Setup

- **Folder Structure** - Kreirana osnovna struktura projekta:
  - `backend/` - FastAPI backend aplikacija
  - `frontend/` - TanStack Start frontend aplikacija
  - `docker/` - Docker konfiguracije
  - `docs/` - Dokumentacija
  - `scripts/` - Utility skripte
  - `.github/workflows/` - CI/CD pipelines
- **`.gitignore`** - Sveobuhvatan gitignore za Python i Node.js projekte
- **`README.md`** - Osnovna dokumentacija sa:
  - Tech stack overview
  - Project structure
  - Prerequisites
  - Quick start uputstva
  - Environment variables reference
- **`CONTRIBUTING.md`** - Vodič za kontribuciju sa:
  - Development setup
  - Git workflow i branch naming
  - Commit message convention (Conventional Commits)
  - Code style guidelines (Python & TypeScript)
  - Testing instructions
  - Pull request process
  - Code review guidelines
- **`.env.example`** - Template za environment varijable

### Task Status
- [x] Task 0.1 - Repository & Project Structure Setup (COMPLETED)
- [x] Task 0.2 - Backend Project Initialization (COMPLETED)
- [x] Task 0.3 - Frontend Project Initialization (COMPLETED)
- [x] Task 0.4 - Docker Development Environment (COMPLETED)

---

## [1.6.0] - 2026-01-02

### Added - Phase 0.4: Docker Development Environment

- **Docker Compose Configuration** - Kompletna development infrastruktura:
  - `docker-compose.dev.yml` sa PostgreSQL 16, Redis 7, i pgAdmin
  - Health checks za sve servise
  - Persistent volumes za data
  - Custom network za komunikaciju
  - pgAdmin kao optional tool (sa `--profile tools`)
- **PostgreSQL Setup** - Enterprise-ready database:
  - `docker/postgres/init.sql` sa svim potrebnim extensions
  - uuid-ossp (UUID generation)
  - pg_trgm (fuzzy text search)
  - unaccent (text normalization)
  - pgvector (AI embeddings)
  - Custom normalize_text() funkcija
- **Redis Configuration** - High-performance caching:
  - Redis 7 sa persistence
  - Memory management (256MB limit)
  - LRU eviction policy
  - Optional password authentication
- **Environment Variables** - Sve potrebne konfiguracije:
  - Dodate Redis varijable u `.env.example`
  - Dodate pgAdmin varijable za development tools
  - Port konfiguracije za sve servise
- **Documentation** - Kompletna setup dokumentacija:
  - Ažuriran README.md sa detaljnim Docker uputstvima
  - Service access informacije
  - Database connection detalji
  - Extensions lista i objašnjenja

### Task Status
- [x] Task 0.4 - Docker Development Environment (COMPLETED)

---

## [1.5.0] - 2026-01-02

### Added - Phase 0.3: Frontend Project Initialization

- **TanStack Start Setup** - Kompletna frontend aplikacija:
  - Inicijaliziran TanStack Start projekat sa React 19
  - Postavljen pnpm za package management
  - Kreirana kompletna `frontend/src/` struktura (routes/, components/ui/, lib/, hooks/, stores/)
- **Core Dependencies** - Frontend stack:
  - @tanstack/react-router (SSR routing)
  - @tanstack/react-query (data fetching)
  - tailwindcss v4 (styling)
  - typescript (type safety)
  - zod (validation)
- **Styling Setup** - Modern UI framework:
  - Tailwind CSS v4 sa custom configuration
  - shadcn/ui komponente (Button, Card, Input, Label)
  - CSS variables za theming (light/dark mode support)
  - Custom color palette sa shadcn/ui design system
- **Layout & Navigation** - Enterprise UI:
  - Ažuriran `__root.tsx` sa enterprise branding
  - Sticky header sa navigation (Home, Dashboard)
  - Responsive design sa shadcn/ui styling
  - TanStack Devtools integration za development

### Task Status
- [x] Task 0.3 - Frontend Project Initialization (COMPLETED)

---

## [1.4.0] - 2026-01-02

### Added - Phase 0.2: Backend Project Initialization

- **Python Project Setup** - Kompletna backend struktura:
  - `pyproject.toml` sa svim core dependencies (FastAPI, SQLAlchemy, Pydantic, etc.)
  - Poetry za dependency management sa development tools (pytest, black, ruff, mypy)
  - Virtual environment sa `backend/venv/`
- **Backend Application Structure** - FastAPI aplikacija:
  - `app/main.py` - FastAPI app instance sa CORS middleware
  - `app/config.py` - Pydantic Settings sa svim environment varijablama
  - Kompletna folder struktura (api/v1/, core/, models/, schemas/, services/, utils/)
  - Health check endpoints (`/health`, `/`)
- **Development Tools** - Code quality i testing:
  - Black formatter (line length: 88)
  - Ruff linter sa comprehensive rules
  - mypy type checker sa strict mode
  - pytest sa asyncio support
  - isort za import sorting
- **Configuration** - Comprehensive settings:
  - Database, Redis, Security (JWT)
  - CORS, S3, Watch Folders, AI/OpenRouter
  - OIDC/SSO, Monitoring, Document Processing
  - Environment-specific properties (is_development, is_production)

### Task Status
- [x] Task 0.2 - Backend Project Initialization (COMPLETED)

---

## [1.2.0] - 2026-01-02

### Added

#### Enterprise_Boilerplate_Specifikacija.md
- **Section 7.5: Labels & Organization** - Hijerarhijski sistem labela sa bojama za organizaciju dokumenata
  - Label i DocumentLabel database schema
  - API endpoints za CRUD i document-label operacije
  - LabelTree response model
- **Section 7.7: Document Processing** - Detekcija tipova fajlova, thumbnails i preview
  - Supported formats (PDF, DOCX, images, spreadsheets)
  - ThumbnailService specifikacija
  - Preview API endpoints
- **Section 7.8: AI-Powered OCR (OpenRouter VLM)** - Vision Language Model OCR
  - OpenRouterClient za async API komunikaciju
  - OCRExtractionService sa structured extraction
  - Dynamic prompts za invoice, table, form extraction
  - Supported models (Qwen-VL, Gemini Flash)
- Renumerisane sekcije: Watch Folders → 7.6, AI Integration → 7.9

#### DEVELOPMENT_PHASES.md
- **Phase 3.4: Labels & Organization** - Nova faza sa 10 taskova
  - Backend tasks (3.4.1 - 3.4.5): Model, Schemas, CRUD API, Document-Label API, Filtering
  - Frontend tasks (3.4.6 - 3.4.10): API Client, Management Page, Color Picker, Label Selector, Filter UI
- **Phase 6.6: Document Processing** - Nova faza sa 5 taskova
  - File Type Detection, Thumbnail Generation, Preview Service, API Endpoints, UI Components
- **Phase 6.7: AI-Powered OCR** - Nova faza sa 6 taskova
  - OpenRouter Integration, Structured Extraction, ARQ Worker, API Endpoints, UI Components, Settings
- Ažuriran Dependency Graph sa Phase 3.4, 6.6, 6.7
- Ažurirana Parallelization Summary tabela
- Ažurirane Team Allocation preporuke
- Ažurirane Estimated Total Duration procene (10-12 weeks za 1 engineer)
- Ažurirana Task Summary tabela (~251h total)

### Changed
- Document Version: 1.1 → 1.2

---

## [1.1.0] - 2026-01-02

### Added

#### Enterprise_Boilerplate_Specifikacija.md
- **Section 7.5: Watch Folders (Auto-Import)** - Novi modul za automatsko praćenje foldera i import fajlova
  - WatchFolder i WatchFolderFile database schema
  - API endpoints za CRUD operacije
  - FileScannerService i FileImporterService specifikacija
  - ARQ Worker tasks za background processing
  - Path security (whitelist/blacklist)
  - Environment variables konfiguracija
- Renumerisana sekcija 7.5 AI Integration → 7.6

#### DEVELOPMENT_PHASES.md
- **Task 1.9: Initial Super Admin Setup (Seeding)** - Automatsko kreiranje Super Admin korisnika pri prvom pokretanju
  - Čitanje credentials iz ENV
  - Auto-generisanje password-a ako nije definisan
  - Startup event integracija
- **Phase 3.5: Watch Folders (Auto-Import)** - Kompletna faza sa 12 taskova
  - Backend tasks (3.5.1 - 3.5.7): Model, Schemas, Scanner, Importer, Worker, API, Security
  - Frontend tasks (3.5.8 - 3.5.12): API Client, List Page, Form, Detail Page, Notifications
  - Docker configuration updates
  - Environment variables
- Renumerisani Frontend taskovi u Phase 1 (1.10 - 1.15)
- Ažuriran Dependency Graph sa Phase 3.5
- Ažurirana Parallelization Summary tabela
- Ažurirane Team Allocation preporuke (dodat Engineer 6 za DMS Features)
- Ažurirane Estimated Total Duration procene
- Dodata Task Summary tabela sa brojem taskova po fazi

### Changed
- Document Version: 1.0 → 1.1

---

## [1.0.0] - 2026-01-02

### Added
- Initial Enterprise_Boilerplate_Specifikacija.md
  - Executive Summary sa Tech Stack Overview
  - Modul 2: Autentifikacija (JWT, OIDC)
  - Modul 3: RBAC (Role-Based Access Control)
  - Modul 4: Full-Text Search (PostgreSQL FTS)
  - Modul 5: Health Monitoring & Observability
  - Modul 6: Docker Deployment
  - Modul 7: Dodatni Moduli (S3, Background Jobs, WebSocket, Multi-Tenancy, AI)
  - Modul 8: Hetzner Cloud Deployment
  - Modul 9: Frontend Architecture (TanStack Start)
  - Modul 10: Implementation Checklist
  - Appendix A: Quick Reference

- Initial DEVELOPMENT_PHASES.md
  - Phase 0: Project Setup & Infrastructure Foundation
  - Phase 1: Authentication Module
  - Phase 2: RBAC (Role-Based Access Control)
  - Phase 3: Full-Text Search
  - Phase 4: Health Monitoring & Observability
  - Phase 5: Docker Production Deployment
  - Phase 6: Additional Features (Optional)
  - Dependency Graph
  - Parallelization Summary
  - Team Allocation Recommendations
  - Estimated Total Duration

---

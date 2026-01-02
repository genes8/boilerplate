# Enterprise Application Boilerplate

**Tech Stack:** FastAPI + TanStack Start + PostgreSQL + Docker  
**Deployment:** Hetzner Cloud  
**Version:** 1.0

---

## Overview

Enterprise-grade boilerplate aplikacija koja služi kao osnova za različite tipove poslovnog softvera: CRM sisteme, Document Management Systems (DMS) sa AI funkcionalnostima, i druge enterprise SaaS aplikacije.

## Tech Stack

| Komponenta | Tehnologija |
|------------|-------------|
| Backend | FastAPI (Python 3.11+) + SQLAlchemy 2.0 + Pydantic v2 |
| Frontend | TanStack Start + React 18 + TypeScript 5.x |
| Database | PostgreSQL 16 + pgvector (za AI embeddings) |
| Cache/Queue | Redis 7.x (caching + background jobs) |
| Containerization | Docker + Docker Compose |
| Cloud Provider | Hetzner Cloud |
| Reverse Proxy | Traefik v3 (SSL/TLS, load balancing) |
| Monitoring | Prometheus + Grafana + Loki (logs) |

## Project Structure

```
/
├── backend/           # FastAPI backend application
├── frontend/          # TanStack Start frontend application
├── docker/            # Docker configuration files
├── docs/              # Documentation
├── scripts/           # Utility scripts
└── .github/workflows/ # CI/CD pipelines
```

## Prerequisites

- **Python 3.11+**
- **Node.js 20+**
- **pnpm** (for frontend package management)
- **Poetry** (for Python dependency management)
- **PostgreSQL 16**
- **Redis 7**
- **Docker & Docker Compose** (for production deployment)

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/genes8/boilerplate.git
cd boilerplate
```

### 2. Environment Setup

```bash
cp .env.example .env
# Edit .env with your configuration
```

### 3. Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip3 install poetry
poetry install

# Run database migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload --port 8000
```

### 4. Frontend Setup

```bash
cd frontend

# Install dependencies
pnpm install

# Start development server
pnpm dev
```

### 5. Infrastructure Services (Local Development)

Make sure PostgreSQL and Redis are running locally:

```bash
# PostgreSQL (default port 5432)
# Redis (default port 6379)
```

Or use Docker for infrastructure only:

```bash
docker-compose -f docker-compose.dev.yml up -d
```

## Environment Variables

See `.env.example` for all required environment variables.

Key variables:
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string
- `JWT_SECRET` - Secret key for JWT tokens (min 32 characters)
- `SUPERADMIN_EMAIL` - Initial super admin email
- `SUPERADMIN_PASSWORD` - Initial super admin password (auto-generated if empty)

## Documentation

- [Technical Specification](./Enterprise_Boilerplate_Specifikacija.md)
- [Development Phases](./DEVELOPMENT_PHASES.md)
- [Contributing Guide](./CONTRIBUTING.md)
- [Changelog](./changelog.md)

## Features

- **Authentication** - JWT-based auth with OIDC/SSO support
- **RBAC** - Role-Based Access Control with granular permissions
- **Full-Text Search** - PostgreSQL FTS with fuzzy search
- **Document Management** - File storage, labels, watch folders
- **AI Integration** - OCR, embeddings, intelligent processing
- **Health Monitoring** - Prometheus metrics, Grafana dashboards
- **Production Ready** - Docker deployment, Traefik reverse proxy

## License

Proprietary - All rights reserved.

---

**Prepared for:** Enes / Factory World Wide AI Division

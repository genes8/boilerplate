# Enterprise Application Boilerplate

## Tehnička Specifikacija i Implementacijski Vodič

**Tech Stack:** FastAPI + TanStack Start + PostgreSQL + Docker  
**Deployment:** Hetzner Cloud  
**Verzija:** 1.0 | Januar 2026  
**Pripremljeno za:** Enes / Factory World Wide AI Division

---

## 1. Executive Summary

Ovaj dokument definiše tehničku specifikaciju za enterprise-grade boilerplate aplikaciju koja može služiti kao osnova za različite tipove poslovnog softvera: CRM sisteme, Document Management Systems (DMS) sa AI funkcionalnostima, i druge enterprise SaaS aplikacije.

Boilerplate je dizajniran za production deployment sa fokusom na skalabilnost, sigurnost i maintainability. Baziran je na analizi Readur projekta i prilagođen specifičnim tehnološkim izborima i poslovnim potrebama.

### Tech Stack Overview

| Komponenta | Tehnologija |
|------------|-------------|
| Backend | FastAPI (Python 3.11+) + SQLAlchemy 2.0 + Pydantic v2 |
| Frontend | TanStack Start + React 18 + TypeScript 5.x |
| Database | PostgreSQL 16 + pgvector (za AI embeddings) |
| Cache/Queue | Redis 7.x (caching + background jobs) |
| Containerization | Docker + Docker Compose |
| Cloud Provider | Hetzner Cloud (VPS + Managed PostgreSQL opciono) |
| Reverse Proxy | Traefik v3 (SSL/TLS, load balancing) |
| Monitoring | Prometheus + Grafana + Loki (logs) |

---

## 2. Modul: Autentifikacija (Authentication)

Autentifikacija je kritična komponenta svake enterprise aplikacije. Ovaj modul implementira JWT-based autentifikaciju sa podrškom za OIDC/SSO integraciju.

### 2.1 Opis Feature-a

Sistem podržava dva tipa autentifikacije: lokalnu (username/password) i enterprise SSO putem OIDC protokola. Lokalna autentifikacija koristi bcrypt za hashing lozinki sa cost factorom 12, dok JWT tokeni imaju konfigurabilan TTL (default 24h).

### 2.2 Komponente

| Komponenta | Tehnologija | Uloga |
|------------|-------------|-------|
| Password Hashing | passlib[bcrypt] | Sigurno čuvanje lozinki (cost=12) |
| JWT Tokens | python-jose[cryptography] | Stateless autentifikacija |
| OIDC Client | authlib | SSO sa Azure AD, Okta, Keycloak |
| Session Store | Redis | Token blacklist, refresh tokens |

### 2.3 API Endpoints

```
POST   /api/v1/auth/register        - Registracija novog korisnika
POST   /api/v1/auth/login           - Login (vraća access + refresh token)
POST   /api/v1/auth/refresh         - Refresh access token
POST   /api/v1/auth/logout          - Logout (invalidira token)
GET    /api/v1/auth/me              - Trenutni korisnik info
POST   /api/v1/auth/password/reset  - Password reset request
GET    /api/v1/auth/oidc/authorize  - OIDC login redirect
GET    /api/v1/auth/oidc/callback   - OIDC callback handler
```

### 2.4 Database Schema

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255),  -- NULL za OIDC korisnike
    auth_provider VARCHAR(50) DEFAULT 'local',  -- 'local', 'oidc'
    oidc_subject VARCHAR(255),   -- OIDC sub claim
    oidc_issuer VARCHAR(500),    -- OIDC issuer URL
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    last_login_at TIMESTAMPTZ
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_oidc ON users(oidc_issuer, oidc_subject);
```

### 2.5 Implementacijske Napomene

1. JWT Secret mora biti minimum 256 bita (32+ karaktera)
2. Access token TTL: 15-60 minuta za produkciju
3. Refresh token TTL: 7-30 dana, stored u Redis sa mogućnošću revokacije
4. Rate limiting na login endpoint: max 5 pokušaja u 15 minuta po IP
5. OIDC: Koristiti PKCE flow za public clients (SPA)

---

## 3. Modul: Role-Based Access Control (RBAC)

RBAC sistem omogućava granularnu kontrolu pristupa resursima bazirano na ulogama i permisijama. Dizajniran je za fleksibilnost i skalabilnost.

### 3.1 Hijerarhija Pristupa

| Role | Permisije | Use Case |
|------|-----------|----------|
| Super Admin | * (sve) | System owner, full control |
| Admin | users:*, settings:*, reports:read | Tenant administrator |
| Manager | team:*, reports:*, documents:* | Team/department lead |
| User | documents:own, profile:own | Regular user |
| Viewer | documents:read, reports:read | Read-only access |

### 3.2 Permission Format

Permisije koriste format: `resource:action` ili `resource:action:scope`

```
users:create          - Kreiranje korisnika
users:read:own        - Čitanje samo svojih podataka
users:read:all        - Čitanje svih korisnika
documents:delete:own  - Brisanje samo svojih dokumenata
```

### 3.3 Database Schema

```sql
CREATE TABLE roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    is_system BOOLEAN DEFAULT FALSE,  -- System roles can't be deleted
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE permissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    resource VARCHAR(100) NOT NULL,
    action VARCHAR(50) NOT NULL,
    scope VARCHAR(50) DEFAULT 'all',  -- 'own', 'team', 'all'
    UNIQUE(resource, action, scope)
);

CREATE TABLE role_permissions (
    role_id UUID REFERENCES roles(id) ON DELETE CASCADE,
    permission_id UUID REFERENCES permissions(id) ON DELETE CASCADE,
    PRIMARY KEY (role_id, permission_id)
);

CREATE TABLE user_roles (
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    role_id UUID REFERENCES roles(id) ON DELETE CASCADE,
    assigned_at TIMESTAMPTZ DEFAULT NOW(),
    assigned_by UUID REFERENCES users(id),
    PRIMARY KEY (user_id, role_id)
);
```

### 3.4 FastAPI Dependency

```python
from fastapi import Depends, HTTPException, status
from typing import Callable

def require_permission(resource: str, action: str) -> Callable:
    """Dependency factory for permission checking."""
    
    async def permission_checker(
        current_user: User = Depends(get_current_user)
    ) -> User:
        if not await has_permission(current_user, resource, action):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    
    return permission_checker


# Usage example:
@router.delete("/users/{user_id}")
async def delete_user(
    user_id: UUID,
    current_user: User = Depends(require_permission("users", "delete"))
):
    """Delete a user (requires users:delete permission)."""
    ...
```

---

## 4. Modul: Full-Text Search

PostgreSQL Full-Text Search (FTS) omogućava napredne mogućnosti pretraživanja bez potrebe za eksternim search engineom poput Elasticsearch. Ovo značajno smanjuje operativnu kompleksnost.

### 4.1 Search Modovi

| Mod | PostgreSQL Funkcija | Use Case |
|-----|---------------------|----------|
| Simple | plainto_tsquery() | Osnovni keyword search |
| Phrase | phraseto_tsquery() | Exact phrase matching |
| Fuzzy | pg_trgm + similarity() | Typo tolerance, OCR errors |
| Boolean | to_tsquery() sa AND/OR/NOT | Complex queries |

### 4.2 Database Setup

```sql
-- Enable extensions
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS unaccent;

-- Documents table with FTS
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(500) NOT NULL,
    content TEXT,
    metadata JSONB DEFAULT '{}',
    owner_id UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Full-text search vector (auto-generated)
    search_vector tsvector GENERATED ALWAYS AS (
        setweight(to_tsvector('english', coalesce(title, '')), 'A') ||
        setweight(to_tsvector('english', coalesce(content, '')), 'B')
    ) STORED
);

-- GIN index for fast FTS
CREATE INDEX idx_documents_search ON documents USING GIN(search_vector);

-- Trigram index for fuzzy search
CREATE INDEX idx_documents_title_trgm ON documents USING GIN(title gin_trgm_ops);
CREATE INDEX idx_documents_content_trgm ON documents USING GIN(content gin_trgm_ops);
```

### 4.3 Search Query Examples

```sql
-- Simple search
SELECT id, title, ts_rank(search_vector, query) as rank
FROM documents, plainto_tsquery('english', 'invoice 2024') query
WHERE search_vector @@ query
ORDER BY rank DESC;

-- Phrase search (exact phrase)
SELECT * FROM documents
WHERE search_vector @@ phraseto_tsquery('english', 'quarterly report');

-- Fuzzy search (typo tolerance, similarity threshold 0.3)
SELECT *, similarity(title, 'recieve') as sim 
FROM documents
WHERE similarity(title, 'recieve') > 0.3
ORDER BY sim DESC;

-- Boolean search (AND, OR, NOT)
SELECT * FROM documents
WHERE search_vector @@ to_tsquery('english', 'budget & 2024 & !draft');

-- Combined: FTS with filters
SELECT d.*, ts_rank(d.search_vector, query) as rank
FROM documents d, plainto_tsquery('english', 'invoice') query
WHERE d.search_vector @@ query
  AND d.owner_id = :user_id
  AND d.created_at > '2024-01-01'
ORDER BY rank DESC
LIMIT 20;
```

### 4.4 FastAPI Search Endpoint

```python
from enum import Enum
from pydantic import BaseModel

class SearchMode(str, Enum):
    SIMPLE = "simple"
    PHRASE = "phrase"
    FUZZY = "fuzzy"
    BOOLEAN = "boolean"

class SearchRequest(BaseModel):
    query: str
    mode: SearchMode = SearchMode.SIMPLE
    limit: int = 20
    offset: int = 0

@router.post("/search")
async def search_documents(
    request: SearchRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Search documents with multiple modes."""
    
    if request.mode == SearchMode.SIMPLE:
        tsquery = func.plainto_tsquery('english', request.query)
    elif request.mode == SearchMode.PHRASE:
        tsquery = func.phraseto_tsquery('english', request.query)
    elif request.mode == SearchMode.BOOLEAN:
        tsquery = func.to_tsquery('english', request.query)
    # ... fuzzy handling with similarity()
    
    results = await db.execute(
        select(Document)
        .where(Document.search_vector.match(tsquery))
        .order_by(func.ts_rank(Document.search_vector, tsquery).desc())
        .limit(request.limit)
        .offset(request.offset)
    )
    
    return results.scalars().all()
```

---

## 5. Modul: Health Monitoring & Observability

Production-ready aplikacija zahteva sveobuhvatan monitoring stack za praćenje performansi, detekciju problema i alerting.

### 5.1 Monitoring Stack

| Komponenta | Alat | Funkcija |
|------------|------|----------|
| Metrics | Prometheus + prometheus-fastapi-instrumentator | Request latency, error rates, custom metrics |
| Visualization | Grafana | Dashboards, alerts visualization |
| Logs | Loki + Promtail | Centralized logging, log aggregation |
| Tracing | OpenTelemetry (optional) | Distributed tracing |
| Alerting | Alertmanager | Email, Slack, PagerDuty notifications |

### 5.2 Health Check Endpoints

```python
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import redis.asyncio as redis

router = APIRouter(tags=["health"])

@router.get("/health")
async def health_check():
    """Basic health check - app is running."""
    return {"status": "healthy"}

@router.get("/health/ready")
async def readiness_check(
    db: AsyncSession = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis)
):
    """Readiness check - all dependencies available."""
    checks = {}
    
    # Database check
    try:
        await db.execute(text("SELECT 1"))
        checks["database"] = "healthy"
    except Exception as e:
        checks["database"] = f"unhealthy: {str(e)}"
    
    # Redis check
    try:
        await redis_client.ping()
        checks["redis"] = "healthy"
    except Exception as e:
        checks["redis"] = f"unhealthy: {str(e)}"
    
    all_healthy = all(v == "healthy" for v in checks.values())
    
    return {
        "status": "ready" if all_healthy else "not_ready",
        "checks": checks
    }

@router.get("/health/live")
async def liveness_check():
    """Liveness check - app is responsive."""
    return {"status": "alive"}
```

### 5.3 Prometheus Metrics Setup

```python
from prometheus_fastapi_instrumentator import Instrumentator, metrics
from prometheus_client import Counter, Histogram

# Custom metrics
LOGIN_ATTEMPTS = Counter(
    "auth_login_attempts_total",
    "Total login attempts",
    ["status"]  # success, failure
)

DOCUMENT_PROCESSING_TIME = Histogram(
    "document_processing_seconds",
    "Time spent processing documents",
    ["document_type"]
)

# Setup instrumentator
def setup_metrics(app: FastAPI):
    Instrumentator().instrument(app).expose(app, endpoint="/metrics")
```

### 5.4 Key Metrics to Track

1. `http_requests_total` - Total HTTP requests by method, path, status
2. `http_request_duration_seconds` - Request latency histogram
3. `db_connections_active` - Active database connections
4. `background_jobs_queued` - Jobs waiting in queue
5. `background_jobs_failed` - Failed job count
6. `auth_login_attempts_total` - Login attempts (success/failure)

### 5.5 Alert Rules (Prometheus)

```yaml
groups:
  - name: app-alerts
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High 5xx error rate detected"
          description: "Error rate is {{ $value }} errors/second"

      - alert: SlowResponses
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 2
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "P95 latency above 2 seconds"

      - alert: DatabaseConnectionsHigh
        expr: db_connections_active > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Database connection pool near limit"

      - alert: BackgroundJobsBacklog
        expr: background_jobs_queued > 1000
        for: 15m
        labels:
          severity: warning
        annotations:
          summary: "Background job queue backing up"
```

---

## 6. Modul: Docker Deployment

Production-ready Docker setup sa multi-stage builds, health checks, i compose orchestration.

### 6.1 Dockerfile (Backend - FastAPI)

```dockerfile
# Build stage
FROM python:3.11-slim as builder

WORKDIR /app

# Install poetry
RUN pip install --no-cache-dir poetry

# Copy dependency files
COPY pyproject.toml poetry.lock ./

# Export requirements
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

# Production stage
FROM python:3.11-slim

WORKDIR /app

# Security: Create non-root user
RUN addgroup --system --gid 1001 appgroup && \
    adduser --system --uid 1001 --gid 1001 appuser

# Install dependencies
COPY --from=builder /app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY --chown=appuser:appgroup ./app ./app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 6.2 Dockerfile (Frontend - TanStack Start)

```dockerfile
# Build stage
FROM node:20-alpine as builder

WORKDIR /app

# Copy package files
COPY package.json pnpm-lock.yaml ./

# Install dependencies
RUN corepack enable && pnpm install --frozen-lockfile

# Copy source
COPY . .

# Build
RUN pnpm build

# Production stage
FROM node:20-alpine

WORKDIR /app

# Copy built assets
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./

# Non-root user
RUN addgroup -g 1001 -S appgroup && \
    adduser -S -u 1001 -G appgroup appuser
USER appuser

EXPOSE 3000

CMD ["node", "dist/server.js"]
```

### 6.3 Docker Compose (Production)

```yaml
version: "3.8"

services:
  # Reverse Proxy
  traefik:
    image: traefik:v3.0
    command:
      - "--api.dashboard=true"
      - "--providers.docker=true"
      - "--providers.docker.exposedbydefault=false"
      - "--entrypoints.web.address=:80"
      - "--entrypoints.websecure.address=:443"
      - "--entrypoints.web.http.redirections.entryPoint.to=websecure"
      - "--certificatesresolvers.letsencrypt.acme.tlschallenge=true"
      - "--certificatesresolvers.letsencrypt.acme.email=${ACME_EMAIL}"
      - "--certificatesresolvers.letsencrypt.acme.storage=/letsencrypt/acme.json"
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - "/var/run/docker.sock:/var/run/docker.sock:ro"
      - "letsencrypt:/letsencrypt"
    networks:
      - web
    restart: unless-stopped

  # Backend API
  api:
    build:
      context: ./backend
      dockerfile: Dockerfile
    environment:
      - DATABASE_URL=postgresql+asyncpg://${DB_USER}:${DB_PASSWORD}@db:5432/${DB_NAME}
      - REDIS_URL=redis://redis:6379/0
      - JWT_SECRET=${JWT_SECRET}
      - ENVIRONMENT=production
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.api.rule=Host(`api.${DOMAIN}`)"
      - "traefik.http.routers.api.tls.certresolver=letsencrypt"
      - "traefik.http.services.api.loadbalancer.server.port=8000"
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - web
      - internal
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: "1"
          memory: "1G"
    restart: unless-stopped

  # Frontend
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.frontend.rule=Host(`app.${DOMAIN}`)"
      - "traefik.http.routers.frontend.tls.certresolver=letsencrypt"
      - "traefik.http.services.frontend.loadbalancer.server.port=3000"
    networks:
      - web
    restart: unless-stopped

  # Database
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: ${DB_NAME}
    volumes:
      - "postgres_data:/var/lib/postgresql/data"
      - "./init.sql:/docker-entrypoint-initdb.d/init.sql:ro"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER} -d ${DB_NAME}"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - internal
    restart: unless-stopped

  # Redis
  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes --maxmemory 256mb --maxmemory-policy allkeys-lru
    volumes:
      - "redis_data:/data"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - internal
    restart: unless-stopped

  # Background Worker (optional)
  worker:
    build:
      context: ./backend
      dockerfile: Dockerfile
    command: ["arq", "app.worker.WorkerSettings"]
    environment:
      - DATABASE_URL=postgresql+asyncpg://${DB_USER}:${DB_PASSWORD}@db:5432/${DB_NAME}
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - internal
    restart: unless-stopped

networks:
  web:
    driver: bridge
  internal:
    driver: bridge

volumes:
  postgres_data:
  redis_data:
  letsencrypt:
```

### 6.4 Environment File (.env.example)

```bash
# Domain
DOMAIN=yourdomain.com
ACME_EMAIL=admin@yourdomain.com

# Database
DB_USER=appuser
DB_PASSWORD=secure_password_here
DB_NAME=appdb

# Security
JWT_SECRET=your_256_bit_secret_key_minimum_32_characters

# Optional
SENTRY_DSN=
OPENAI_API_KEY=
```

---

## 7. Dodatni Moduli (Pregled)

### 7.1 File Storage (S3-Compatible)

Za production file storage, koristiti S3-compatible storage (MinIO self-hosted ili Hetzner Object Storage).

- **Python library:** boto3 (works with any S3-compatible API)
- **Pre-signed URLs** za secure file access
- **Multipart upload** za large files
- **Hetzner Object Storage:** ~€5/TB/mesec

```python
import boto3
from botocore.config import Config

s3_client = boto3.client(
    "s3",
    endpoint_url="https://fsn1.your-objectstorage.com",
    aws_access_key_id=settings.S3_ACCESS_KEY,
    aws_secret_access_key=settings.S3_SECRET_KEY,
    config=Config(signature_version="s3v4")
)

# Generate pre-signed URL for download
url = s3_client.generate_presigned_url(
    "get_object",
    Params={"Bucket": "documents", "Key": "file.pdf"},
    ExpiresIn=3600  # 1 hour
)
```

### 7.2 Background Jobs

Za async task processing:

- **ARQ** (async Redis queue) - lightweight, async-native
- **Celery** - za kompleksnije workflow-ove
- **Task types:** email sending, PDF generation, AI processing, data sync

```python
# ARQ worker example
from arq import create_pool
from arq.connections import RedisSettings

async def process_document(ctx, document_id: str):
    """Background task for document processing."""
    # OCR, AI analysis, etc.
    pass

class WorkerSettings:
    functions = [process_document]
    redis_settings = RedisSettings.from_dsn(settings.REDIS_URL)
```

### 7.3 Real-time Notifications

WebSocket support za real-time features:

- FastAPI WebSocket endpoints
- Redis Pub/Sub za message broadcasting
- Frontend: TanStack Query + WebSocket integration

```python
from fastapi import WebSocket, WebSocketDisconnect

@router.websocket("/ws/notifications")
async def notifications_websocket(
    websocket: WebSocket,
    current_user: User = Depends(get_current_user_ws)
):
    await websocket.accept()
    
    try:
        async for message in redis_pubsub.listen():
            if message["type"] == "message":
                await websocket.send_json(message["data"])
    except WebSocketDisconnect:
        pass
```

### 7.4 Multi-Tenancy

Za SaaS aplikacije, podržati više tenanta:

- **Schema-per-tenant** (PostgreSQL schemas) - best isolation
- **Row-level security** (tenant_id column) - simpler
- **Tenant identification:** subdomain ili JWT claim

```python
# Row-level tenancy example
class TenantMixin:
    tenant_id: Mapped[UUID] = mapped_column(
        ForeignKey("tenants.id"),
        nullable=False,
        index=True
    )

class Document(Base, TenantMixin):
    __tablename__ = "documents"
    # ... other fields
```

### 7.5 Labels & Organization

Labels modul omogućava organizaciju dokumenata kroz hijerarhijski sistem labela sa bojama.

#### Database Schema

```sql
CREATE TABLE labels (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    color VARCHAR(7) NOT NULL,  -- Hex color "#FF5733"
    parent_id UUID REFERENCES labels(id) ON DELETE CASCADE,
    owner_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(owner_id, name, parent_id)
);

CREATE TABLE document_labels (
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    label_id UUID NOT NULL REFERENCES labels(id) ON DELETE CASCADE,
    assigned_at TIMESTAMPTZ DEFAULT NOW(),
    assigned_by UUID REFERENCES users(id),
    PRIMARY KEY (document_id, label_id)
);

CREATE INDEX idx_labels_owner ON labels(owner_id);
CREATE INDEX idx_labels_parent ON labels(parent_id);
CREATE INDEX idx_document_labels_label ON document_labels(label_id);
```

#### API Endpoints

```
POST   /api/v1/labels              - Create label
GET    /api/v1/labels              - List labels (tree structure)
GET    /api/v1/labels/{id}         - Get label details
PUT    /api/v1/labels/{id}         - Update label
DELETE /api/v1/labels/{id}         - Delete label

GET    /api/v1/documents/{id}/labels           - Get document labels
POST   /api/v1/documents/{id}/labels           - Add labels
DELETE /api/v1/documents/{id}/labels/{label_id} - Remove label
POST   /api/v1/documents/bulk/labels           - Bulk add labels
```

#### Label Tree Response

```python
class LabelTree(BaseModel):
    id: UUID
    name: str
    color: str
    children: list["LabelTree"] = []
    document_count: int = 0
```

### 7.6 Watch Folders (Auto-Import)

Watch Folders modul omogućava automatsko praćenje foldera na serveru i import novih fajlova u sistem. Koristi se za automatski import skeniranih dokumenata, sync sa mrežnim diskovima, i integraciju sa postojećim workflow-ima.

#### Komponente

| Komponenta | Uloga |
|------------|-------|
| WatchFolder Model | Konfiguracija praćenog foldera |
| WatchFolderFile Model | Tracking discovered/imported fajlova |
| FileScannerService | Skeniranje foldera, hash calculation |
| FileImporterService | Import fajlova u S3 + Document creation |
| ARQ Worker | Background job za periodic scanning |

#### Database Schema

```sql
CREATE TABLE watch_folders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    path VARCHAR(1000) NOT NULL,
    owner_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    is_active BOOLEAN DEFAULT TRUE,
    scan_interval INTEGER DEFAULT 60,  -- Seconds between scans
    file_pattern VARCHAR(255) DEFAULT '*.*',  -- Glob pattern
    auto_label_id UUID REFERENCES labels(id) ON DELETE SET NULL,
    delete_after_import BOOLEAN DEFAULT FALSE,
    last_scanned_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(owner_id, path)
);

CREATE TABLE watch_folder_files (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    watch_folder_id UUID NOT NULL REFERENCES watch_folders(id) ON DELETE CASCADE,
    file_path VARCHAR(1000) NOT NULL,
    file_hash VARCHAR(64) NOT NULL,  -- SHA256 za deduplication
    file_size BIGINT NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',  -- pending, imported, failed, skipped
    document_id UUID REFERENCES documents(id) ON DELETE SET NULL,
    error_message TEXT,
    discovered_at TIMESTAMPTZ DEFAULT NOW(),
    imported_at TIMESTAMPTZ,
    
    UNIQUE(watch_folder_id, file_hash)
);

CREATE INDEX idx_watch_folders_owner ON watch_folders(owner_id);
CREATE INDEX idx_watch_folders_active ON watch_folders(is_active) WHERE is_active = TRUE;
CREATE INDEX idx_watch_folder_files_status ON watch_folder_files(status);
CREATE INDEX idx_watch_folder_files_hash ON watch_folder_files(file_hash);
```

#### API Endpoints

```
GET    /api/v1/watch-folders              - Lista watch foldera
POST   /api/v1/watch-folders              - Kreiraj watch folder
GET    /api/v1/watch-folders/{id}         - Detalji + statistika
PUT    /api/v1/watch-folders/{id}         - Update settings
DELETE /api/v1/watch-folders/{id}         - Obriši watch folder
POST   /api/v1/watch-folders/{id}/scan    - Triggeruj scan manually
GET    /api/v1/watch-folders/{id}/files   - Lista discovered fajlova
POST   /api/v1/watch-folders/{id}/files/{file_id}/retry  - Retry failed import
POST   /api/v1/watch-folders/{id}/files/{file_id}/skip   - Skip file
```

#### File Scanner Service

```python
class FileScannerService:
    async def scan_folder(self, watch_folder: WatchFolder) -> list[DiscoveredFile]:
        """Skenira folder i vraća listu novih fajlova."""
        pass
    
    async def calculate_file_hash(self, file_path: str) -> str:
        """SHA256 hash za deduplication."""
        pass
    
    async def is_file_already_imported(self, file_hash: str) -> bool:
        """Proverava da li je fajl već importovan."""
        pass
    
    async def matches_pattern(self, filename: str, pattern: str) -> bool:
        """Proverava da li fajl odgovara glob patternu."""
        pass
```

#### ARQ Worker Tasks

```python
async def scan_watch_folder(ctx, watch_folder_id: UUID):
    """ARQ task - skenira jedan watch folder."""
    pass

async def import_discovered_file(ctx, watch_folder_file_id: UUID):
    """ARQ task - importuje jedan fajl."""
    pass

async def schedule_all_watch_folders(ctx):
    """ARQ cron - pokreće scan za sve aktivne foldere."""
    pass
```

#### Path Security

```python
ALLOWED_BASE_PATHS = [
    "/mnt/imports",
    "/mnt/shared",
    "/home/*/uploads"
]

FORBIDDEN_PATHS = [
    "/etc", "/root", "/var", "/usr", "/bin", "/sbin"
]

def validate_watch_path(path: str) -> bool:
    """Proverava da li je path dozvoljen."""
    pass
```

#### Environment Variables

```bash
WATCH_FOLDERS_ENABLED=true
WATCH_FOLDERS_ALLOWED_PATHS=/mnt/imports,/mnt/shared
WATCH_FOLDERS_DEFAULT_INTERVAL=60
WATCH_FOLDERS_MAX_FILE_SIZE=104857600  # 100MB
```

### 7.7 Document Processing

Modul za detekciju tipova fajlova, generisanje thumbnails i preview dokumenata.

#### Komponente

| Komponenta | Tehnologija | Uloga |
|------------|-------------|-------|
| File Detection | python-magic | MIME type detection |
| Thumbnails | pdf2image, Pillow | Generate preview images |
| Preview Service | S3 pre-signed URLs | Secure document access |

#### Supported Formats

| Kategorija | Formati |
|------------|---------|
| Documents | PDF, DOCX, DOC, TXT, RTF, ODT |
| Images | PNG, JPG, JPEG, GIF, WEBP, TIFF, BMP |
| Spreadsheets | XLSX, XLS, CSV, ODS |

#### API Endpoints

```
GET /api/v1/documents/{id}/preview    - Get preview URL
GET /api/v1/documents/{id}/thumbnail  - Get thumbnail URL
GET /api/v1/documents/{id}/pages      - Get page count
GET /api/v1/documents/{id}/pages/{n}  - Get specific page preview
```

#### Thumbnail Service

```python
class ThumbnailService:
    async def generate_pdf_thumbnail(self, file_path: str) -> bytes:
        """Generate thumbnail from first PDF page."""
        pass
    
    async def generate_image_thumbnail(self, file_path: str) -> bytes:
        """Resize image to thumbnail dimensions."""
        pass
    
    async def generate_thumbnail(
        self, 
        file_path: str, 
        mime_type: str
    ) -> bytes:
        """Auto-detect and generate appropriate thumbnail."""
        pass
```

#### Environment Variables

```bash
THUMBNAIL_WIDTH=300
THUMBNAIL_HEIGHT=400
SUPPORTED_FORMATS=pdf,docx,doc,txt,png,jpg,jpeg,gif,xlsx,xls,csv
```

### 7.8 AI-Powered OCR (OpenRouter VLM)

AI-powered OCR koristi Vision Language Models (VLM) preko OpenRouter API-ja za ekstrakciju teksta iz slika i PDF-ova.

#### Komponente

| Komponenta | Uloga |
|------------|-------|
| OpenRouterClient | Async HTTP client za OpenRouter API |
| ImageProcessing | Optimizacija slika, Base64 encoding |
| OCRExtractionService | Strukturirana ekstrakcija teksta |
| ARQ Worker | Background processing sa rate limiting |

#### Supported Models

| Model | Use Case | Cost |
|-------|----------|------|
| qwen/qwen2-vl-72b-instruct | Primary - high accuracy | Higher |
| google/gemini-flash-1.5 | Fallback - fast & cheap | Lower |

#### API Endpoints

```
POST /api/v1/documents/{id}/ocr        - Start OCR processing
GET  /api/v1/documents/{id}/ocr/status - Get OCR status
GET  /api/v1/documents/{id}/ocr/result - Get OCR result
POST /api/v1/documents/bulk/ocr        - Batch OCR
```

#### OpenRouter Client

```python
class OpenRouterClient:
    async def vision_completion(
        self,
        images: list[str],  # Base64 encoded
        prompt: str,
        model: str = "qwen/qwen2-vl-72b-instruct"
    ) -> str:
        """Send images to VLM for processing."""
        pass
    
    async def get_available_models(self) -> list[Model]:
        """List available vision models."""
        pass
```

#### OCR Extraction Service

```python
class OCRExtractionService:
    async def extract_text(self, document_id: UUID) -> str:
        """Basic text extraction."""
        pass
    
    async def extract_structured(
        self, 
        document_id: UUID,
        output_format: str = "markdown"  # markdown, json, plain
    ) -> str:
        """Structured extraction with formatting."""
        pass
    
    async def extract_table(self, document_id: UUID) -> list[dict]:
        """Extract tables as structured data."""
        pass
```

#### Dynamic Prompts

```python
PROMPTS = {
    "invoice": "Extract all invoice data including: vendor, date, items, amounts...",
    "table": "Convert this table to Markdown format with proper alignment...",
    "form": "Extract all form fields as JSON with field names and values..."
}
```

#### Environment Variables

```bash
OPENROUTER_API_KEY=sk-or-v1-xxxxx
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OCR_PRIMARY_MODEL=qwen/qwen2-vl-72b-instruct
OCR_FALLBACK_MODEL=google/gemini-flash-1.5
OCR_MAX_RETRIES=3
OCR_RATE_LIMIT_DELAY=5
```

### 7.9 AI Integration Ready (pgvector)

Priprema za AI features:

- **pgvector extension** za embedding storage
- **Semantic search** capability
- **LLM integration points** (OpenAI, Claude, local models)
- **RAG pipeline** architecture

```sql
-- Enable pgvector
CREATE EXTENSION IF NOT EXISTS vector;

-- Add embedding column
ALTER TABLE documents ADD COLUMN embedding vector(1536);

-- Create HNSW index for fast similarity search
CREATE INDEX idx_documents_embedding ON documents 
  USING hnsw (embedding vector_cosine_ops);

-- Semantic search query
SELECT id, title, 1 - (embedding <=> $1::vector) as similarity
FROM documents
WHERE 1 - (embedding <=> $1::vector) > 0.7
ORDER BY embedding <=> $1::vector
LIMIT 10;
```

---

## 8. Hetzner Cloud Deployment

### 8.1 Recommended Setup

| Komponenta | Hetzner Produkt | Spec | Cena (approx) |
|------------|-----------------|------|---------------|
| App Server | CX31 ili CX41 | 4-8 vCPU, 8-16GB RAM | €15-30/mesec |
| Database | Self-hosted PostgreSQL | Na istom serveru ili dedicated | Included / €15+ |
| Object Storage | Hetzner Object Storage | S3-compatible | €5/TB |
| Backup | Hetzner Backup | Automatic snapshots | 20% of server |
| Load Balancer | Hetzner LB (optional) | Za HA setup | €5+ |

### 8.2 Initial Setup Commands

```bash
# 1. Create server via Hetzner Cloud Console or CLI
hcloud server create --name app-prod --type cx31 --image ubuntu-22.04

# 2. SSH into server
ssh root@<server-ip>

# 3. Update system
apt update && apt upgrade -y

# 4. Install Docker
curl -fsSL https://get.docker.com | sh

# 5. Install Docker Compose
apt install docker-compose-plugin

# 6. Add your user to docker group
usermod -aG docker $USER

# 7. Setup firewall (Hetzner Cloud Firewall recommended)
ufw allow 22/tcp   # SSH
ufw allow 80/tcp   # HTTP
ufw allow 443/tcp  # HTTPS
ufw enable

# 8. Clone your repo and deploy
git clone <your-repo>
cd <your-repo>
cp .env.example .env  # Configure environment
nano .env             # Edit with your values

# 9. Start services
docker compose -f docker-compose.prod.yml up -d

# 10. Check logs
docker compose logs -f
```

### 8.3 Maintenance Commands

```bash
# Update and restart
git pull
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d

# Database backup
docker compose exec db pg_dump -U user app > backup_$(date +%Y%m%d).sql

# View logs
docker compose logs -f api
docker compose logs --tail=100 api

# Restart single service
docker compose restart api

# Scale API (if using replicas)
docker compose up -d --scale api=3
```

---

## 9. Frontend Architecture (TanStack Start)

### 9.1 Zašto TanStack Start

| Feature | Next.js | TanStack Start |
|---------|---------|----------------|
| Routing | File-based, magic | Type-safe, explicit |
| Data Fetching | Server Components, complex | TanStack Query, simple |
| Bundle Size | Larger | Smaller, optimized |
| Type Safety | Partial | Full end-to-end |
| Learning Curve | Steeper (RSC, etc.) | Moderate |

### 9.2 Key TanStack Libraries

- **TanStack Router** - Type-safe routing sa loaders
- **TanStack Query** - Server state management, caching
- **TanStack Table** - Powerful data tables
- **TanStack Form** - Form handling sa validation

### 9.3 Recommended UI Libraries

- **Shadcn/ui** - Accessible, customizable components (Radix-based)
- **Tailwind CSS** - Utility-first styling
- **Lucide Icons** - Consistent icon set
- **Zod** - Schema validation (shared with backend Pydantic)

### 9.4 Project Structure

```
frontend/
├── src/
│   ├── routes/                 # TanStack Router routes
│   │   ├── __root.tsx          # Root layout
│   │   ├── index.tsx           # Home page
│   │   ├── auth/
│   │   │   ├── login.tsx
│   │   │   └── register.tsx
│   │   ├── dashboard/
│   │   │   └── index.tsx
│   │   └── documents/
│   │       ├── index.tsx
│   │       └── $id.tsx         # Dynamic route
│   ├── components/             # Reusable components
│   │   ├── ui/                 # Shadcn components
│   │   └── features/           # Feature-specific
│   ├── lib/
│   │   ├── api.ts              # API client (fetch wrapper)
│   │   ├── auth.ts             # Auth utilities
│   │   └── utils.ts
│   ├── hooks/                  # Custom hooks
│   │   ├── useAuth.ts
│   │   └── usePermissions.ts
│   └── stores/                 # Zustand stores (if needed)
├── package.json
├── tsconfig.json
└── vite.config.ts
```

### 9.5 API Client with TanStack Query

```typescript
// lib/api.ts
const API_BASE = import.meta.env.VITE_API_URL;

export async function fetchApi<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const token = localStorage.getItem("access_token");
  
  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token && { Authorization: `Bearer ${token}` }),
      ...options?.headers,
    },
  });
  
  if (!response.ok) {
    throw new ApiError(response.status, await response.json());
  }
  
  return response.json();
}

// hooks/useDocuments.ts
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";

export function useDocuments() {
  return useQuery({
    queryKey: ["documents"],
    queryFn: () => fetchApi<Document[]>("/api/v1/documents"),
  });
}

export function useCreateDocument() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (data: CreateDocumentDto) =>
      fetchApi<Document>("/api/v1/documents", {
        method: "POST",
        body: JSON.stringify(data),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["documents"] });
    },
  });
}
```

---

## 10. Implementation Checklist

### Phase 1: Core Infrastructure
- [ ] Project scaffold (FastAPI + TanStack Start)
- [ ] Docker Compose development setup
- [ ] PostgreSQL + Redis containers
- [ ] Database migrations (Alembic)
- [ ] Environment configuration
- [ ] Basic CI/CD pipeline

### Phase 2: Authentication
- [ ] User model + migrations
- [ ] Registration endpoint
- [ ] Login + JWT generation
- [ ] Token refresh flow
- [ ] Password reset flow
- [ ] OIDC integration (Keycloak test)
- [ ] Frontend auth pages

### Phase 3: RBAC
- [ ] Roles + Permissions tables
- [ ] Permission checking dependency
- [ ] Seed default roles
- [ ] Admin user management UI
- [ ] Role assignment UI

### Phase 4: Search
- [ ] pg_trgm + FTS setup
- [ ] Search API endpoints
- [ ] Search modes implementation
- [ ] Search UI with filters
- [ ] Pagination + sorting

### Phase 5: Monitoring & Deployment
- [ ] Health endpoints
- [ ] Prometheus metrics integration
- [ ] Production Docker Compose
- [ ] Hetzner server setup
- [ ] SSL/TLS (Let's Encrypt via Traefik)
- [ ] Grafana dashboards
- [ ] Alert rules configuration

### Phase 6: Additional Features
- [ ] File upload/storage (S3)
- [ ] Background jobs (ARQ)
- [ ] Real-time notifications (WebSocket)
- [ ] Audit logging
- [ ] API documentation (auto-generated)

---

## Appendix A: Quick Reference

### A.1 Essential Commands

```bash
# Development
docker compose up -d                         # Start all services
docker compose logs -f api                   # Follow API logs
docker compose exec api alembic upgrade head # Run migrations
docker compose exec db psql -U user -d app   # DB shell

# Production
docker compose -f docker-compose.prod.yml up -d
docker compose -f docker-compose.prod.yml pull   # Update images
docker compose -f docker-compose.prod.yml logs -f

# Database
docker compose exec db pg_dump -U user app > backup.sql
docker compose exec db psql -U user -d app < backup.sql

# Debugging
docker compose exec api python -m pdb -c continue app/main.py
docker compose exec api pytest -v
```

### A.2 Useful Links

- **FastAPI Docs:** https://fastapi.tiangolo.com
- **TanStack Start:** https://tanstack.com/start
- **TanStack Query:** https://tanstack.com/query
- **Hetzner Cloud:** https://console.hetzner.cloud
- **PostgreSQL FTS:** https://www.postgresql.org/docs/current/textsearch.html
- **pgvector:** https://github.com/pgvector/pgvector
- **Shadcn/ui:** https://ui.shadcn.com
- **Traefik:** https://doc.traefik.io/traefik/

### A.3 Security Checklist

- [ ] JWT secrets are 256+ bits
- [ ] Passwords hashed with bcrypt (cost 12+)
- [ ] HTTPS enforced in production
- [ ] Rate limiting on auth endpoints
- [ ] CORS properly configured
- [ ] SQL injection prevention (parameterized queries)
- [ ] XSS prevention (content security policy)
- [ ] Secrets not in version control
- [ ] Regular dependency updates
- [ ] Database backups automated

---

*Kraj Dokumenta*

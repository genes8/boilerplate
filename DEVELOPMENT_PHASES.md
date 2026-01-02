# Enterprise Boilerplate - Development Phases & Task Breakdown

## Overview

Ovaj dokument organizuje razvoj u **6 glavnih faza** sa detaljnim TODO taskovima.
Svaki task je označen sa:
- **[SEQ]** - Mora se raditi sekvencijalno (zavisi od prethodnog)
- **[PAR]** - Može se raditi paralelno sa drugim [PAR] taskovima u istoj fazi
- **Estimated Time** - Procena vremena
- **Dependencies** - Zavisnosti od drugih taskova

---

## Phase 0: Project Setup & Infrastructure Foundation
**Duration:** 2-3 dana  
**Team Size:** 1 engineer  
**Blocking:** Sve ostale faze zavise od ove

### Tasks

#### 0.1 [SEQ] Repository & Project Structure Setup
**Estimated:** 2h  
**Dependencies:** None  
**Assignee:** _____________

- [ ] Kreirati Git repository
- [ ] Definisati `.gitignore` za Python i Node.js
- [ ] Kreirati osnovnu folder strukturu:
  ```
  /
  ├── backend/
  ├── frontend/
  ├── docker/
  ├── docs/
  ├── scripts/
  └── .github/workflows/
  ```
- [ ] Kreirati `README.md` sa osnovnim uputstvima
- [ ] Kreirati `CONTRIBUTING.md`

#### 0.2 [SEQ] Backend Project Initialization
**Estimated:** 3h  
**Dependencies:** 0.1  
**Assignee:** _____________

- [x] Inicijalizirati Python projekat sa `pyproject.toml`
- [x] Postaviti Poetry za dependency management
- [x] Kreirati `backend/app/` strukturu:
  ```
  backend/
  ├── app/
  │   ├── __init__.py
  │   ├── main.py
  │   ├── config.py
  │   ├── api/
  │   │   └── v1/
  │   ├── core/
  │   ├── models/
  │   ├── schemas/
  │   ├── services/
  │   └── utils/
  ├── tests/
  ├── alembic/
  ├── pyproject.toml
  └── poetry.lock
  ```
- [x] Instalirati core dependencies:
  - fastapi
  - uvicorn
  - sqlalchemy[asyncio]
  - asyncpg
  - pydantic
  - pydantic-settings
  - alembic
  - redis
- [x] Kreirati bazni `config.py` sa Pydantic Settings
- [x] Kreirati `main.py` sa FastAPI app instance

#### 0.3 [SEQ] Frontend Project Initialization
**Estimated:** 3h  
**Dependencies:** 0.1  
**Assignee:** _____________

- [ ] Inicijalizirati TanStack Start projekat
- [ ] Postaviti pnpm za package management
- [ ] Kreirati `frontend/src/` strukturu:
  ```
  frontend/
  ├── src/
  │   ├── routes/
  │   ├── components/
  │   │   └── ui/
  │   ├── lib/
  │   ├── hooks/
  │   └── stores/
  ├── public/
  ├── package.json
  ├── tsconfig.json
  ├── vite.config.ts
  └── tailwind.config.js
  ```
- [ ] Instalirati core dependencies:
  - @tanstack/react-router
  - @tanstack/react-query
  - tailwindcss
  - typescript
  - zod
- [ ] Postaviti Tailwind CSS
- [ ] Instalirati i konfigurisati shadcn/ui
- [ ] Kreirati bazni layout (`__root.tsx`)

#### 0.4 [PAR] Docker Development Environment
**Estimated:** 2h  
**Dependencies:** 0.2, 0.3  
**Assignee:** _____________

- [ ] Kreirati `docker-compose.dev.yml`:
  - PostgreSQL 16 container
  - Redis 7 container
  - pgAdmin (optional, za development)
- [ ] Kreirati `docker/postgres/init.sql` za inicijalne extensions:
  - pg_trgm
  - unaccent
  - pgvector
- [ ] Kreirati `.env.example` sa svim potrebnim varijablama
- [ ] Dokumentovati lokalni setup u README

#### 0.5 [PAR] Database Connection & Alembic Setup
**Estimated:** 2h  
**Dependencies:** 0.2, 0.4  
**Assignee:** _____________

- [ ] Konfigurisati SQLAlchemy async engine
- [ ] Kreirati `database.py` sa session management
- [ ] Inicijalizirati Alembic:
  - `alembic init alembic`
  - Konfigurisati `alembic.ini`
  - Konfigurisati `env.py` za async
- [ ] Kreirati `Base` model klasu
- [ ] Testirati konekciju na bazu

#### 0.6 [PAR] Redis Connection Setup
**Estimated:** 1h  
**Dependencies:** 0.2, 0.4  
**Assignee:** _____________

- [ ] Kreirati `redis.py` sa connection pool
- [ ] Implementirati dependency za Redis client
- [ ] Kreirati utility funkcije za cache operations
- [ ] Testirati konekciju na Redis

#### 0.7 [SEQ] CI/CD Pipeline - Basic
**Estimated:** 2h  
**Dependencies:** 0.2, 0.3  
**Assignee:** _____________

- [ ] Kreirati `.github/workflows/ci.yml`:
  - Lint check (ruff za Python, eslint za TS)
  - Type check (mypy, tsc)
  - Unit tests
- [ ] Kreirati `Makefile` sa common commands
- [ ] Postaviti pre-commit hooks

---

## Phase 1: Authentication Module
**Duration:** 4-5 dana  
**Team Size:** 2 engineers (1 backend, 1 frontend)  
**Dependencies:** Phase 0 complete

### Backend Tasks

#### 1.1 [SEQ] User Model & Migration
**Estimated:** 2h  
**Dependencies:** Phase 0  
**Assignee:** _____________

- [ ] Kreirati `models/user.py` sa User modelom:
  - id (UUID)
  - email (unique)
  - username (unique)
  - password_hash
  - auth_provider
  - oidc_subject, oidc_issuer
  - is_active, is_verified
  - created_at, updated_at, last_login_at
- [ ] Kreirati Alembic migraciju
- [ ] Primeniti migraciju

#### 1.2 [SEQ] Auth Schemas (Pydantic)
**Estimated:** 1h  
**Dependencies:** 1.1  
**Assignee:** _____________

- [ ] Kreirati `schemas/auth.py`:
  - UserCreate
  - UserLogin
  - UserResponse
  - TokenResponse
  - PasswordResetRequest
  - PasswordResetConfirm
- [ ] Kreirati `schemas/user.py`:
  - UserUpdate
  - UserProfile

#### 1.3 [SEQ] Password Hashing Service
**Estimated:** 1h  
**Dependencies:** 1.1  
**Assignee:** _____________

- [ ] Instalirati `passlib[bcrypt]`
- [ ] Kreirati `services/security.py`:
  - `hash_password(password: str) -> str`
  - `verify_password(plain: str, hashed: str) -> bool`
- [ ] Konfigurisati bcrypt cost factor (12)
- [ ] Napisati unit testove

#### 1.4 [SEQ] JWT Token Service
**Estimated:** 2h  
**Dependencies:** 1.1  
**Assignee:** _____________

- [ ] Instalirati `python-jose[cryptography]`
- [ ] Kreirati `services/jwt.py`:
  - `create_access_token(user_id: UUID) -> str`
  - `create_refresh_token(user_id: UUID) -> str`
  - `decode_token(token: str) -> TokenPayload`
- [ ] Implementirati token expiration
- [ ] Implementirati refresh token storage u Redis
- [ ] Napisati unit testove

#### 1.5 [SEQ] Auth Dependencies
**Estimated:** 2h  
**Dependencies:** 1.4  
**Assignee:** _____________

- [ ] Kreirati `api/deps.py`:
  - `get_current_user` dependency
  - `get_current_active_user` dependency
  - `get_optional_user` dependency
- [ ] Implementirati token extraction iz headera
- [ ] Implementirati token validation
- [ ] Handle expired/invalid tokens

#### 1.6 [SEQ] Auth API Endpoints
**Estimated:** 4h  
**Dependencies:** 1.2, 1.3, 1.4, 1.5  
**Assignee:** _____________

- [ ] Kreirati `api/v1/auth.py` router:
  - `POST /register` - User registration
  - `POST /login` - Login, return tokens
  - `POST /refresh` - Refresh access token
  - `POST /logout` - Invalidate tokens
  - `GET /me` - Current user info
- [ ] Implementirati email validation
- [ ] Implementirati username validation
- [ ] Dodati rate limiting na login endpoint
- [ ] Napisati integration testove

#### 1.7 [PAR] Password Reset Flow
**Estimated:** 3h  
**Dependencies:** 1.6  
**Assignee:** _____________

- [ ] Kreirati password reset token generation
- [ ] Implementirati `POST /password/reset` - Request reset
- [ ] Implementirati `POST /password/reset/confirm` - Confirm reset
- [ ] Kreirati email template za reset link
- [ ] (Placeholder) Email sending service

#### 1.8 [PAR] OIDC Integration
**Estimated:** 4h  
**Dependencies:** 1.6  
**Assignee:** _____________

- [ ] Instalirati `authlib`
- [ ] Kreirati `services/oidc.py`:
  - OIDC client configuration
  - Token exchange
  - User info extraction
- [ ] Implementirati `GET /oidc/authorize` - Redirect to provider
- [ ] Implementirati `GET /oidc/callback` - Handle callback
- [ ] Implementirati user creation/linking za OIDC users
- [ ] Testirati sa Keycloak/Azure AD

#### 1.9 [SEQ] Initial Super Admin Setup (Seeding)
**Estimated:** 2h  
**Dependencies:** 1.1, 1.3, 2.7 (Seed Default Roles)  
**Assignee:** _____________

- [ ] Kreirati `app/core/init_db.py`:
  ```python
  async def create_superadmin(db: AsyncSession):
      """Kreira Super Admin ako ne postoji."""
      email = settings.SUPERADMIN_EMAIL
      password = settings.SUPERADMIN_PASSWORD
      
      # Proveri da li već postoji
      existing = await db.execute(select(User).where(User.email == email))
      if existing.scalar_one_or_none():
          return
      
      # Generiši password ako nije definisan
      if not password:
          password = secrets.token_urlsafe(16)
          print("=" * 50)
          print("  SUPERADMIN CREATED")
          print("=" * 50)
          print(f"  Email: {email}")
          print(f"  Password: {password}")
          print("  ⚠️  SAVE THIS PASSWORD - IT WON'T BE SHOWN AGAIN!")
          print("=" * 50)
      
      # Kreiraj usera sa Super Admin rolom
      user = User(
          email=email,
          username="admin",
          password_hash=hash_password(password),
          is_active=True,
          is_verified=True
      )
      db.add(user)
      superadmin_role = await get_role_by_name(db, "Super Admin")
      user.roles.append(superadmin_role)
      await db.commit()
  ```
- [ ] Dodati startup event u `main.py`:
  ```python
  @app.on_event("startup")
  async def startup():
      async with async_session() as db:
          await create_superadmin(db)
  ```
- [ ] Dodati u `.env.example`:
  ```
  SUPERADMIN_EMAIL=admin@example.com
  SUPERADMIN_PASSWORD=  # Leave empty for auto-generated
  ```
- [ ] Dokumentovati u README.md

### Frontend Tasks

#### 1.10 [PAR] Auth API Client
**Estimated:** 2h  
**Dependencies:** Phase 0  
**Assignee:** _____________

- [ ] Kreirati `lib/api.ts` - Fetch wrapper sa auth headers
- [ ] Kreirati `lib/auth-api.ts`:
  - `login(email, password)`
  - `register(data)`
  - `logout()`
  - `refreshToken()`
  - `getCurrentUser()`
- [ ] Implementirati automatic token refresh
- [ ] Implementirati token storage (localStorage/httpOnly cookie)

#### 1.11 [PAR] Auth State Management
**Estimated:** 2h  
**Dependencies:** 1.10  
**Assignee:** _____________

- [ ] Kreirati `hooks/useAuth.ts`:
  - `user` state
  - `isAuthenticated` computed
  - `login()`, `logout()`, `register()` methods
- [ ] Kreirati auth context/provider
- [ ] Implementirati persistent auth state

#### 1.12 [SEQ] Login Page
**Estimated:** 3h  
**Dependencies:** 1.10, 1.11  
**Assignee:** _____________

- [ ] Kreirati `routes/auth/login.tsx`
- [ ] Implementirati login form:
  - Email input
  - Password input
  - Remember me checkbox
  - Submit button
- [ ] Implementirati form validation (Zod)
- [ ] Implementirati error handling
- [ ] Dodati "Forgot password" link
- [ ] Dodati SSO login button (optional)

#### 1.13 [PAR] Registration Page
**Estimated:** 3h  
**Dependencies:** 1.10, 1.11  
**Assignee:** _____________

- [ ] Kreirati `routes/auth/register.tsx`
- [ ] Implementirati registration form:
  - Email input
  - Username input
  - Password input
  - Confirm password input
  - Terms acceptance checkbox
- [ ] Implementirati form validation
- [ ] Implementirati password strength indicator
- [ ] Redirect to login after success

#### 1.14 [PAR] Password Reset Pages
**Estimated:** 2h  
**Dependencies:** 1.10  
**Assignee:** _____________

- [ ] Kreirati `routes/auth/forgot-password.tsx`
- [ ] Kreirati `routes/auth/reset-password.tsx`
- [ ] Implementirati request form
- [ ] Implementirati reset form sa token validation

#### 1.15 [SEQ] Protected Routes
**Estimated:** 2h  
**Dependencies:** 1.11  
**Assignee:** _____________

- [ ] Kreirati `components/ProtectedRoute.tsx`
- [ ] Implementirati redirect to login za unauthenticated users
- [ ] Implementirati loading state dok se proverava auth
- [ ] Kreirati `routes/dashboard/index.tsx` kao protected page

---

## Phase 2: RBAC (Role-Based Access Control)
**Duration:** 3-4 dana  
**Team Size:** 2 engineers  
**Dependencies:** Phase 1 complete

### Backend Tasks

#### 2.1 [SEQ] RBAC Models & Migrations
**Estimated:** 3h  
**Dependencies:** Phase 1  
**Assignee:** _____________

- [ ] Kreirati `models/role.py`:
  - Role model (id, name, description, is_system)
- [ ] Kreirati `models/permission.py`:
  - Permission model (id, resource, action, scope)
- [ ] Kreirati `models/role_permission.py`:
  - Many-to-many relationship
- [ ] Kreirati `models/user_role.py`:
  - User-Role relationship sa assigned_at, assigned_by
- [ ] Kreirati Alembic migracije
- [ ] Primeniti migracije

#### 2.2 [SEQ] RBAC Schemas
**Estimated:** 1h  
**Dependencies:** 2.1  
**Assignee:** _____________

- [ ] Kreirati `schemas/role.py`:
  - RoleCreate, RoleUpdate, RoleResponse
- [ ] Kreirati `schemas/permission.py`:
  - PermissionCreate, PermissionResponse
- [ ] Kreirati `schemas/user_role.py`:
  - UserRoleAssign, UserRoleResponse

#### 2.3 [SEQ] Permission Checking Service
**Estimated:** 3h  
**Dependencies:** 2.1  
**Assignee:** _____________

- [ ] Kreirati `services/rbac.py`:
  - `has_permission(user, resource, action) -> bool`
  - `get_user_permissions(user) -> List[Permission]`
  - `get_user_roles(user) -> List[Role]`
- [ ] Implementirati permission caching u Redis
- [ ] Implementirati wildcard permissions (`*`)
- [ ] Implementirati scope checking (own, team, all)
- [ ] Napisati unit testove

#### 2.4 [SEQ] Permission Dependencies
**Estimated:** 2h  
**Dependencies:** 2.3  
**Assignee:** _____________

- [ ] Kreirati `require_permission(resource, action)` dependency factory
- [ ] Kreirati `require_role(role_name)` dependency
- [ ] Kreirati `require_any_permission(permissions)` dependency
- [ ] Integrirati sa existing auth dependencies

#### 2.5 [SEQ] RBAC API Endpoints
**Estimated:** 4h  
**Dependencies:** 2.2, 2.4  
**Assignee:** _____________

- [ ] Kreirati `api/v1/roles.py`:
  - `GET /roles` - List all roles
  - `POST /roles` - Create role (admin only)
  - `GET /roles/{id}` - Get role details
  - `PUT /roles/{id}` - Update role
  - `DELETE /roles/{id}` - Delete role (non-system only)
- [ ] Kreirati `api/v1/permissions.py`:
  - `GET /permissions` - List all permissions
- [ ] Napisati integration testove

#### 2.6 [SEQ] User Role Management API
**Estimated:** 2h  
**Dependencies:** 2.5  
**Assignee:** _____________

- [ ] Dodati u `api/v1/users.py`:
  - `GET /users/{id}/roles` - Get user roles
  - `POST /users/{id}/roles` - Assign role
  - `DELETE /users/{id}/roles/{role_id}` - Remove role
- [ ] Implementirati audit logging za role changes

#### 2.7 [SEQ] Seed Default Roles & Permissions
**Estimated:** 2h  
**Dependencies:** 2.1  
**Assignee:** _____________

- [ ] Kreirati `scripts/seed_rbac.py`
- [ ] Definisati default roles:
  - Super Admin
  - Admin
  - Manager
  - User
  - Viewer
- [ ] Definisati default permissions za svaki resource
- [ ] Kreirati Alembic data migration za seeding

### Frontend Tasks

#### 2.8 [PAR] Permission Hook
**Estimated:** 2h  
**Dependencies:** Phase 1 Frontend  
**Assignee:** _____________

- [ ] Kreirati `hooks/usePermissions.ts`:
  - `hasPermission(resource, action) -> boolean`
  - `hasRole(roleName) -> boolean`
  - `permissions` - lista svih permissions
- [ ] Fetch permissions on auth
- [ ] Cache permissions

#### 2.9 [PAR] Permission Components
**Estimated:** 2h  
**Dependencies:** 2.8  
**Assignee:** _____________

- [ ] Kreirati `components/CanAccess.tsx`:
  ```tsx
  <CanAccess permission="users:create">
    <CreateUserButton />
  </CanAccess>
  ```
- [ ] Kreirati `components/RequireRole.tsx`
- [ ] Implementirati fallback rendering

#### 2.10 [SEQ] Admin - Role Management UI
**Estimated:** 4h  
**Dependencies:** 2.5, 2.8, 2.9  
**Assignee:** _____________

- [ ] Kreirati `routes/admin/roles/index.tsx` - Role list
- [ ] Kreirati `routes/admin/roles/[id].tsx` - Role details/edit
- [ ] Implementirati role creation form
- [ ] Implementirati permission assignment UI
- [ ] Implementirati role deletion (sa confirmation)

#### 2.11 [SEQ] Admin - User Role Assignment UI
**Estimated:** 3h  
**Dependencies:** 2.6, 2.10  
**Assignee:** _____________

- [ ] Kreirati user management page
- [ ] Implementirati role assignment dropdown/modal
- [ ] Prikazati current roles za svakog usera
- [ ] Implementirati bulk role assignment

---

## Phase 3: Full-Text Search
**Duration:** 3-4 dana  
**Team Size:** 2 engineers  
**Dependencies:** Phase 0 complete (može paralelno sa Phase 1 & 2)

### Backend Tasks

#### 3.1 [SEQ] Document Model & Migration
**Estimated:** 2h  
**Dependencies:** Phase 0  
**Assignee:** _____________

- [ ] Kreirati `models/document.py`:
  - id (UUID)
  - title
  - content
  - metadata (JSONB)
  - owner_id (FK to users)
  - search_vector (tsvector, generated)
  - created_at, updated_at
- [ ] Kreirati Alembic migraciju sa:
  - GIN index za search_vector
  - Trigram indexes za fuzzy search
- [ ] Primeniti migraciju

#### 3.2 [SEQ] Document Schemas
**Estimated:** 1h  
**Dependencies:** 3.1  
**Assignee:** _____________

- [ ] Kreirati `schemas/document.py`:
  - DocumentCreate
  - DocumentUpdate
  - DocumentResponse
  - DocumentList (sa pagination)
- [ ] Kreirati `schemas/search.py`:
  - SearchRequest (query, mode, filters)
  - SearchResponse (results, total, highlights)

#### 3.3 [SEQ] Document CRUD Service
**Estimated:** 2h  
**Dependencies:** 3.1, 3.2  
**Assignee:** _____________

- [ ] Kreirati `services/document.py`:
  - `create_document()`
  - `get_document()`
  - `update_document()`
  - `delete_document()`
  - `list_documents()` sa pagination
- [ ] Implementirati ownership checking
- [ ] Napisati unit testove

#### 3.4 [SEQ] Search Service
**Estimated:** 4h  
**Dependencies:** 3.1  
**Assignee:** _____________

- [ ] Kreirati `services/search.py`:
  - `search_simple(query)` - plainto_tsquery
  - `search_phrase(query)` - phraseto_tsquery
  - `search_fuzzy(query)` - pg_trgm similarity
  - `search_boolean(query)` - to_tsquery
- [ ] Implementirati ranking sa ts_rank
- [ ] Implementirati highlighting sa ts_headline
- [ ] Implementirati filtering (owner, date range, metadata)
- [ ] Implementirati pagination
- [ ] Napisati unit testove

#### 3.5 [SEQ] Document API Endpoints
**Estimated:** 3h  
**Dependencies:** 3.3, 3.4  
**Assignee:** _____________

- [ ] Kreirati `api/v1/documents.py`:
  - `GET /documents` - List documents
  - `POST /documents` - Create document
  - `GET /documents/{id}` - Get document
  - `PUT /documents/{id}` - Update document
  - `DELETE /documents/{id}` - Delete document
- [ ] Primeniti RBAC permissions
- [ ] Napisati integration testove

#### 3.6 [SEQ] Search API Endpoint
**Estimated:** 2h  
**Dependencies:** 3.4, 3.5  
**Assignee:** _____________

- [ ] Kreirati `api/v1/search.py`:
  - `POST /search` - Search documents
  - `GET /search/suggestions` - Autocomplete (optional)
- [ ] Implementirati search mode selection
- [ ] Implementirati filter parameters
- [ ] Napisati integration testove

### Frontend Tasks

#### 3.7 [PAR] Document API Client
**Estimated:** 2h  
**Dependencies:** Phase 0 Frontend  
**Assignee:** _____________

- [ ] Kreirati `lib/document-api.ts`:
  - `getDocuments(params)`
  - `getDocument(id)`
  - `createDocument(data)`
  - `updateDocument(id, data)`
  - `deleteDocument(id)`
  - `searchDocuments(query, options)`
- [ ] Kreirati TanStack Query hooks:
  - `useDocuments()`
  - `useDocument(id)`
  - `useCreateDocument()`
  - `useSearch()`

#### 3.8 [SEQ] Document List Page
**Estimated:** 3h  
**Dependencies:** 3.7  
**Assignee:** _____________

- [ ] Kreirati `routes/documents/index.tsx`
- [ ] Implementirati document table/grid view
- [ ] Implementirati pagination
- [ ] Implementirati sorting
- [ ] Dodati create document button
- [ ] Dodati delete action

#### 3.9 [PAR] Document Detail/Edit Page
**Estimated:** 3h  
**Dependencies:** 3.7  
**Assignee:** _____________

- [ ] Kreirati `routes/documents/[id].tsx`
- [ ] Implementirati document view
- [ ] Implementirati edit mode
- [ ] Implementirati metadata display/edit
- [ ] Dodati delete confirmation

#### 3.10 [SEQ] Search UI
**Estimated:** 4h  
**Dependencies:** 3.7, 3.8  
**Assignee:** _____________

- [ ] Kreirati `components/SearchBar.tsx`:
  - Search input
  - Search mode selector (simple, phrase, fuzzy, boolean)
  - Search button
- [ ] Kreirati `routes/search.tsx` - Search results page
- [ ] Implementirati search results display
- [ ] Implementirati result highlighting
- [ ] Implementirati filters sidebar:
  - Date range
  - Owner
  - Custom metadata filters
- [ ] Implementirati "no results" state

---

## Phase 3.4: Labels & Organization
**Duration:** 2-3 dana  
**Team Size:** 1-2 engineers  
**Dependencies:** Phase 0, Phase 3 (Documents)

### Opis

Labels modul omogućava organizaciju dokumenata kroz hijerarhijski sistem labela sa bojama. Podržava parent-child relacije za kreiranje kategorija i podkategorija.

### Backend Tasks

#### 3.4.1 [SEQ] Label Model & Migration
**Estimated:** 2h  
**Dependencies:** Phase 3.1  
**Assignee:** _____________

- [ ] Kreirati `models/label.py`:
  ```python
  class Label(Base):
      id: UUID
      name: str                    # "Invoice", "Contract", "HR"
      color: str                   # Hex color "#FF5733"
      parent_id: UUID | None       # FK to labels (self-referential)
      owner_id: UUID               # FK to users
      created_at: datetime
      updated_at: datetime
  ```
- [ ] Kreirati `models/document_label.py` (junction table):
  ```python
  class DocumentLabel(Base):
      document_id: UUID            # FK to documents
      label_id: UUID               # FK to labels
      assigned_at: datetime
      assigned_by: UUID            # FK to users
  ```
- [ ] Kreirati Alembic migraciju
- [ ] Dodati indexe za parent_id i owner_id

#### 3.4.2 [SEQ] Label Schemas
**Estimated:** 1h  
**Dependencies:** 3.4.1  
**Assignee:** _____________

- [ ] Kreirati `schemas/label.py`:
  - LabelCreate (name, color, parent_id)
  - LabelUpdate (name, color, parent_id)
  - LabelResponse (id, name, color, parent_id, children)
  - LabelTree (recursive structure za hijerarhiju)

#### 3.4.3 [SEQ] Label CRUD API
**Estimated:** 3h  
**Dependencies:** 3.4.2  
**Assignee:** _____________

- [ ] Kreirati `api/v1/labels.py`:
  - `POST /labels` - Create label
  - `GET /labels` - List labels (tree structure)
  - `GET /labels/{id}` - Get label details
  - `PUT /labels/{id}` - Update label
  - `DELETE /labels/{id}` - Delete label (cascade to children optional)
- [ ] Implementirati tree structure response
- [ ] Implementirati color validation (hex format)
- [ ] Napisati integration testove

#### 3.4.4 [SEQ] Document-Label Operations API
**Estimated:** 2h  
**Dependencies:** 3.4.3  
**Assignee:** _____________

- [ ] Dodati u `api/v1/documents.py`:
  - `GET /documents/{id}/labels` - Get document labels
  - `POST /documents/{id}/labels` - Add labels to document
  - `DELETE /documents/{id}/labels/{label_id}` - Remove label
  - `POST /documents/bulk/labels` - Bulk add labels to multiple documents
  - `DELETE /documents/bulk/labels` - Bulk remove labels
- [ ] Implementirati bulk operations
- [ ] Napisati integration testove

#### 3.4.5 [PAR] Label-based Filtering
**Estimated:** 2h  
**Dependencies:** 3.4.4  
**Assignee:** _____________

- [ ] Dodati label filter u document list endpoint
- [ ] Implementirati filter po multiple labels (AND/OR logic)
- [ ] Dodati label filter u search endpoint
- [ ] Optimizovati query performance

### Frontend Tasks

#### 3.4.6 [PAR] Label API Client
**Estimated:** 1h  
**Dependencies:** 3.4.3  
**Assignee:** _____________

- [ ] Kreirati `lib/labels-api.ts`:
  - `list()`, `create()`, `update()`, `delete()`
  - `addToDocument()`, `removeFromDocument()`
  - `bulkAdd()`, `bulkRemove()`
- [ ] Kreirati TanStack Query hooks

#### 3.4.7 [PAR] Label Management Page
**Estimated:** 3h  
**Dependencies:** 3.4.6  
**Assignee:** _____________

- [ ] Kreirati `routes/labels/index.tsx`
- [ ] Implementirati tree view za hierarchical labels
- [ ] Implementirati drag & drop za reordering (optional)
- [ ] Add/Edit/Delete actions

#### 3.4.8 [PAR] Color Picker Component
**Estimated:** 1h  
**Dependencies:** 3.4.6  
**Assignee:** _____________

- [ ] Kreirati `components/ColorPicker.tsx`
- [ ] Predefined color palette
- [ ] Custom hex input
- [ ] Preview

#### 3.4.9 [PAR] Label Selector Component
**Estimated:** 2h  
**Dependencies:** 3.4.6  
**Assignee:** _____________

- [ ] Kreirati `components/LabelSelector.tsx`
- [ ] Multi-select dropdown sa search
- [ ] Label chips sa bojama
- [ ] Create new label inline

#### 3.4.10 [SEQ] Label Filter in Document List
**Estimated:** 2h  
**Dependencies:** 3.4.9  
**Assignee:** _____________

- [ ] Dodati label filter u document list sidebar
- [ ] Implementirati AND/OR toggle
- [ ] Prikazati active filters kao chips
- [ ] Clear all filters button

---

## Phase 3.5: Watch Folders (Auto-Import)
**Duration:** 3-4 dana  
**Team Size:** 1 backend engineer  
**Dependencies:** Phase 0, Phase 1 (Auth), Phase 3.4 (Labels), Phase 6.1 (S3 Storage), Phase 6.2 (ARQ Background Jobs)

### Opis

Watch Folders omogućava automatsko praćenje foldera na serveru i import novih fajlova u sistem. Koristi se za:
- Automatski import skeniranih dokumenata
- Sync sa mrežnim diskovima
- Integraciju sa postojećim workflow-ima

### Backend Tasks

#### 3.5.1 [SEQ] WatchFolder Model & Migration
**Estimated:** 2h  
**Dependencies:** Phase 0  
**Assignee:** _____________

- [ ] Kreirati `models/watch_folder.py`:
  ```python
  class WatchFolder(Base):
      id: UUID
      name: str                    # "Scanner Import", "Shared Drive"
      path: str                    # "/mnt/scanner/invoices"
      owner_id: UUID               # FK to users
      is_active: bool              # Enable/disable watching
      scan_interval: int           # Seconds between scans (default: 60)
      file_pattern: str            # Glob pattern: "*.pdf", "*.{pdf,png,jpg}"
      auto_label_id: UUID | None   # Auto-apply label to imports
      delete_after_import: bool    # Move to trash after import (default: False)
      last_scanned_at: datetime
      created_at: datetime
      updated_at: datetime
  ```
- [ ] Kreirati `models/watch_folder_file.py`:
  ```python
  class WatchFolderFile(Base):
      id: UUID
      watch_folder_id: UUID        # FK to watch_folders
      file_path: str               # Original path
      file_hash: str               # SHA256 hash (za deduplication)
      file_size: int               # Bytes
      status: str                  # 'pending', 'imported', 'failed', 'skipped'
      document_id: UUID | None     # FK to documents (after import)
      error_message: str | None    # If failed
      discovered_at: datetime
      imported_at: datetime | None
  ```
- [ ] Kreirati Alembic migraciju
- [ ] Dodati indexe:
  - `idx_watch_folder_files_hash` (za brzu deduplication proveru)
  - `idx_watch_folder_files_status`

#### 3.5.2 [SEQ] WatchFolder Schemas
**Estimated:** 1h  
**Dependencies:** 3.5.1  
**Assignee:** _____________

- [ ] Kreirati `schemas/watch_folder.py`:
  - WatchFolderCreate (name, path, scan_interval, file_pattern, auto_label_id, delete_after_import)
  - WatchFolderUpdate (name, is_active, scan_interval, file_pattern, auto_label_id)
  - WatchFolderResponse (id, name, path, is_active, stats)
  - WatchFolderStats (total_files, pending, imported, failed)
  - WatchFolderFileResponse

#### 3.5.3 [SEQ] File Scanner Service
**Estimated:** 3h  
**Dependencies:** 3.5.1  
**Assignee:** _____________

- [ ] Kreirati `services/file_scanner.py`:
  - `scan_folder(watch_folder) -> list[DiscoveredFile]`
  - `calculate_file_hash(file_path) -> str` (SHA256, streaming za large files)
  - `is_file_already_imported(file_hash) -> bool`
  - `matches_pattern(filename, pattern) -> bool` (fnmatch)
- [ ] Implementirati glob pattern matching
- [ ] Implementirati recursive scanning (optional)
- [ ] Napisati unit testove

#### 3.5.4 [SEQ] File Import Service
**Estimated:** 3h  
**Dependencies:** 3.5.3, Phase 6.1 (S3 Storage)  
**Assignee:** _____________

- [ ] Kreirati `services/file_importer.py`:
  - `import_file(watch_folder, file_path) -> Document`
  - `handle_post_import(watch_folder, file_path)` (delete/move)
- [ ] Implementirati file reading (streaming za large files)
- [ ] Implementirati S3 upload
- [ ] Implementirati Document creation
- [ ] Implementirati auto-labeling
- [ ] Error handling sa retry logic

#### 3.5.5 [SEQ] Watch Folder Worker (Background Job)
**Estimated:** 3h  
**Dependencies:** 3.5.3, 3.5.4, Phase 6.2 (ARQ Setup)  
**Assignee:** _____________

- [ ] Kreirati `tasks/watch_folder.py`:
  - `scan_watch_folder(ctx, watch_folder_id)` - ARQ task
  - `import_discovered_file(ctx, watch_folder_file_id)` - ARQ task
  - `schedule_all_watch_folders(ctx)` - ARQ cron job
- [ ] Konfigurisati ARQ cron job (svake minute)
- [ ] Implementirati concurrency control (max 5 importa istovremeno)
- [ ] Implementirati retry logic za failed imports

#### 3.5.6 [SEQ] WatchFolder API Endpoints
**Estimated:** 3h  
**Dependencies:** 3.5.2, 3.5.3, 3.5.4  
**Assignee:** _____________

- [ ] Kreirati `api/v1/watch_folders.py`:
  - `GET /watch-folders` - Lista svih watch foldera (user's own)
  - `POST /watch-folders` - Kreiraj novi watch folder
  - `GET /watch-folders/{id}` - Detalji + statistika
  - `PUT /watch-folders/{id}` - Update settings
  - `DELETE /watch-folders/{id}` - Obriši watch folder
  - `POST /watch-folders/{id}/scan` - Triggeruj scan manually
  - `GET /watch-folders/{id}/files` - Lista discovered fajlova
  - `POST /watch-folders/{id}/files/{file_id}/retry` - Retry failed import
  - `POST /watch-folders/{id}/files/{file_id}/skip` - Skip file
- [ ] Path validation (security)
- [ ] Napisati integration testove

#### 3.5.7 [SEQ] Path Validation & Security
**Estimated:** 2h  
**Dependencies:** 3.5.6  
**Assignee:** _____________

- [ ] Kreirati `services/path_validator.py`:
  - `validate_watch_path(path) -> bool`
  - `sanitize_path(path) -> str`
- [ ] Implementirati whitelist pristup (ALLOWED_BASE_PATHS)
- [ ] Implementirati blacklist proveru (FORBIDDEN_PATHS)
- [ ] Implementirati symlink resolution
- [ ] Konfigurisati allowed paths u settings

### Frontend Tasks

#### 3.5.8 [PAR] WatchFolder API Client
**Estimated:** 1h  
**Dependencies:** 3.5.6  
**Assignee:** _____________

- [ ] Kreirati `lib/watch-folders-api.ts`:
  - `list()`, `create()`, `get()`, `update()`, `delete()`
  - `triggerScan()`, `getFiles()`, `retryFile()`, `skipFile()`
- [ ] Kreirati TanStack Query hooks

#### 3.5.9 [PAR] WatchFolder List Page
**Estimated:** 3h  
**Dependencies:** 3.5.8  
**Assignee:** _____________

- [ ] Kreirati `routes/watch-folders/index.tsx`
- [ ] Prikazati listu sa: Name, Path, Status toggle, Last scanned, Stats badges
- [ ] "Add Watch Folder" button
- [ ] Actions: Edit, Delete, Trigger Scan

#### 3.5.10 [PAR] WatchFolder Create/Edit Form
**Estimated:** 2h  
**Dependencies:** 3.5.8  
**Assignee:** _____________

- [ ] Kreirati `components/WatchFolderForm.tsx`:
  - Name input
  - Path input (sa validation feedback)
  - Scan interval slider (30s - 5min)
  - File pattern input
  - Auto-label dropdown
  - Delete after import toggle
- [ ] Validation sa Zod

#### 3.5.11 [PAR] WatchFolder Detail Page
**Estimated:** 3h  
**Dependencies:** 3.5.8  
**Assignee:** _____________

- [ ] Kreirati `routes/watch-folders/$id.tsx`
- [ ] Prikazati: Watch folder info, Statistics cards, File list table
- [ ] Filter by status tabs
- [ ] "Scan Now" button
- [ ] Actions (Retry, Skip) za failed/pending files

#### 3.5.12 [PAR] Status Indicators & Notifications
**Estimated:** 2h  
**Dependencies:** 3.5.11  
**Assignee:** _____________

- [ ] Kreirati status badge component
- [ ] Toast notifications za scan/import events
- [ ] Dashboard widget (optional)

### Docker Configuration

Dodati u `docker-compose.dev.yml`:
```yaml
services:
  api:
    volumes:
      - ./watch-folders:/mnt/imports:ro
```

Dodati u `docker-compose.prod.yml`:
```yaml
services:
  api:
    volumes:
      - /mnt/imports:/mnt/imports:ro
      - /mnt/shared:/mnt/shared:ro
```

### Environment Variables

```bash
WATCH_FOLDERS_ENABLED=true
WATCH_FOLDERS_ALLOWED_PATHS=/mnt/imports,/mnt/shared
WATCH_FOLDERS_DEFAULT_INTERVAL=60
WATCH_FOLDERS_MAX_FILE_SIZE=104857600  # 100MB
```

---

## Phase 4: Health Monitoring & Observability
**Duration:** 2-3 dana  
**Team Size:** 1-2 engineers  
**Dependencies:** Phase 0 complete (može paralelno sa ostalim fazama)

### Tasks

#### 4.1 [SEQ] Health Check Endpoints
**Estimated:** 2h  
**Dependencies:** Phase 0  
**Assignee:** _____________

- [ ] Kreirati `api/v1/health.py`:
  - `GET /health` - Basic health (app running)
  - `GET /health/ready` - Readiness (DB, Redis connected)
  - `GET /health/live` - Liveness (app responsive)
- [ ] Implementirati dependency checks:
  - Database connection
  - Redis connection
  - (Optional) External services
- [ ] Napisati testove

#### 4.2 [SEQ] Prometheus Metrics Integration
**Estimated:** 3h  
**Dependencies:** 4.1  
**Assignee:** _____________

- [ ] Instalirati `prometheus-fastapi-instrumentator`
- [ ] Konfigurisati instrumentator u `main.py`
- [ ] Expose `/metrics` endpoint
- [ ] Kreirati custom metrics:
  - `auth_login_attempts_total`
  - `document_operations_total`
  - `search_queries_total`
  - `background_jobs_queued`
- [ ] Dokumentovati dostupne metrike

#### 4.3 [PAR] Structured Logging
**Estimated:** 2h  
**Dependencies:** Phase 0  
**Assignee:** _____________

- [ ] Konfigurisati structured JSON logging
- [ ] Kreirati logging middleware za request/response
- [ ] Dodati correlation ID za request tracing
- [ ] Konfigurisati log levels per environment
- [ ] Kreirati `utils/logging.py` helpers

#### 4.4 [PAR] Docker Monitoring Stack
**Estimated:** 3h  
**Dependencies:** 4.2  
**Assignee:** _____________

- [ ] Kreirati `docker/monitoring/docker-compose.yml`:
  - Prometheus container
  - Grafana container
  - Loki container (logs)
  - Promtail container (log collector)
- [ ] Kreirati `docker/monitoring/prometheus.yml` config
- [ ] Kreirati `docker/monitoring/promtail.yml` config
- [ ] Dokumentovati setup

#### 4.5 [SEQ] Grafana Dashboards
**Estimated:** 3h  
**Dependencies:** 4.4  
**Assignee:** _____________

- [ ] Kreirati Application Overview dashboard:
  - Request rate
  - Error rate
  - Latency percentiles
  - Active users
- [ ] Kreirati Database dashboard:
  - Connection pool status
  - Query latency
  - Slow queries
- [ ] Kreirati Business Metrics dashboard:
  - Logins per day
  - Documents created
  - Search queries
- [ ] Export dashboards kao JSON

#### 4.6 [SEQ] Alert Rules
**Estimated:** 2h  
**Dependencies:** 4.4  
**Assignee:** _____________

- [ ] Kreirati `docker/monitoring/alerts.yml`:
  - HighErrorRate (5xx > 10%)
  - SlowResponses (P95 > 2s)
  - DatabaseConnectionsHigh (> 80%)
  - BackgroundJobsBacklog (> 1000)
  - ServiceDown (health check failing)
- [ ] Konfigurisati Alertmanager (optional)
- [ ] Dokumentovati alert responses

---

## Phase 5: Docker Production Deployment
**Duration:** 3-4 dana  
**Team Size:** 1-2 engineers (DevOps focus)  
**Dependencies:** Phase 0, 1, 2, 3 complete

### Tasks

#### 5.1 [SEQ] Backend Production Dockerfile
**Estimated:** 2h  
**Dependencies:** Phase 1 Backend  
**Assignee:** _____________

- [ ] Kreirati `backend/Dockerfile`:
  - Multi-stage build
  - Non-root user
  - Health check
  - Optimized layer caching
- [ ] Testirati build locally
- [ ] Optimizovati image size
- [ ] Dokumentovati build arguments

#### 5.2 [PAR] Frontend Production Dockerfile
**Estimated:** 2h  
**Dependencies:** Phase 1 Frontend  
**Assignee:** _____________

- [ ] Kreirati `frontend/Dockerfile`:
  - Multi-stage build (build + runtime)
  - Non-root user
  - Optimized for SSR
- [ ] Testirati build locally
- [ ] Optimizovati image size

#### 5.3 [SEQ] Production Docker Compose
**Estimated:** 4h  
**Dependencies:** 5.1, 5.2  
**Assignee:** _____________

- [ ] Kreirati `docker-compose.prod.yml`:
  - Traefik reverse proxy
  - API service (sa replicas)
  - Frontend service
  - PostgreSQL
  - Redis
  - Worker service
- [ ] Konfigurisati Traefik:
  - SSL/TLS sa Let's Encrypt
  - HTTP to HTTPS redirect
  - Load balancing
- [ ] Konfigurisati networks (web, internal)
- [ ] Konfigurisati volumes
- [ ] Konfigurisati resource limits
- [ ] Kreirati `.env.prod.example`

#### 5.4 [SEQ] Database Init Script
**Estimated:** 1h  
**Dependencies:** 5.3  
**Assignee:** _____________

- [ ] Kreirati `docker/postgres/init.sql`:
  - Create extensions (pg_trgm, unaccent, pgvector)
  - Create application user
  - Set permissions
- [ ] Testirati sa fresh database

#### 5.5 [SEQ] Hetzner Server Setup Guide
**Estimated:** 3h  
**Dependencies:** 5.3  
**Assignee:** _____________

- [ ] Dokumentovati server provisioning:
  - Server type selection
  - OS installation
  - Initial security setup
- [ ] Kreirati `scripts/server-setup.sh`:
  - System updates
  - Docker installation
  - Firewall configuration
  - User setup
- [ ] Dokumentovati DNS setup
- [ ] Dokumentovati backup strategy

#### 5.6 [SEQ] Deployment Scripts
**Estimated:** 2h  
**Dependencies:** 5.3, 5.5  
**Assignee:** _____________

- [ ] Kreirati `scripts/deploy.sh`:
  - Pull latest code
  - Build images
  - Run migrations
  - Restart services
  - Health check verification
- [ ] Kreirati `scripts/rollback.sh`
- [ ] Kreirati `scripts/backup-db.sh`
- [ ] Dokumentovati deployment process

#### 5.7 [PAR] CI/CD Production Pipeline
**Estimated:** 3h  
**Dependencies:** 5.1, 5.2  
**Assignee:** _____________

- [ ] Kreirati `.github/workflows/deploy.yml`:
  - Build Docker images
  - Push to registry
  - Deploy to server (SSH)
  - Run migrations
  - Health check
- [ ] Konfigurisati GitHub secrets
- [ ] Implementirati staging environment (optional)
- [ ] Dokumentovati pipeline

---

## Phase 6: Additional Features (Optional/Future)
**Duration:** Variable  
**Team Size:** Variable  
**Dependencies:** Core phases complete

### 6.1 File Storage (S3-Compatible)

#### 6.1.1 [SEQ] S3 Service Setup
**Estimated:** 3h  
**Assignee:** _____________

- [ ] Instalirati `boto3`
- [ ] Kreirati `services/storage.py`:
  - `upload_file()`
  - `download_file()`
  - `generate_presigned_url()`
  - `delete_file()`
- [ ] Konfigurisati za Hetzner Object Storage
- [ ] Napisati testove

#### 6.1.2 [SEQ] File Upload API
**Estimated:** 2h  
**Assignee:** _____________

- [ ] Kreirati `api/v1/files.py`:
  - `POST /files/upload`
  - `GET /files/{id}/download`
  - `DELETE /files/{id}`
- [ ] Implementirati multipart upload za large files
- [ ] Implementirati file type validation

#### 6.1.3 [PAR] File Upload UI
**Estimated:** 3h  
**Assignee:** _____________

- [ ] Kreirati `components/FileUpload.tsx`
- [ ] Implementirati drag & drop
- [ ] Implementirati progress indicator
- [ ] Implementirati file preview

### 6.2 Background Jobs (ARQ)

#### 6.2.1 [SEQ] ARQ Worker Setup
**Estimated:** 2h  
**Assignee:** _____________

- [ ] Instalirati `arq`
- [ ] Kreirati `app/worker.py`:
  - WorkerSettings
  - Redis connection
- [ ] Kreirati `app/tasks/` folder

#### 6.2.2 [SEQ] Email Sending Task
**Estimated:** 2h  
**Assignee:** _____________

- [ ] Kreirati `tasks/email.py`
- [ ] Implementirati email templates
- [ ] Integrirati sa password reset flow

#### 6.2.3 [PAR] Document Processing Task
**Estimated:** 3h  
**Assignee:** _____________

- [ ] Kreirati `tasks/document.py`
- [ ] Implementirati async document processing
- [ ] Implementirati retry logic

### 6.3 Real-time Notifications

#### 6.3.1 [SEQ] WebSocket Setup
**Estimated:** 3h  
**Assignee:** _____________

- [ ] Kreirati `api/v1/ws.py`:
  - WebSocket endpoint
  - Connection management
- [ ] Implementirati Redis Pub/Sub za broadcasting
- [ ] Implementirati authentication za WebSocket

#### 6.3.2 [PAR] Notification Frontend
**Estimated:** 3h  
**Assignee:** _____________

- [ ] Kreirati `hooks/useNotifications.ts`
- [ ] Kreirati `components/NotificationBell.tsx`
- [ ] Implementirati toast notifications

### 6.4 AI Integration (pgvector)

#### 6.4.1 [SEQ] Embedding Service
**Estimated:** 4h  
**Assignee:** _____________

- [ ] Dodati embedding column u Document model
- [ ] Kreirati `services/embedding.py`:
  - OpenAI embedding generation
  - Embedding storage
- [ ] Implementirati semantic search

#### 6.4.2 [SEQ] RAG Pipeline
**Estimated:** 6h  
**Assignee:** _____________

- [ ] Kreirati `services/rag.py`
- [ ] Implementirati document chunking
- [ ] Implementirati context retrieval
- [ ] Implementirati LLM integration

### 6.5 Multi-Tenancy

#### 6.5.1 [SEQ] Tenant Model & Middleware
**Estimated:** 4h  
**Assignee:** _____________

- [ ] Kreirati Tenant model
- [ ] Implementirati tenant identification (subdomain/header)
- [ ] Kreirati tenant middleware
- [ ] Update all models sa tenant_id

#### 6.5.2 [SEQ] Tenant Management API
**Estimated:** 3h  
**Assignee:** _____________

- [ ] Kreirati tenant CRUD endpoints
- [ ] Implementirati tenant isolation
- [ ] Implementirati tenant admin role

### 6.6 Document Processing
**Duration:** 3-4 dana  
**Dependencies:** Phase 6.1 (S3 Storage)

#### 6.6.1 [SEQ] File Type Detection
**Estimated:** 2h  
**Assignee:** _____________

- [ ] Instalirati `python-magic`
- [ ] Kreirati `services/file_detection.py`:
  - `detect_mime_type(file_path) -> str`
  - `is_supported_format(mime_type) -> bool`
  - `get_file_category(mime_type) -> str` (document, image, video, etc.)
- [ ] Definisati supported formats lista:
  - Documents: PDF, DOCX, DOC, TXT, RTF, ODT
  - Images: PNG, JPG, JPEG, GIF, WEBP, TIFF, BMP
  - Spreadsheets: XLSX, XLS, CSV, ODS
- [ ] Napisati unit testove

#### 6.6.2 [SEQ] Thumbnail Generation
**Estimated:** 4h  
**Dependencies:** 6.6.1  
**Assignee:** _____________

- [ ] Instalirati `pdf2image`, `Pillow`
- [ ] Kreirati `services/thumbnail.py`:
  - `generate_pdf_thumbnail(file_path) -> bytes`
  - `generate_image_thumbnail(file_path) -> bytes`
  - `generate_thumbnail(file_path, mime_type) -> bytes`
- [ ] Konfigurisati thumbnail dimensions (default: 300x400)
- [ ] Implementirati caching thumbnails u S3
- [ ] Kreirati ARQ task za async thumbnail generation
- [ ] Napisati unit testove

#### 6.6.3 [SEQ] Document Preview Service
**Estimated:** 3h  
**Dependencies:** 6.6.2  
**Assignee:** _____________

- [ ] Kreirati `services/preview.py`:
  - `get_preview_url(document_id) -> str`
  - `get_thumbnail_url(document_id) -> str`
  - `generate_preview_pages(document_id, page_range) -> list[str]`
- [ ] Implementirati pre-signed URL generation za S3
- [ ] Implementirati page-by-page PDF preview

#### 6.6.4 [SEQ] Preview API Endpoints
**Estimated:** 2h  
**Dependencies:** 6.6.3  
**Assignee:** _____________

- [ ] Dodati u `api/v1/documents.py`:
  - `GET /documents/{id}/preview` - Get preview URL
  - `GET /documents/{id}/thumbnail` - Get thumbnail URL
  - `GET /documents/{id}/pages` - Get page count
  - `GET /documents/{id}/pages/{page}` - Get specific page preview
- [ ] Implementirati caching headers
- [ ] Napisati integration testove

#### 6.6.5 [PAR] Preview UI Components
**Estimated:** 4h  
**Dependencies:** 6.6.4  
**Assignee:** _____________

- [ ] Instalirati `react-pdf` ili `@react-pdf-viewer/core`
- [ ] Kreirati `components/DocumentPreview.tsx`:
  - PDF viewer sa page navigation
  - Zoom controls
  - Fullscreen mode
- [ ] Kreirati `components/ImageViewer.tsx`:
  - Zoom in/out
  - Pan
  - Rotate
- [ ] Kreirati `components/TextViewer.tsx`:
  - Syntax highlighting za code files
  - Line numbers
- [ ] Kreirati `components/ThumbnailGrid.tsx`:
  - Grid view sa thumbnails
  - Lazy loading

### 6.7 AI-Powered OCR (OpenRouter VLM)
**Duration:** 4-5 dana  
**Dependencies:** Phase 6.1 (S3), Phase 6.2 (ARQ), Phase 6.6 (Document Processing)

### Opis

AI-powered OCR koristi Vision Language Models (VLM) preko OpenRouter API-ja za ekstrakciju teksta iz slika i PDF-ova. Podržava strukturiranu ekstrakciju (tabele, JSON) i multi-page dokumente.

#### 6.7.1 [SEQ] OpenRouter Integration & Vision Pipeline
**Estimated:** 4h  
**Assignee:** _____________

- [ ] Kreirati `services/openrouter.py`:
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
- [ ] Implementirati async HTTP client (httpx)
- [ ] Konfigurisati OpenRouter API key u settings
- [ ] Kreirati `services/image_processing.py`:
  - `optimize_image(image_bytes) -> bytes` (resize to max 2048px)
  - `convert_to_base64(image_bytes) -> str`
  - `pdf_page_to_image(pdf_path, page_num) -> bytes`
- [ ] Napisati unit testove

#### 6.7.2 [SEQ] Structured Extraction Engine
**Estimated:** 5h  
**Dependencies:** 6.7.1  
**Assignee:** _____________

- [ ] Kreirati `services/ocr_extraction.py`:
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
- [ ] Kreirati dynamic prompts za različite tipove dokumenata:
  - Invoice extraction prompt
  - Table to Markdown prompt
  - Form field extraction prompt
- [ ] Implementirati multi-page PDF handling:
  - Parallel page processing
  - Result aggregation
- [ ] Implementirati fallback logic:
  - Primary: qwen/qwen2-vl-72b-instruct
  - Fallback: google/gemini-flash-1.5
- [ ] Napisati integration testove

#### 6.7.3 [SEQ] Async OCR Worker (ARQ)
**Estimated:** 4h  
**Dependencies:** 6.7.2  
**Assignee:** _____________

- [ ] Kreirati `tasks/ocr.py`:
  ```python
  async def process_document_ocr(ctx, document_id: UUID, options: dict):
      """ARQ task for OCR processing."""
      pass
  
  async def batch_ocr(ctx, document_ids: list[UUID]):
      """Batch OCR for multiple documents."""
      pass
  ```
- [ ] Implementirati rate limit management:
  - Track 429 responses
  - Exponential backoff
  - Queue management
- [ ] Implementirati partial updates:
  - Redis pub/sub za progress ("Processing page 3/10...")
  - Status updates u database
- [ ] Implementirati cost tracking:
  - Token usage per request
  - Estimated cost calculation
- [ ] Error handling i retry logic

#### 6.7.4 [SEQ] OCR API Endpoints
**Estimated:** 2h  
**Dependencies:** 6.7.3  
**Assignee:** _____________

- [ ] Kreirati `api/v1/ocr.py`:
  - `POST /documents/{id}/ocr` - Start OCR processing
  - `GET /documents/{id}/ocr/status` - Get OCR status
  - `GET /documents/{id}/ocr/result` - Get OCR result
  - `POST /documents/bulk/ocr` - Batch OCR
- [ ] Implementirati WebSocket za real-time progress (optional)
- [ ] Napisati integration testove

#### 6.7.5 [PAR] OCR UI Components
**Estimated:** 4h  
**Dependencies:** 6.7.4  
**Assignee:** _____________

- [ ] Kreirati `components/OCRResultViewer.tsx`:
  - Markdown renderer za formatted text
  - JSON viewer za structured data
  - Table renderer
- [ ] Kreirati `components/OCRProgress.tsx`:
  - Progress bar sa page info
  - Estimated time remaining
  - Cancel button
- [ ] Kreirati `components/CostTracker.tsx`:
  - Token usage display
  - Estimated cost per document
  - Monthly usage summary
- [ ] Kreirati `components/SmartCopy.tsx`:
  - Copy as Markdown
  - Copy as JSON
  - Copy as plain text
  - Copy table as CSV

#### 6.7.6 [PAR] OCR Settings & Configuration
**Estimated:** 2h  
**Dependencies:** 6.7.4  
**Assignee:** _____________

- [ ] Kreirati OCR settings page:
  - Default model selection
  - Output format preference
  - Auto-OCR on upload toggle
- [ ] Kreirati per-document OCR options:
  - Model override
  - Output format
  - Language hint

### Environment Variables za Phase 6.6 & 6.7

```bash
# Document Processing
THUMBNAIL_WIDTH=300
THUMBNAIL_HEIGHT=400
SUPPORTED_FORMATS=pdf,docx,doc,txt,png,jpg,jpeg,gif,xlsx,xls,csv

# OpenRouter OCR
OPENROUTER_API_KEY=sk-or-v1-xxxxx
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OCR_PRIMARY_MODEL=qwen/qwen2-vl-72b-instruct
OCR_FALLBACK_MODEL=google/gemini-flash-1.5
OCR_MAX_RETRIES=3
OCR_RATE_LIMIT_DELAY=5
```

---

## Dependency Graph

```
Phase 0 (Foundation)
    │
    ├──────────────────────────────────────┐
    │                                      │
    ▼                                      ▼
Phase 1 (Auth)                    Phase 3 (Search)
    │                                      │
    ▼                                      ▼
Phase 2 (RBAC)                    Phase 3.4 (Labels)
    │                                      │
    │                                      ▼
    │                             Phase 3.5 (Watch Folders)*
    │                                      │
    └──────────────┬───────────────────────┘
                   │
                   ▼
            Phase 4 (Monitoring)
                   │
                   ▼
            Phase 5 (Deployment)
                   │
                   ▼
            Phase 6 (Optional Features)
                   │
                   ├── 6.1 S3 Storage
                   ├── 6.2 Background Jobs (ARQ)
                   ├── 6.3 Real-time Notifications
                   ├── 6.4 AI Integration (pgvector)
                   ├── 6.5 Multi-Tenancy
                   ├── 6.6 Document Processing**
                   └── 6.7 AI-Powered OCR***

* Phase 3.5 zavisi od Phase 3.4 (Labels), Phase 6.1 (S3) i Phase 6.2 (ARQ)
** Phase 6.6 zavisi od Phase 6.1 (S3)
*** Phase 6.7 zavisi od Phase 6.1, 6.2 i 6.6
```

## Parallelization Summary

| Phase | Can Run In Parallel With |
|-------|-------------------------|
| Phase 0 | - (must be first) |
| Phase 1 | Phase 3, Phase 4 |
| Phase 2 | Phase 3, Phase 4 |
| Phase 3 | Phase 1, Phase 2, Phase 4 |
| Phase 3.4 | After Phase 3 |
| Phase 3.5 | After Phase 3.4, 6.1 & 6.2 |
| Phase 4 | Phase 1, Phase 2, Phase 3 |
| Phase 5 | - (needs 1,2,3 complete) |
| Phase 6 | After Phase 5 |

## Team Allocation Recommendation

### Option A: 2 Engineers
- **Engineer 1 (Backend):** Phase 0 → Phase 1 Backend → Phase 2 Backend → Phase 6.1/6.2 → Phase 3.5 → Phase 5
- **Engineer 2 (Frontend):** Phase 0 Frontend → Phase 1 Frontend → Phase 2 Frontend → Phase 3 Frontend → Phase 3.5 Frontend

### Option B: 3 Engineers
- **Engineer 1 (Backend Core):** Phase 0 Backend → Phase 1 Backend → Phase 2 Backend
- **Engineer 2 (Frontend):** Phase 0 Frontend → Phase 1 Frontend → Phase 2 Frontend → Phase 3 Frontend → Phase 3.5 Frontend
- **Engineer 3 (Search + DevOps):** Phase 3 Backend → Phase 6.1/6.2 → Phase 3.5 Backend → Phase 4 → Phase 5

### Option C: 4+ Engineers (Maximum Parallelization)
- **Engineer 1:** Phase 0 → Phase 1 Backend
- **Engineer 2:** Phase 0 Frontend → Phase 1 Frontend
- **Engineer 3:** Phase 3 → Phase 3.4 (after Phase 0)
- **Engineer 4:** Phase 4 (after Phase 0)
- **Engineer 5 (DevOps):** Phase 5 (after core phases)
- **Engineer 6 (DMS Features):** Phase 6.1 → Phase 6.2 → Phase 3.5 → Phase 6.6 → Phase 6.7

---

## Estimated Total Duration

| Scenario | Duration |
|----------|----------|
| 1 Engineer (Sequential) | 10-12 weeks |
| 2 Engineers (Parallel) | 5-6 weeks |
| 3 Engineers (Optimized) | 4-5 weeks |
| 4+ Engineers (Maximum) | 3-4 weeks |

---

## Task Summary

| Phase | Backend Tasks | Frontend Tasks | Total Hours |
|-------|---------------|----------------|-------------|
| Phase 0 | 5 | 2 | ~15h |
| Phase 1 | 9 | 6 | ~35h |
| Phase 2 | 7 | 4 | ~25h |
| Phase 3 | 6 | 4 | ~25h |
| Phase 3.4 | 5 | 5 | ~20h |
| Phase 3.5 | 7 | 5 | ~30h |
| Phase 4 | 6 | 0 | ~15h |
| Phase 5 | 7 | 0 | ~20h |
| Phase 6.1-6.5 | Variable | Variable | ~30h |
| Phase 6.6 | 5 | 1 | ~15h |
| Phase 6.7 | 6 | 2 | ~21h |
| **Total** | **63** | **29** | **~251h** |

---

*Document Version: 1.2*  
*Last Updated: January 2026*

# Changelog

All notable changes to this project will be documented in this file.

---

## [2.7.0] - 2026-01-03

### Added - Phase 3: Full-Text Search Frontend (Tasks 3.7-3.10)

Kompletna frontend implementacija za Document Management i Full-Text Search sa Motion.dev animacijama.

- **Document API Client** (`lib/document-api.ts`) - Task 3.7:
  - TypeScript tipovi za Document, SearchRequest, SearchResponse
  - `getDocuments()`, `getDocument()`, `createDocument()`, `updateDocument()`, `deleteDocument()`
  - `searchDocuments()`, `getSuggestions()`

- **TanStack Query Hooks** (`hooks/useDocuments.ts`) - Task 3.7:
  - `useDocuments()` - Lista dokumenata sa pagination
  - `useDocument(id)` - Pojedinačni dokument
  - `useCreateDocument()`, `useUpdateDocument()`, `useDeleteDocument()` - Mutations
  - `useSearch()`, `useSearchSuggestions()` - Search hooks
  - Query key factory pattern za cache invalidation

- **Document List Page** (`routes/documents/index.tsx`) - Task 3.8:
  - Grid/List view toggle sa Motion animacijama
  - Staggered enter animacije za document cards
  - Pagination sa animated buttons
  - Sorting (created_at, updated_at, title)
  - Create document dialog
  - Delete confirmation dialog
  - Hover effects i micro-interactions

- **Document Detail/Edit Page** (`routes/documents/$documentId.tsx`) - Task 3.9:
  - Document view sa metadata display
  - Inline edit mode
  - Save/Cancel sa loading states
  - Delete confirmation
  - Motion spring animacije

- **Search Page** (`routes/search.tsx`) - Task 3.10:
  - Full-text search sa 4 moda (simple, phrase, fuzzy, boolean)
  - Search suggestions dropdown
  - Filters panel (date range, owner)
  - Search results sa highlighting
  - Pagination
  - Motion animacije za results

- **SearchBar Component** (`components/SearchBar.tsx`) - Task 3.10:
  - Reusable search input sa suggestions
  - Keyboard navigation (Enter, Escape)
  - Animated suggestions dropdown

### UI/UX Features

- **Motion.dev Animacije**:
  - Staggered container/item variants
  - Spring physics za hover effects
  - AnimatePresence za mount/unmount
  - whileHover, whileTap, whileInView gesturi
  - Layout animations

- **Dark Theme Design**:
  - Neutral-950 background, neutral-50 text
  - Gradient icons (blue-500 to cyan-500)
  - Border hover effects
  - Backdrop blur za sticky headers

### Task Status
- [x] Task 3.7 - Document API Client (COMPLETED)
- [x] Task 3.8 - Document List Page (COMPLETED)
- [x] Task 3.9 - Document Detail/Edit Page (COMPLETED)
- [x] Task 3.10 - Search UI (COMPLETED)

---

## [2.6.0] - 2026-01-03

### Added - Phase 3: Full-Text Search (Tasks 3.1-3.6)

Kompletna backend implementacija za Document Management i Full-Text Search.

- **Document Model** (`app/models/document.py`) - Task 3.1:
  - `id` (UUID), `title`, `content`, `meta` (JSONB)
  - `owner_id` (FK), `search_vector` (TSVECTOR)
  - Trigger za automatsko ažuriranje search_vector

- **Alembic Migracija** (`003_create_documents_table.py`):
  - GIN index za `search_vector` (full-text search)
  - Trigram indexes za fuzzy search
  - Weighted search: title (A), content (B)

- **Document Schemas** (`app/schemas/document.py`) - Task 3.2:
  - DocumentCreate, DocumentUpdate, DocumentResponse
  - DocumentListResponse sa pagination

- **Search Schemas** (`app/schemas/search.py`) - Task 3.2:
  - SearchMode enum (simple, phrase, fuzzy, boolean)
  - SearchRequest, SearchFilters
  - SearchResponse, SearchResultItem, SearchHighlight
  - SearchSuggestionsResponse

- **Document CRUD Service** (`app/services/document.py`) - Task 3.3:
  - `create_document()`, `get_document()`, `update_document()`, `delete_document()`
  - `list_documents()` sa pagination
  - `check_document_ownership()`, `get_document_with_owner_check()`

- **Search Service** (`app/services/search.py`) - Task 3.4:
  - `search_simple()` - plainto_tsquery
  - `search_phrase()` - phraseto_tsquery (exact phrase)
  - `search_fuzzy()` - pg_trgm similarity (typo tolerance)
  - `search_boolean()` - to_tsquery (AND/OR/NOT)
  - ts_rank ranking, ts_headline highlighting
  - Filtering: owner, date range, metadata (JSONB)
  - `get_suggestions()` - Autocomplete

- **Document API** (`app/api/v1/documents.py`) - Task 3.5:
  - `GET /documents` - List (RBAC: own vs all)
  - `POST /documents` - Create
  - `GET /documents/{id}` - Get details
  - `PUT /documents/{id}` - Update
  - `DELETE /documents/{id}` - Delete

- **Search API** (`app/api/v1/search.py`) - Task 3.6:
  - `POST /search` - Search documents (4 modes)
  - `GET /search/suggestions` - Autocomplete

### Fixed - RBAC Super Admin Wildcard & UserRole Assignment

- Popravljeno Super Admin wildcard u `app/core/seed_rbac.py`:
  - Pre: `("system", "*", PermissionScope.ALL.value)`
  - Posle: `("*", "*", PermissionScope.ALL.value)` - pravi wildcard za sve permissions
- Popravljena wildcard logika u `seed_roles()` za dodelu svih permissions Super Admin roli
- Popravljeno `app/core/init_db.py` - UserRole assignment:
  - Pre: `user.roles.append(role)` - ne kreira zapis u user_roles tabeli
  - Posle: Direktan `UserRole(user_id, role_id)` insert - radi ispravno
- admin@example.com sada ima Super Admin rolu sa punim pristupom

### Removed - Frontend Demo Folder

- Obrisan `frontend/src/routes/demo` folder (TanStack Start boilerplate demo fajlovi)

### Added - Unit Tests

- `tests/test_document_service.py` - 14 testova za Document service
- `tests/test_search_service.py` - 14 testova za Search service

### Added - Integration Tests

- `tests/test_document_api.py` - 11 testova za Document API
- `tests/test_search_api.py` - 12 testova za Search API

### Task Status
- [x] Task 3.1 - Document Model & Migration (COMPLETED)
- [x] Task 3.2 - Document Schemas (COMPLETED)
- [x] Task 3.3 - Document CRUD Service (COMPLETED)
- [x] Task 3.4 - Search Service (COMPLETED)
- [x] Task 3.5 - Document API Endpoints (COMPLETED)
- [x] Task 3.6 - Search API Endpoint (COMPLETED)

---

## [2.5.0] - 2026-01-03

### Changed - Landing Page Redesign

Kompletno redizajnirana landing page sa modernim UI i Motion animacijama.

- **Estetika** - Editorial/Industrial dizajn:
  - Crno-bela paleta (neutral-950 background, neutral-50 text)
  - Drastična tipografija (7xl-9xl naslov)
  - Asimetričan layout sa generošnim whitespace-om
  - Uklonjeni ljubičasti gradijenti

- **Motion Animacije**:
  - Instalirana `motion` biblioteka (v12.23.26)
  - Staggered enter animacije za hero section
  - Scroll-triggered animacije za features i tech stack
  - Spring physics animacije
  - Hover gesturi (whileHover, whileTap, whileInView)
  - Animirani background grid

- **UI Komponente**:
  - Badge sa pulse indicator
  - Stats section sa hover efekti
  - Feature cards sa gradient hover efekti
  - Tech stack section sa micro-interactions
  - CTA section sa scale animacijama

- **Ispravke**:
  - Uklonjen `as string` cast iz auth/register i auth/login ruta
  - Ispravljene TypeScript greške za Motion variants
  - Dodat `params={{}}` za sve Link komponente
  - Ispravljena vidljivost "Create Account" dugmeta

---

## [2.4.1] - 2026-01-03

### Changed - DEVELOPMENT_PHASES.md Updated

Ažuriran status taskova u Phase 2 Frontend (Tasks 2.8-2.11).

- **Task 2.8** - Permission Hook (COMPLETED)
- **Task 2.9** - Permission Components (COMPLETED)
- **Task 2.10** - Admin Role Management UI (COMPLETED)
- **Task 2.11** - Admin User Role Assignment UI (COMPLETED)

Svi Phase 2 taskovi su sada označeni kao completed.

---

## [2.4.0] - 2026-01-03

### Added - Phase 2: RBAC Frontend (Tasks 2.8-2.11)

Kompletna frontend implementacija za RBAC sistem.

- **RBAC API Client** (lib/rbac-api.ts):
  - TypeScript tipovi za Role, Permission, UserRole, UserWithRoles
  - API funkcije za roles CRUD, permissions, user roles
  - Bulk role assignment support

- **Permission Hook** (Task 2.8):
  - `hooks/usePermissions.ts` - Custom hook za permission checking
  - `hasPermission(resource, action, scope)` - Provera pojedinačne dozvole
  - `hasAnyPermission()` / `hasAllPermissions()` - Bulk provere
  - `hasRole()` / `hasAnyRole()` - Provera uloga
  - `isAdmin()` / `isSuperAdmin()` - Helper metode
  - Automatic fetch on auth, scope hierarchy support

- **Permission Components** (Task 2.9):
  - `components/CanAccess.tsx` - Conditional rendering based on permissions
    - Support za permission string format (`users:create`)
    - Support za resource/action/scope props
    - Support za `any` i `all` permission checks
    - Fallback rendering
  - `components/RequireRole.tsx` - Conditional rendering based on roles
    - Single role ili multiple roles check
    - `requireAll` option za AND logic
    - Fallback rendering

- **Admin Role Management UI** (Task 2.10):
  - `routes/admin/roles/index.tsx` - Role list stranica
    - Grid prikaz sa role cards
    - Search functionality
    - Create role dialog
    - Delete role confirmation
    - Role color coding
  - `routes/admin/roles/$roleId.tsx` - Role details/edit stranica
    - Edit role name i description
    - Permission management dialog
    - Grouped permissions by resource
    - Add/remove permissions
    - System role protection

- **Admin User Role Assignment UI** (Task 2.11):
  - `routes/admin/users/index.tsx` - User management stranica
    - Paginated user table
    - Search by email/username
    - User status badges (Active, Verified)
    - Current roles display
    - Add role dialog per user
    - Remove role inline
    - Bulk role assignment za selected users
    - Checkbox selection

- **UI Components**:
  - `components/ui/dialog.tsx` - Modal dialog komponenta
  - `components/ui/badge.tsx` - Badge sa variants (success, warning, info)
  - `components/ui/select.tsx` - Select dropdown komponenta
  - `components/ui/textarea.tsx` - Textarea komponenta

- **Backend Enhancement**:
  - `GET /api/v1/auth/me/permissions` - Endpoint za frontend permission checking
  - Vraća permissions i roles za trenutnog korisnika

### Task Status
- [x] Task 2.8 - Permission Hook (COMPLETED)
- [x] Task 2.9 - Permission Components (COMPLETED)
- [x] Task 2.10 - Admin Role Management UI (COMPLETED)
- [x] Task 2.11 - Admin User Role Assignment UI (COMPLETED)

---

## [2.3.0] - 2026-01-03

### Added - Phase 2: RBAC (Role-Based Access Control)

Kompletna implementacija RBAC sistema za upravljanje ulogama i dozvolama.

- **RBAC Models** (Task 2.1):
  - `app/models/role.py` - Role model (id, name, description, is_system)
  - `app/models/permission.py` - Permission model (resource, action, scope)
  - `app/models/role_permission.py` - Many-to-many Role-Permission relationship
  - `app/models/user_role.py` - User-Role relationship sa assigned_at, assigned_by
  - Alembic migracija `001_create_rbac_tables.py`

- **RBAC Schemas** (Task 2.2):
  - `app/schemas/role.py` - RoleCreate, RoleUpdate, RoleResponse, RoleListResponse
  - `app/schemas/permission.py` - PermissionCreate, PermissionResponse, PermissionAssign
  - `app/schemas/user_role.py` - UserRoleAssign, UserRoleBulkAssign, UserRolesResponse

- **Permission Checking Service** (Task 2.3):
  - `app/services/rbac.py` - RBACService klasa sa:
    - `has_permission()` - Provera pojedinačne dozvole
    - `has_any_permission()` / `has_all_permissions()` - Bulk provere
    - `has_role()` / `has_any_role()` - Provera uloga
    - `is_admin()` / `is_super_admin()` - Helper metode
    - Redis caching za permissions (5 min TTL)
  - CRUD operacije za Role i Permission

- **Permission Dependencies** (Task 2.4):
  - `app/api/deps.py` - Prošireno sa:
    - `require_permission(resource, action, scope)` - Dependency factory
    - `require_role(role_name)` - Role-based dependency
    - `require_any_role(role_names)` - Any role dependency
    - `require_any_permission(permissions)` - Any permission dependency
    - `RequireAdmin` / `RequireSuperAdmin` - Predefinisane dependencies
    - `RBACServiceDep` - Type alias za RBAC service injection

- **RBAC API Endpoints** (Task 2.5):
  - `app/api/v1/roles.py`:
    - `GET /roles` - Lista svih uloga
    - `POST /roles` - Kreiranje nove uloge
    - `GET /roles/{id}` - Detalji uloge
    - `PUT /roles/{id}` - Ažuriranje uloge
    - `DELETE /roles/{id}` - Brisanje uloge (samo non-system)
    - `POST /roles/{id}/permissions` - Dodela dozvola ulozi
    - `DELETE /roles/{id}/permissions/{perm_id}` - Uklanjanje dozvole
  - `app/api/v1/permissions.py`:
    - `GET /permissions` - Lista svih dozvola

- **User Role Management API** (Task 2.6):
  - `app/api/v1/users.py`:
    - `GET /users/{id}/roles` - Uloge korisnika
    - `POST /users/{id}/roles` - Dodela uloge korisniku
    - `DELETE /users/{id}/roles/{role_id}` - Uklanjanje uloge
    - `POST /users/bulk/roles` - Bulk dodela uloge

- **Seed Default Roles & Permissions** (Task 2.7):
  - `app/core/seed_rbac.py` - Seeding funkcije sa:
    - 30+ default permissions (users, roles, documents, labels, watch_folders)
    - 5 default roles: Super Admin, Admin, Manager, User, Viewer
    - Scope hierarchy: own < team < all
    - Wildcard permissions support (*)
  - `app/core/init_db.py` - Ažurirano da:
    - Automatski seed-uje RBAC podatke pri startu
    - Dodeljuje Super Admin rolu superadmin korisniku

- **Permission Scopes**:
  - `own` - Pristup samo sopstvenim resursima
  - `team` - Pristup resursima tima
  - `all` - Pristup svim resursima

- **Default Roles**:
  - **Super Admin** - Pun pristup sistemu (wildcard *)
  - **Admin** - Upravljanje korisnicima, ulogama, dokumentima
  - **Manager** - Team-level pristup dokumentima
  - **User** - Pristup sopstvenim resursima
  - **Viewer** - Read-only pristup sopstvenim resursima

- **Audit Logging** (Task 2.6):
  - `app/models/audit_log.py` - AuditLog model sa AuditAction enum
  - `app/services/audit.py` - AuditService za logging role changes
  - `app/api/v1/users.py` - Integrisan audit logging za role assignment/removal
  - Alembic migracija `002_add_audit_logs.py`
  - Logging IP adrese i user agent-a
  - Audit log entries za: role_assigned, role_removed, role_created, role_updated, role_deleted, permission_assigned, permission_removed

- **Testing** (Tasks 2.3, 2.5):
  - `tests/test_rbac_service.py` - Unit testovi za RBACService (13 testova)
  - `tests/test_rbac_api.py` - Integration testovi za RBAC API (17 testova)
  - Testovi pokrivaju: permission checking, wildcard permissions, scope hierarchy, role checks, CRUD operacije, audit logging

---

## [2.2.0] - 2026-01-02

### Changed - HTTP-only Cookie Authentication

Migracija sa localStorage na HTTP-only cookies za sigurnije čuvanje tokena.

- **Backend Changes**:
  - `app/core/cookies.py` - Cookie utility funkcije (set_auth_cookies, clear_auth_cookies)
  - `app/config.py` - Dodati COOKIE_DOMAIN, COOKIE_SECURE, COOKIE_SAMESITE settings
  - `app/api/deps.py` - Ažuriran da čita token iz cookies ili Authorization header
  - `app/api/v1/auth.py` - Login, refresh, logout endpoints postavljaju/brišu cookies
  - `app/api/v1/oidc.py` - OIDC callback postavlja cookies

- **Frontend Changes**:
  - `lib/api.ts` - API client sa `credentials: 'include'` za slanje cookies
  - `lib/auth-api.ts` - Uklonjen tokenStorage, koristi cookies
  - `lib/auth-context.tsx` - Uklonjen tokenStorage dependency

- **Security Improvements**:
  - Tokeni nisu dostupni JavaScript-u (XSS protection)
  - HTTP-only cookies sa SameSite policy
  - Secure flag za HTTPS u produkciji
  - Refresh token cookie ograničen na `/api/v1/auth` path

---

## [2.1.0] - 2026-01-02

### Added - Phase 1: Authentication Module (Frontend Tasks 1.10-1.15)

- **Auth API Client** (Task 1.10):
  - `lib/api.ts` - Fetch wrapper sa automatic auth headers
  - Automatic token refresh na 401 response
  - `lib/auth-api.ts` - Auth API funkcije (login, register, logout, refresh, etc.)

- **Auth State Management** (Task 1.11):
  - `lib/auth-context.tsx` - React Context za auth state
  - `hooks/useAuth.ts` - Custom hook za auth operacije
  - Persistent auth state sa automatic user fetch

- **Login Page** (Task 1.12):
  - `routes/auth/login.tsx` - Modern login stranica
  - Email/password form sa Zod validacijom
  - Remember me checkbox, forgot password link
  - SSO buttons (Google, GitHub) - placeholder
  - Gradient split-screen dizajn

- **Registration Page** (Task 1.13):
  - `routes/auth/register.tsx` - Registration stranica
  - Password strength indicator
  - Password requirements checklist
  - Terms acceptance checkbox

- **Password Reset Pages** (Task 1.14):
  - `routes/auth/forgot-password.tsx` - Request reset
  - `routes/auth/reset-password.tsx` - Confirm reset
  - Success/error state handling

- **Protected Routes** (Task 1.15):
  - `components/ProtectedRoute.tsx` - Auth guard komponenta
  - `routes/dashboard/index.tsx` - Protected dashboard
  - Redirect to login za unauthenticated users
  - Loading state dok se proverava auth

- **UI Components**:
  - `components/ui/checkbox.tsx` - Checkbox komponenta
  - `components/ui/separator.tsx` - Separator komponenta

- **Root Layout Update**:
  - AuthProvider integrisan u `__root.tsx`

### Task Status
- [x] Task 1.10 - Auth API Client (COMPLETED)
- [x] Task 1.11 - Auth State Management (COMPLETED)
- [x] Task 1.12 - Login Page (COMPLETED)
- [x] Task 1.13 - Registration Page (COMPLETED)
- [x] Task 1.14 - Password Reset Pages (COMPLETED)
- [x] Task 1.15 - Protected Routes (COMPLETED)

---

## [2.0.0] - 2026-01-02

### Added - Phase 1: Authentication Module (Backend Tasks 1.1-1.7)

- **User Model & Migration** (Task 1.1):
  - `app/models/user.py` sa kompletnim User modelom
  - UUID primary key, email/username (unique), password_hash
  - auth_provider, oidc_subject, oidc_issuer za SSO support
  - is_active, is_verified, last_login_at tracking
  - Alembic migracija `4c476b041802_create_users_table.py`
  - Indexi za email, username, auth_provider, OIDC fields

- **Auth Schemas** (Task 1.2):
  - `app/schemas/auth.py`:
    - UserCreate, UserLogin, UserResponse
    - TokenResponse, TokenPayload, RefreshTokenRequest
    - PasswordResetRequest, PasswordResetConfirm, PasswordChange
    - MessageResponse
  - `app/schemas/user.py`:
    - UserUpdate, UserProfile, UserInDB

- **Password Hashing Service** (Task 1.3):
  - `app/services/security.py` sa bcrypt hashing
  - `hash_password()`, `verify_password()`, `needs_rehash()`
  - Bcrypt cost factor 12 (production-ready)

- **JWT Token Service** (Task 1.4):
  - `app/services/jwt.py` sa kompletnim JWT management
  - `create_access_token()`, `create_refresh_token()`, `create_tokens()`
  - `decode_token()`, `is_token_expired()`
  - Refresh token storage u Redis
  - `store_refresh_token()`, `validate_refresh_token()`, `invalidate_refresh_token()`

- **Auth Dependencies** (Task 1.5):
  - `app/api/deps.py` sa FastAPI dependencies
  - `get_current_user` - extracts user from JWT
  - `get_current_active_user` - validates user is active
  - `get_optional_user` - returns None if not authenticated
  - Type aliases: CurrentUser, CurrentActiveUser, OptionalUser

- **Auth API Endpoints** (Task 1.6):
  - `app/api/v1/auth.py` router sa endpoints:
    - `POST /api/v1/auth/register` - User registration
    - `POST /api/v1/auth/login` - Login, return tokens
    - `POST /api/v1/auth/refresh` - Refresh access token
    - `POST /api/v1/auth/logout` - Invalidate tokens
    - `GET /api/v1/auth/me` - Current user info
    - `POST /api/v1/auth/change-password` - Change password
  - Email i username validation
  - Proper error handling

- **Password Reset Flow** (Task 1.7):
  - `app/services/password_reset.py`:
    - `create_password_reset_token()` - generates secure token
    - `verify_password_reset_token()` - validates token
    - `invalidate_password_reset_token()` - cleanup after use
  - Endpoints:
    - `POST /api/v1/auth/password/reset` - Request reset
    - `POST /api/v1/auth/password/reset/confirm` - Confirm reset
  - Token storage u Redis sa 30min expiration
  - Security: always returns success (no email enumeration)

- **API Router Setup**:
  - `app/api/v1/__init__.py` sa api_v1_router
  - Integrated u `main.py`

- **Unit Tests** (Task 1.3, 1.4):
  - `tests/test_security.py` - Password hashing tests
  - `tests/test_jwt.py` - JWT token tests
  - `tests/conftest.py` - Pytest fixtures
  - `tests/test_auth_api.py` - Integration tests za auth endpoints

- **Rate Limiting** (Task 1.6):
  - `app/core/rate_limit.py` - Redis-based rate limiting
  - Login: 5 requests/minute, 5min block
  - Register: 3 requests/minute, 10min block
  - Password reset: 3 requests/minute, 10min block

- **Email Service** (Task 1.7):
  - `app/services/email.py` - Placeholder email service
  - HTML templates za password reset, welcome, email verification
  - Development mode: logs emails to console

- **OIDC Integration** (Task 1.8):
  - `app/services/oidc.py` - OIDC service sa authlib
  - `app/api/v1/oidc.py` - OIDC endpoints:
    - `GET /api/v1/oidc/authorize` - Initiate OIDC login
    - `GET /api/v1/oidc/callback` - Handle callback
  - User creation/linking za OIDC users
  - State/nonce storage u Redis

- **Super Admin Setup** (Task 1.9):
  - `app/core/init_db.py` - Database initialization
  - Auto-create super admin on startup
  - Auto-generate password if not provided
  - Integrated u application lifespan

### Task Status
- [x] Task 1.1 - User Model & Migration (COMPLETED)
- [x] Task 1.2 - Auth Schemas (COMPLETED)
- [x] Task 1.3 - Password Hashing Service (COMPLETED)
- [x] Task 1.4 - JWT Token Service (COMPLETED)
- [x] Task 1.5 - Auth Dependencies (COMPLETED)
- [x] Task 1.6 - Auth API Endpoints (COMPLETED)
- [x] Task 1.7 - Password Reset Flow (COMPLETED)
- [x] Task 1.8 - OIDC Integration (COMPLETED)
- [x] Task 1.9 - Initial Super Admin Setup (COMPLETED)

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

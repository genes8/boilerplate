# Contributing Guide

Hvala na interesovanju za doprinos ovom projektu! Ovaj dokument opisuje proces i smernice za kontribuciju.

---

## Development Setup

### Prerequisites

- Python 3.11+
- Node.js 20+
- pnpm
- Poetry
- PostgreSQL 16
- Redis 7

### Local Environment

1. **Fork & Clone**
   ```bash
   git clone https://github.com/genes8/boilerplate.git
   cd boilerplate
   ```

2. **Backend Setup**
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate
   poetry install
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   pnpm install
   ```

4. **Environment Configuration**
   ```bash
   cp .env.example .env
   # Configure your local environment
   ```

---

## Git Workflow

### Branch Naming Convention

- `feature/` - Nova funkcionalnost (npr. `feature/user-authentication`)
- `bugfix/` - Ispravka buga (npr. `bugfix/login-redirect`)
- `hotfix/` - Hitna ispravka za produkciju (npr. `hotfix/security-patch`)
- `refactor/` - Refaktorisanje koda (npr. `refactor/api-structure`)
- `docs/` - Dokumentacija (npr. `docs/api-reference`)

### Commit Messages

Koristimo [Conventional Commits](https://www.conventionalcommits.org/) format:

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types:**
- `feat` - Nova funkcionalnost
- `fix` - Ispravka buga
- `docs` - Dokumentacija
- `style` - Formatiranje (bez promene logike)
- `refactor` - Refaktorisanje
- `test` - Testovi
- `chore` - Maintenance taskovi

**Examples:**
```bash
feat(auth): add JWT refresh token endpoint
fix(search): correct fuzzy search threshold
docs(api): update authentication endpoints
refactor(models): extract base model class
test(auth): add login integration tests
chore(deps): update fastapi to 0.109.0
```

---

## Code Style

### Python (Backend)

- **Formatter:** Black (line length: 88)
- **Linter:** Ruff
- **Type Checker:** mypy
- **Import Sorting:** isort

```bash
# Format code
black .
isort .

# Lint
ruff check .

# Type check
mypy .
```

### TypeScript (Frontend)

- **Formatter:** Prettier
- **Linter:** ESLint
- **Type Checker:** TypeScript strict mode

```bash
# Format code
pnpm format

# Lint
pnpm lint

# Type check
pnpm typecheck
```

---

## Testing

### Backend Tests

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_auth.py

# Run specific test
pytest tests/test_auth.py::test_login_success
```

### Frontend Tests

```bash
cd frontend

# Run tests
pnpm test

# Run with coverage
pnpm test:coverage
```

---

## Pull Request Process

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature
   ```

2. **Make Changes**
   - Write code
   - Add tests
   - Update documentation

3. **Run Checks Locally**
   ```bash
   # Backend
   cd backend
   black .
   ruff check .
   mypy .
   pytest

   # Frontend
   cd frontend
   pnpm lint
   pnpm typecheck
   pnpm test
   ```

4. **Commit Changes**
   ```bash
   git add .
   git commit -m "feat(scope): description"
   ```

5. **Push & Create PR**
   ```bash
   git push origin feature/your-feature
   ```

6. **PR Requirements**
   - Descriptive title following commit convention
   - Description of changes
   - Link to related issue (if applicable)
   - All CI checks passing
   - Code review approval

---

## Code Review Guidelines

### For Authors

- Keep PRs focused and small (< 400 lines when possible)
- Provide context in PR description
- Respond to feedback promptly
- Request re-review after addressing comments

### For Reviewers

- Be constructive and respectful
- Explain the "why" behind suggestions
- Approve when satisfied, don't block on minor issues
- Use suggestions feature for small changes

---

## Project Structure

```
/
├── backend/
│   ├── app/
│   │   ├── api/v1/        # API endpoints
│   │   ├── core/          # Core functionality
│   │   ├── models/        # SQLAlchemy models
│   │   ├── schemas/       # Pydantic schemas
│   │   ├── services/      # Business logic
│   │   └── utils/         # Utilities
│   ├── tests/             # Backend tests
│   └── alembic/           # Database migrations
├── frontend/
│   ├── src/
│   │   ├── routes/        # Page routes
│   │   ├── components/    # React components
│   │   ├── lib/           # Utilities & API clients
│   │   ├── hooks/         # Custom hooks
│   │   └── stores/        # State management
│   └── public/            # Static assets
├── docker/                # Docker configs
├── docs/                  # Documentation
└── scripts/               # Utility scripts
```

---

## Questions?

Ako imate pitanja, otvorite Issue ili kontaktirajte maintainere.

---

Hvala na doprinosu! 🚀

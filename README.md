# Job Board API

Django + DRF backend for a job board platform with a multi-role system (employers/candidates), JWT authentication, job listing CRUD with filtering and pagination, full application lifecycle management with PDF resume uploads, async email notifications via Celery and Redis, and a four-service Docker Compose deployment.

## Tech Stack

- Django 4.2 + Django REST Framework
- PostgreSQL
- JWT Authentication (djangorestframework-simplejwt) with custom token claims
- Celery + Redis (async tasks)
- django-filter (filtering, search, ordering)
- Docker Compose (web, db, redis, celery worker)
- Pytest + DRF APIClient (testing)

## Features

- Custom User model with role support (employer / candidate)
- JWT auth with `role` and `username` embedded directly in the token payload
- Three-layer permission system: authentication, role check, object-level ownership
- Job listing CRUD scoped to the owning employer, with filtering by location/status/salary range, full-text search, and pagination
- Application lifecycle with PDF resume upload and a strict status state machine (`applied` → `reviewed` → `accepted`/`rejected`), enforced at the serializer layer
- Async email notifications on status change via Celery + Redis, decoupled from the request/response cycle, with automatic retry on failure
- N+1 query prevention via `select_related` on every queryset that serializes a foreign key, plus an optimized Django admin
- Dockerized four-service deployment (web, PostgreSQL, Redis, Celery worker) with health checks and a shared media volume
- Test suite covering authentication, permission boundaries, and state machine transitions

## Setup (Local Development)

1. Clone the repository
2. Create virtual environment: `python -m venv venv`
3. Activate: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Create a `.env` file based on `.env.example`
6. Run migrations: `python manage.py migrate`
7. Create superuser: `python manage.py createsuperuser`
8. Run server: `python manage.py runserver`

## Setup (Docker)

1. Create a `.env` file based on `.env.example`. Set `DB_HOST=db` and `CELERY_BROKER_URL=redis://redis:6379/0`
2. Build and start all services: `docker-compose up --build`
3. Run migrations are applied automatically on startup
4. Create a superuser: `docker-compose exec web python manage.py createsuperuser`
5. API is available at `http://127.0.0.1:8000/`

## API Overview

### Authentication
- `POST /api/accounts/register/` - register as employer or candidate
- `POST /api/accounts/login/` - obtain JWT access/refresh token pair (custom claims: `role`, `username`)
- `POST /api/accounts/login/refresh/` - rotate access token
- `GET /api/accounts/profile/` - retrieve the authenticated user's profile

### Jobs
- `GET /api/jobs/` - list open job postings (public). Supports `?location=`, `?status=`, `?salary_min=`, `?salary_max=`, `?created_after=`, `?search=`, `?ordering=`, and pagination
- `POST /api/jobs/` - create a job posting (employer only)
- `GET /api/jobs/<id>/` - retrieve a single job posting (public)
- `PUT /api/jobs/<id>/` - update a job posting (owning employer only)
- `PATCH /api/jobs/<id>/` - partially update a job posting (owning employer only)
- `DELETE /api/jobs/<id>/` - delete a job posting (owning employer only)

### Applications
- `POST /api/jobs/<id>/apply/` - submit an application, optionally with a resume PDF (candidate only)
- `GET /api/jobs/applications/` - list applications, scoped by role (employers see applications to their jobs, candidates see their own)
- `GET /api/jobs/applications/<id>/` - retrieve a single application
- `PATCH /api/jobs/applications/<id>/status/` - update application status (owning employer only, enforces valid state transitions)
- `PATCH /api/jobs/applications/<id>/resume/` - upload or replace a resume on an existing application (owning candidate only)

## Authentication Flow

All protected endpoints require a JWT access token in the Authorization header:

```
Authorization: Bearer <access_token>
```

1. Register at `POST /api/accounts/register/` with username, email, password, and role
2. Log in at `POST /api/accounts/login/` to receive access and refresh tokens
3. The access token expires in 30 minutes; refresh it at `POST /api/accounts/login/refresh/`
4. The access token payload contains `role` and `username` as custom claims, so downstream consumers don't need a database lookup to know the user's role

## Access Control

Role-based permissions are enforced at the view layer using custom DRF permission classes (`IsEmployer`, `IsCandidate`, `IsJobOwner`, `IsApplicationOwner`, `IsApplicationJobOwner`). Employers can only manage jobs and applications they own. Candidates can only view jobs and manage their own applications. List endpoints are protected by scoped querysets; detail endpoints are protected by object-level permission checks. Application status follows a strict state machine (`applied` → `reviewed` → `accepted`/`rejected`) validated at the serializer level, independent of the view logic.

## Async Tasks

Application status updates trigger an async email notification to the candidate via Celery, using Redis as the message broker. The API response returns immediately; the email is sent by a separate worker process. Failed sends retry automatically up to 3 times with a 60 second delay.

Run the worker locally (outside Docker):

```bash
celery -A core worker --loglevel=info
```

## Running Tests

```bash
# Run full test suite
pytest

# Run with coverage report
pytest --cov=. --cov-report=term-missing

# Run a specific test file
pytest jobs/tests.py -v

# Run a specific test
pytest jobs/tests.py::StatusTransitionTestCase::test_invalid_transition_applied_to_accepted -v
```

Inside Docker:

```bash
docker-compose exec web pytest -v
```

## Architecture Notes

- `settings.AUTH_USER_MODEL` and `get_user_model()` are used everywhere instead of direct imports of the User model, to avoid circular imports and keep the user model swappable.
- Every queryset that serializes a foreign key uses `select_related` to avoid N+1 queries, both in views and in the Django admin.
- The employer/candidate identity on writes is always taken from `request.user`, never from client-supplied input, to prevent identity spoofing.
- File uploads use local filesystem storage in development. In production this would be swapped for cloud object storage (e.g. S3 via `django-storages`) without changing model or view code, since Django's `FileField` abstracts the storage backend.

## Known Limitations / Production Gaps

- Local filesystem storage for resumes does not work across multiple server instances; production needs S3 or equivalent.
- No refresh token blacklisting on logout (`BLACKLIST_AFTER_ROTATION` is off).
- No rate limiting on authentication endpoints.
- Single `settings.py` rather than separated development/production settings.

## Status

Feature-complete: authentication, role-based permissions, job and application CRUD, resume uploads, filtering/search/pagination, async email notifications, Docker Compose deployment, and test suite are all implemented and passing.

## Build Log

- Project setup, DRF, PostgreSQL, JWT configuration ✅
- Custom User model with role field, Job and Application models ✅
- Admin customization, N+1 query optimization, migration internals ✅
- Serializers with validation and state machine enforcement ✅
- JWT authentication endpoints (register, login, refresh) with custom claims (role, username) ✅
- Job CRUD views with method-level permissions, ownership checks, N+1 prevention (`select_related`), and PATCH support ✅
- Custom permissions (`IsEmployer`, `IsCandidate`, `IsJobOwner`), profile endpoint, declarative views ✅
- Application lifecycle (apply, role-based listing, retrieve, status updates with state machine) ✅
- Resume PDF upload with validation, dedicated upload endpoint, and multipart handling ✅
- Filtering, search, and pagination for jobs and applications ✅
- Celery and Redis setup with asynchronous email notifications and retry support ✅
- Docker Compose with four services (web, db, redis, celery) ✅
- Test suite with DRF APIClient covering authentication, jobs, applications, and status transitions ✅
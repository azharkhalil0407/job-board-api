# Job Board API

A production-style backend for a job board platform, built with Django and Django REST Framework. Supports two user roles, employers and candidates, with JWT authentication, role-based access control, full job and application lifecycle management, PDF resume uploads, async email notifications, and a containerized multi-service deployment.

This project is designed to demonstrate real backend engineering practices: clean separation of concerns, query optimization, state machine enforcement, custom permission logic, and asynchronous task handling, not just CRUD scaffolding.

## Tech Stack

- **Framework:** Django 4.2 + Django REST Framework
- **Database:** PostgreSQL
- **Authentication:** JWT (SimpleJWT) with custom token claims
- **Async Tasks:** Celery + Redis (email notifications)
- **Containerization:** Docker Compose (web, PostgreSQL, Redis, Celery worker)
- **Testing:** Pytest + DRF APIClient
- **File Handling:** PDF resume uploads via Django FileField

## Features

- Multi-role authentication (employer / candidate) with role embedded in JWT payload
- Custom DRF permission classes enforcing object-level ownership (employers manage only their own jobs and applicants; candidates manage only their own applications)
- Job listing CRUD with filtering, search, and pagination
- Full application lifecycle with enforced status transitions (`applied → reviewed → accepted/rejected`), validated at the serializer level as a state machine, not left to client trust
- Resume PDF upload tied to each application
- Async email notifications on application status changes via Celery and Redis, decoupled from the request/response cycle
- N+1 query prevention using `select_related` / `prefetch_related` across views and admin
- Dockerized for consistent local and deployment environments

## Setup (Local Development)

1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate it: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Create a `.env` file (see `.env.example`) with your database credentials and secret key
6. Run migrations: `python manage.py migrate`
7. Create a superuser: `python manage.py createsuperuser`
8. Run the server: `python manage.py runserver`

## Setup (Docker)

```bash
docker-compose up --build
```

Spins up four services: the Django app, PostgreSQL, Redis, and a Celery worker for async email processing.

## API Overview

### Authentication
- `POST /api/accounts/register/` — register as employer or candidate
- `POST /api/accounts/login/` — obtain JWT access/refresh token pair (includes role and username as custom claims)
- `POST /api/accounts/login/refresh/` — rotate access token

### Jobs
- `GET /api/jobs/` — list job postings, filterable by location, status, and salary range, paginated
- `POST /api/jobs/` — create a job posting (employer only)
- `GET /api/jobs/<id>/` — retrieve a single job posting
- `PUT /api/jobs/<id>/` — update a job posting (owning employer only)
- `DELETE /api/jobs/<id>/` — delete a job posting (owning employer only)

### Applications
- `POST /api/jobs/<id>/apply/` — submit an application with resume PDF (candidate only)
- `GET /api/applications/` — list applications, scoped to the authenticated user's role
- `PATCH /api/applications/<id>/status/` — update application status (owning employer only, enforces valid transitions)

## Access Control

Role-based permissions are enforced at the view layer using custom DRF permission classes, not just filtered querysets. Employers can only act on jobs and applications they own. Candidates can only view open jobs and manage their own applications. Application status changes follow a strict state machine validated at the serializer level, preventing invalid transitions like `accepted → applied`.

## Architecture Notes

- Custom user model (`accounts.User`) extending `AbstractUser` with a `role` field, configured before the first migration to avoid schema conflicts
- Serializers separated by purpose (`RegisterSerializer`, `UserSerializer`, status-update serializers) rather than one serializer trying to handle every case
- Admin panel configured as a real internal tool with inline editing, computed columns, and `list_select_related` to avoid N+1 queries in list views
- Async email sending offloaded to Celery so application status updates don't block the request/response cycle

## Build Log

- [x] Day 1: Project setup, DRF, PostgreSQL, JWT config
- [x] Day 2: Custom User model with role field, Job and Application models
- [x] Day 3: Admin customization, N+1 query optimization, migration internals
- [x] Day 4: Serializers with validation and state machine enforcement
- [x] Day 5: JWT auth endpoints (register, login, refresh) with custom claims (role, username)
- [x] Day 6: Job CRUD views with method-level permissions, ownership checks, N+1 prevention (select_related), and PATCH support
- [x] Day 7: Custom permissions (IsEmployer, IsCandidate, IsJobOwner), profile endpoint, declarative views
- [ ] Day 8: Application lifecycle endpoints
- [ ] Day 9: Resume PDF upload
- [ ] Day 10: Filtering, search, pagination
- [ ] Day 11: Celery + Redis async email
- [ ] Day 12: Docker Compose (4 services)
- [ ] Day 13: Test suite
- [ ] Day 14: Polish, final docs
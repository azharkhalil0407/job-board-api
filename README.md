# Job Board API

Django + DRF backend for a job board platform with multi-role system (employers/candidates), JWT auth, job listings, applications with PDF uploads, async email notifications, and Docker Compose.

## Tech Stack

- Django 4.2 + Django REST Framework
- PostgreSQL
- JWT Authentication (SimpleJWT)
- Celery + Redis (async tasks)
- Docker Compose (4 services)
- Pytest (testing)

## Setup (Local Development)

1. Clone the repository
2. Create virtual environment: `python -m venv venv`
3. Activate: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Create `.env` file (see `.env.example`)
6. Run migrations: `python manage.py migrate`
7. Create superuser: `python manage.py createsuperuser`
8. Run server: `python manage.py runserver`

## API Endpoints (to be implemented)

- `/api/accounts/` - registration, login, profile
- `/api/jobs/` - job listings CRUD, filtering, pagination
- `/api/jobs/<id>/apply/` - submit application with PDF
- `/api/applications/` - manage application status

## Progress

- [x] Day 1: Django project setup, DRF, PostgreSQL, JWT config
- [x] Day 2: Custom User model (role), Job and Application models with unique constraint and admin
- [x] Day 3: Admin customization (inline applications, list_select_related N+1 fix, Debug Toolbar, migration internals)
- [x] Day 4: DRF serializers (RegisterSerializer, UserSerializer, JobSerializer, ApplicationSerializer, ApplicationStatusUpdateSerializer with status transitions)
- [ ] Day 5-14: JWT auth endpoints, views, permissions, Celery, Docker, testing

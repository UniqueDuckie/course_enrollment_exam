# Course Enrollment Platform API

A secure, database-backed RESTful API built with FastAPI for managing course enrollments. Features JWT authentication, role-based access control (student / admin), PostgreSQL with Alembic migrations, and a full pytest suite.

## Tech stack

- **FastAPI** — web framework
- **SQLAlchemy 2.x** — ORM
- **PostgreSQL** — production database (SQLite is used for the test suite)
- **Alembic** — migrations
- **PyJWT + bcrypt** — auth tokens and password hashing
- **pytest + httpx** — automated tests

## Project structure

```
course-enrollment-platform-api/
├── app/
│   ├── main.py              # FastAPI app + router registration
│   ├── config.py            # Settings (env-driven)
│   ├── database.py          # Engine, Session, Base, get_db
│   ├── models.py            # SQLAlchemy models
│   ├── security.py          # Password hashing + JWT
│   ├── dependencies.py      # get_current_user, require_admin, require_student
│   ├── schemas/             # Pydantic request/response models
│   ├── repository/          # DB access layer
│   ├── services/            # Business logic
│   └── routers/             # auth, courses, enrollments, admin
├── alembic/                 # Migration environment + versions
├── tests/                   # pytest suite (one file per router)
├── scripts/                 # ERD-to-SQL helpers (design artefacts)
├── erd.dbml                 # ERD source for dbdiagram.io
├── alembic.ini
├── requirements.txt
├── .env.example
└── README.md
```

## Setup

### 1. Clone

```bash
git clone https://github.com/kolawoluu/course-enrollment-platform-api.git
cd course-enrollment-platform-api
```

### 2. Create a virtual environment and install dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure environment

```bash
cp .env.example .env
# Edit .env: set DATABASE_URL and a strong JWT_SECRET
```

For local development without PostgreSQL you can leave the default `DATABASE_URL=sqlite:///./enrollment.db`.

### 4. Run migrations

```bash
alembic upgrade head
```

### 5. Start the API

```bash
uvicorn app.main:app --reload
```

Interactive docs are at <http://localhost:8000/docs>.

## Running tests

The test suite uses an in-memory SQLite database — no external services required.

```bash
pytest
```

For more output:

```bash
pytest -v
```

## Endpoints

### Authentication

| Method | Path | Auth | Description |
| --- | --- | --- | --- |
| POST | `/auth/register` | public | Register a new user |
| POST | `/auth/login` | public | Exchange credentials for a JWT (OAuth2 password form) |
| GET | `/auth/me` | authenticated | Current user profile |

### Courses

| Method | Path | Auth | Description |
| --- | --- | --- | --- |
| GET | `/courses` | public | List active courses |
| GET | `/courses/{id}` | public | Retrieve a course |
| POST | `/courses` | admin | Create a course |
| PUT | `/courses/{id}` | admin | Update a course |
| PATCH | `/courses/{id}/activate` | admin | Activate a course |
| PATCH | `/courses/{id}/deactivate` | admin | Deactivate a course |

### Enrollment (student)

| Method | Path | Auth | Description |
| --- | --- | --- | --- |
| POST | `/enrollments` | student | Enroll in a course |
| DELETE | `/enrollments/{course_id}` | student | Deregister from a course |

### Courses (admin, delete)

| Method | Path | Auth | Description |
| --- | --- | --- | --- |
| DELETE | `/courses/{id}` | admin | Soft-delete a course |

### Admin oversight

| Method | Path | Auth | Description |
| --- | --- | --- | --- |
| GET | `/admin/enrollments` | admin | List all enrollments (supports `skip`, `limit`, `include_deleted`) |
| GET | `/admin/courses/{id}/enrollments` | admin | List enrollments for a course |
| DELETE | `/admin/enrollments/{id}` | admin | Force-remove (soft-delete) an enrollment |
| GET | `/admin/audit-logs` | admin | Read the enrollment audit log |

### Bonus extensions

- **Pagination** — `skip` and `limit` query params on every list endpoint (`/courses`, `/admin/enrollments`, `/admin/courses/{id}/enrollments`, `/admin/audit-logs`).
- **Soft deletes** — `DELETE /courses/{id}` and enrollment deletions set `deleted_at` instead of removing rows. Re-enrolling after deregistration restores the original row.
- **Audit logs** — every enroll / deregister / admin-remove writes an entry to `enrollment_audit_logs` with the actor's id and role.
- **Rate limiting** — `slowapi` middleware caps `/auth/register` at 5/min and `/auth/login` at 10/min per IP (configurable via env).

## Business rules enforced

- Email must be unique and well-formed.
- Passwords are hashed with bcrypt.
- Inactive users cannot authenticate.
- Course `code` is unique; `capacity` must be > 0.
- Only students can enroll or deregister themselves.
- A student cannot enroll in the same course twice.
- Enrollment is rejected if the course is inactive or at capacity.
- All admin oversight endpoints require the `admin` role.

## Status codes used

- `200 OK` — successful read / update
- `201 Created` — successful resource creation
- `204 No Content` — successful delete
- `400 Bad Request` — business-rule violation (e.g. course full, inactive course)
- `401 Unauthorized` — missing or invalid token
- `403 Forbidden` — wrong role
- `404 Not Found` — resource missing
- `409 Conflict` — uniqueness violation (duplicate email, course code, enrollment)
- `422 Unprocessable Entity` — request body fails validation

## Database schema (ERD)

The ERD source is in [`erd.dbml`](erd.dbml). Paste it into [dbdiagram.io](https://dbdiagram.io) to render.

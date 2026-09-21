# FETIN Triage — Backend

<p align="center">
  <img src="https://img.shields.io/badge/FastAPI-0.136-009688?logo=fastapi&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white" alt="Python 3.11+" />
  <img src="https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql&logoColor=white" alt="PostgreSQL" />
  <img src="https://img.shields.io/badge/AI-Google_Gemini-4285F4?logo=google" alt="Google Gemini" />
  <img src="https://github.com/cauahenriquereis/fetin-project-backend/actions/workflows/python-app.yml/badge.svg" alt="CI status" />
  <img src="https://img.shields.io/badge/License-MIT-green" alt="MIT License" />
</p>

<p align="center">
  <strong>AI-assisted hospital triage API.</strong><br />
  Receives symptoms and vital signs, classifies urgency, and manages a priority-ordered patient queue.
</p>

<p align="center">
  <a href="https://fetin-project-backend-production.up.railway.app/docs">Swagger UI</a> ·
  <a href="https://fetin-triagem-ia.vercel.app/">Live application</a> ·
  <a href="https://github.com/cauahenriquereis/fetin-project-frontend">Frontend repository</a>
</p>

> **Project status:** Functional proof of concept deployed to production. This project is intended for demonstration and academic purposes and must not be used as a substitute for professional medical evaluation.

## About the project

FETIN Triage is a FastAPI service that supports a complete triage workflow. It validates patient data, uses Google Gemini to help classify urgency from symptoms and vital signs, stores the patient state in PostgreSQL, and exposes the queue to the medical team through authenticated endpoints.

### Workflow

```text
POST /patients/register
          ↓
PATCH /patients/{id}/vitals
          ↓
Google Gemini classifies urgency
          ↓
Patient enters the priority queue
          ↓
Doctor updates status through the dashboard
```

## Features

- Patient registration and symptom intake
- AI-assisted urgency classification using symptoms and vital signs
- Vital-sign recording for temperature, blood pressure, SpO₂, and heart rate
- Priority queue ordered by urgency and registration time
- JWT authentication for doctor operations
- Email notifications when queue status changes
- Validation for implausible or non-medical symptom descriptions
- Versioned database migrations with Alembic
- Interactive OpenAPI documentation through Swagger UI

## Architecture

```text
Next.js frontend
       |
       v
FastAPI backend ─────> Google Gemini
       |
       v
PostgreSQL (Neon)
```

## Technology

- **API:** FastAPI and Uvicorn
- **Language:** Python 3.11+
- **Database:** PostgreSQL
- **ORM and migrations:** SQLAlchemy and Alembic
- **AI:** Google Gemini API
- **Authentication:** JWT
- **Email:** Resend API
- **Testing:** pytest, pytest-asyncio, and httpx
- **Quality and CI:** Flake8 and GitHub Actions
- **Deployment:** Railway

## Quick start

### Requirements

- Python 3.11 or newer
- PostgreSQL database, such as a [Neon](https://neon.tech) instance
- Google Gemini API key
- Resend API key

### Installation

```bash
git clone https://github.com/cauahenriquereis/fetin-project-backend.git
cd fetin-project-backend
python -m venv .venv

# Linux/macOS
source .venv/bin/activate

# Windows PowerShell
# .venv\\Scripts\\Activate.ps1

python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Environment variables

Create `.env` in the project root:

```env
DATABASE_URL=postgresql://user:password@host/dbname
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
DOCTOR_PASSWORD=your-doctor-dashboard-password
GEMINI_API_KEY=your-gemini-api-key
RESEND_API_KEY=your-resend-api-key
```

The application validates these variables during startup. Never commit `.env` or real credentials.

### Migrations and local server

```bash
alembic upgrade head
uvicorn main:app --reload
```

The API runs at [http://localhost:8000](http://localhost:8000). Interactive documentation is available at [http://localhost:8000/docs](http://localhost:8000/docs).

## API overview

| Method | Endpoint | Description |
| --- | --- | --- |
| `POST` | `/patients/register` | Register a patient |
| `GET` | `/patients/{id}` | Retrieve a patient |
| `PATCH` | `/patients/{id}/vitals` | Submit vital signs and classify urgency |
| `GET` | `/queue/status` | Retrieve the priority queue |
| `GET` | `/queue/status/{id}` | Retrieve a patient's queue status |
| `PATCH` | `/queue/{id}` | Update patient status |
| `DELETE` | `/queue/{id}` | Remove a patient from the queue |
| `POST` | `/doctor/login` | Authenticate a doctor and issue a JWT |
| `...` | `/doctor/...` | Doctor dashboard operations |

See the [production Swagger documentation](https://fetin-project-backend-production.up.railway.app/docs) for complete schemas and endpoints.

## Testing and continuous integration

Run the test suite locally:

```bash
pytest
```

The tests cover patient, queue, and doctor routes, authentication, token handling, and Gemini and email services. External dependencies are mocked where appropriate.

The [GitHub Actions workflow](.github/workflows/python-app.yml) runs automatically on pushes to `main` and pull requests targeting `main`. It:

- installs dependencies with Python 3.11;
- runs Flake8 checks; and
- executes pytest against a PostgreSQL 16 service container.

## Project structure

```text
.
├── main.py                 # FastAPI application entry point
├── config.py               # Environment variables and application config
├── models.py               # SQLAlchemy models
├── schemas.py              # Pydantic schemas
├── dependencies.py         # Shared FastAPI dependencies
├── patients_routes.py      # Patient registration and vital signs
├── queue_routes.py         # Queue operations
├── doctor_routes.py        # Authentication and doctor operations
├── gemini_service.py       # AI classification service
├── email_service.py        # Email notification service
├── alembic/                # Database migrations
├── alembic.ini
├── pytest.ini
├── requirements.txt
└── tests/                  # Automated tests
```

## Deployment

The production API is deployed on [Railway](https://railway.app), with automatic deployment from the `main` branch.

CI and deployment are already configured:

- **GitHub Actions** validates linting and tests.
- **Railway** publishes the API and handles production deployment.

## Roadmap

- Optional Bluetooth integration with vital-sign devices, currently out of scope

## License

This project is distributed under the [MIT License](LICENSE).

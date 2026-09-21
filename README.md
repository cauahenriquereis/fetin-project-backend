# FETIN Triage — Backend

[![CI](https://github.com/cauahenriquereis/fetin-project-backend/actions/workflows/python-app.yml/badge.svg)](https://github.com/cauahenriquereis/fetin-project-backend/actions/workflows/python-app.yml)

FastAPI backend for an AI-assisted hospital triage system. The API receives patient symptoms and vital signs, classifies urgency with Google Gemini, and manages a priority-ordered queue for the medical team.

The frontend is maintained in a separate repository: [fetin-project-frontend](https://github.com/cauahenriquereis/fetin-project-frontend).

## Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture and flow](#architecture-and-flow)
- [Tech stack](#tech-stack)
- [Getting started](#getting-started)
- [API overview](#api-overview)
- [Testing and code quality](#testing-and-code-quality)
- [Project structure](#project-structure)
- [Deployment](#deployment)
- [Roadmap](#roadmap)

## Overview

- **Production API:** [Railway](https://fetin-project-backend-production.up.railway.app)
- **Interactive API documentation:** [Swagger UI](https://fetin-project-backend-production.up.railway.app/docs)
- **Frontend application:** [fetin-triagem-ia.vercel.app](https://fetin-triagem-ia.vercel.app/)

> The doctor dashboard at `/medico` is password-protected. Contact the project owner if you need demo credentials.

## Features

- Patient registration and symptom intake
- AI-based urgency classification using symptoms and vital signs
- Vital-sign recording for temperature, blood pressure, SpO₂, and heart rate
- Priority queue ordered by urgency and registration time
- JWT authentication for doctor dashboard endpoints
- Email notifications when queue status changes
- Input validation for implausible or non-medical symptom descriptions
- Database migrations managed with Alembic

## Architecture and flow

```text
Next.js frontend
       |
       v
FastAPI backend ─────> Google Gemini (urgency classification)
       |
       v
PostgreSQL (Neon)
```

1. The patient submits symptoms through `POST /patients/register`.
2. A nurse submits vital signs through `PATCH /patients/{id}/vitals`.
3. The backend classifies urgency and places the patient in the priority queue.
4. The doctor dashboard reads the queue and updates patient status.

## Tech stack

- **Framework:** FastAPI
- **Language:** Python 3.11+
- **Database:** PostgreSQL (Neon in production)
- **ORM and migrations:** SQLAlchemy and Alembic
- **AI:** Google Gemini API
- **Authentication:** JWT
- **Email:** Resend API
- **Testing:** pytest, pytest-asyncio, and httpx
- **Deployment:** Railway
- **CI:** GitHub Actions

## Getting started

### Prerequisites

- Python 3.11 or newer
- PostgreSQL database, such as a free [Neon](https://neon.tech) instance
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

Create a `.env` file in the project root. The application validates these variables during startup:

```env
DATABASE_URL=postgresql://user:password@host/dbname
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
DOCTOR_PASSWORD=your-doctor-dashboard-password
GEMINI_API_KEY=your-gemini-api-key
RESEND_API_KEY=your-resend-api-key
```

Never commit `.env` or real credentials to the repository.

### Database migrations

```bash
alembic upgrade head
```

### Run locally

```bash
uvicorn main:app --reload
```

The API is available at `http://localhost:8000`. Open [`http://localhost:8000/docs`](http://localhost:8000/docs) for the interactive Swagger documentation.

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

See the [Swagger documentation](https://fetin-project-backend-production.up.railway.app/docs) for complete request and response schemas.

## Testing and code quality

Run the test suite locally with:

```bash
pytest
```

The test suite covers patient, queue, and doctor routes, authentication, token handling, and the Gemini and email services. External services are mocked where appropriate.

Every push to `main` and pull request targeting `main` is checked by [GitHub Actions](.github/workflows/python-app.yml). The workflow runs Flake8 and the pytest suite using Python 3.11 and a PostgreSQL service container.

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

The production API is deployed on [Railway](https://railway.app), with automatic deployment on pushes to `main`.

CI and deployment are separate concerns: GitHub Actions validates linting and tests, while Railway publishes the application.

## Roadmap

- Optional Bluetooth integration with vital-sign devices (thermometer, blood pressure monitor, and pulse oximeter), currently out of scope

## License

This project is available under the [MIT License](LICENSE).

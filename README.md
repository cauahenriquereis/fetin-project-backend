<img width="1919" height="997" alt="image" src="https://github.com/user-attachments/assets/f86302ce-a980-4fa1-91cd-1b18491a31dd" /># FETIN Triage - Backend

An AI-assisted hospital triage system that receives patient symptoms and vital signs, classifies urgency using generative AI, and manages a priority-ordered patient queue.

This repository contains the backend API. The frontend lives in a separate repository.

## Live Demo

- 🌐 **App:** https://fetin-triagem-ia.vercel.app/
- 📑 **API docs (Swagger):** https://fetin-project-backend-production.up.railway.app/docs
- 🖥️ **Frontend repository:** https://github.com/cauahenriquereis/fetin-project-frontend

### Doctor dashboard

> **Note:** The doctor dashboard (`/medico`) is password-protected. Feel free to reach out if you'd like demo credentials to explore it.

**Login screen:**

<img width="1919" height="997" alt="Doctor login screen" src="https://github.com/user-attachments/assets/41b4b7af-3681-4a4f-ae41-301c773dfbb5" />

**Dashboard view:**

<img width="1915" height="998" alt="Doctor dashboard" src="https://github.com/user-attachments/assets/0cef48d0-fb32-42be-8742-814a95a7c7bf" />


## Table of Contents

- [Features](#features)
- [Live Demo](#live-demo)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Environment Variables](#environment-variables)
  - [Database Setup](#database-setup)
  - [Running the Server](#running-the-server)
- [API Overview](#api-overview)
- [Testing](#testing)
- [Project Structure](#project-structure)
- [Deployment](#deployment)
- [Roadmap](#roadmap)

## Features

- Patient registration and symptom intake
- AI-based urgency classification (Google Gemini) combining reported symptoms and vital signs
- Nurse-facing endpoint for recording vital signs (temperature, blood pressure, SpO2, heart rate)
- Priority queue management with automatic ordering by urgency
- JWT-authenticated doctor dashboard endpoints
- Email notifications on queue status updates
- Input validation for symptom plausibility (flags non-medical/invalid input via AI)

## Tech Stack

- **Framework:** FastAPI
- **Database:** PostgreSQL (hosted on Neon)
- **ORM / Migrations:** SQLAlchemy + Alembic
- **AI:** Google Gemini API
- **Auth:** JWT
- **Email:** Resend API
- **Testing:** pytest, pytest-asyncio, httpx
- **Hosting:** Railway

## Architecture

```
Client (Next.js frontend)
        |
        v
   FastAPI backend  ---->  Gemini AI (urgency classification)
        |
        v
  PostgreSQL (Neon)
```

The typical patient flow:

1. Patient fills out the intake form → `POST /patients/register` (status: `aguardando_sinais_vitais`)
2. Nurse records vital signs → `PATCH /patients/{id}/vitals` (triggers AI classification, assigns priority)
3. Patient enters the queue, ordered by urgency and registration time
4. Doctor dashboard consumes the queue and updates patient status as they are seen

## Getting Started

### Prerequisites

- Python 3.11+
- A PostgreSQL database (e.g. a free [Neon](https://neon.tech) instance)
- A Google Gemini API key

### Installation

```bash
git clone <repository-url>
cd <repository-folder>
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file in the project root:

```env
DATABASE_URL=postgresql://user:password@host/dbname
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
DOCTOR_PASSWORD=your-doctor-dashboard-password
GEMINI_API_KEY=your-gemini-api-key
RESEND_API_KEY=your-resend-api-key
```

### Database Setup

Run migrations with Alembic:

```bash
alembic upgrade head
```

### Running the Server

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`, with interactive docs at `http://localhost:8000/docs`.

## API Overview

| Method | Endpoint                        | Description                                  |
|--------|----------------------------------|-----------------------------------------------|
| POST   | `/patients/register`            | Register a new patient                        |
| GET    | `/patients/{id}`                | Get a patient by ID                           |
| PATCH  | `/patients/{id}/vitals`         | Submit vital signs, triggers AI classification|
| GET    | `/queue/status`                 | Get the current queue, ordered by priority    |
| GET    | `/queue/status/{id}`            | Get a specific patient's position/status      |
| PATCH  | `/queue/{id}`                   | Update a patient's status                     |
| DELETE | `/queue/{id}`                   | Remove a patient from the queue               |
| POST   | `/doctor/login`                 | Doctor authentication (issues JWT)            |
| ...    | `/doctor/...`                   | Doctor dashboard actions (see `doctor_routes.py`) |

Full request/response schemas are available via the auto-generated Swagger docs at `/docs`.

## Testing

The test suite covers all routers (`patients`, `queue`), authentication dependencies, and the Gemini/email services, using mocked sessions and mocked external calls (no real DB or AI calls in tests).

```bash
pytest
```

## Project Structure

```
.
├── main.py
├── config.py
├── models.py
├── schemas.py
├── dependencies.py
├── patients_routes.py
├── queue_routes.py
├── doctor_routes.py
├── gemini_service.py
├── email_service.py
├── alembic/
├── alembic.ini
├── pytest.ini
├── requirements.txt
└── tests/
    ├── conftest.py
    ├── test_patients_routes.py
    ├── test_queue_routes.py
    ├── test_gemini_service.py
    ├── test_email_service.py
    ├── test_token_generator.py
    └── test_verify_token.py
```

## Deployment

The backend is deployed on [Railway](https://railway.app), connected to the GitHub repository for automatic deploys on push to the main branch.

## Roadmap

- CI pipeline to run the test suite automatically on push/PR (GitHub Actions)
- Optional Bluetooth integration with vital-sign measurement devices (thermometer, blood pressure monitor, pulse oximeter) — currently out of scope

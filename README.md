# Credify

A production-ready REST API for customer onboarding and loan underwriting. It supports customer registration, loan eligibility checks, loan creation, and viewing loans. All identifiers (customer_id, loan_id) are UUIDs.

- Framework: Django 5 + Django REST Framework
- DB: PostgreSQL (Dockerized)
- Python: 3.13 (container)
- IDs: UUIDs
- EMI calculation: Compound interest (monthly)

## Features

- Register customers with approved credit limits
- Compute credit score and return corrected interest when needed
- Create loans if eligible and persist them
- View a loan by ID and list all loans for a customer
- Robust validation and error handling with proper HTTP status codes

## Quick Start

### Prerequisites
- Docker and Docker Compose (recommended)
- Or: Python 3.12+, PostgreSQL 14+ (for local runs)

### Environment
Create a `.env` in the project root (used by docker-compose and settings):

```env
POSTGRES_DB=alemno_db
POSTGRES_USER=alemno
POSTGRES_PASSWORD=supersecret
```

### Run with Docker
```powershell
docker compose up --build
```
- API base URL: `http://localhost:8000`

### Run locally (without Docker) on Windows (PowerShell)
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r src\requirements.txt

$env:POSTGRES_DB="alemno_db"
$env:POSTGRES_USER="alemno"
$env:POSTGRES_PASSWORD="supersecret"
$env:POSTGRES_HOST="localhost"
$env:POSTGRES_PORT="5432"

cd src
python manage.py migrate
python manage.py runserver 8000
```

## Project Structure

```
src/
    alemno/                # Django project settings/urls/wsgi
    core/                  # App: models, serializers, views, urls
    services/              # Business logic (eligibility, scoring, creation)
    entrypoint.sh          # Container entrypoint running migrations + server
    manage.py
Dockerfile
docker-compose.yml
```

## Data Model (simplified)

- Customer
    - customer_id (UUID, PK)
    - first_name, last_name, age, phone_number
    - monthly_income (Decimal)
    - approved_limit (Decimal): 36 × monthly_income, rounded to nearest lakh (100,000)

- Loan
    - loan_id (UUID, PK)
    - customer (FK → Customer)
    - loan_amount (Decimal)
    - tenure (months, int)
    - interest_rate (annual %, Decimal)
    - monthly_payment (Decimal)
    - emis_paid_on_time (int)
    - date_of_approval, end_date (dates)

## API Overview

Base URL: `http://localhost:8000`

### 1) Register a customer
`POST /register`

Request
```json
{
    "first_name": "John",
    "last_name": "Doe",
    "age": 30,
    "monthly_income": 50000,
    "phone_number": "9876543210"
}
```

Response 201 Created
```json
{
    "customer_id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "John Doe",
    "age": 30,
    "monthly_income": 50000.0,
    "approved_limit": 1800000.0,
    "phone_number": "9876543210"
}
```

### 2) Check loan eligibility
`POST /check-eligibility`

Request
```json
{
    "customer_id": "550e8400-e29b-41d4-a716-446655440000",
    "loan_amount": 500000,
    "interest_rate": 10.5,
    "tenure": 36
}
```

Response 200 OK (example)
```json
{
    "customer_id": "550e8400-e29b-41d4-a716-446655440000",
    "approval": true,
    "interest_rate": 10.5,
    "corrected_interest_rate": 10.5,
    "tenure": 36,
    "monthly_installment": 16134.33
}
```

### 3) Create a loan
`POST /create-loan`

Request
```json
{
    "customer_id": "550e8400-e29b-41d4-a716-446655440000",
    "loan_amount": 500000,
    "interest_rate": 10.5,
    "tenure": 36
}
```

Response 201 Created (approved)
```json
{
    "loan_id": "660e8400-e29b-41d4-a716-446655440001",
    "customer_id": "550e8400-e29b-41d4-a716-446655440000",
    "loan_approved": true,
    "message": "Loan approved",
    "monthly_installment": 16134.33
}
```

### 4) View a loan by ID
`GET /view-loan/{loan_id}`

Response 200 OK (example)
```json
{
    "loan_id": "660e8400-e29b-41d4-a716-446655440001",
    "customer": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "first_name": "John",
        "last_name": "Doe",
        "phone_number": "9876543210",
        "age": 30
    },
    "loan_amount": 500000.0,
    "interest_rate": 10.5,
    "monthly_installment": 16134.33,
    "tenure": 36
}
```

### 5) View all loans for a customer
`GET /view-loans/{customer_id}`

Response 200 OK (list)
```json
[
    {
        "loan_id": "660e8400-e29b-41d4-a716-446655440001",
        "loan_amount": 500000.0,
        "interest_rate": 10.5,
        "monthly_installment": 16134.33,
        "repayments_left": 36
    }
]
```

## Financial Notes

- EMI uses monthly compounding: r = (annual_rate/100)/12. Uses Decimal internally.
- approved_limit = 36 × monthly_income, rounded to nearest lakh (100,000).

## Troubleshooting

- Postgres not ready: docker compose waits on DB healthcheck; if flapping, run `docker compose down -v && docker compose up --build`.
- DisallowedHost: ensure `ALLOWED_HOSTS` in settings includes your host.
- Migrations on start: container entrypoint runs `python manage.py migrate` automatically.
- Port conflict: change `"8000:8000"` in docker-compose.

## Production Tips

- Set strong `SECRET_KEY`, disable `DEBUG`, set `ALLOWED_HOSTS` properly.
- Run behind a reverse proxy (Nginx) and serve via Gunicorn/Uvicorn.
- Use managed Postgres, enable backups, monitor connections.
- Apply migrations in CI/CD before deploy.
- Configure structured logging to stdout or a sink.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for changes
4. Open a pull request with context

## License

Add a license file (e.g., MIT) at the repo root.

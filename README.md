<p align="center">
  <img src="assets/credify-mark.svg" alt="Credify ledger mark" width="112">
</p>

<h1 align="center">Credify</h1>

<p align="center">A Django REST API for customer records, loan eligibility checks, and loan records.</p>

<div align="center">

[Overview](#overview) · [Run locally](#run-locally) · [API](#api) · [Data model](#data-model) · [Project notes](#project-notes)

</div>

## Overview

Credify stores customers and loans in PostgreSQL. Its API registers customers, checks loan eligibility, creates loans, and returns loan records. Customer and loan records use UUID identifiers.

The project uses Django and Django REST Framework. The container image uses Python 3.13.1; the project metadata requires Python 3.12 or newer.

## Run locally

You need Docker Compose. Before startup, configure the root `.env` file with values for `POSTGRES_DB`, `POSTGRES_USER`, and `POSTGRES_PASSWORD`. The compose file passes these values to PostgreSQL. Keep the file private.

From the repository root, start the API and database:

```sh
docker compose up --build
```

The API listens at `http://localhost:8000`. The root route returns API information. Stop the services with `Ctrl+C`; run `docker compose down` to remove the containers. The database volume remains unless you remove it.

For a local Python setup, install the packages in `src/requirements.txt`, provide a reachable PostgreSQL database through `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST`, and `POSTGRES_PORT`, then run migrations and Django from `src/`. The included container setup is the shortest documented path.

## API

Routes are defined in [`src/core/urls.py`](src/core/urls.py). They do not use a trailing slash.

| Method | Route | Purpose |
| --- | --- | --- |
| `POST` | `/register` | Create a customer from a name, age, monthly income, and phone number. The API calculates an approved limit. |
| `POST` | `/check-eligibility` | Check a loan request for an existing customer. Send `customer_id`, `loan_amount`, `interest_rate`, and `tenure`. |
| `POST` | `/create-loan` | Evaluate and, when approved, create a loan for an existing customer. |
| `GET` | `/view-loan/{loan_id}` | Return a loan and selected customer fields. |
| `GET` | `/view-loans/{customer_id}` | List loans for a customer, including remaining repayments. |

For example, register a customer with:

```sh
curl -X POST http://localhost:8000/register \
  -H 'Content-Type: application/json' \
  -d '{"first_name":"Ada","last_name":"Lovelace","age":30,"monthly_income":50000,"phone_number":"9876543210"}'
```

Eligibility and loan creation accept a UUID customer ID, a positive loan amount, an annual interest rate, and a tenure in months. The serializers limit interest rates to 100 percent and tenure to 600 months. See [`src/core/serializers.py`](src/core/serializers.py) for request validation and response fields.

## Data model

- **Customer:** UUID, name, age, phone number, monthly income, and approved limit. The model sets the limit to 36 times monthly income, rounded to the nearest 100,000 when no limit is supplied.
- **Loan:** UUID, customer reference, amount, annual interest rate, tenure, monthly payment, and repayment dates. Remaining repayments are calculated from the tenure and the number of EMIs paid on time.

The API’s eligibility and installment logic is implemented in [`src/core/views.py`](src/core/views.py). Review it before using these calculations for financial decisions.

## Project notes

- Compose maps the API to host port `8000` and runs PostgreSQL as a separate service.
- The app container runs database migrations when it starts.
- The repository does not include a root license file.

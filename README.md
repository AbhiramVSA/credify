# Alemno Backend API

A Django-based Credit Approval System with APIs for customer registration, loan applications, and loan management.

## Features

- Customer Registration with automatic credit limit calculation
- Comprehensive input validation and error handling
- PostgreSQL database with Docker support
- RESTful API design with proper HTTP status codes

## API Endpoints

### POST /register

Register a new customer with automatic approved credit limit calculation.

**Request Body:**
```json
{
    "first_name": "John",
    "last_name": "Doe", 
    "age": 30,
    "monthly_income": 50000,
    "phone_number": "9876543210"
}
```

**Response (201 Created):**
```json
{
    "customer_id": 1,
    "name": "John Doe",
    "age": 30,
    "monthly_income": "50000.00",
    "approved_limit": "1800000.00",
    "phone_number": "9876543210"
}
```

**Credit Limit Calculation:**
- `approved_limit = 36 * monthly_income` (rounded to nearest lakh)
- Example: ₹50,000 monthly income → ₹18,00,000 approved limit

**Validation Rules:**
- `first_name`: Required, max 64 characters
- `last_name`: Required, max 64 characters  
- `age`: Required, integer between 18-120
- `monthly_income`: Required, positive decimal
- `phone_number`: Required, 7-15 digits only

**Error Responses:**

*400 Bad Request* - Validation errors:
```json
{
    "error": "Validation failed",
    "details": {
        "age": ["Customer must be at least 18 years old."],
        "phone_number": ["Phone number must be between 7 and 15 digits."]
    }
}
```

*409 Conflict* - Duplicate customer:
```json
{
    "error": "Customer registration failed", 
    "details": "A customer with this information may already exist"
}
```

*500 Internal Server Error* - Server errors:
```json
{
    "error": "Internal server error",
    "details": "An unexpected error occurred during registration"
}
```

## Setup and Installation

### Using Docker (Recommended)

1. Clone the repository:
```bash
git clone <repo-url>
cd alemno-backend
```

2. Create environment file:
```bash
# Create .env file in root directory
POSTGRES_DB=alemno_db
POSTGRES_USER=alemno
POSTGRES_PASSWORD=supersecret
```

3. Build and run with Docker:
```bash
docker-compose up --build
```

The API will be available at `http://localhost:8000`

### Manual Setup

1. Install dependencies:
```bash
pip install -r src/requirements.txt
```

2. Set up PostgreSQL database and update `src/alemno/settings.py`

3. Run migrations:
```bash
cd src
python manage.py migrate
```

4. Start development server:
```bash
python manage.py runserver
```

## Testing the API

Use the provided test script:
```bash
python test_api.py
```

Or test manually with curl:
```bash
curl -X POST http://localhost:8000/register \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "age": 30,
    "monthly_income": 50000,
    "phone_number": "9876543210"
  }'
```

## Database Schema

### Customer Model
- `customer_id`: Auto-generated primary key
- `first_name`: Customer's first name
- `last_name`: Customer's last name  
- `age`: Customer's age (18-120)
- `phone_number`: Phone number (7-15 digits)
- `monthly_income`: Monthly income amount
- `approved_limit`: Auto-calculated credit limit
- `created`: Registration timestamp

## Project Structure

```
alemno-backend/
├── src/
│   ├── alemno/          # Django project settings
│   ├── core/            # Main application
│   │   ├── models.py    # Customer and Loan models
│   │   ├── views.py     # API endpoints
│   │   ├── serializers.py # API serializers
│   │   └── urls.py      # URL routing
│   └── manage.py
├── docker-compose.yml   # Docker configuration
├── Dockerfile
└── README.md
```

## Technologies Used

- **Django 5.2.6**: Web framework
- **Django REST Framework**: API development
- **PostgreSQL**: Database
- **Docker**: Containerization
- **Python 3.12+**: Programming language

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

[Add your license information here]

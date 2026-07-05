# SynapseHR Backend

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Copy `.env.example` to `.env` and configure:
```bash
cp .env.example .env
```

3. Run the application:
```bash
python -m app.main
```

Or with uvicorn:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

4. Access API docs:
- Swagger: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

## Development

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app

# Lint
ruff check app/

# Format
black app/
```

## Docker

```bash
docker build -t synapsehr-backend .
docker run -p 8000:8000 synapsehr-backend
```

# SynapseHR

An autonomous AI workforce platform that executes HR operations, not just answers HR questions.

## Tech Stack

### Frontend
- **Framework**: Astro
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: Custom components with shadcn/ui patterns
- **State Management**: Nano Stores
- **Icons**: Lucide

### Backend
- **Framework**: FastAPI
- **Language**: Python 3.12+
- **ORM**: SQLAlchemy 2.x
- **Database**: PostgreSQL 17+
- **Migrations**: Alembic
- **Authentication**: JWT (Access + Refresh tokens)
- **Validation**: Pydantic v2

### AI
- **Framework**: LangGraph
- **LLM**: OpenAI / Anthropic / Gemini (configurable)
- **RAG**: ChromaDB + Sentence Transformers
- **Embeddings**: Provider-configurable

### Infrastructure
- **Containerization**: Docker
- **Database**: PostgreSQL 17
- **Vector DB**: ChromaDB

## Getting Started

### Prerequisites
- Python 3.12+
- Node.js 20+
- PostgreSQL 17+

### Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Run database migrations
python -m alembic upgrade head

# Seed database
python -m scripts.seed

# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### Docker Setup

```bash
# From the docker/compose directory
cd docker/compose
docker-compose up -d
```

## Demo Accounts

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@synapsehr.com | Admin@123 |
| HR | hr@synapsehr.com | HR@12345 |
| Manager | manager@synapsehr.com | Manager@123 |
| Employee | employee@synapsehr.com | Employee@123 |

## Production Deployment

```bash
# Set required environment variables
export APP_SECRET_KEY=$(openssl rand -hex 32)
export JWT_SECRET_KEY=$(openssl rand -hex 32)
export POSTGRES_PASSWORD=$(openssl rand -hex 16)
export CORS_ORIGINS='["https://yourdomain.com"]'

# Start production stack
cd docker/compose
docker-compose -f docker-compose.prod.yml up -d

# Seed the database
docker exec synapsehr-backend python -m scripts.seed
```

**Required production environment variables:**
- `APP_SECRET_KEY` — random 64-char hex string
- `JWT_SECRET_KEY` — random 64-char hex string
- `POSTGRES_PASSWORD` — strong database password
- `AI_API_KEY` — OpenAI/Anthropic API key (if using AI features)
- `CORS_ORIGINS` — JSON array of allowed origins

## API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

## Features

- **Authentication**: JWT-based authentication with role-based access control
- **Employee Management**: Create, view, update, and manage employees
- **Department Management**: Organize employees into departments
- **Leave Management**: Apply for leave, check balances, approve/reject requests
- **Document Generation**: Generate HR documents (offer letters, experience letters, etc.)
- **AI Assistant**: Natural language interface for HR operations
- **Knowledge Base**: RAG-powered policy search
- **Workflow Engine**: Automated multi-step workflows
- **Notifications**: In-app notifications
- **Analytics**: Dashboard metrics and reports

## Project Structure

```
SynapseHR/
├── backend/           # FastAPI backend
│   ├── app/          # Application code
│   │   ├── api/      # API routes
│   │   ├── core/     # Configuration, security
│   │   ├── models/   # SQLAlchemy models
│   │   ├── schemas/  # Pydantic schemas
│   │   ├── services/ # Business logic
│   │   ├── repositories/ # Data access
│   │   ├── agents/   # AI agents
│   │   ├── tools/    # AI tools
│   │   └── workflows/ # Workflow engine
│   └── migrations/   # Alembic migrations
├── frontend/         # Astro frontend
│   └── src/
│       ├── components/ # UI components
│       ├── layouts/    # Page layouts
│       ├── pages/      # Routes
│       ├── services/   # API client
│       ├── stores/     # State management
│       └── types/      # TypeScript types
├── docker/           # Docker configuration
├── docs/             # Project documentation
└── scripts/          # Utility scripts
```

## License

MIT License

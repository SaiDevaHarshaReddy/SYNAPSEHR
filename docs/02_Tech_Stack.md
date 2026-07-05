02 — Technology Stack & Engineering Standards
Purpose

This document defines every technology, framework, library, engineering standard, and development convention used throughout SynapseHR.

Every future implementation must follow this specification unless explicitly modified.

Guiding Principles
Production-quality code only.
Modular architecture.
Strong typing.
Security by default.
Scalable architecture.
Clean separation of concerns.
Minimize dependencies.
Prefer stable libraries over experimental ones.
Primary Programming Languages
Frontend

TypeScript

Reason:

Better maintainability
Strong typing
Excellent IDE support
Reduced runtime errors
Backend

Python 3.12+

Reason:

Best ecosystem for AI
FastAPI compatibility
LangGraph support
Excellent async capabilities
Database

SQL (PostgreSQL)

Frontend Stack
Framework

Astro

Purpose

Server-side rendering
Static generation
Component-based architecture
High performance
UI Language

TypeScript

Styling

Tailwind CSS

Purpose

Utility-first
Responsive layouts
Maintainable design system
UI Components

shadcn/ui (Astro-compatible where appropriate)

Purpose

Accessible components
Consistent design
Modern interface
Icons

Lucide Icons

Charts

Chart.js

Used for

Leave analytics
Department statistics
AI performance
Workflow reports
Forms

Native HTML Forms + TypeScript validation

Future compatibility with schema validation.

State Management

Use Astro islands.

Avoid global state unless necessary.

When required:

Nano Stores
Routing

Astro File-based Routing

Notifications

Toast system

Backend Stack
Framework

FastAPI

Responsibilities

REST API
Authentication
Business logic
AI integration
API Documentation

OpenAPI (Swagger)

Generated automatically.

ORM

SQLAlchemy 2.x

Purpose

Database abstraction
Relationships
Transactions
Database Migration

Alembic

Validation

Pydantic v2

Purpose

Request validation
Response validation
Configuration
Authentication

JWT

Features

Access Tokens
Refresh Tokens
Role-Based Access Control (RBAC)
Password Hashing

bcrypt

Database
Engine

PostgreSQL

Reason

ACID compliance
JSON support
Mature ecosystem
Full-text search
Reliable transactions
AI Stack
LLM Provider

Must support interchangeable providers.

Supported providers:

OpenAI
Anthropic
Google Gemini
OpenRouter

Never hardcode a single provider.

AI Framework

LangGraph

Reason

Stateful workflows
Multi-agent orchestration
Tool calling
Memory
Human approval
LLM Framework

LangChain

Use only where it simplifies integrations.

Avoid unnecessary abstraction.

Embedding Model

Sentence Transformers

Vector Database

ChromaDB

Initial implementation.

Future support:

pgvector
Pinecone
Document Processing

Support

PDF
DOCX
TXT
Markdown
AI Memory

Conversation Memory

Workflow Memory

User Context

Agent State

Storage
Local Development

Filesystem

Folders

uploads/

generated_documents/

knowledge/

Future cloud compatibility:

AWS S3

Cloudflare R2

Azure Blob

PDF Generation

Python ReportLab

Email

SMTP abstraction layer

Future providers

SendGrid
Amazon SES
Mailgun
Logging

Python Logging

Structured logging

Log Levels

INFO
WARNING
ERROR
DEBUG
Containerization

Docker

Every service must have

Dockerfile

docker-compose.yml

Deployment Targets

Frontend

Vercel
Cloudflare Pages

Backend

Railway
Render
Fly.io
VPS

Database

Managed PostgreSQL

Development Tools

IDE

VS Code or compatible AI IDE

Recommended Extensions

Python
Astro
Tailwind CSS
ESLint
Prettier
Docker
Code Formatting

Frontend

Prettier

Backend

Black

Import sorting

isort

Linting

Ruff

Git Strategy

Main Branch

main

Development Branch

develop

Feature Branches

feature/auth

feature/dashboard

feature/ai-agent

feature/workflows

Commit Style

Use Conventional Commits

Examples

feat(auth): implement JWT login

fix(ai): correct tool invocation

docs(api): update endpoints

refactor(workflow): simplify planner

test(database): add migration tests
Folder Structure
SynapseHR/

docs/

frontend/

backend/

docker/

scripts/

tests/

uploads/

knowledge/

generated_documents/

README.md
Backend Structure
backend/

app/

api/

models/

schemas/

services/

repositories/

agents/

tools/

workflows/

middleware/

auth/

database/

core/

utils/

tests/

main.py
Frontend Structure
frontend/

src/

components/

layouts/

pages/

lib/

services/

stores/

styles/

types/

assets/

public/
API Standards

RESTful APIs

JSON only

Versioned

/api/v1/

Every endpoint

Validation
Authentication (where required)
Error handling
OpenAPI documentation
Security Standards

Never expose

API Keys
Secrets
Database passwords

Store all secrets in

.env

Never commit

.env
Performance Standards

Frontend

Lazy loading
Optimized assets
Minimal JavaScript

Backend

Async endpoints
Connection pooling
Query optimization

AI

Cache embeddings
Batch retrieval
Efficient prompts
roadmap.sh Skills Required

This project assumes knowledge of the following roadmap.sh topics.

Core Web
HTML
CSS
JavaScript
TypeScript
Version Control
Git
GitHub
Backend
Python
FastAPI
REST APIs
Authentication
SQL
PostgreSQL
Frontend
Astro
Tailwind CSS
Responsive Design
Accessibility
AI
Prompt Engineering
AI Agents
LangGraph
LangChain
Retrieval-Augmented Generation (RAG)
Vector Databases
Embeddings
Tool Calling
DevOps
Docker
Environment Variables
CI/CD Basics
Software Engineering
System Design
Clean Architecture
SOLID Principles
Repository Pattern
Dependency Injection (where appropriate)
Error Handling
Logging
Testing
Engineering Rules

Every implementation must satisfy the following:

Modular design.
Single Responsibility Principle.
Reusable components.
Strong typing.
Input validation.
Comprehensive error handling.
No duplicated business logic.
Document public interfaces.
Keep AI logic isolated from UI.
Keep database access inside repositories.
Business logic belongs in services, not API routes.
Definition of Done

A feature is considered complete only when it includes:

Functional implementation
Validation
Error handling
Logging
Tests
Documentation
Type safety
Responsive UI (if applicable)
Security review
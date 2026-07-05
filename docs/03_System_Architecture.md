03 — System Architecture
Purpose

This document defines the complete architecture of SynapseHR. It describes how every layer of the application interacts, how AI agents operate, how requests flow through the system, and how the platform scales while remaining maintainable.

Every future implementation must conform to this architecture.

Architectural Style

The platform follows a Layered Modular Monolith architecture.

During the initial implementation, all services run within a single backend application while remaining logically separated.

This enables:

Faster development
Easier testing
Simpler deployment
Future migration to microservices
High-Level Architecture
                        ┌──────────────────────┐
                        │    Astro Frontend    │
                        └──────────┬───────────┘
                                   │
                            HTTPS / REST API
                                   │
                        ┌──────────▼───────────┐
                        │    FastAPI Backend   │
                        └──────────┬───────────┘
                                   │
       ┌───────────────┬───────────┼───────────────┬───────────────┐
       │               │           │               │               │
       ▼               ▼           ▼               ▼               ▼
 Authentication   Business Logic   AI Engine    PostgreSQL    File Storage
                                     │
                              ┌──────▼──────┐
                              │ LangGraph   │
                              └──────┬──────┘
                                     │
          ┌──────────────┬────────────┼────────────┬──────────────┐
          ▼              ▼            ▼            ▼              ▼
     Planner Agent   HR Agent   Policy Agent  Doc Agent   Notification Agent
                                     │
                               Business Tools
Layered Architecture

The backend is divided into distinct layers.

1. Presentation Layer

Responsible for:

HTTP endpoints
Request parsing
Response formatting
Authentication checks

Contains:

api/

No business logic belongs here.

2. Service Layer

Responsible for:

Business rules
Workflow orchestration
Validation
Transactions

Contains:

services/
3. Repository Layer

Responsible for:

Database queries
CRUD operations
SQLAlchemy interaction

Contains:

repositories/

Repositories never contain business logic.

4. AI Layer

Responsible for:

Planning
Tool selection
Memory
RAG
Agent execution

Contains:

agents/
tools/
workflows/
5. Database Layer

Responsible for:

Persistence
Relationships
Transactions
Request Lifecycle

Example:

Employee asks:

"I need leave for three days next week."

Flow:

Frontend

↓

POST /chat

↓

Authentication

↓

Chat Service

↓

Planner Agent

↓

Leave Agent

↓

Policy Retrieval

↓

Leave Balance Tool

↓

Workflow Engine

↓

Manager Approval

↓

Database Update

↓

Notification

↓

Response

↓

Frontend
AI Execution Pipeline

Every AI request follows the same pipeline.

User Input

↓

Intent Detection

↓

Planner Agent

↓

Task Decomposition

↓

Knowledge Retrieval

↓

Tool Selection

↓

Workflow Execution

↓

Validation

↓

Database Updates

↓

Notifications

↓

Audit Logging

↓

Response Generation
AI Agent Hierarchy

Only one agent communicates directly with users.

User

↓

Planner Agent

↓

Specialized Agents

Specialized agents include:

HR Agent
Leave Agent
Policy Agent
Document Agent
Approval Agent
Analytics Agent
Notification Agent

Each agent owns a single responsibility.

Agent Responsibilities
Planner Agent

Responsibilities:

Understand user intent
Break tasks into steps
Route work to other agents
Decide execution order

Never accesses databases directly.

HR Agent

Handles:

Employee information
HR workflows
General HR requests
Leave Agent

Handles:

Leave balances
Leave creation
Leave approval logic
Holidays
Policy Agent

Handles:

Company policies
Employee handbook
Benefits
Compliance

Uses RAG exclusively.

Document Agent

Responsible for generating:

Offer letters
Appointment letters
Experience certificates
Promotion letters
Salary certificates
Approval Agent

Responsible for:

Manager approvals
HR approvals
Multi-level approval chains
Notification Agent

Responsible for:

Email
In-app notifications
Approval reminders
Workflow updates
Tool Layer

Agents never modify systems directly.

Instead they invoke tools.

Examples:

check_leave_balance()

create_leave_request()

generate_offer_letter()

get_employee()

update_database()

send_email()

notify_manager()

retrieve_policy()

calculate_remaining_leave()

log_workflow()

Every tool performs exactly one responsibility.

Knowledge Retrieval (RAG)

Knowledge sources:

Employee Handbook

Leave Policy

Benefits Guide

Holiday Calendar

HR SOP

Company Rules

Flow:

Question

↓

Embedding

↓

Vector Search

↓

Relevant Chunks

↓

LLM

↓

Answer

The model must never hallucinate company policies.

Database Communication

Only repositories communicate with PostgreSQL.

Service

↓

Repository

↓

SQLAlchemy

↓

PostgreSQL

No AI agent performs SQL queries directly.

Authentication Flow
Login

↓

Credential Verification

↓

JWT Generation

↓

Frontend Storage

↓

Authenticated Requests

↓

Role Validation

↓

Business Logic

Roles:

Employee
Manager
HR
Administrator
Document Generation Flow
User Request

↓

Planner

↓

Document Agent

↓

Collect Data

↓

Generate Template

↓

PDF Generator

↓

Store Document

↓

Return Download Link
Workflow Engine

Every business process is represented as a workflow.

Example:

Leave Request

Employee

↓

Validation

↓

Policy Check

↓

Balance Check

↓

Approval Required?

↓

Manager Approval

↓

Database Update

↓

Notification

↓

Complete
Error Handling Strategy

Every layer catches only errors it can handle.

Controller

↓

Service

↓

Repository

Unexpected errors propagate upward.

Every exception is logged.

No stack traces are exposed to users.

Logging Strategy

Every important action creates an audit record.

Examples:

Login
Leave Request
Approval
AI Tool Call
AI Decision
Document Generation

Logs contain:

Timestamp
User
Action
Result
Duration
Security Boundaries

AI cannot:

Access secrets
Execute arbitrary code
Read unrestricted files
Modify the database directly
Skip approval workflows

All privileged operations require business validation.

Scalability Strategy

Future scaling:

Astro

↓

Load Balancer

↓

Multiple FastAPI Instances

↓

Shared PostgreSQL

↓

Dedicated AI Service

↓

Separate Vector Database

The architecture should support horizontal scaling without major redesign.

Design Principles

The system follows:

SOLID
Clean Architecture
DRY
KISS
Separation of Concerns
Repository Pattern
Dependency Injection (where appropriate)
Module Dependency Rules

Allowed:

API

↓

Services

↓

Repositories

↓

Database

AI:

Planner

↓

Agents

↓

Tools

↓

Services

Forbidden:

API calling repositories directly
Agents executing SQL
Frontend accessing database
Services importing UI code
Circular dependencies
Future Integrations

Architecture should support adding:

Slack
Microsoft Teams
Google Workspace
Outlook
Workday
SAP
BambooHR
Jira

without modifying core business logic.

Definition of Architecture Completion

The architecture is complete when:

Every module has one responsibility.
Every dependency direction is respected.
AI remains isolated from infrastructure.
Business logic is centralized.
Database access occurs only through repositories.
New features can be added without restructuring the project.
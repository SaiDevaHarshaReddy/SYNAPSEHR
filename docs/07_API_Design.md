# 07 — REST API Design

# Purpose

This document defines the public REST API exposed by SynapseHR.

The REST API acts as the only communication layer between the Astro frontend and the FastAPI backend.

Every client must communicate exclusively through these APIs.

No frontend component may communicate directly with the database or AI providers.

---

# Design Principles

The API shall

- Follow REST conventions
- Return JSON only
- Be stateless
- Be versioned
- Be documented using OpenAPI
- Be strongly validated
- Support pagination
- Use consistent error responses

---

# Base URL

/api/v1

Example

/api/v1/auth/login

/api/v1/employees

/api/v1/chat

---

# HTTP Methods

GET

Retrieve resources.

POST

Create resources.

PUT

Replace resources.

PATCH

Partial update.

DELETE

Soft delete unless otherwise specified.

---

# Authentication

Every protected endpoint requires

Authorization

Bearer <JWT>

Authentication is validated before reaching business logic.

---

# Standard Response Format

Every successful response should follow

{
    "success": true,
    "message": "...",
    "data": {}
}

Every error response should follow

{
    "success": false,
    "error": {
        "code": "...",
        "message": "...",
        "request_id": "..."
    }
}

---

# API Modules

The API is divided into business domains.

Auth

Employees

Departments

Leave

Policies

Documents

Chat

Analytics

Notifications

Admin

Workflow

Knowledge Base

---

# Authentication APIs

POST

/auth/login

Purpose

Authenticate user.

Returns

Access Token

Refresh Token

User Profile

------------------------------------

POST

/auth/refresh

Purpose

Issue new access token.

------------------------------------

POST

/auth/logout

Purpose

Invalidate refresh token.

------------------------------------

POST

/auth/forgot-password

Purpose

Generate reset token.

------------------------------------

POST

/auth/reset-password

Purpose

Reset password.

---

# Employee APIs

GET

/employees

List employees.

Supports

Pagination

Sorting

Filtering

Searching

------------------------------------

GET

/employees/{id}

Retrieve employee profile.

------------------------------------

POST

/employees

Create employee.

------------------------------------

PATCH

/employees/{id}

Update employee.

------------------------------------

DELETE

/employees/{id}

Deactivate employee.

---

# Department APIs

GET

/departments

GET

/departments/{id}

POST

/departments

PATCH

/departments/{id}

DELETE

/departments/{id}

---

# Leave APIs

GET

/leave/balance

Returns

Current balances.

------------------------------------

GET

/leave/history

Returns

Leave history.

------------------------------------

POST

/leave/request

Creates leave request.

------------------------------------

GET

/leave/{id}

Retrieve request.

------------------------------------

PATCH

/leave/{id}/cancel

Cancel request.

------------------------------------

POST

/leave/{id}/approve

Approve leave.

------------------------------------

POST

/leave/{id}/reject

Reject leave.

---

# Policy APIs

GET

/policies

List documents.

------------------------------------

GET

/policies/{id}

Retrieve policy.

------------------------------------

POST

/policies/upload

Upload PDF.

------------------------------------

DELETE

/policies/{id}

Archive document.

---

# AI Chat APIs

POST

/chat

Purpose

Main AI endpoint.

Input

Conversation

↓

Planner Agent

↓

Workflow

↓

Response

------------------------------------

GET

/chat/history

Returns

Conversation history.

------------------------------------

GET

/chat/{conversation_id}

Returns

Messages.

------------------------------------

DELETE

/chat/{conversation_id}

Archive conversation.

---

# Document APIs

POST

/documents/generate

Supported

Offer Letter

Experience Letter

Salary Certificate

Promotion Letter

Warning Letter

Appointment Letter

------------------------------------

GET

/documents

List generated documents.

------------------------------------

GET

/documents/{id}

Download document.

---

# Notification APIs

GET

/notifications

Returns notifications.

------------------------------------

PATCH

/notifications/{id}/read

Mark as read.

------------------------------------

DELETE

/notifications/{id}

Archive notification.

---

# Workflow APIs

GET

/workflows

List workflow executions.

------------------------------------

GET

/workflows/{id}

Detailed execution timeline.

------------------------------------

POST

/workflows/{id}/retry

Retry failed workflow.

---

# Analytics APIs

GET

/analytics/dashboard

Dashboard metrics.

------------------------------------

GET

/analytics/leave

Leave reports.

------------------------------------

GET

/analytics/employees

Employee reports.

------------------------------------

GET

/analytics/ai

AI statistics.

---

# Admin APIs

GET

/admin/users

GET

/admin/logs

GET

/admin/audit

POST

/admin/roles

PATCH

/admin/settings

---

# Pagination

Collection endpoints support

page

limit

sort

order

search

Example

/employees?page=2&limit=20

---

# Filtering

Supported

department

status

manager

date range

organization

---

# Versioning

Current

/api/v1/

Future

/api/v2/

Older versions remain supported during migration.

---

# Validation

Every request

Pydantic validation

↓

Business validation

↓

Repository validation

---

# File Upload

Supported

PDF

DOCX

TXT

PNG

JPEG

Maximum

25 MB

---

# Rate Limiting

Applied to

Authentication

AI Chat

File Upload

Password Reset

---

# API Documentation

Swagger

OpenAPI

Generated automatically.

Available only to authorized users in production.

---

# Future APIs

Payroll

Attendance

Recruitment

Performance Reviews

Expenses

Training

without breaking existing endpoints.

---

# Definition of Completion

The REST API is complete when

- Every business module exposes REST endpoints.
- Responses are consistent.
- Authentication protects all secured routes.
- Validation exists for every request.
- OpenAPI documentation is generated.
- Future expansion is possible without breaking clients.
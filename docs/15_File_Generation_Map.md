# 15 — File Generation Map

# Purpose

This document defines the complete file generation strategy for SynapseHR.

Claude must generate the project exactly according to this structure.

No major architectural changes should be introduced unless explicitly approved.

The file structure is considered part of the software architecture.

---

# Root Structure

SynapseHR/

docs/

frontend/

backend/

docker/

scripts/

uploads/

knowledge/

generated_documents/

tests/

README.md

.gitignore

.env.example

LICENSE

---

# Frontend Structure

frontend/

astro.config.mjs

package.json

tsconfig.json

tailwind.config.js

src/

assets/

components/

layouts/

pages/

services/

stores/

types/

hooks/

styles/

utils/

middleware/

public/

---

# Components

components/

common/

auth/

dashboard/

employees/

departments/

leave/

documents/

chat/

analytics/

notifications/

settings/

workflow/

ui/

Each component folder should contain

Page Components

Reusable Components

Dialogs

Forms

Cards

Tables

Modals

---

# Pages

pages/

login/

dashboard/

employees/

departments/

leave/

documents/

analytics/

chat/

notifications/

settings/

profile/

admin/

404.astro

index.astro

---

# Layouts

layouts/

PublicLayout

DashboardLayout

AdminLayout

ChatLayout

---

# Backend Structure

backend/

app/

api/

v1/

auth/

employees/

departments/

leave/

documents/

analytics/

chat/

notifications/

workflow/

admin/

core/

database/

models/

schemas/

repositories/

services/

agents/

tools/

workflows/

middleware/

utils/

tests/

main.py

---

# AI Structure

agents/

planner/

policy/

leave/

document/

approval/

analytics/

notification/

memory/

conversation/

Each agent owns

Agent

Prompt

Configuration

Response Model

Helper Functions

---

# Tool Structure

tools/

employee/

leave/

policy/

documents/

notifications/

analytics/

workflow/

Every tool performs exactly one deterministic operation.

---

# Workflow Structure

workflows/

leave/

document_generation/

employee_onboarding/

employee_exit/

promotion/

Each workflow contains

State

Transitions

Validation

Recovery

Configuration

---

# RAG Structure

rag/

loader/

parser/

chunking/

embedding/

retriever/

context_builder/

vector_store/

knowledge/

---

# Database Structure

models/

One file per entity.

schemas/

Separate request and response schemas.

repositories/

One repository per aggregate.

---

# API Structure

Every business module contains

router.py

service.py

schemas.py

dependencies.py

exceptions.py

---

# Testing Structure

tests/

unit/

integration/

api/

workflow/

ai/

performance/

security/

Mirror the production structure wherever possible.

---

# Docker Structure

docker/

backend/

frontend/

postgres/

nginx/

compose/

---

# Generated Documents

generated_documents/

offer_letters/

appointment_letters/

salary_certificates/

experience_letters/

promotion_letters/

warning_letters/

termination_letters/

---

# Knowledge Storage

knowledge/

policies/

employee_handbook/

benefits/

holidays/

training/

uploaded/

---

# Scripts

scripts/

setup/

seed/

migration/

deployment/

maintenance/

---

# Naming Rules

Folders

snake_case

Python Files

snake_case.py

Classes

PascalCase

Functions

snake_case

Variables

snake_case

Constants

UPPER_CASE

---

# Generation Order

Claude should generate files in the following order.

1

Project Skeleton

↓

2

Backend Foundation

↓

3

Frontend Foundation

↓

4

Database

↓

5

Authentication

↓

6

Business Modules

↓

7

REST APIs

↓

8

AI System

↓

9

RAG

↓

10

Workflow Engine

↓

11

Notifications

↓

12

Analytics

↓

13

Testing

↓

14

Deployment

---

# Generation Rules

Never create duplicate files.

Never place business logic inside routes.

Never place SQL inside services.

Never place AI logic inside repositories.

Never create placeholder modules.

Every generated file should be immediately compilable.

---

# Completion Criteria

The project structure is complete when

Every folder exists.

Every planned module exists.

Every dependency follows architecture.

The project builds successfully.

No unnecessary files exist.
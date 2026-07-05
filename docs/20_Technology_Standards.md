# 20 — Technology Standards

# Purpose

This document defines the mandatory technology standards for SynapseHR.

Claude must follow these standards unless explicitly instructed otherwise.

---

# Frontend

Framework

Astro

Language

TypeScript

Package Manager

pnpm

Styling

TailwindCSS

UI Components

shadcn/ui (adapted for Astro)

Icons

Lucide Icons

Fonts

Inter

State Management

Nano Stores

HTTP Client

Axios

Schema Validation

Zod

Date Library

dayjs

Markdown

Marked

Syntax Highlighting

Shiki

Theme

Dark First

Future

Light Theme

---

# Backend

Framework

FastAPI

Language

Python 3.12+

Package Manager

uv

ORM

SQLAlchemy 2.x

Database Migration

Alembic

Authentication

JWT

Password Hashing

bcrypt

Validation

Pydantic v2

Dependency Injection

FastAPI Depends

Background Jobs

FastAPI BackgroundTasks

Future

Celery

Logging

structlog

Configuration

pydantic-settings

Testing

pytest

httpx

---

# Database

Database

PostgreSQL 17+

Future Vector Extension

pgvector

Development

Docker Container

Production

Managed PostgreSQL

---

# AI

Framework

LangGraph

LLM Framework

LangChain (only where beneficial)

Model Providers

OpenAI

Anthropic

Google Gemini

OpenRouter

Structured Output

Pydantic Models

Prompt Storage

Markdown Files

Memory

LangGraph State

Conversation Store

---

# RAG

Document Loader

LangChain

Embeddings

Provider Configurable

Vector Database

ChromaDB

Future

pgvector

Chunking

Recursive Character Splitter

Retrieval

Similarity Search

Future

Hybrid Search

---

# Storage

Documents

Local Storage (Development)

Future

AWS S3

Azure Blob

Google Cloud Storage

---

# Authentication

JWT

Refresh Tokens

RBAC

Future

OAuth2

SSO

---

# Infrastructure

Containerization

Docker

Reverse Proxy

Nginx

Environment Variables

.env

Future

Docker Compose

Kubernetes

---

# API

Architecture

REST

Documentation

OpenAPI

Swagger

JSON Responses

Versioning

/api/v1

---

# Development

Version Control

Git

Repository

GitLab

Branch Strategy

Git Flow

Formatter

Black

Linter

Ruff

Type Checker

mypy

---

# Frontend Quality

ESLint

Prettier

TypeScript Strict Mode

Responsive Design

WCAG AA

---

# Backend Quality

Black

Ruff

pytest

Type Hints Required

Async Endpoints

Repository Pattern

Dependency Injection

---

# Testing

Unit Tests

Integration Tests

API Tests

Workflow Tests

AI Tests

End-to-End Tests

---

# Performance

Frontend

Lazy Loading

Code Splitting

Image Optimization

Backend

Async APIs

Connection Pooling

Caching Ready

Database Indexes

---

# Monitoring

Structured Logs

Health Checks

Future

Prometheus

Grafana

OpenTelemetry

---

# Security

HTTPS

JWT

RBAC

Input Validation

Secure Headers

Rate Limiting

Secrets via Environment Variables

---

# Forbidden Technologies

Do not use

PHP

jQuery

Flask

Django

MongoDB

Firebase Authentication

Bootstrap

Material UI

Inline CSS

Inline JavaScript

---

# Definition of Completion

Technology selection is complete when

Every dependency is consistent.

No duplicate libraries exist.

Every technology follows project standards.

The entire stack remains maintainable.
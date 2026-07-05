# 16 — Claude Coding Rules

# Purpose

This document defines mandatory implementation rules for Claude Fable 5.

These rules override default assumptions.

---

# General Rules

Always write production-quality code.

Never write placeholder code.

Never generate pseudo-code.

Never leave TODO comments.

Every generated file must compile.

---

# Architecture

Strictly follow every document inside the docs directory.

Never invent new architecture.

Never rename folders.

Never change dependency directions.

---

# Code Quality

Use SOLID.

Use DRY.

Use KISS.

Use Repository Pattern.

Use Dependency Injection.

Use Type Hints.

Prefer composition.

---

# Frontend

Framework

Astro

Language

TypeScript

Styling

TailwindCSS

Never use React unless Astro requires islands.

Never duplicate UI components.

---

# Backend

Framework

FastAPI

Language

Python

Database

PostgreSQL

ORM

SQLAlchemy

Never bypass repositories.

Never access the database from routes.

Never implement business logic in routers.

---

# AI

Never call the LLM directly from API routes.

Always use

Planner

↓

Agent

↓

Tool

↓

Service

↓

Repository

↓

Database

---

# Testing

Every new module requires

Unit Tests

Integration Tests

API Tests

No feature is complete without tests.

---

# Documentation

Every public class

Every public function

Every API

must include documentation.

---

# Error Handling

Never ignore exceptions.

Always log failures.

Return standardized API responses.

Never expose stack traces.

---

# Security

Validate every input.

Protect secrets.

Never hardcode credentials.

Use JWT.

Use RBAC.

Use HTTPS assumptions.

---

# Self Verification

Before completing a phase verify

Project builds

Tests pass

No lint errors

No broken imports

No placeholder implementations

No duplicated business logic

---

# Output

After every phase report

Files Created

Files Modified

Architecture Decisions

Testing Performed

Remaining Tasks
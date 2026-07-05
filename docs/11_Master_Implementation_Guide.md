# 11 — Master Implementation Guide

# Purpose

This document defines the implementation strategy that every AI coding model must follow while developing SynapseHR.

This document has higher priority than implementation assumptions.

Whenever uncertainty exists, follow this document.

---

# Primary Goal

Develop a production-ready SaaS application.

This is NOT a prototype.

This is NOT a demo application.

This is NOT a hackathon-only implementation.

Every implementation decision should assume long-term maintainability.

---

# Engineering Principles

The implementation must prioritize

Correctness

Maintainability

Scalability

Security

Readability

Modularity

Performance

Testing

---

# Development Strategy

The system shall be implemented incrementally.

Never generate the complete project in one iteration.

Every phase must compile successfully before moving to the next.

---

# Phase Order

Phase 1

Project initialization

----------------

Phase 2

Backend foundation

----------------

Phase 3

Frontend foundation

----------------

Phase 4

Authentication

----------------

Phase 5

Database

----------------

Phase 6

Core APIs

----------------

Phase 7

AI infrastructure

----------------

Phase 8

RAG

----------------

Phase 9

Business workflows

----------------

Phase 10

Analytics

----------------

Phase 11

Notifications

----------------

Phase 12

Testing

----------------

Phase 13

Deployment

---

# Coding Standards

Every class

One responsibility.

Every function

One logical operation.

Every module

Independent.

Avoid large files.

Avoid duplicated logic.

Prefer composition.

Avoid inheritance unless justified.

---

# File Generation

Whenever creating files

Explain

Purpose

Responsibilities

Dependencies

before implementation.

---

# Dependency Rules

Never introduce circular imports.

Always use dependency injection.

Never bypass services.

Never bypass repositories.

---

# AI Rules

The AI subsystem must remain isolated.

Never place AI logic inside

Routes

Repositories

Database Models

Middleware

---

# Database Rules

Never access the database directly from

Routes

Agents

Frontend

Middleware

Only repositories communicate with SQLAlchemy.

---

# Testing Rules

Every major feature requires

Unit Tests

Integration Tests

API Tests

Critical workflows require end-to-end tests.

---

# Completion Rule

A phase is complete only when

The project builds.

Tests pass.

No placeholder implementations remain.

Documentation is updated.

No TODO comments remain.

---

# Final Goal

Produce production-ready software that can be deployed without architectural changes.
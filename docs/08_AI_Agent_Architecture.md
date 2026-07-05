# 08 — AI Agent Architecture

# Purpose

This document defines the complete Artificial Intelligence architecture of SynapseHR.

Unlike traditional AI chatbots, SynapseHR employs a multi-agent architecture in which specialized autonomous agents collaborate to execute complete business workflows.

The AI subsystem is responsible for understanding user intent, planning actions, retrieving organizational knowledge, invoking business tools, executing workflows, requesting approvals when required, and generating explainable responses.

The AI must never bypass business rules defined by backend services.

---

# Design Principles

The AI subsystem shall

- Act as an intelligent employee, not merely a chatbot.
- Reason before acting.
- Plan before executing.
- Use tools instead of hallucinating.
- Retrieve company knowledge before answering.
- Explain every important action.
- Produce deterministic outputs whenever possible.
- Remain provider-independent.

---

# High-Level Architecture

User

↓

Planner Agent

↓

Intent Classification

↓

Task Planning

↓

Knowledge Retrieval (if required)

↓

Tool Selection

↓

Workflow Execution

↓

Response Generation

↓

Audit Logging

---

# Multi-Agent Model

The system uses one Coordinator Agent and multiple Specialized Agents.

Only the Planner Agent communicates directly with the user.

All remaining agents execute delegated responsibilities.

---

# Agent Hierarchy

User

↓

Planner Agent

├── HR Agent

├── Leave Agent

├── Policy Agent

├── Document Agent

├── Approval Agent

├── Notification Agent

├── Analytics Agent

└── Workflow Agent

---

# Planner Agent

Purpose

The Planner Agent acts as the central reasoning engine.

Responsibilities

- Understand user intent.
- Determine required workflow.
- Decide whether AI reasoning is required.
- Decide whether RAG is required.
- Decide which specialized agent to invoke.
- Combine final responses.

The Planner Agent never performs business operations directly.

---

# HR Agent

Responsibilities

- Employee information
- HR procedures
- Organization hierarchy
- General HR guidance

Uses

EmployeeService

DepartmentService

Policy Retrieval

---

# Leave Agent

Responsibilities

- Leave eligibility
- Leave balance
- Leave policies
- Leave requests
- Leave approvals

Uses

LeaveService

PolicyAgent

ApprovalAgent

---

# Policy Agent

Responsibilities

- Company handbook
- HR policies
- Benefits
- Compliance
- Internal documentation

This agent always uses Retrieval-Augmented Generation (RAG).

It must never answer from model memory alone when company documentation exists.

---

# Document Agent

Responsibilities

Generate

Offer Letter

Appointment Letter

Experience Letter

Salary Certificate

Promotion Letter

Warning Letter

Relieving Letter

Termination Letter

Uses

Template Engine

PDF Generator

EmployeeService

---

# Approval Agent

Responsibilities

Determine

Who must approve

Approval hierarchy

Approval status

Escalation

Reminder scheduling

---

# Notification Agent

Responsibilities

Email

In-App Notifications

Approval Requests

Workflow Updates

Completion Notifications

---

# Analytics Agent

Responsibilities

Generate business insights

Leave trends

Department reports

AI usage statistics

Workflow metrics

Executive summaries

---

# Workflow Agent

Coordinates multi-step business processes.

Examples

Leave Application

Employee Onboarding

Employee Exit

Promotion

Department Transfer

Document Generation

---

# Agent Communication

Agents never communicate directly with each other.

Communication always flows through the Planner Agent.

Allowed

Planner

↓

Specialized Agent

↓

Planner

Forbidden

Leave Agent

↓

Document Agent

Policy Agent

↓

Notification Agent

---

# AI State

Every AI execution maintains a shared execution state.

State contains

Current User

Current Organization

Conversation Context

Workflow Status

Current Step

Previous Tool Results

Memory References

Retrieved Documents

Execution Metadata

---

# Conversation Memory

Memory exists at three levels.

Short-Term

Current conversation.

Session

Previous conversations.

Long-Term

User preferences

Workflow history

Organization context

Memory must never expose another user's information.

---

# Tool Calling

The AI never performs business operations itself.

Instead

Planner

↓

Agent

↓

Tool

↓

Business Service

↓

Repository

↓

Database

Examples

check_leave_balance()

create_leave_request()

generate_offer_letter()

search_policy()

send_notification()

schedule_approval()

Every tool performs one deterministic task.

---

# Structured Outputs

Every agent returns structured data instead of free-form text whenever possible.

Example

Intent

Confidence

Required Tools

Workflow

Business Result

Final Response

This enables reliable orchestration.

---

# AI Decision Pipeline

User Request

↓

Intent Detection

↓

Planner

↓

Task Decomposition

↓

RAG (if required)

↓

Tool Selection

↓

Execution

↓

Validation

↓

Response

↓

Audit Log

---

# Guardrails

The AI must never

Bypass authentication.

Ignore RBAC.

Invent employee records.

Invent leave balances.

Invent policy content.

Skip approval workflows.

Access unauthorized data.

Execute SQL.

Modify the database directly.

All modifications occur through backend services.

---

# Human Approval

Certain workflows require mandatory human approval.

Examples

Leave Approval

Promotion

Termination

Role Changes

Salary Updates

The AI prepares requests but does not override human decisions.

---

# Provider Independence

The AI subsystem must support

OpenAI

Anthropic

Google Gemini

OpenRouter

Changing providers must require configuration changes only.

---

# Prompt Management

Prompts shall be stored outside application code.

Prompt categories

Planner

HR

Leave

Policy

Document

Approval

Notification

System

Prompt versioning should be supported.

---

# Observability

Every AI execution records

Prompt Version

Model

Execution Time

Retrieved Documents

Tools Invoked

Workflow

Token Usage

Success/Failure

This information feeds analytics and debugging.

---

# Failure Strategy

If an AI step fails

Retry deterministic tool calls where appropriate.

Fall back to human-readable error messages.

Never fabricate successful execution.

Always preserve workflow consistency.

---

# Extensibility

Future agents may include

Payroll Agent

Recruitment Agent

Attendance Agent

Travel Agent

Expense Agent

Asset Management Agent

The Planner Agent should support registering additional agents without architectural changes.

---

# Definition of Completion

The AI subsystem is complete when

- The Planner Agent coordinates all AI workflows.
- Specialized agents remain independent.
- Business operations occur only through tools and services.
- Company knowledge is retrieved through RAG.
- Every important AI decision is explainable.
- Guardrails prevent unsafe or unauthorized actions.
- The architecture supports future AI capabilities without redesign.
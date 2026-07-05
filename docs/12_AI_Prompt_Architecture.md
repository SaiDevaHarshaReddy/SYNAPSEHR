# 12 — AI Prompt Architecture

# Purpose

This document defines how prompts are structured, versioned, and managed throughout SynapseHR.

Prompt engineering is treated as software architecture.

Prompts are version-controlled assets.

---

# Prompt Categories

System Prompts

Planner Prompts

Agent Prompts

Tool Prompts

RAG Prompts

Summarization Prompts

Evaluation Prompts

---

# Prompt Hierarchy

System Prompt

↓

Planner Prompt

↓

Agent Prompt

↓

Tool Prompt

↓

LLM Response

Every prompt inherits constraints from higher levels.

---

# System Prompt

Responsibilities

Define

AI identity

Safety

Behavior

Reasoning style

Formatting

Security constraints

The system prompt must remain provider-independent.

---

# Planner Prompt

Responsibilities

Understand intent.

Select workflow.

Determine required tools.

Determine whether RAG is required.

Determine human approval.

Never execute business logic.

---

# Agent Prompt

Every specialized agent owns its own prompt.

Examples

Leave Agent

Policy Agent

Document Agent

Notification Agent

Analytics Agent

Approval Agent

Each prompt contains only domain knowledge.

---

# Tool Prompt

Tool prompts define

Input

Output

Constraints

Validation

Failure behavior

Tools should return structured outputs.

---

# Prompt Storage

Store prompts outside application code.

Suggested structure

prompts/

system/

planner/

agents/

tools/

rag/

---

# Prompt Versioning

Every prompt contains

Version

Created Date

Updated Date

Description

Author

Breaking Changes

---

# Prompt Testing

Every prompt should be tested for

Correctness

Determinism

Security

Hallucination

Formatting

Latency

---

# Prompt Rules

Never hardcode organization policies.

Always retrieve organization knowledge through RAG.

Never fabricate business operations.

Never bypass approval workflows.

Never expose confidential information.

---

# Context Management

Every prompt receives

Current User

Current Organization

Conversation Context

Workflow State

Retrieved Documents

Relevant Memory

No unnecessary context should be injected.

---

# Structured Output

Whenever possible

Require JSON

or

Pydantic-compatible structured outputs.

Avoid free-form responses for business operations.

---

# Future Compatibility

The prompt architecture should support

OpenAI

Anthropic

Gemini

OpenRouter

Local LLMs

without rewriting prompt logic.

---

# Completion Criteria

The prompt subsystem is complete when

Prompts are modular.

Versioned.

Reusable.

Provider-independent.

Secure.

Testable.
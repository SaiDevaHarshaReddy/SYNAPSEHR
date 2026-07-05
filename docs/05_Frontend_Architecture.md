05 — Frontend Architecture
Purpose

This document defines the frontend architecture of SynapseHR.

The frontend shall provide a modern, responsive, secure, and accessible interface while remaining independent of backend implementation details.

It must support future expansion without requiring architectural redesign.

Technology Stack

Framework

Astro

Language

TypeScript

Styling

Tailwind CSS

Component Library

shadcn/ui (Astro-compatible)

Charts

Chart.js

Icons

Lucide

State Management

Nano Stores

Package Manager

pnpm

Design Principles

The frontend shall:

Be component-driven.
Be mobile responsive.
Follow accessibility standards (WCAG AA).
Minimize client-side JavaScript.
Use Astro Islands for interactivity.
Separate presentation from business logic.
Keep components reusable.
Keep API logic centralized.
Folder Structure
frontend/

src/

components/

layouts/

pages/

lib/

services/

stores/

hooks/

styles/

types/

assets/

public/

middleware/

utils/
Components Directory

Components are grouped by domain.

components/

common/

auth/

dashboard/

employee/

leave/

chat/

documents/

analytics/

workflow/

notification/

ui/
Layouts

The application uses three layouts.

Public Layout

Used for

Login
Forgot Password
Reset Password
Dashboard Layout

Used for

Employee Portal
Manager Portal
HR Portal
Admin Portal

Contains

Sidebar
Header
Breadcrumbs
Notifications
User Menu
Full Screen Layout

Used for

AI Chat
Document Preview
Routing

Astro File Routing

Example

/

login

dashboard

employees

leave

documents

analytics

chat

settings

profile

admin
Navigation Structure
Dashboard

Employees

Leave

AI Assistant

Documents

Analytics

Notifications

Settings

Menus appear based on user role.

User Interface Principles

Every screen should

Load quickly
Display loading states
Display empty states
Display error states
Support keyboard navigation
Authentication Flow
Login

↓

JWT Received

↓

Store Securely

↓

Fetch User

↓

Determine Role

↓

Load Dashboard
Role-Based Navigation

Employee

Dashboard
Leave
Documents
AI Assistant
Notifications
Profile

Manager

Everything Employee has

Plus

Team
Approvals
Reports

HR

Everything Manager has

Plus

Employees
Policies
Documents
Analytics

Administrator

Full Access

Dashboard Widgets

Cards

Total Employees
Pending Approvals
Today's Leave
AI Tasks Completed
Documents Generated
Notifications
Workflow Success Rate

Charts

Leave Trend
Department Distribution
AI Activity
Monthly Requests
AI Assistant Screen

Contains

Left Panel

Conversation History

Center

Chat Interface

Right Panel

Workflow Timeline

Current Agent

Sources Used

Execution Status

This allows users to understand how AI reached its conclusions.

Employee Profile

Sections

Personal Details

Employment Details

Leave Balance

Reporting Manager

Documents

Activity Timeline

Leave Module

Features

Leave Calendar

Leave Balance

Leave History

Apply Leave

Approval Status

AI Suggestions

Document Module

Displays

Generated Documents

Upload Documents

Preview

Download

Version History

Analytics Module

Displays

Employee Statistics

Leave Analytics

Department Metrics

Workflow Analytics

AI Performance

Notification Center

Supports

Unread Notifications

Workflow Updates

Approvals

System Messages

Email Status

Forms

Every form shall include

Validation

Error Messages

Loading State

Success State

Accessibility Labels

Keyboard Navigation

API Layer

All API communication goes through

services/

Components never call fetch() directly.

Example

components

↓

services

↓

backend API
State Management

Use Nano Stores for

Authentication

Current User

Notifications

Theme

Avoid global state unless necessary.

Error Handling

Every page shall handle

404

401

403

500

Network Failure

Session Expiration

Gracefully.

Loading Strategy

Use

Skeleton Screens

Progress Indicators

Optimistic Updates where appropriate

Lazy Loading

Theme

Support

Light

Dark

System Preference

Responsive Breakpoints

Mobile

Tablet

Laptop

Desktop

Large Desktop

Every page must function correctly across all screen sizes.

Accessibility

Support

Keyboard Navigation

Screen Readers

ARIA Labels

Focus Indicators

High Contrast

Reduced Motion

Performance Goals

Initial Load

< 2 seconds

Lighthouse

90+

Accessibility

95+

Best Practices

95+

SEO

90+

Security

Never expose

JWT

API Keys

Secrets

Internal IDs

Sensitive Data

Use HTTPS only.

Future Expansion

The frontend should support future modules

Payroll

Attendance

Recruitment

Performance Reviews

Expenses

Travel

Training

without redesigning the navigation.

Definition of Completion

The frontend architecture is complete when

Components are reusable.
Routing is modular.
Pages are responsive.
API communication is centralized.
Role-based UI is implemented.
Accessibility requirements are met.
Performance goals are achievable.
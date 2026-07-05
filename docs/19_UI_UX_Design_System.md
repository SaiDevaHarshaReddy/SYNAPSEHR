# 19 — UI / UX Design System

# Purpose

This document defines the complete visual language, user experience principles, layout system, and interaction design for SynapseHR.

The interface should feel like a modern AI-native SaaS platform rather than a traditional HR management system.

The AI Assistant is the primary interaction point of the application.

---

# Design Philosophy

The interface should communicate

Professional

Modern

Minimal

Fast

Trustworthy

AI-first

Avoid unnecessary visual clutter.

Every screen should focus on helping users complete tasks quickly.

---

# Design Inspiration

Use inspiration from

Notion

Linear

Vercel Dashboard

GitHub

OpenAI ChatGPT

Anthropic Claude

Stripe Dashboard

Avoid copying any single product.

Create a unique visual identity.

---

# Color Palette

Primary

Indigo

Accent

Cyan

Success

Green

Warning

Amber

Danger

Red

Neutral

Slate / Zinc

Use a dark theme by default.

Support light mode in the future.

---

# Typography

Use

Inter

Fallback

system-ui

Hierarchy

Display

Heading

Subheading

Body

Caption

Code

Maintain consistent spacing and font weights.

---

# Layout System

Desktop

Top Navigation

Left Sidebar

Main Content Area

Optional Right AI Activity Panel

Mobile

Bottom Navigation

Collapsible Sidebar

Responsive Cards

---

# Navigation

Sidebar Sections

Dashboard

AI Assistant

Employees

Departments

Leave

Documents

Analytics

Notifications

Settings

Admin

Sidebar should remain collapsible.

---

# Landing Dashboard

The first screen should not be employee tables.

Instead display

Welcome message

AI Command Center

Quick Actions

Recent Activity

Pending Approvals

Organization Insights

Recent Notifications

Workflow Status

---

# AI Command Center

This is the primary feature.

Large conversational input.

Example placeholder

"Ask HR anything or automate a task..."

Suggested prompts

Generate an experience letter.

Apply for leave.

Show company leave policy.

Find all employees in Engineering.

Create onboarding workflow.

---

# AI Conversation

Messages should appear as conversation bubbles.

Each AI response should display

Reasoning Summary

Tools Used

Documents Retrieved

Workflow Status

Execution Time

Source References

Never expose raw chain-of-thought.

Only expose concise execution summaries.

---

# Workflow Timeline

Whenever AI performs actions

Display

Intent Detected

Planning

Knowledge Retrieval

Tool Execution

Approval

Completion

Users should understand what AI is doing.

---

# Quick Actions

Large action cards

Examples

Generate Document

Request Leave

Search Policy

Find Employee

Create Workflow

Ask AI

---

# Employee Pages

Display

Profile Card

Contact Information

Department

Reporting Manager

Documents

Recent Activity

Leave Balance

Performance Summary

Use tabs instead of long scrolling pages.

---

# Tables

Support

Sorting

Filtering

Searching

Pagination

Column Visibility

Bulk Actions

Sticky Headers

Responsive Layout

---

# Forms

Use multi-step forms where appropriate.

Provide

Validation

Helpful error messages

Auto-save (future)

Loading indicators

Success feedback

---

# Analytics

Display

KPI Cards

Trend Charts

Department Comparison

Workflow Metrics

AI Usage

Recent Reports

Use charts only when they improve understanding.

Avoid decorative graphs.

---

# Notifications

Separate

Unread

Read

Archived

Support

Toast Notifications

Notification Center

Workflow Alerts

Approval Requests

---

# Loading States

Use

Skeleton Screens

Progress Indicators

Spinners only for very short operations.

Never leave blank pages during loading.

---

# Empty States

Provide meaningful guidance.

Example

"No documents generated yet."

Include suggested next actions.

---

# Error States

Display

Friendly message

Problem summary

Suggested action

Retry button

Avoid technical jargon.

---

# Accessibility

Meet WCAG AA guidelines.

Support

Keyboard navigation

Screen readers

Visible focus indicators

Color contrast

Responsive text sizing

---

# Responsive Design

Desktop

Laptop

Tablet

Mobile

The interface must remain usable across all supported screen sizes.

---

# Icons

Use

Lucide Icons

Maintain consistent sizing and spacing.

Avoid mixing icon libraries.

---

# Animations

Use subtle animations only.

Examples

Page transitions

Loading indicators

Expandable cards

Notification appearance

Avoid excessive motion.

---

# Performance

Lazy load

Large tables

Charts

AI conversation history

Analytics

Documents

Optimize images and assets.

---

# Design Consistency

Every page should use

Shared spacing

Shared typography

Shared colors

Shared button styles

Shared form components

Shared cards

Shared modals

---

# Component Library

Reusable components include

Buttons

Cards

Inputs

Dropdowns

Tables

Badges

Dialogs

Toast Notifications

Tabs

Accordions

Breadcrumbs

Avatar

Search Bar

Command Palette

---

# Future Enhancements

Voice Input

Dark / Light Theme

Realtime Collaboration

Multi-language Support

Custom Dashboards

AI Personalization

---

# Definition of Completion

The UI/UX implementation is complete when

The interface is modern.

The AI Assistant is the primary interaction method.

Every page follows the design system.

Components are reusable.

The application is responsive.

Accessibility requirements are satisfied.

The user experience clearly reflects an AI-first HR platform rather than a generic CRUD dashboard.
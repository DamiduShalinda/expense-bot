# WhatsApp Expense Tracker – Project Plan

## Overview

A WhatsApp-based chatbot for tracking expenses, credit card usage, and account balances.
Built using Django and regex-based parsing (MVP), with a clean upgrade path to NLP later.

Project management will be handled using **Trello**.
WhatsApp integration will be via **Twilio WhatsApp API** initially (can migrate to WhatsApp Cloud API).

---

## Goals

- Track daily expenses via WhatsApp chat
- Handle credit card billing cycles correctly
- Manage multiple accounts (bank, cash)
- Provide summaries and balances on demand
- Keep MVP simple, reliable, and extensible

---

## Tech Stack

- **Backend**: Django, Django REST Framework
- **Database**: PostgreSQL
- **Async Tasks**: Celery + Redis (reports, reminders)
- **Messaging**: WhatsApp API (Twilio)
- **Project Management**: Trello
- **Deployment**: Docker, AWS / DigitalOcean

---

## High-Level Architecture

WhatsApp User  
↓  
WhatsApp API (Twilio / Cloud API)  
↓  
Webhook (Django DRF)  
↓  
Intent Router  
↓  
Regex Parser  
↓  
Validation Layer  
↓  
Service Layer  
↓  
Django ORM  
↓  
PostgreSQL  

---

## Core Features (MVP)

### 1. Expense Tracking

- Add expense
- Edit expense
- Delete expense
- Categorize expenses
- View monthly summaries

### 2. Credit Card Management

- Billing cycle handling
- Statement-based expenses
- Outstanding amount
- Available credit
- Due date tracking

### 3. Account Management

- Bank accounts
- Cash account
- Balance calculation

---

## Supported Message Formats (Initial)

```text
Spent 1200 on groceries from HDFC card
Paid 450 electricity from SBI account
Show expenses for September
Balance of ICICI card
```

---

## Scope and Assumptions

- PostgreSQL is the primary datastore for all entities.
- WhatsApp messages are received via Twilio webhook; outbound replies use Twilio API.
- The MVP uses regex parsing; later phases may swap in NLP without changing service interfaces.

---

## Milestones

### Milestone 1 — Foundation (Week 1)

- Django project and app scaffolding
- PostgreSQL connection and migrations
- Core models (User, Account, Card, Expense, Category)
- Basic webhook endpoint (no external validation yet)

### Milestone 2 — Core Flow (Week 2)

- Intent Router and Regex Parsing Agent
- Validation Agent rules (duplicates, missing fields)
- Expense Service Agent (create/update/delete)
- Notification Agent responses for success/errors

### Milestone 3 — Queries and Reports (Week 3)

- Balance queries (Account Agent, Credit Card Agent)
- Summary queries (Reporting Agent)
- Monthly aggregation

### Milestone 4 — Reliability and Ops (Week 4)

- Webhook signature validation
- Idempotency for duplicate webhook delivery
- Logging, error monitoring, and audit trail
- Docker packaging

---

## Detailed Implementation Plan

### 1. Data Modeling (PostgreSQL)

- Tables:
  - `users`: WhatsApp number, locale, timezone
  - `accounts`: type (bank/cash), name, balance
  - `cards`: issuer, last4, billing_cycle_day, credit_limit
  - `categories`: name, aliases
  - `expenses`: amount, currency, date, category_id, source_type, source_id, note
  - `messages`: raw_text, parsed_intent, status, idempotency_key
- Indexing:
  - `expenses` on (user_id, date)
  - `expenses` on (user_id, category_id)
  - `messages` on (idempotency_key)

### 2. Webhook Agent

- DRF view for webhook POST
- Verify signature (Twilio)
- Persist raw message + metadata for replay/debugging
- Enqueue processing (Celery) for non-blocking responses

### 3. Intent Router Agent

- Central router: map message to intent via regex list
- Reject ambiguous matches; log for analysis
- Return intent + raw parsed data

### 4. Regex Parsing Agent

- Implement patterns from `REGEX_SPEC.md`
- Normalize input (lowercase, synonym replacement)
- Extract named groups only; reject missing required fields

### 5. Validation Agent

- Check for missing/invalid amounts
- Validate category/source existence
- Detect duplicates in last N minutes with same amount/category/source

### 6. Expense Service Agent

- Create, update, delete expenses
- Adjust balances on create/delete (account/card)
- Assign category fallback when unknown (e.g., "uncategorized")

### 7. Credit Card Agent

- Calculate statement window based on billing cycle
- Provide outstanding balance + available credit

### 8. Account Agent

- Compute current balances from ledger of expenses
- Provide account summaries

### 9. Reporting Agent

- Monthly totals
- Category breakdown
- CSV export (stored in object storage or local path)

### 10. Notification Agent

- Confirmations and errors
- Suggested corrections for missing fields

---

## Trello Board Structure (Suggested)

- Lists:
  - Backlog
  - In Progress
  - Review
  - Done
- Card naming: `[Agent] - Task description`
  - Example: `[Regex Parsing Agent] - Implement expense create pattern`

---

## Testing Strategy

- Unit tests:
  - Regex matching with positive/negative cases
  - Validation rules
  - Billing cycle computations
- Integration tests:
  - Webhook to service layer flow
  - End-to-end message handling

---

## Deployment Notes

- Dockerized Django app
- PostgreSQL as managed service (RDS/DO Managed DB)
- Redis for Celery
- Environment variables for API keys

---

## Open Questions

- Multi-currency support in MVP or later?
- Default categories list?
- Confirmation flow for ambiguous inputs?

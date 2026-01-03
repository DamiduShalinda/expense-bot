
# agents.md

## Purpose

This document defines logical agents (modules/services) used in the WhatsApp Expense Tracker.
Each agent has a single responsibility and communicates via the service layer.

---

## Agent Definitions

### 1. Webhook Agent

**Responsibility**

- Receive WhatsApp messages
- Validate webhook signatures
- Send replies back to WhatsApp API

**Implementation**

- Django REST Framework views

---

### 2. Intent Router Agent

**Responsibility**

- Identify message intent
  - Expense creation
  - Query
  - Balance check
- Route message to appropriate handler

---

### 3. Regex Parsing Agent

**Responsibility**

- Extract structured data from text
  - Amount
  - Category
  - Source (card/account)
  - Date (optional)
- Normalize text input

---

### 4. Validation Agent

**Responsibility**

- Business rule validation
- Detect duplicates
- Handle invalid or incomplete inputs

---

### 5. Expense Service Agent

**Responsibility**

- Create, update, delete expenses
- Assign categories
- Link transactions to accounts/cards

---

### 6. Credit Card Agent

**Responsibility**

- Billing cycle calculations
- Statement grouping
- Outstanding amount calculation
- Available credit calculation

---

### 7. Account Agent

**Responsibility**

- Bank and cash account handling
- Balance computation
- Account-level summaries

---

### 8. Reporting Agent

**Responsibility**

- Monthly summaries
- Category-wise reports
- CSV export generation

---

### 9. Notification Agent

**Responsibility**

- Confirmation prompts
- Error messages
- Reminders (due dates, summaries)

---

## Agent Communication Rules

- Agents communicate via service calls only
- No direct DB access outside service agents
- Agents should be stateless where possible

---

## Notes

- Regex Parsing Agent can be replaced with NLP later
- Each agent should map cleanly to a Django service/module
- Trello cards should reference agent names for clarity

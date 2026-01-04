# Regex Specification – WhatsApp Expense Tracker

## Purpose
This document defines all supported regex patterns used by the Regex Parsing Agent.
It serves as a single source of truth for message formats supported by the system.

Rules:
- Regex patterns must be strict and deterministic
- Ambiguous messages must be rejected
- Every regex must map to a single intent
- Each pattern must extract named groups
- Patterns are anchored with ^ and $

---

## Global Preprocessing Rules

Before applying any regex:
1. Convert message to lowercase
2. Trim whitespace
3. Collapse multiple spaces to a single space
4. Replace synonyms:
   - paid -> spent
   - purchase -> spent
   - bought -> spent
5. Normalize currency symbols (₹, rs -> inr)

---

## Shared Tokens (Reference)

- Amount: `(?P<amount>\d+(?:\.\d{1,2})?)`
- Currency (optional): `(?P<currency>inr)?`
- Category: `(?P<category>[a-z][a-z ]{1,30}[a-z])`
- Source (name): `(?P<source>[a-z0-9][a-z0-9 ]{1,30}[a-z0-9])`
- Source type: `(?P<source_type>card|account|cash)`
- Expense ID: `(?P<expense_id>\d+)`
- Date (ISO): `(?P<date>\d{4}-\d{2}-\d{2})`
- Date (day-month-year): `(?P<date>\d{2}/\d{2}/\d{4})`
- Month name: `(?P<month>jan|january|feb|february|mar|march|apr|april|may|jun|june|jul|july|aug|august|sep|sept|september|oct|october|nov|november|dec|december)`
- Year: `(?P<year>20\d{2})`

Notes:
- Category and source are limited in length to avoid accidental matches.
- Month names are normalized in the Date Parser after regex match.

---

## Intent Categories

- EXPENSE_CREATE
- EXPENSE_UPDATE
- EXPENSE_DELETE
- BALANCE_QUERY
- SUMMARY_QUERY
- CREDIT_CARD_QUERY
- ACCOUNT_LIST
- CARD_LIST
- TRANSACTION_LIST
- ACCOUNT_UPSERT
- CARD_UPSERT
- CATEGORY_LIST
- LOAN_UPSERT
- LOAN_PAYMENT
- LOAN_LIST
- HELP

Each regex pattern must declare:
- Intent
- Description
- Example
- Named capture groups

---

## 1. Expense Creation – Card

### Intent
`EXPENSE_CREATE`

### Description
Creates a new expense linked to a credit card.

### Pattern
`^spent (?P<amount>\d+(?:\.\d{1,2})?) ?(?P<currency>inr)? on (?P<category>[a-z][a-z ]{1,30}[a-z]) from (?P<source>[a-z0-9][a-z0-9 ]{1,30}[a-z0-9]) card(?: last4 (?P<card_last4>\d{4}))?(?: on (?P<date>\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4}))?$`

### Example
spent 1200 on groceries from hdfc card last4 1234

### Named Groups
- amount
- currency
- category
- source
- source_type (implicit = card)
- date (optional)
- card_last4 (optional)

---

## 2. Expense Creation – Account

### Intent
`EXPENSE_CREATE`

### Description
Creates a new expense linked to a bank account or cash.

### Pattern
`^spent (?P<amount>\d+(?:\.\d{1,2})?) ?(?P<currency>inr)? on (?P<category>[a-z][a-z ]{1,30}[a-z]) from (?P<source>[a-z0-9][a-z0-9 ]{1,30}[a-z0-9]) (?P<source_type>account|cash)(?: on (?P<date>\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4}))?$`

### Example
spent 450 on electricity from sbi account

### Named Groups
- amount
- currency
- category
- source
- source_type
- date (optional)

---

## 3. Expense Update – By ID

### Intent
`EXPENSE_UPDATE`

### Description
Updates a specific expense by its numeric id.

### Pattern
`^update expense (?P<expense_id>\d+) amount (?P<amount>\d+(?:\.\d{1,2})?) ?(?P<currency>inr)?(?: category (?P<category>[a-z][a-z ]{1,30}[a-z]))?(?: source (?P<source>[a-z0-9][a-z0-9 ]{1,30}[a-z0-9]) (?P<source_type>card|account|cash)(?: last4 (?P<card_last4>\d{4}))?)?(?: on (?P<date>\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4}))?$`

### Example
update expense 23 amount 2500 category rent source hdfc card on 2024-09-01

### Named Groups
- expense_id
- amount
- currency
- category (optional)
- source (optional)
- source_type (optional)
- card_last4 (optional)
- date (optional)

---

## 4. Expense Delete – By ID

### Intent
`EXPENSE_DELETE`

### Description
Deletes a specific expense by its numeric id.

### Pattern
`^(delete|remove) expense (?P<expense_id>\d+)$`

### Example
delete expense 23

### Named Groups
- expense_id

---

## 5. Balance Query – Account or Cash

### Intent
`BALANCE_QUERY`

### Description
Returns the balance of a bank account or cash.

### Pattern
`^balance of (?P<source>[a-z0-9][a-z0-9 ]{1,30}[a-z0-9]) (?P<source_type>account|cash)$`

### Example
balance of sbi account

### Named Groups
- source
- source_type (implicit = card)
- source_type

---

## 6. Balance Query – Card

### Intent
`BALANCE_QUERY`

### Description
Returns the current balance (spend total) for a credit card.

### Pattern
`^balance of (?P<source>[a-z0-9][a-z0-9 ]{1,30}[a-z0-9]) card(?: last4 (?P<card_last4>\d{4}))?$`

### Example
balance of hdfc card last4 1234

### Named Groups
- source
- card_last4 (optional)

---

## 7. Summary Query – Month Name

### Intent
`SUMMARY_QUERY`

### Description
Returns expense summary for a month by name.

### Pattern
`^(show|summary) expenses for (?P<month>jan|january|feb|february|mar|march|apr|april|may|jun|june|jul|july|aug|august|sep|sept|september|oct|october|nov|november|dec|december)(?: (?P<year>20\d{2}))?$`

### Example
show expenses for september 2024

### Named Groups
- month
- year (optional)

---

## 8. Summary Query – Relative Month

### Intent
`SUMMARY_QUERY`

### Description
Returns expense summary for a relative month window.

### Pattern
`^(show|summary) expenses (?P<relative_period>this month|last month)$`

### Example
summary expenses this month

### Named Groups
- relative_period

---

## 9. Credit Card Query – Due / Available Credit

### Intent
`CREDIT_CARD_QUERY`

### Description
Returns credit card metrics like due amount or available credit.

### Pattern
`^(?P<metric>due|available credit|outstanding) for (?P<source>[a-z0-9][a-z0-9 ]{1,30}[a-z0-9]) card(?: last4 (?P<card_last4>\d{4}))?$`

### Example
available credit for hdfc card last4 1234

### Named Groups
- metric
- source
- card_last4 (optional)

---

## 10. Account List

### Intent
`ACCOUNT_LIST`

### Description
Lists all accounts for the user.

### Pattern
`^((list|show) )?accounts$`

### Example
list accounts

### Named Groups
- None

---

## 11. Card List

### Intent
`CARD_LIST`

### Description
Lists all cards for the user.

### Pattern
`^((list|show) )?cards$`

### Example
show cards

### Named Groups
- None

---

## 12. Transaction List

### Intent
`TRANSACTION_LIST`

### Description
Lists recent transactions (expenses).

### Pattern
`^((list|show) )?(transactions|expenses)$`

### Example
list transactions

### Named Groups
- None

---

## 13. Account Upsert

### Intent
`ACCOUNT_UPSERT`

### Description
Creates or updates an account (bank/cash) with a starting or updated balance.

### Pattern
`^(add|create|update|set) account (?P<source>[a-z0-9][a-z0-9 ]{1,30}[a-z0-9]) (?P<source_type>account|cash) balance (?P<balance>\d+(?:\.\d{1,2})?) ?(?P<currency>inr)?$`

### Example
add account sbi account balance 12000

### Named Groups
- source
- source_type
- balance
- currency (optional)

---

## 14. Card Upsert

### Intent
`CARD_UPSERT`

### Description
Creates or updates a credit card with credit limit, billing cycle, and optional last 4 digits.

### Pattern
`^(add|create|update|set) card (?P<source>[a-z0-9][a-z0-9 ]{1,30}[a-z0-9])(?: card)? limit (?P<credit_limit>\d+(?:\.\d{1,2})?) ?(?P<currency>inr)?(?: cycle (?P<billing_cycle_day>\d{1,2}))?(?: last4 (?P<last4>\d{4}))?$`

### Example
add card hdfc limit 50000 cycle 5 last4 1234

### Named Groups
- source
- credit_limit
- currency (optional)
- billing_cycle_day (optional)
- last4 (optional)

---

## 15. Category List

### Intent
`CATEGORY_LIST`

### Description
Lists all categories and their aggregated spend.

### Pattern
`^((list|show) )?categories$`

### Example
list categories

### Named Groups
- None

---

## 16. Loan Upsert

### Intent
`LOAN_UPSERT`

### Description
Creates or updates a loan with principal amount and optional description.

### Pattern
`^(add|create|set) loan (?P<loan_name>[a-z0-9][a-z0-9 ]{1,40}[a-z0-9]) amount (?P<amount>\d+(?:\.\d{1,2})?) ?(?P<currency>inr)?(?: description (?P<description>[a-z0-9][a-z0-9 ,\.-]{1,120}[a-z0-9]))?$`

### Example
add loan home amount 500000 description home renovation

### Named Groups
- loan_name
- amount
- currency (optional)
- description (optional)

---

## 17. Loan Payment

### Intent
`LOAN_PAYMENT`

### Description
Records a loan payment, allowing partial or full payoff.

### Pattern
`^pay loan (?P<loan_name>[a-z0-9][a-z0-9 ]{1,40}[a-z0-9]) amount (?P<amount>\d+(?:\.\d{1,2})?) ?(?P<currency>inr)?(?: on (?P<date>\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4}))?$`

### Example
pay loan home amount 15000 on 2024-01-15

### Named Groups
- loan_name
- amount
- currency (optional)
- date (optional)

---

## 18. Loan List

### Intent
`LOAN_LIST`

### Description
Lists all loans with outstanding and principal amounts.

### Pattern
`^((list|show) )?loans$`

### Example
list loans

### Named Groups
- None

---

## 19. Help

### Intent
`HELP`

### Description
Lists all supported message formats with examples.

### Pattern
`^(help|commands)$`

### Example
help

### Named Groups
- None

---

## Rejection Rules

- If multiple patterns match, reject with "ambiguous input"
- If any required group is missing, reject with "missing field"
- If amount is zero or negative, reject with "invalid amount"

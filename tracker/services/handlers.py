from django.utils import timezone

from .cards import get_credit_summary, list_cards, upsert_card
from .accounts import (
    describe_account,
    get_balance_summary,
    list_accounts,
    upsert_account,
)
from .categories import list_categories as list_categories_summary
from .expenses import create_expense, delete_expense, list_expenses, update_expense
from .loans import list_loans as list_loans_summary, pay_loan, upsert_loan
from .help import get_help_text
from .notifications import expense_created, expense_deleted, expense_updated
from .reporting import summarize_month, summarize_relative


def handle_intent(user, intent: str, data: dict) -> str:
    if intent == "EXPENSE_CREATE":
        expense = create_expense(user, data)
        return expense_created(expense)
    if intent == "EXPENSE_UPDATE":
        expense = update_expense(user, data)
        if not expense:
            return "Expense not found."
        return expense_updated(expense)
    if intent == "EXPENSE_DELETE":
        deleted, restored_account = delete_expense(user, data["expense_id"])
        if not deleted:
            return "Expense not found."
        return expense_deleted(data["expense_id"], restored_account)
    if intent == "BALANCE_QUERY":
        if data.get("source_type") == "card":
            return get_credit_summary(
                user, data["source"], "outstanding", data.get("card_last4")
            )
        return get_balance_summary(user, data["source"], data["source_type"])
    if intent == "SUMMARY_QUERY":
        if data.get("relative_period"):
            return summarize_relative(user, data["relative_period"])
        return summarize_month(user, data["month"], data.get("year"))
    if intent == "CREDIT_CARD_QUERY":
        return get_credit_summary(
            user, data["source"], data["metric"], data.get("card_last4")
        )
    if intent == "ACCOUNT_LIST":
        return list_accounts(user)
    if intent == "CARD_LIST":
        return list_cards(user)
    if intent == "TRANSACTION_LIST":
        return list_expenses(user)
    if intent == "CATEGORY_LIST":
        return list_categories_summary(user)
    if intent == "LOAN_LIST":
        return list_loans_summary(user)
    if intent == "ACCOUNT_UPSERT":
        account, created = upsert_account(
            user,
            data["source"],
            data["source_type"],
            balance=data.get("balance"),
        )
        action = "Created" if created else "Updated"
        return f"{action} {describe_account(account)}"
    if intent == "CARD_UPSERT":
        card, created = upsert_card(
            user,
            data["source"],
            credit_limit=data.get("credit_limit"),
            billing_cycle_day=data.get("billing_cycle_day"),
            last4=data.get("last4"),
        )
        action = "Created" if created else "Updated"
        suffix = f" {card.last4}" if card.last4 else ""
        return (
            f"{action} {card.issuer}{suffix} card. "
            f"Limit {card.credit_limit:.2f} inr, billing cycle day {card.billing_cycle_day}."
        )
    if intent == "LOAN_UPSERT":
        loan, created = upsert_loan(
            user,
            data["loan_name"],
            data["amount"],
            description=data.get("description"),
        )
        action = "Created" if created else "Updated"
        return (
            f"{action} loan {loan.name}. Outstanding {loan.outstanding_amount:.2f} "
            f"inr on principal {loan.principal_amount:.2f} inr."
        )
    if intent == "LOAN_PAYMENT":
        paid_on = data.get("date") or timezone.localdate()
        loan, message = pay_loan(user, data["loan_name"], data["amount"], paid_on)
        if loan is None:
            return message
        return message
    if intent == "HELP":
        return get_help_text()
    return "Unsupported request."

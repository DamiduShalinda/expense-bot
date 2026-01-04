from ..models import Expense
from .cards import get_outstanding


def _account_status(expense: Expense) -> str:
    if not expense.source_account:
        return ""
    account = expense.source_account
    return f" Remaining {account.name} {account.type} balance: {account.balance:.2f} inr."


def _card_status(expense: Expense) -> str:
    if not expense.source_card:
        return ""
    card = expense.source_card
    outstanding = get_outstanding(card)
    available = card.credit_limit - outstanding
    suffix = f" {card.last4}" if card.last4 else ""
    card_name = f"{card.issuer}{suffix}".strip()
    return (
        f" Outstanding on {card_name}: {outstanding:.2f} inr. "
        f"Available credit: {available:.2f} inr."
    )


def expense_created(expense: Expense) -> str:
    category = expense.category.name if expense.category else "uncategorized"
    message = (
        f"Added expense {expense.amount:.2f} {expense.currency} for {category} "
        f"on {expense.date}."
    )
    if expense.source_account:
        message += _account_status(expense)
    elif expense.source_card:
        message += _card_status(expense)
    return message


def expense_updated(expense: Expense) -> str:
    message = f"Updated expense {expense.id}."
    if expense.source_account:
        message += _account_status(expense)
    elif expense.source_card:
        message += _card_status(expense)
    return message


def expense_deleted(expense_id: int, account=None) -> str:
    message = f"Deleted expense {expense_id}."
    if account:
        message += f" Restored {account.name} {account.type} balance: {account.balance:.2f} inr."
    return message


def error(message: str) -> str:
    return message

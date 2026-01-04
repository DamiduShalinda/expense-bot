from ..models import Expense
from .cards import get_outstanding
from .currency import get_user_currency


def _account_status(expense: Expense) -> str:
    if not expense.source_account:
        return ""
    account = expense.source_account
    currency = get_user_currency(account.user).upper()
    return f" Remaining {account.name} {account.type} balance: {account.balance:.2f} {currency}."


def _card_status(expense: Expense) -> str:
    if not expense.source_card:
        return ""
    card = expense.source_card
    outstanding = get_outstanding(card)
    available = card.credit_limit - outstanding
    suffix = f" {card.last4}" if card.last4 else ""
    card_name = f"{card.issuer}{suffix}".strip()
    currency = get_user_currency(card.user).upper()
    return (
        f" Outstanding on {card_name}: {outstanding:.2f} {currency}. "
        f"Available credit: {available:.2f} {currency}."
    )


def expense_created(expense: Expense) -> str:
    category = expense.category.name if expense.category else "uncategorized"
    message = (
        f"Added expense {expense.amount:.2f} {expense.currency.upper()} for {category} "
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
        currency = get_user_currency(account.user).upper()
        message += (
            f" Restored {account.name} {account.type} balance: {account.balance:.2f} {currency}."
        )
    return message


def error(message: str) -> str:
    return message

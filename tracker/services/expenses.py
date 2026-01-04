from django.utils import timezone

from ..models import Category, Expense
from .accounts import adjust_balance, get_or_create_account
from .cards import get_or_create_card
from .currency import get_user_currency, normalize_currency_code


def _get_or_create_category(user, name: str | None) -> Category | None:
    if not name:
        return None
    category, _created = Category.objects.get_or_create(user=user, name=name.strip())
    return category


def create_expense(user, data: dict) -> Expense:
    category = _get_or_create_category(user, data.get("category"))
    source_type = data.get("source_type")
    source_account = None
    source_card = None

    if source_type in {"account", "cash"}:
        source_account = get_or_create_account(user, data["source"], source_type)
    elif source_type == "card":
        source_card = get_or_create_card(user, data["source"], data.get("card_last4"))

    currency_code = normalize_currency_code(
        data.get("currency") or get_user_currency(user)
    )

    expense = Expense.objects.create(
        user=user,
        amount=data["amount"],
        currency=currency_code,
        date=data.get("date") or timezone.localdate(),
        category=category,
        source_type=source_type,
        source_account=source_account,
        source_card=source_card,
    )

    if source_account:
        adjust_balance(source_account, -expense.amount)
    return expense


def update_expense(user, data: dict) -> Expense | None:
    expense = Expense.objects.filter(user=user, id=data["expense_id"]).first()
    if not expense:
        return None

    original_account = expense.source_account
    original_card = expense.source_card
    original_amount = expense.amount

    if data.get("amount") is not None:
        expense.amount = data["amount"]
    if data.get("currency"):
        expense.currency = normalize_currency_code(data["currency"])
    if data.get("date"):
        expense.date = data["date"]
    if data.get("category"):
        expense.category = _get_or_create_category(user, data["category"])

    if data.get("source") and data.get("source_type"):
        if data["source_type"] in {"account", "cash"}:
            expense.source_account = get_or_create_account(
                user, data["source"], data["source_type"]
            )
            expense.source_card = None
        else:
            expense.source_card = get_or_create_card(
                user, data["source"], data.get("card_last4")
            )
            expense.source_account = None
        expense.source_type = data["source_type"]

    expense.save()

    if original_account or expense.source_account:
        if original_account:
            adjust_balance(original_account, original_amount)
        if expense.source_account:
            adjust_balance(expense.source_account, -expense.amount)

    return expense


def delete_expense(user, expense_id: int):
    expense = Expense.objects.filter(user=user, id=expense_id).first()
    if not expense:
        return False, None
    restored_account = expense.source_account
    if restored_account:
        adjust_balance(restored_account, expense.amount)
    expense.delete()
    return True, restored_account


def list_expenses(user, limit: int = 10) -> str:
    expenses = Expense.objects.filter(user=user).order_by("-date", "-id")[:limit]
    if not expenses:
        return "No transactions found."
    lines = []
    for expense in expenses:
        category = expense.category.name if expense.category else "uncategorized"
        source = "unknown"
        if expense.source_type in {"account", "cash"} and expense.source_account:
            source = f"{expense.source_account.name} {expense.source_type}"
        elif expense.source_type == "card" and expense.source_card:
            source = f"{expense.source_card.issuer} card"
        lines.append(
            f"- {expense.amount:.2f} {expense.currency.upper()} on {category} from {source} on {expense.date}"
        )
    return "Recent transactions:\n" + "\n".join(lines)

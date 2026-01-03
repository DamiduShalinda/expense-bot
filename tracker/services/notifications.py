from ..models import Expense


def expense_created(expense: Expense) -> str:
    category = expense.category.name if expense.category else "uncategorized"
    return (
        f"Added expense {expense.amount:.2f} {expense.currency} for {category} "
        f"on {expense.date}."
    )


def expense_updated(expense: Expense) -> str:
    return f"Updated expense {expense.id}."


def expense_deleted(expense_id: int) -> str:
    return f"Deleted expense {expense_id}."


def error(message: str) -> str:
    return message

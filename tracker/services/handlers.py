from .cards import get_credit_summary, list_cards
from .accounts import get_balance_summary, list_accounts
from .expenses import create_expense, delete_expense, list_expenses, update_expense
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
        deleted = delete_expense(user, data["expense_id"])
        if not deleted:
            return "Expense not found."
        return expense_deleted(data["expense_id"])
    if intent == "BALANCE_QUERY":
        if data.get("source_type") == "card":
            return get_credit_summary(user, data["source"], "outstanding")
        return get_balance_summary(user, data["source"], data["source_type"])
    if intent == "SUMMARY_QUERY":
        if data.get("relative_period"):
            return summarize_relative(user, data["relative_period"])
        return summarize_month(user, data["month"], data.get("year"))
    if intent == "CREDIT_CARD_QUERY":
        return get_credit_summary(user, data["source"], data["metric"])
    if intent == "ACCOUNT_LIST":
        return list_accounts(user)
    if intent == "CARD_LIST":
        return list_cards(user)
    if intent == "TRANSACTION_LIST":
        return list_expenses(user)
    if intent == "HELP":
        return get_help_text()
    return "Unsupported request."

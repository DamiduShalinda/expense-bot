from datetime import timedelta

from django.utils import timezone

from .errors import ValidationError
from ..models import Expense


def validate_payload(intent: str, data: dict, user):
    amount = data.get("amount")
    if intent in {"EXPENSE_CREATE", "EXPENSE_UPDATE"}:
        if amount is None:
            raise ValidationError("Missing amount.")
        if amount <= 0:
            raise ValidationError("Amount must be greater than zero.")

    if intent == "EXPENSE_CREATE":
        category = data.get("category")
        source = data.get("source")
        if not category or not source:
            raise ValidationError("Missing category or source.")

        duplicate_window = timezone.now() - timedelta(minutes=10)
        if data.get("source_type") == "card":
            source_filter = {"source_card__issuer__iexact": source}
        elif data.get("source_type") in {"account", "cash"}:
            source_filter = {"source_account__name__iexact": source}
        else:
            source_filter = {}

        duplicate = Expense.objects.filter(
            user=user,
            amount=amount,
            category__name__iexact=category,
            created_at__gte=duplicate_window,
            **source_filter,
        ).exists()
        if duplicate:
            raise ValidationError("Potential duplicate detected. Please confirm.")

    if intent in {"EXPENSE_UPDATE", "EXPENSE_DELETE"} and not data.get("expense_id"):
        raise ValidationError("Missing expense id.")

    if intent == "ACCOUNT_UPSERT":
        balance = data.get("balance")
        if balance is None:
            raise ValidationError("Missing balance.")
        if balance < 0:
            raise ValidationError("Balance must be zero or greater.")
        if data.get("source_type") not in {"account", "cash"}:
            raise ValidationError("Invalid account type.")
        if not data.get("source"):
            raise ValidationError("Missing account name.")

    if intent == "CARD_UPSERT":
        credit_limit = data.get("credit_limit")
        if credit_limit is None:
            raise ValidationError("Missing credit limit.")
        if credit_limit <= 0:
            raise ValidationError("Credit limit must be greater than zero.")
        cycle_day = data.get("billing_cycle_day")
        if cycle_day is not None and not (1 <= cycle_day <= 31):
            raise ValidationError("Billing cycle day must be between 1 and 31.")

    if intent == "LOAN_UPSERT":
        loan_amount = data.get("amount")
        if loan_amount is None or loan_amount <= 0:
            raise ValidationError("Loan amount must be greater than zero.")
        if not data.get("loan_name"):
            raise ValidationError("Missing loan name.")

    if intent == "LOAN_PAYMENT":
        payment_amount = data.get("amount")
        if payment_amount is None or payment_amount <= 0:
            raise ValidationError("Payment amount must be greater than zero.")
        if not data.get("loan_name"):
            raise ValidationError("Missing loan name.")

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

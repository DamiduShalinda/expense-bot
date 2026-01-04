from decimal import Decimal

from django.db import models
from django.db.models.functions import Coalesce

from ..models import Category
from .currency import get_user_currency


def list_categories(user) -> str:
    currency = get_user_currency(user).upper()
    categories = (
        Category.objects.filter(user=user)
        .annotate(
            total=Coalesce(
                models.Sum("expense__amount"),
                models.Value(Decimal("0.00")),
            )
        )
        .order_by("name")
    )
    if not categories:
        return "No categories found."
    lines: list[str] = []
    for category in categories:
        alias_count = len(category.aliases or [])
        alias_text = f", {alias_count} alias(es)" if alias_count else ""
        lines.append(f"- {category.name}: {category.total:.2f} {currency}{alias_text}")
    return "Categories:\n" + "\n".join(lines)

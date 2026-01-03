from datetime import date, timedelta
from decimal import Decimal

from django.db import models
from django.utils import timezone

from ..models import Card, Expense


def get_or_create_card(user, issuer: str) -> Card:
    card, _created = Card.objects.get_or_create(
        user=user,
        issuer=issuer.strip(),
        defaults={"credit_limit": Decimal("0.00")},
    )
    return card


def _statement_window(billing_cycle_day: int, today: date | None = None):
    if today is None:
        today = timezone.localdate()
    if billing_cycle_day < 1:
        billing_cycle_day = 1
    cycle_day = min(billing_cycle_day, 28)
    if today.day >= cycle_day:
        start = date(today.year, today.month, cycle_day)
    else:
        previous_month = today.replace(day=1) - timedelta(days=1)
        start = date(previous_month.year, previous_month.month, cycle_day)
    next_month = (start.replace(day=1) + timedelta(days=32)).replace(day=1)
    end = next_month - timedelta(days=1)
    return start, end


def get_outstanding(card: Card) -> Decimal:
    start, end = _statement_window(card.billing_cycle_day)
    total = (
        Expense.objects.filter(
            source_card=card,
            date__gte=start,
            date__lte=end,
        )
        .aggregate(total=models.Sum("amount"))
        .get("total")
    )
    return total or Decimal("0.00")


def get_credit_summary(user, issuer: str, metric: str) -> str:
    card = Card.objects.filter(user=user, issuer__iexact=issuer.strip()).first()
    if not card:
        return f"No card named {issuer} found."
    outstanding = get_outstanding(card)
    available = card.credit_limit - outstanding
    if metric == "available credit":
        return f"Available credit for {card.issuer}: {available:.2f} inr"
    if metric == "due":
        return f"Due amount for {card.issuer}: {outstanding:.2f} inr"
    return f"Outstanding for {card.issuer}: {outstanding:.2f} inr"


def list_cards(user) -> str:
    cards = Card.objects.filter(user=user).order_by("issuer", "last4")
    if not cards:
        return "No cards found."
    lines = []
    for card in cards:
        suffix = f" {card.last4}" if card.last4 else ""
        lines.append(f"- {card.issuer}{suffix}")
    return "Cards:\n" + "\n".join(lines)

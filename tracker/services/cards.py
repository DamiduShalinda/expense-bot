from datetime import date, timedelta
from decimal import Decimal

from django.db import models
from django.utils import timezone

from ..models import Card, Expense
from .currency import get_user_currency
from .errors import ValidationError


def _normalize_last4(last4: str | None) -> str:
    return (last4 or "").strip()


def _card_queryset(user, issuer: str, last4: str | None = None):
    qs = Card.objects.filter(user=user, issuer__iexact=issuer.strip())
    normalized_last4 = _normalize_last4(last4)
    if normalized_last4:
        qs = qs.filter(last4__iexact=normalized_last4)
    return qs


def get_or_create_card(user, issuer: str, last4: str | None = None) -> Card:
    qs = _card_queryset(user, issuer, last4)
    cards = list(qs)
    if cards:
        if len(cards) > 1 and not _normalize_last4(last4):
            raise ValidationError(f"Multiple cards found for {issuer}. Please include last4 digits.")
        return cards[0]
    normalized_last4 = _normalize_last4(last4)
    card = Card.objects.create(
        user=user,
        issuer=issuer.strip(),
        last4=normalized_last4,
        credit_limit=Decimal("0.00"),
    )
    return card


def upsert_card(
    user,
    issuer: str,
    credit_limit: Decimal | None = None,
    billing_cycle_day: int | None = None,
    last4: str | None = None,
):
    formatted_last4 = _normalize_last4(last4)
    card, created = Card.objects.get_or_create(
        user=user,
        issuer=issuer.strip(),
        last4=formatted_last4,
        defaults={
            "billing_cycle_day": billing_cycle_day or 1,
            "credit_limit": credit_limit or Decimal("0.00"),
        },
    )
    update_fields: list[str] = []
    if credit_limit is not None and card.credit_limit != credit_limit:
        card.credit_limit = credit_limit
        update_fields.append("credit_limit")
    if billing_cycle_day is not None and card.billing_cycle_day != billing_cycle_day:
        card.billing_cycle_day = billing_cycle_day
        update_fields.append("billing_cycle_day")
    if formatted_last4 and card.last4 != formatted_last4:
        card.last4 = formatted_last4
        update_fields.append("last4")
    if update_fields:
        card.save(update_fields=update_fields)
    return card, created


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


def get_credit_summary(user, issuer: str, metric: str, last4: str | None = None) -> str:
    currency = get_user_currency(user).upper()
    cards = list(_card_queryset(user, issuer, last4))
    normalized_last4 = _normalize_last4(last4)
    if not cards:
        suffix = f" ending {normalized_last4}" if normalized_last4 else ""
        return f"No card named {issuer}{suffix} found."
    if len(cards) > 1 and not normalized_last4:
        return f"Multiple cards found for {issuer}. Please specify last4 digits."
    card = cards[0]
    outstanding = get_outstanding(card)
    card_name = f"{card.issuer} {card.last4}".strip()
    available = card.credit_limit - outstanding
    if metric == "available credit":
        return f"Available credit for {card_name}: {available:.2f} {currency}"
    if metric == "due":
        return f"Due amount for {card_name}: {outstanding:.2f} {currency}"
    return f"Outstanding for {card_name}: {outstanding:.2f} {currency}"


def list_cards(user) -> str:
    currency = get_user_currency(user).upper()
    cards = Card.objects.filter(user=user).order_by("issuer", "last4")
    if not cards:
        return "No cards found."
    lines = []
    for card in cards:
        suffix = f" {card.last4}" if card.last4 else ""
        outstanding = get_outstanding(card)
        available = card.credit_limit - outstanding
        lines.append(
            f"- {card.issuer}{suffix} | limit {card.credit_limit:.2f} {currency} | "
            f"outstanding {outstanding:.2f} {currency} | available {available:.2f} {currency}"
        )
    return "Cards:\n" + "\n".join(lines)

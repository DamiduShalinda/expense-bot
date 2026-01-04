from calendar import monthrange
from datetime import date, timedelta

from django.db.models import Sum
from django.utils import timezone

from ..models import Expense
from .currency import get_user_currency


MONTH_MAP = {
    "jan": 1,
    "january": 1,
    "feb": 2,
    "february": 2,
    "mar": 3,
    "march": 3,
    "apr": 4,
    "april": 4,
    "may": 5,
    "jun": 6,
    "june": 6,
    "jul": 7,
    "july": 7,
    "aug": 8,
    "august": 8,
    "sep": 9,
    "sept": 9,
    "september": 9,
    "oct": 10,
    "october": 10,
    "nov": 11,
    "november": 11,
    "dec": 12,
    "december": 12,
}


def _month_window(month: int, year: int):
    last_day = monthrange(year, month)[1]
    return date(year, month, 1), date(year, month, last_day)


def summarize_month(user, month_name: str, year: int | None) -> str:
    month = MONTH_MAP.get(month_name)
    if not month:
        return "Invalid month."
    if not year:
        year = timezone.localdate().year
    start, end = _month_window(month, year)
    total = (
        Expense.objects.filter(user=user, date__gte=start, date__lte=end)
        .aggregate(total=Sum("amount"))
        .get("total")
    ) or 0
    currency = get_user_currency(user).upper()
    return f"Total expenses for {month_name} {year}: {total:.2f} {currency}"


def summarize_relative(user, relative_period: str) -> str:
    today = timezone.localdate()
    if relative_period == "this month":
        start, end = _month_window(today.month, today.year)
    else:
        prev_month = today.replace(day=1) - timedelta(days=1)
        start, end = _month_window(prev_month.month, prev_month.year)
    total = (
        Expense.objects.filter(user=user, date__gte=start, date__lte=end)
        .aggregate(total=Sum("amount"))
        .get("total")
    ) or 0
    currency = get_user_currency(user).upper()
    return f"Total expenses for {relative_period}: {total:.2f} {currency}"

import re
from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from django.utils import timezone


@dataclass(frozen=True)
class ParsedMatch:
    intent: str
    data: dict[str, Any]
    pattern_name: str


_SPACE_RE = re.compile(r"\s+")
_CURRENCY_RE = re.compile(r"(₹|rs\.?)", re.IGNORECASE)


def preprocess_message(text: str) -> str:
    normalized = text.strip().lower()
    normalized = _SPACE_RE.sub(" ", normalized)
    normalized = normalized.replace("paid", "spent")
    normalized = normalized.replace("purchase", "spent")
    normalized = normalized.replace("bought", "spent")
    normalized = _CURRENCY_RE.sub("inr", normalized)
    return normalized


def _parse_amount(value: str | None) -> Decimal | None:
    if not value:
        return None
    return Decimal(value)


def _parse_int(value: str | None) -> int | None:
    if not value:
        return None
    return int(value)


def _parse_date(value: str | None):
    if not value:
        return None
    if "-" in value:
        return timezone.datetime.strptime(value, "%Y-%m-%d").date()
    return timezone.datetime.strptime(value, "%d/%m/%Y").date()


PATTERNS = [
    {
        "name": "expense_create_card",
        "intent": "EXPENSE_CREATE",
        "pattern": re.compile(
            r"^spent (?P<amount>\d+(?:\.\d{1,2})?) ?(?P<currency>inr)? on "
            r"(?P<category>[a-z][a-z ]{1,30}[a-z]) from "
            r"(?P<source>[a-z0-9][a-z0-9 ]{1,30}[a-z0-9]) card"
            r"(?: last4 (?P<card_last4>\d{4}))?"
            r"(?: on (?P<date>\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4}))?$"
        ),
    },
    {
        "name": "expense_create_account",
        "intent": "EXPENSE_CREATE",
        "pattern": re.compile(
            r"^spent (?P<amount>\d+(?:\.\d{1,2})?) ?(?P<currency>inr)? on "
            r"(?P<category>[a-z][a-z ]{1,30}[a-z]) from "
            r"(?P<source>[a-z0-9][a-z0-9 ]{1,30}[a-z0-9]) "
            r"(?P<source_type>account|cash)"
            r"(?: on (?P<date>\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4}))?$"
        ),
    },
    {
        "name": "expense_update",
        "intent": "EXPENSE_UPDATE",
        "pattern": re.compile(
            r"^update expense (?P<expense_id>\d+) amount "
            r"(?P<amount>\d+(?:\.\d{1,2})?) ?(?P<currency>inr)?"
            r"(?: category (?P<category>[a-z][a-z ]{1,30}[a-z]))?"
            r"(?: source (?P<source>[a-z0-9][a-z0-9 ]{1,30}[a-z0-9]) "
            r"(?P<source_type>card|account|cash)"
            r"(?: last4 (?P<card_last4>\d{4}))?)?"
            r"(?: on (?P<date>\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4}))?$"
        ),
    },
    {
        "name": "expense_delete",
        "intent": "EXPENSE_DELETE",
        "pattern": re.compile(r"^(delete|remove) expense (?P<expense_id>\d+)$"),
    },
    {
        "name": "balance_query_account",
        "intent": "BALANCE_QUERY",
        "pattern": re.compile(
            r"^balance of (?P<source>[a-z0-9][a-z0-9 ]{1,30}[a-z0-9]) "
            r"(?P<source_type>account|cash)$"
        ),
    },
    {
        "name": "balance_query_card",
        "intent": "BALANCE_QUERY",
        "pattern": re.compile(
            r"^balance of (?P<source>[a-z0-9][a-z0-9 ]{1,30}[a-z0-9]) card"
            r"(?: last4 (?P<card_last4>\d{4}))?$"
        ),
    },
    {
        "name": "summary_query_month",
        "intent": "SUMMARY_QUERY",
        "pattern": re.compile(
            r"^(show|summary) expenses for (?P<month>jan|january|feb|february|mar|march|"
            r"apr|april|may|jun|june|jul|july|aug|august|sep|sept|september|oct|october|"
            r"nov|november|dec|december)(?: (?P<year>20\d{2}))?$"
        ),
    },
    {
        "name": "summary_query_relative",
        "intent": "SUMMARY_QUERY",
        "pattern": re.compile(r"^(show|summary) expenses (?P<relative_period>this month|last month)$"),
    },
    {
        "name": "credit_card_query",
        "intent": "CREDIT_CARD_QUERY",
        "pattern": re.compile(
            r"^(?P<metric>due|available credit|outstanding) for "
            r"(?P<source>[a-z0-9][a-z0-9 ]{1,30}[a-z0-9]) card"
            r"(?: last4 (?P<card_last4>\d{4}))?$"
        ),
    },
    {
        "name": "account_list",
        "intent": "ACCOUNT_LIST",
        "pattern": re.compile(r"^((list|show) )?accounts$"),
    },
    {
        "name": "card_list",
        "intent": "CARD_LIST",
        "pattern": re.compile(r"^((list|show) )?cards$"),
    },
    {
        "name": "transaction_list",
        "intent": "TRANSACTION_LIST",
        "pattern": re.compile(r"^((list|show) )?(transactions|expenses)$"),
    },
    {
        "name": "loan_upsert",
        "intent": "LOAN_UPSERT",
        "pattern": re.compile(
            r"^(add|create|set) loan "
            r"(?P<loan_name>[a-z0-9][a-z0-9 ]{1,40}[a-z0-9]) amount "
            r"(?P<amount>\d+(?:\.\d{1,2})?) ?(?P<currency>inr)?"
            r"(?: description (?P<description>[a-z0-9][a-z0-9 ,\.-]{1,120}[a-z0-9]))?$"
        ),
    },
    {
        "name": "loan_payment",
        "intent": "LOAN_PAYMENT",
        "pattern": re.compile(
            r"^pay loan (?P<loan_name>[a-z0-9][a-z0-9 ]{1,40}[a-z0-9]) amount "
            r"(?P<amount>\d+(?:\.\d{1,2})?) ?(?P<currency>inr)?"
            r"(?: on (?P<date>\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4}))?$"
        ),
    },
    {
        "name": "loan_list",
        "intent": "LOAN_LIST",
        "pattern": re.compile(r"^((list|show) )?loans$"),
    },
    {
        "name": "account_upsert",
        "intent": "ACCOUNT_UPSERT",
        "pattern": re.compile(
            r"^(add|create|update|set) account "
            r"(?P<source>[a-z0-9][a-z0-9 ]{1,30}[a-z0-9]) "
            r"(?P<source_type>account|cash) balance "
            r"(?P<balance>\d+(?:\.\d{1,2})?) ?(?P<currency>inr)?$"
        ),
    },
    {
        "name": "card_upsert",
        "intent": "CARD_UPSERT",
        "pattern": re.compile(
            r"^(add|create|update|set) card "
            r"(?P<source>[a-z0-9][a-z0-9 ]{1,30}[a-z0-9])(?: card)? "
            r"limit (?P<credit_limit>\d+(?:\.\d{1,2})?) ?(?P<currency>inr)?"
            r"(?: cycle (?P<billing_cycle_day>\d{1,2}))?"
            r"(?: last4 (?P<last4>\d{4}))?$"
        ),
    },
    {
        "name": "category_list",
        "intent": "CATEGORY_LIST",
        "pattern": re.compile(r"^((list|show) )?categories$"),
    },
    {
        "name": "help",
        "intent": "HELP",
        "pattern": re.compile(r"^(help|commands)$"),
    },
]


def parse_message(text: str) -> list[ParsedMatch]:
    normalized = preprocess_message(text)
    matches: list[ParsedMatch] = []
    for spec in PATTERNS:
        match = spec["pattern"].match(normalized)
        if not match:
            continue
        data = match.groupdict()
        if spec["name"] == "expense_create_card":
            data["source_type"] = "card"
        if spec["name"] == "balance_query_card":
            data["source_type"] = "card"
        data["amount"] = _parse_amount(data.get("amount"))
        data["balance"] = _parse_amount(data.get("balance"))
        data["credit_limit"] = _parse_amount(data.get("credit_limit"))
        data["billing_cycle_day"] = _parse_int(data.get("billing_cycle_day"))
        data["expense_id"] = int(data["expense_id"]) if data.get("expense_id") else None
        data["date"] = _parse_date(data.get("date"))
        if data.get("card_last4"):
            data["card_last4"] = data["card_last4"].strip()
        matches.append(ParsedMatch(intent=spec["intent"], data=data, pattern_name=spec["name"]))
    return matches

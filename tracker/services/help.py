_GENERAL_HELP = [
    "Supported commands (use 'help accounts', 'help cards', 'help transactions', 'help categories', 'help loans', 'help summary', or 'help settings' for focused help):",
    "- spent 1200 on groceries from hdfc card",
    "- spent 450 on electricity from sbi account",
    "- spent 300 on snacks from wallet cash",
    "- spent 900 on fuel from hdfc card last4 1234",
    "- update expense 23 amount 2500 category rent source hdfc card on 2024-09-01",
    "- delete expense 23",
    "- balance of sbi account",
    "- balance of hdfc card last4 1234",
    "- show expenses for september 2024",
    "- summary expenses this month",
    "- available credit for hdfc card",
    "- add account sbi account balance 12000",
    "- add card hdfc limit 50000 cycle 5 last4 1234",
    "- add loan home amount 500000 description home renovation",
    "- pay loan home amount 15000 on 2024-01-15",
    "- list accounts",
    "- show cards",
    "- list categories",
    "- list loans",
    "- list transactions",
    "- set currency usd",
]

_TOPICAL_HELP = {
    "accounts": [
        "Accounts help:",
        "- list accounts",
        "- add account sbi account balance 12000",
        "- add account wallet cash balance 500",
        "- balance of sbi account",
        "- balance of wallet cash",
        "- update account sbi account balance 15000",
    ],
    "cards": [
        "Cards help:",
        "- show cards",
        "- add card hdfc limit 50000 cycle 5 last4 1234",
        "- available credit for hdfc card last4 1234",
        "- outstanding for hdfc card",
        "- due for hdfc card last4 1234",
    ],
    "transactions": [
        "Transactions help:",
        "- spent 1200 on groceries from hdfc card",
        "- spent 450 on electricity from sbi account",
        "- update expense 23 amount 2500 category rent source hdfc card on 2024-09-01",
        "- delete expense 23",
        "- list transactions",
        "- show expenses for september 2024",
    ],
    "categories": [
        "Categories help:",
        "- list categories",
        "- summary expenses this month",
        "- show expenses for september 2024",
        "- summary expenses last month",
    ],
    "loans": [
        "Loans help:",
        "- add loan home amount 500000 description home renovation",
        "- pay loan home amount 15000 on 2024-01-15",
        "- list loans",
    ],
    "summary": [
        "Summary help:",
        "- summary expenses this month",
        "- summary expenses last month",
        "- show expenses for september 2024",
        "- show expenses for december 2024",
    ],
    "settings": [
        "Settings help:",
        "- set currency usd",
        "- set default currency sar",
        "- update currency eur",
        "Currency commands change the default for all future expenses unless explicitly overridden.",
    ],
}

_TOPIC_ALIASES = {
    "account": "accounts",
    "accounts": "accounts",
    "cash": "accounts",
    "card": "cards",
    "cards": "cards",
    "credit card": "cards",
    "credit cards": "cards",
    "transaction": "transactions",
    "transactions": "transactions",
    "expense": "transactions",
    "expenses": "transactions",
    "category": "categories",
    "categories": "categories",
    "loan": "loans",
    "loans": "loans",
    "summary": "summary",
    "summaries": "summary",
    "report": "summary",
    "reports": "summary",
    "general": "general",
    "setting": "settings",
    "settings": "settings",
    "currency": "settings",
    "currencies": "settings",
    "default currency": "settings",
}


def _render(lines: list[str]) -> str:
    return "\n".join(lines)


def _normalize_topic(topic: str | None) -> str | None:
    if not topic:
        return None
    normalized = " ".join(topic.strip().split())
    normalized = normalized.lower()
    if not normalized:
        return None
    return _TOPIC_ALIASES.get(normalized, normalized)


def get_help_text(topic: str | None = None) -> str:
    normalized_topic = _normalize_topic(topic)
    if not normalized_topic or normalized_topic == "general":
        return _render(_GENERAL_HELP)
    section = _TOPICAL_HELP.get(normalized_topic)
    if section:
        return _render(section)
    return _render(_GENERAL_HELP)

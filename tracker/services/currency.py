DEFAULT_CURRENCY = "inr"


def normalize_currency_code(code: str | None) -> str:
    if not code:
        return DEFAULT_CURRENCY
    normalized = code.strip().lower()
    return normalized or DEFAULT_CURRENCY


def get_user_currency(user) -> str:
    return normalize_currency_code(getattr(user, "default_currency", None))

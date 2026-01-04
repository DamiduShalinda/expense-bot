from .currency import get_user_currency, normalize_currency_code


def set_default_currency(user, currency_code: str):
    normalized = normalize_currency_code(currency_code)
    changed = normalized != get_user_currency(user)
    if changed:
        user.default_currency = normalized
        user.save(update_fields=["default_currency"])
    return normalized, changed

from decimal import Decimal

from ..models import Account
from .currency import get_user_currency


def get_or_create_account(user, name: str, account_type: str) -> Account:
    account, _created = Account.objects.get_or_create(
        user=user,
        name=name.strip(),
        type=account_type,
        defaults={"balance": Decimal("0.00")},
    )
    return account


def upsert_account(user, name: str, account_type: str, balance: Decimal | None = None):
    account, created = Account.objects.get_or_create(
        user=user,
        name=name.strip(),
        type=account_type,
        defaults={"balance": balance or Decimal("0.00")},
    )
    update_fields: list[str] = []
    if balance is not None and account.balance != balance:
        account.balance = balance
        update_fields.append("balance")
    if update_fields:
        account.save(update_fields=update_fields)
    return account, created


def adjust_balance(account: Account, delta: Decimal):
    account.balance += delta
    account.save(update_fields=["balance"])


def describe_account(account: Account) -> str:
    currency = get_user_currency(account.user).upper()
    return f"{account.name} ({account.type}) balance: {account.balance:.2f} {currency}"


def get_balance_summary(user, name: str, account_type: str) -> str:
    account = Account.objects.filter(
        user=user, name__iexact=name.strip(), type=account_type
    ).first()
    if not account:
        return f"No {account_type} account named {name} found."
    return describe_account(account)


def list_accounts(user) -> str:
    currency = get_user_currency(user).upper()
    accounts = Account.objects.filter(user=user).order_by("type", "name")
    if not accounts:
        return "No accounts found."
    lines = [
        f"- {account.name} ({account.type}): {account.balance:.2f} {currency}"
        for account in accounts
    ]
    return "Accounts:\n" + "\n".join(lines)

from decimal import Decimal

from django.utils import timezone

from ..models import Loan, LoanPayment


def upsert_loan(user, name: str, amount: Decimal, description: str | None = None):
    loan_name = name.strip()
    description_text = (description or "").strip()
    loan, created = Loan.objects.get_or_create(
        user=user,
        name=loan_name,
        defaults={
            "description": description_text,
            "principal_amount": amount,
            "outstanding_amount": amount,
            "status": Loan.STATUS_ACTIVE,
        },
    )
    if created:
        return loan, created

    update_fields: list[str] = []
    if description_text and loan.description != description_text:
        loan.description = description_text
        update_fields.append("description")
    if amount is not None and loan.principal_amount != amount:
        loan.principal_amount = amount
        update_fields.append("principal_amount")
        if loan.outstanding_amount > amount:
            loan.outstanding_amount = amount
            update_fields.append("outstanding_amount")
    if loan.status != Loan.STATUS_ACTIVE:
        loan.status = Loan.STATUS_ACTIVE
        update_fields.append("status")
    if update_fields:
        loan.save(update_fields=update_fields)
    return loan, created


def pay_loan(user, name: str, amount: Decimal, paid_at):
    loan = Loan.objects.filter(user=user, name__iexact=name.strip()).first()
    if not loan:
        return None, f"No loan named {name} found."
    if loan.outstanding_amount <= 0:
        return loan, f"Loan {loan.name} is already fully paid."

    payment_amount = min(amount, loan.outstanding_amount)
    payment = LoanPayment.objects.create(
        loan=loan,
        amount=payment_amount,
        paid_at=paid_at or timezone.localdate(),
    )
    loan.outstanding_amount -= payment_amount
    loan.outstanding_amount = max(Decimal("0.00"), loan.outstanding_amount)
    if loan.outstanding_amount == Decimal("0.00"):
        loan.status = Loan.STATUS_PAID
    loan.save(update_fields=["outstanding_amount", "status"])

    status = "Loan fully repaid." if loan.status == Loan.STATUS_PAID else "Partial payment recorded."
    return (
        loan,
        f"Paid {payment_amount:.2f} inr towards {loan.name}. {status} Outstanding: "
        f"{loan.outstanding_amount:.2f} inr.",
    )


def list_loans(user) -> str:
    loans = Loan.objects.filter(user=user).order_by("status", "name")
    if not loans:
        return "No loans found."
    lines: list[str] = []
    for loan in loans:
        status = "paid" if loan.status == Loan.STATUS_PAID else "active"
        lines.append(
            f"- {loan.name}: outstanding {loan.outstanding_amount:.2f} / "
            f"{loan.principal_amount:.2f} inr ({status})"
        )
        if loan.description:
            lines.append(f"  desc: {loan.description}")
    return "Loans:\n" + "\n".join(lines)

from django.db import models
from django.utils import timezone


class WhatsAppUser(models.Model):
    phone_number = models.CharField(max_length=32, unique=True)
    locale = models.CharField(max_length=16, default="en")
    timezone = models.CharField(max_length=64, default="UTC")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.phone_number


class Account(models.Model):
    TYPE_BANK = "bank"
    TYPE_CASH = "cash"
    TYPE_CHOICES = [
        (TYPE_BANK, "Bank"),
        (TYPE_CASH, "Cash"),
    ]

    user = models.ForeignKey(WhatsAppUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=64)
    type = models.CharField(max_length=16, choices=TYPE_CHOICES)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "name", "type")

    def __str__(self) -> str:
        return f"{self.name} ({self.type})"


class Card(models.Model):
    user = models.ForeignKey(WhatsAppUser, on_delete=models.CASCADE)
    issuer = models.CharField(max_length=64)
    last4 = models.CharField(max_length=4, blank=True)
    billing_cycle_day = models.PositiveSmallIntegerField(default=1)
    credit_limit = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "issuer", "last4")

    def __str__(self) -> str:
        return f"{self.issuer} {self.last4}".strip()


class Category(models.Model):
    user = models.ForeignKey(WhatsAppUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=64)
    aliases = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "name")

    def __str__(self) -> str:
        return self.name


class Expense(models.Model):
    SOURCE_CARD = "card"
    SOURCE_ACCOUNT = "account"
    SOURCE_CASH = "cash"
    SOURCE_CHOICES = [
        (SOURCE_CARD, "Card"),
        (SOURCE_ACCOUNT, "Account"),
        (SOURCE_CASH, "Cash"),
    ]

    user = models.ForeignKey(WhatsAppUser, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=8, default="inr")
    date = models.DateField(default=timezone.now)
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL)
    source_type = models.CharField(max_length=16, choices=SOURCE_CHOICES)
    source_account = models.ForeignKey(
        Account, null=True, blank=True, on_delete=models.SET_NULL
    )
    source_card = models.ForeignKey(Card, null=True, blank=True, on_delete=models.SET_NULL)
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["user", "date"]),
            models.Index(fields=["user", "category"]),
        ]

    def __str__(self) -> str:
        return f"{self.amount} {self.currency} on {self.date}"


class Message(models.Model):
    STATUS_RECEIVED = "received"
    STATUS_PROCESSED = "processed"
    STATUS_REJECTED = "rejected"
    STATUS_CHOICES = [
        (STATUS_RECEIVED, "Received"),
        (STATUS_PROCESSED, "Processed"),
        (STATUS_REJECTED, "Rejected"),
    ]

    user = models.ForeignKey(WhatsAppUser, on_delete=models.CASCADE)
    raw_text = models.TextField()
    parsed_intent = models.CharField(max_length=64, blank=True)
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default=STATUS_RECEIVED)
    idempotency_key = models.CharField(max_length=128, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["idempotency_key"]),
        ]

    def __str__(self) -> str:
        return f"{self.idempotency_key} ({self.status})"

# Create your models here.

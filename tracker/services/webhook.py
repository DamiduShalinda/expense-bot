from .errors import ValidationError
from ..models import Message, WhatsAppUser


def get_or_create_user(phone_number: str) -> WhatsAppUser:
    user, _created = WhatsAppUser.objects.get_or_create(phone_number=phone_number)
    return user


def ensure_message(user: WhatsAppUser, raw_text: str, idempotency_key: str) -> Message:
    if Message.objects.filter(idempotency_key=idempotency_key).exists():
        raise ValidationError("Duplicate message ignored.")
    return Message.objects.create(
        user=user,
        raw_text=raw_text,
        idempotency_key=idempotency_key,
    )


def mark_message(message: Message, status: str, intent: str | None = None):
    fields = ["status"]
    message.status = status
    if intent is not None:
        message.parsed_intent = intent
        fields.append("parsed_intent")
    message.save(update_fields=fields)

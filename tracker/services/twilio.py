import base64
import hashlib
import hmac
import logging
from twilio.rest import Client

from django.conf import settings

logger = logging.getLogger(__name__)


def is_twilio_configured() -> bool:
    return bool(settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN and settings.TWILIO_WHATSAPP_FROM)


def validate_twilio_request(request) -> bool:
    auth_token = settings.TWILIO_AUTH_TOKEN
    signature = request.headers.get("X-Twilio-Signature", "")
    if not auth_token or not signature:
        return False

    url = request.build_absolute_uri()
    params = request.POST
    if params:
        parts = [url]
        for key in sorted(params.keys()):
            for value in params.getlist(key):
                parts.append(f"{key}{value}")
        data = "".join(parts)
    else:
        data = url

    digest = hmac.new(auth_token.encode("utf-8"), data.encode("utf-8"), hashlib.sha1).digest()
    computed = base64.b64encode(digest).decode("utf-8")
    return hmac.compare_digest(computed, signature)


def send_whatsapp_message(to_number: str, body: str) -> None:
    print(to_number, body)
    client = Client(
        settings.TWILIO_ACCOUNT_SID,
        settings.TWILIO_AUTH_TOKEN,
    )

    message =  client.messages.create(
        from_=settings.TWILIO_WHATSAPP_FROM,   # "whatsapp:+14155238886"
        to=to_number,                          # "whatsapp:+94710170677"
        body=body,
    )

    print(message.sid)

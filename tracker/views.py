import hashlib
import json
import logging

from django.conf import settings
from django.http import HttpResponseNotAllowed, JsonResponse, HttpResponseNotFound
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from .services.errors import IntentRoutingError, ValidationError
from .services.handlers import handle_intent
from .services.intent_router import route_intent
from .services.twilio import is_twilio_configured, send_whatsapp_message, validate_twilio_request
from .services.validation import validate_payload
from .services.webhook import ensure_message, get_or_create_user, mark_message

logger = logging.getLogger(__name__)


def _mask_sender(sender: str | None) -> str | None:
    if not sender:
        return None
    if len(sender) <= 6:
        return sender
    return f"{sender[:2]}***{sender[-2:]}"


def _summarize_payload(raw_payload: dict) -> dict:
    return {
        "message_id": raw_payload.get("MessageSid") or raw_payload.get("message_id") or raw_payload.get("id"),
        "sender": _mask_sender(raw_payload.get("From") or raw_payload.get("from") or raw_payload.get("phone")),
        "demo_mode": raw_payload.get("demo"),
        "has_body": bool(raw_payload.get("Body") or raw_payload.get("message") or raw_payload.get("text")),
    }


def _get_payload(request):
    if request.content_type and "application/json" in request.content_type:
        try:
            return json.loads(request.body.decode("utf-8"))
        except json.JSONDecodeError:
            return {}
    return request.POST


def _build_idempotency_key(message_id: str | None, sender: str, text: str) -> str:
    if message_id:
        return message_id
    raw = f"{sender}:{text}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


@csrf_exempt
def whatsapp_webhook(request):
    if request.method != "POST":
        logger.warning("Webhook called with invalid method: %s", request.method)
        return HttpResponseNotAllowed(["POST"])

    payload = _get_payload(request)
    logger.info("Incoming WhatsApp webhook: %s", _summarize_payload(payload))
    demo_mode = payload.get("demo") in ("1", "true", "yes")
    if settings.TWILIO_VALIDATE_SIGNATURE and not demo_mode and not validate_twilio_request(request):
        logger.warning("Rejected webhook due to invalid Twilio signature: %s", _summarize_payload(payload))
        return JsonResponse({"status": "error", "message": "Invalid Twilio signature."}, status=403)
    message_text = payload.get("Body") or payload.get("message") or payload.get("text")
    sender = payload.get("From") or payload.get("from") or payload.get("phone")
    message_id = payload.get("MessageSid") or payload.get("message_id") or payload.get("id")

    if not message_text or not sender:
        logger.error("Webhook missing sender or message: %s", _summarize_payload(payload))
        return JsonResponse({"status": "error", "message": "Missing sender or message."}, status=400)

    user = get_or_create_user(sender)
    idempotency_key = _build_idempotency_key(message_id, sender, message_text)

    try:
        message = ensure_message(user, message_text, idempotency_key)
        intent, data = route_intent(message_text)
        validate_payload(intent, data, user)
        response_text = handle_intent(user, intent, data)
        if not demo_mode and is_twilio_configured():
            send_whatsapp_message(sender, response_text)
        mark_message(message, "processed", intent)
        return JsonResponse({"status": "ok", "message": response_text})
    except (IntentRoutingError, ValidationError) as exc:
        if "message" in locals():
            mark_message(message, "rejected")
        logger.warning(
            "Validation error for message %s (intent=%s): %s",
            message.id if "message" in locals() else "unknown",
            intent if "intent" in locals() else "unknown",
            exc,
        )
        payload = {"status": "error", "message": str(exc)}
        status = 400
        if str(exc).lower().startswith("duplicate message"):
            payload["status"] = "ok"
            status = 200
        if sender and not demo_mode and is_twilio_configured():
            try:
                send_whatsapp_message(sender, payload["message"])
            except Exception:
                logger.exception("Failed to send Twilio error response.")
        return JsonResponse(payload, status=status)
    except Exception as exc:
        if "message" in locals():
            mark_message(message, "failed")
        logger.exception(
            "Unhandled webhook error for payload %s",
            _summarize_payload(payload),
        )
        error_text = "Sorry, something went wrong. Please try again."
        if sender and not demo_mode and is_twilio_configured():
            try:
                send_whatsapp_message(sender, error_text)
            except Exception:
                logger.exception("Failed to send Twilio error response.")
        return JsonResponse({"status": "error", "message": str(exc)}, status=502)


def demo_ui(request):
    if not settings.DEBUG:
        return HttpResponseNotFound()
    return render(request, "tracker/demo.html")

from .errors import IntentRoutingError
from .regex_parser import parse_message


def route_intent(text: str):
    matches = parse_message(text)
    if not matches:
        raise IntentRoutingError("Unsupported message format.")
    if len(matches) > 1:
        raise IntentRoutingError("Ambiguous input. Please clarify your request.")
    match = matches[0]
    if match.intent == "EXPENSE_CREATE" and not match.data.get("source_type"):
        match.data["source_type"] = "card"
    return match.intent, match.data

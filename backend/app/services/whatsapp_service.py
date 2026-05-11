import re
from typing import List, Dict, Optional

import requests
from app.core.config import settings


def _strip_html(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text or "").strip()


def _normalize_whatsapp_number(number: Optional[str]) -> Optional[str]:
    if not number:
        return None
    cleaned = re.sub(r"[^\d+]+", "", number)
    if not cleaned:
        return None
    if not cleaned.startswith('+'):
        cleaned = f'+{cleaned}'
    return f'whatsapp:{cleaned}'


class WhatsAppService:
    def __init__(self):
        self.account_sid = settings.twilio_account_sid.strip()
        self.auth_token = settings.twilio_auth_token.strip()
        self.from_number = _normalize_whatsapp_number(settings.twilio_from_number.strip()) or ''
        self.enabled = bool(self.account_sid and self.auth_token and self.from_number)
        self.base_url = f"https://api.twilio.com/2010-04-01/Accounts/{self.account_sid}/Messages.json"

    def send_message(self, to_number: str, body: str) -> Dict[str, str]:
        if not self.enabled:
            return {"sent": False, "detail": "WhatsApp no está configurado."}

        recipient = _normalize_whatsapp_number(to_number)
        if not recipient:
            return {"sent": False, "detail": "Número WhatsApp inválido."}

        payload = {
            "From": self.from_number,
            "To": recipient,
            "Body": body,
        }

        try:
            response = requests.post(
                self.base_url,
                auth=(self.account_sid, self.auth_token),
                data=payload,
                timeout=15,
            )
            response.raise_for_status()
            return {"sent": True, "detail": "WhatsApp enviado."}
        except Exception as exc:
            return {"sent": False, "detail": str(exc)}

    def send_bulk(self, recipients: List[str], body: str) -> Dict[str, object]:
        results = []
        text = _strip_html(body)
        for recipient in recipients:
            if recipient:
                results.append({"to": recipient, **self.send_message(recipient, text)})

        sent_count = sum(1 for result in results if result.get("sent"))
        return {"sent": sent_count, "results": results}

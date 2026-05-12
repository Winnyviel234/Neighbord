import smtplib
import re
from email.message import EmailMessage
from email.utils import formataddr, formatdate, make_msgid
from pathlib import Path

from app.core.config import settings


class EmailService:
    def __init__(self):
        self.username = settings.mail_username.strip()
        self.password = re.sub(r"\s+", "", settings.mail_password or "")
        self.from_email = (settings.mail_from or settings.mail_username).strip()
        self.from_name = settings.mail_from_name.strip() or settings.app_name
        self.enabled = bool(self.username and self.password and self.from_email)

    def _logo_path(self) -> Path | None:
        path = Path(__file__).resolve().parents[3] / "frontend" / "public" / "neighbor-logo.png"
        return path if path.exists() else None

    def _wrap_html(self, body: str, logo_cid: str | None) -> str:
        logo = f'<img src="cid:{logo_cid}" alt="{self.from_name}" width="56" style="display:block;border-radius:10px" />' if logo_cid else ""
        return f"""<!doctype html>
<html>
  <body style="margin:0;background:#f4f8fb;font-family:Arial,Helvetica,sans-serif;color:#0b2545">
    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background:#f4f8fb;padding:24px 0">
      <tr>
        <td align="center">
          <table role="presentation" width="620" cellspacing="0" cellpadding="0" style="max-width:620px;width:100%;background:#ffffff;border:1px solid #dbe7f0;border-radius:12px;overflow:hidden">
            <tr>
              <td style="padding:22px 24px;background:#0b5cab;color:#ffffff">
                <table role="presentation" cellspacing="0" cellpadding="0">
                  <tr>
                    <td style="padding-right:14px">{logo}</td>
                    <td>
                      <div style="font-size:20px;font-weight:800;line-height:1.2">{self.from_name}</div>
                      <div style="font-size:13px;opacity:.9;margin-top:3px">Comunicacion oficial de la comunidad</div>
                    </td>
                  </tr>
                </table>
              </td>
            </tr>
            <tr>
              <td style="padding:26px 24px;font-size:15px;line-height:1.6;color:#334155">
                {body}
              </td>
            </tr>
          </table>
        </td>
      </tr>
    </table>
  </body>
</html>"""

    def send(self, recipients: list[str], subject: str, html: str, text: str | None = None) -> dict:
        if not self.enabled:
            return {"sent": False, "detail": "Correo no configurado. Revisa MAIL_USERNAME, MAIL_PASSWORD y MAIL_FROM."}

        msg = EmailMessage()
        msg["From"] = formataddr((self.from_name, self.from_email))
        msg["To"] = ", ".join(recipients)
        msg["Subject"] = subject
        msg["Date"] = formatdate(localtime=True)
        msg["Message-ID"] = make_msgid(domain=self.from_email.split("@")[-1])
        msg.set_content(text or subject)
        logo_path = self._logo_path()
        logo_cid = make_msgid(domain=self.from_email.split("@")[-1])[1:-1] if logo_path else None
        msg.add_alternative(self._wrap_html(html, logo_cid), subtype="html")
        if logo_path:
            html_part = msg.get_payload()[-1]
            html_part.add_related(logo_path.read_bytes(), maintype="image", subtype="png", cid=f"<{logo_cid}>")

        try:
            with smtplib.SMTP(settings.mail_server, settings.mail_port) as smtp:
                smtp.starttls()
                smtp.login(self.username, self.password)
                refused = smtp.send_message(msg)
                if refused:
                    return {
                        "sent": False,
                        "detail": f"El servidor rechazo estos destinatarios: {', '.join(refused.keys())}"
                    }
        except smtplib.SMTPAuthenticationError:
            return {
                "sent": False,
                "detail": "Gmail rechazo las credenciales SMTP. Usa una clave de aplicacion de 16 caracteres sin espacios y verifica que MAIL_USERNAME y MAIL_FROM sean la misma cuenta."
            }
        except Exception as exc:
            return {"sent": False, "detail": str(exc)}

        return {
            "sent": True,
            "recipients": recipients,
            "detail": "Gmail acepto el mensaje para entrega. Si no aparece en bandeja de entrada, revisa spam, promociones o el correo enviado de la cuenta remitente."
        }

    def welcome(self, email: str, name: str):
        return self.send([email], "Bienvenido a Neighbord", f"<h2>Hola {name}</h2><p>Tu registro fue recibido.</p>")

    def account_approved(self, email: str, name: str):
        return self.send([email], "Cuenta aprobada", f"<h2>Hola {name}</h2><p>Tu cuenta ya está aprobada.</p>")

    def payment_receipt(self, email: str, concept: str, amount: float):
        return self.send([email], "Comprobante de pago", f"<p>Pago registrado: {concept} por RD$ {amount:,.2f}</p>")

    def debt_alert(self, email: str, amount: float):
        return self.send([email], "Alerta de mora", f"<p>Tienes un balance pendiente de RD$ {amount:,.2f}.</p>")

    def meeting_reminder(self, recipients: list[str], title: str, when: str):
        return self.send(recipients, "Recordatorio de reunión", f"<p>{title}: {when}</p>")

    def announcement(self, recipients: list[str], title: str, body: str):
        return self.send(recipients, title, f"<h2>{title}</h2><p>{body}</p>")

    def request_status(self, email: str, title: str, status: str):
        return self.send([email], "Actualización de solicitud", f"<p>{title}: {status}</p>")

    def new_vote(self, recipients: list[str], title: str):
        return self.send(recipients, "Nueva votación disponible", f"<p>{title}</p>")

    def password_reset(self, email: str, name: str, reset_url: str):
        return self.send(
            [email],
            "Recuperar contraseña",
            f"""
            <h2>Hola {name}</h2>
            <p>Recibimos una solicitud para cambiar la contraseña de tu cuenta.</p>
            <p>Este enlace vence en 30 minutos y solo se puede usar una vez.</p>
            <p><a href="{reset_url}" style="display:inline-block;background:#0b5cab;color:#ffffff;padding:12px 16px;border-radius:8px;text-decoration:none;font-weight:bold">Cambiar contraseña</a></p>
            <p>Si no solicitaste este cambio, puedes ignorar este correo.</p>
            """,
            f"Abre este enlace para cambiar tu contraseña: {reset_url}"
        )

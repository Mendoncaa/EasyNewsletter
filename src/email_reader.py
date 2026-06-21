"""IMAP email reader for newsletter fetching."""

import email
import email.utils
import imaplib
from datetime import datetime, timedelta
from email.header import decode_header
from dataclasses import dataclass

from src.config import Config


@dataclass
class RawEmail:
    """Raw email data extracted from IMAP."""
    subject: str
    sender: str
    date: str
    html_body: str
    text_body: str


def _decode_header_value(value: str) -> str:
    """Decode an email header that may be encoded (RFC 2047)."""
    if not value:
        return ""
    decoded_parts = decode_header(value)
    result = []
    for part, charset in decoded_parts:
        if isinstance(part, bytes):
            result.append(part.decode(charset or "utf-8", errors="replace"))
        else:
            result.append(part)
    return " ".join(result)


def _extract_body(msg: email.message.Message) -> tuple[str, str]:
    """Extract HTML and plain text body from an email message.

    Returns (html_body, text_body).
    """
    html_body = ""
    text_body = ""

    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition", ""))

            # Skip attachments
            if "attachment" in content_disposition:
                continue

            payload = part.get_payload(decode=True)
            if payload is None:
                continue

            charset = part.get_content_charset() or "utf-8"
            decoded = payload.decode(charset, errors="replace")

            if content_type == "text/html":
                html_body = decoded
            elif content_type == "text/plain":
                text_body = decoded
    else:
        payload = msg.get_payload(decode=True)
        if payload:
            charset = msg.get_content_charset() or "utf-8"
            decoded = payload.decode(charset, errors="replace")
            if msg.get_content_type() == "text/html":
                html_body = decoded
            else:
                text_body = decoded

    return html_body, text_body


def _parse_date(msg: email.message.Message) -> str:
    """Extract and format the email date."""
    date_str = msg.get("Date", "")
    if date_str:
        parsed = email.utils.parsedate_to_datetime(date_str)
        return parsed.strftime("%Y-%m-%d %H:%M")
    return "Data desconhecida"


def fetch_newsletters(days_back: int = 1) -> list[RawEmail]:
    """Connect to IMAP and fetch newsletter emails from the last N days.

    Args:
        days_back: Number of days to look back for emails.

    Returns:
        List of RawEmail objects with extracted content.
    """
    since_date = (datetime.now() - timedelta(days=days_back)).strftime("%d-%b-%Y")

    print(f"   📧 A conectar a {Config.IMAP_SERVER}...")

    mail = imaplib.IMAP4_SSL(Config.IMAP_SERVER, Config.IMAP_PORT)
    try:
        mail.login(Config.EMAIL_ADDRESS, Config.EMAIL_PASSWORD)
        mail.select("INBOX", readonly=True)

        # Search for emails since the specified date
        status, msg_ids = mail.search(None, f'(SINCE "{since_date}")')
        if status != "OK" or not msg_ids[0]:
            print("   📭 Nenhum email encontrado.")
            return []

        id_list = msg_ids[0].split()
        print(f"   📨 {len(id_list)} emails encontrados desde {since_date}")

        emails = []
        for msg_id in id_list:
            status, msg_data = mail.fetch(msg_id, "(RFC822)")
            if status != "OK":
                continue

            raw_email = msg_data[0][1]
            msg = email.message_from_bytes(raw_email)

            subject = _decode_header_value(msg.get("Subject", "Sem assunto"))
            sender = _decode_header_value(msg.get("From", "Desconhecido"))
            date = _parse_date(msg)
            html_body, text_body = _extract_body(msg)

            # Only include emails that have content
            if html_body or text_body:
                emails.append(RawEmail(
                    subject=subject,
                    sender=sender,
                    date=date,
                    html_body=html_body,
                    text_body=text_body,
                ))

        print(f"   ✅ {len(emails)} emails com conteúdo extraídos")
        return emails
    finally:
        mail.logout()
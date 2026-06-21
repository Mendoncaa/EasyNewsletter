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
    date: datetime | None
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


def _parse_date(msg: email.message.Message) -> datetime | None:
    """Extract datetime from email Date header."""
    date_str = msg.get("Date", "")
    if date_str:
        try:
            return email.utils.parsedate_to_datetime(date_str)
        except (ValueError, TypeError):
            pass
    return None


def fetch_newsletters(days_back: int = 1) -> list[RawEmail]:
    """Connect to IMAP and fetch newsletter emails from the last N days.

    Filters emails to only include actual newsletters (detected via
    List-Unsubscribe header, which is legally required on all newsletters).

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

        # Load sender blacklist from config
        blacklist = {s.lower() for s in Config.EMAIL_SENDER_BLACKLIST}

        # Phase 1: Fetch only headers to filter cheaply (no full body download)
        HEADER_FIELDS = "(BODY.PEEK[HEADER.FIELDS (FROM SUBJECT DATE LIST-UNSUBSCRIBE)])"
        newsletter_ids = []
        skipped = 0

        for msg_id in id_list:
            status, header_data = mail.fetch(msg_id, HEADER_FIELDS)
            if status != "OK":
                continue

            header_bytes = header_data[0][1]
            header_msg = email.message_from_bytes(header_bytes)

            # Filter: only include emails with List-Unsubscribe header
            if not header_msg.get("List-Unsubscribe"):
                skipped += 1
                continue

            # Filter: check sender blacklist
            sender = _decode_header_value(header_msg.get("From", ""))
            if any(blocked in sender.lower() for blocked in blacklist):
                skipped += 1
                continue

            newsletter_ids.append(msg_id)

        print(f"   🔍 {len(newsletter_ids)} newsletters identificadas ({skipped} filtrados)")

        if not newsletter_ids:
            return []

        # Phase 2: Fetch full body only for newsletters that passed filtering
        emails = []
        for msg_id in newsletter_ids:
            status, msg_data = mail.fetch(msg_id, "(RFC822)")
            if status != "OK":
                continue

            raw_email = msg_data[0][1]
            msg = email.message_from_bytes(raw_email)

            subject = _decode_header_value(msg.get("Subject", "Sem assunto"))
            sender = _decode_header_value(msg.get("From", "Desconhecido"))
            date = _parse_date(msg)
            html_body, text_body = _extract_body(msg)

            if html_body or text_body:
                emails.append(RawEmail(
                    subject=subject,
                    sender=sender,
                    date=date,
                    html_body=html_body,
                    text_body=text_body,
                ))

        print(f"   ✅ {len(emails)} newsletters extraídas")
        return emails
    finally:
        mail.logout()
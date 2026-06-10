import os
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
from datetime import datetime, timezone
from dotenv import load_dotenv
import streamlit as st

# Import database functions
from modules.database import (
    get_user_by_id,
    get_user_preferences,
    add_notification_history,
    get_last_whatsapp_sent_time,
    queue_notification,
    get_pending_notifications,
    mark_notification_sent,
    get_users,
    get_user_interests,
    has_user_been_notified
)

# Load environment variables
load_dotenv()

def get_secret(key: str, default: str = "") -> str:
    """Helper to retrieve configuration from streamlit secrets or environment variables."""
    try:
        if key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass
    return os.getenv(key, default)

def send_smtp_email(to_email: str, subject: str, body: str) -> bool:
    """Sends an email using Gmail SMTP server."""
    smtp_server = get_secret("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(get_secret("SMTP_PORT", "587"))
    smtp_user = get_secret("SMTP_USER", "")
    smtp_password = get_secret("SMTP_PASSWORD", "")

    if not smtp_user or not smtp_password:
        print("SMTP Error: SMTP_USER or SMTP_PASSWORD not configured.")
        return False

    msg = MIMEMultipart()
    msg['From'] = smtp_user
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain', 'utf-8'))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.sendmail(smtp_user, to_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"SMTP Error: {e}")
        return False

def send_telegram_message(chat_id: str, message: str) -> bool:
    """Sends a message to a Telegram chat using Telegram Bot API."""
    token = get_secret("TELEGRAM_BOT_TOKEN", "")
    if not token or not chat_id:
        print("Telegram Error: TELEGRAM_BOT_TOKEN or Chat ID not configured.")
        return False

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.status_code == 200
    except Exception as e:
        print(f"Telegram Error: {e}")
        return False

def send_waha_whatsapp(phone: str, message: str) -> bool:
    """Sends a WhatsApp message via WAHA API."""
    base_url = get_secret("WAHA_API_URL", "http://localhost:3000")
    session = get_secret("WAHA_SESSION", "default")
    api_key = get_secret("WAHA_API_KEY", "")
    
    clean_phone = phone.strip().replace("+", "")
    chat_id = f"{clean_phone}@c.us"
    
    url = f"{base_url}/api/sendText"
    payload = {
        "chatId": chat_id,
        "text": message,
        "session": session
    }

    headers = {}
    if api_key:
        headers["X-Api-Key"] = api_key

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        return response.status_code in [200, 201]
    except Exception as e:
        print(f"WAHA WhatsApp Error: {e}")
        return False

def check_whatsapp_rate_limit(phone: str) -> bool:
    """
    Returns True if we can send a WhatsApp to this number right now
    (at least 60 seconds have elapsed since the last successful message).
    """
    last_sent = get_last_whatsapp_sent_time(phone)
    if not last_sent:
        return True  # Never sent before, safe to send
    
    # Calculate difference in seconds
    now = datetime.now()
    # DuckDB timestamps are naive or timezone-aware depending on DB config.
    # We compare by removing timezone or keeping them aligned.
    if last_sent.tzinfo is not None:
        delta = (datetime.now(timezone.utc) - last_sent).total_seconds()
    else:
        delta = (now - last_sent).total_seconds()
        
    return delta >= 60.0

def send_notification_multichannel(user_id: int, title: str, link: str, summary: str) -> dict:
    """
    Sends an article notification to all enabled channels for a user.
    Enforces the 1-minute rate limit on WhatsApp.
    """
    user = get_user_by_id(user_id)
    if not user:
        return {"status": "error", "message": "User not found"}

    prefs = get_user_preferences(user_id)
    results = {}
    
    # Format message body
    email_body = f"""Hola, {user['nombre']}.

Hemos identificado un nuevo artículo científico que coincide con tus intereses registrados en BiblioMap UCV:

Título: {title}
Enlace: {link if link else 'No disponible'}
Resumen: {summary if summary else 'No disponible'}

--
BiblioMap UCV
Mapea la ciencia, encuentra brechas, conecta con el mundo.
Universidad Central de Venezuela (UCV) | LEGIN
"""

    chat_body = f"""<b>[BiblioMap UCV] Alerta Científica</b>

Hola, {user['nombre']}.
Se ha detectado una nueva publicación de tu interés:

📚 <b>{title}</b>
🔗 <a href="{link if link else '#'}">Ver Artículo</a>

<i>Enviado desde BiblioMap UCV</i>"""

    whatsapp_body = f"""*Alerta Científica — BiblioMap UCV*

Hola, {user['nombre']}.
Se ha detectado una nueva publicación de tu interés:

📚 *{title}*
🔗 Enlace: {link if link else 'No disponible'}"""

    # --- EMAIL CHANNEL ---
    if prefs.get("SMTP", {}).get("activo") and user["email"]:
        subject = f"[BiblioMap UCV] Alerta Científica: {title[:50]}..."
        success = send_smtp_email(user["email"], subject, email_body)
        status = "EXITOSO" if success else "FALLIDO"
        add_notification_history(user_id, title, "SMTP", status)
        results["SMTP"] = status

    # --- TELEGRAM CHANNEL ---
    tg_pref = prefs.get("TELEGRAM", {})
    chat_id = tg_pref.get("config", {}).get("chat_id", "")
    if tg_pref.get("activo") and chat_id:
        success = send_telegram_message(chat_id, chat_body)
        status = "EXITOSO" if success else "FALLIDO"
        add_notification_history(user_id, title, "TELEGRAM", status)
        results["TELEGRAM"] = status

    # --- WHATSAPP CHANNEL ---
    if prefs.get("WHATSAPP", {}).get("activo") and user["telefono"]:
        phone = user["telefono"]
        if check_whatsapp_rate_limit(phone):
            # Safe to send immediately
            success = send_waha_whatsapp(phone, whatsapp_body)
            status = "EXITOSO" if success else "FALLIDO"
            add_notification_history(user_id, title, "WHATSAPP", status)
            results["WHATSAPP"] = status
        else:
            # Under rate limit: queue for later
            queue_notification(user_id, title, whatsapp_body)
            results["WHATSAPP"] = "ENCOLADO (Espera anti-baneo)"
            
    return results

def process_whatsapp_queue() -> int:
    """
    Processes the queue of pending WhatsApp notifications.
    Respects the 1-minute delay per contact.
    Returns the number of messages successfully sent.
    """
    pending = get_pending_notifications()
    sent_count = 0
    
    # Keep track of contacts processed in this run to avoid sending twice to the same contact in a single batch
    processed_contacts = set()
    
    for item in pending:
        user_id = item["usuario_id"]
        user = get_user_by_id(user_id)
        if not user or not user["telefono"]:
            mark_notification_sent(item["id"])  # Invalid item, mark sent to discard
            continue
            
        phone = user["telefono"]
        if phone in processed_contacts:
            continue  # Skip for this run to keep spacing
            
        if check_whatsapp_rate_limit(phone):
            # Send WhatsApp
            success = send_waha_whatsapp(phone, item["mensaje"])
            status = "EXITOSO" if success else "FALLIDO"
            add_notification_history(user_id, item["titulo_articulo"], "WHATSAPP", status)
            mark_notification_sent(item["id"])
            processed_contacts.add(phone)
            if success:
                sent_count += 1
                
    return sent_count

def match_and_notify_users(df) -> list:
    """
    Scans a DataFrame of articles and matches them against registered user interests.
    Sends notifications to matched users for new articles they haven't been notified of yet.
    Returns a list of notification reports.
    """
    if df.empty:
        return []

    users = get_users()
    reports = []

    for user in users:
        user_id = user["id"]
        interests = get_user_interests(user_id)
        if not interests:
            continue

        for _, row in df.iterrows():
            title = row.get("title", "")
            if not title:
                continue

            # Check if title contains any interest keyword (case-insensitive substring match)
            matched_interest = None
            for interest in interests:
                if interest.strip().lower() in title.lower():
                    matched_interest = interest
                    break

            if matched_interest:
                # Check if already notified
                if not has_user_been_notified(user_id, title):
                    link = row.get("landing_page_url", "") or row.get("doi", "")
                    summary = row.get("abstract", "") or row.get("description", "") or f"Artículo científico sobre: '{matched_interest}'."
                    
                    # Send notification
                    res = send_notification_multichannel(user_id, title, link, summary)
                    reports.append({
                        "usuario": user["nombre"],
                        "articulo": title,
                        "interes": matched_interest,
                        "canales": res
                    })
    return reports

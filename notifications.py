import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import requests
import streamlit as st


def send_line_notification(message, webhook_url=None):
  url = ""
  try:
    url = webhook_url or st.secrets.get("LINE_WEBHOOK_URL", "")
  except Exception:
    url = ""

  if not url:
    return False, "ยังไม่ได้ตั้งค่า Webhook URL"

  try:
    payload = {"content": message, "text": message, "message": message}
    res = requests.post(url, json=payload, timeout=5)
    if res.status_code in [200, 204]:
      return True, "ส่งแจ้งเตือนสำเร็จ"
    return False, f"HTTP Error: {res.status_code}"
  except Exception as e:
    return False, f"เกิดข้อผิดพลาด: {e}"


def send_invoice_email(
    to_email, subject, body_text, pdf_bytes=None, filename="Invoice.pdf"
):
  sender_email = ""
  sender_password = ""
  try:
    sender_email = st.secrets.get("SMTP_EMAIL", "")
    sender_password = st.secrets.get("SMTP_PASSWORD", "")
  except Exception:
    pass

  if not sender_email or not sender_password:
    return False, "ยังไม่ได้ตั้งค่า SMTP_EMAIL และ SMTP_PASSWORD ใน Secrets"

  try:
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body_text, "plain", "utf-8"))

    if pdf_bytes:
      part = MIMEApplication(pdf_bytes, Name=filename)
      part["Content-Disposition"] = f'attachment; filename="{filename}"'
      msg.attach(part)

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(sender_email, sender_password)
    server.sendmail(sender_email, to_email, msg.as_string())
    server.quit()
    return True, f"ส่งอีเมลไปยัง {to_email} สำเร็จ!"
  except Exception as e:
    return False, f"เกิดข้อผิดพลาดในการส่งอีเมล: {e}"
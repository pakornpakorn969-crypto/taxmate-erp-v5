import html
from datetime import datetime, timedelta
from database import get_connection, log_audit

MAX_FAILED_ATTEMPTS = 5
LOCKOUT_MINUTES = 15

def sanitize_input(text: str) -> str:
    if not text:
        return ""
    return html.escape(str(text).strip())

def check_account_lockout(username: str) -> tuple[bool, str]:
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT failed_attempts, lockout_until FROM users WHERE username = ?", (username,))
    row = c.fetchone()
    conn.close()
    
    if not row:
        return False, ""
        
    failed_attempts, lockout_until = row
    if lockout_until:
        try:
            lockout_time = datetime.strptime(lockout_until, "%Y-%m-%d %H:%M:%S")
            if datetime.now() < lockout_time:
                remaining = int((lockout_time - datetime.now()).total_seconds() / 60) + 1
                return True, f"🔒 บัญชีถูกระงับชั่วคราวเนื่องจากสุ่มรหัสผ่านผิดเกินกำหนด โปรดลองใหม่ในอีก {remaining} นาที"
        except Exception:
            pass
            
    return False, ""

def record_login_attempt(username: str, is_success: bool):
    conn = get_connection()
    c = conn.cursor()
    
    if is_success:
        c.execute("UPDATE users SET failed_attempts = 0, lockout_until = NULL WHERE username = ?", (username,))
    else:
        c.execute("SELECT failed_attempts FROM users WHERE username = ?", (username,))
        row = c.fetchone()
        if row:
            current_failed = (row[0] or 0) + 1
            if current_failed >= MAX_FAILED_ATTEMPTS:
                lock_until = (datetime.now() + timedelta(minutes=LOCKOUT_MINUTES)).strftime("%Y-%m-%d %H:%M:%S")
                c.execute("UPDATE users SET failed_attempts = ?, lockout_until = ? WHERE username = ?", (current_failed, lock_until, username))
                log_audit(username, "ACCOUNT_LOCKED", f"ระงับบัญชีเนื่องจากกรอกรหัสผิด {current_failed} ครั้ง")
            else:
                c.execute("UPDATE users SET failed_attempts = ? WHERE username = ?", (current_failed, username))
                
    conn.commit()
    conn.close()
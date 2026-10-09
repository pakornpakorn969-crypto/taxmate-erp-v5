import hashlib
import os
from datetime import datetime
from database import get_connection, log_audit, seed_financial_data_for_user
from security import check_account_lockout, record_login_attempt, sanitize_input

def hash_password(password: str, salt: bytes = None):
    if salt is None:
        salt = os.urandom(16)
    pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return pwd_hash.hex(), salt.hex()

def verify_password(stored_password_hash: str, stored_salt: str, provided_password: str) -> bool:
    try:
        salt_bytes = bytes.fromhex(stored_salt)
        pwd_hash, _ = hash_password(provided_password, salt_bytes)
        return pwd_hash == stored_password_hash
    except Exception:
        return False

def register_user(username, password, company_name, role="user"):
    clean_username = sanitize_input(username)
    clean_company = sanitize_input(company_name)
    
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE username = ?", (clean_username,))
    if c.fetchone():
        conn.close()
        return False, "ชื่อผู้ใช้งานนี้มีอยู่ในระบบแล้ว"
        
    pwd_hash, salt = hash_password(password)
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        c.execute('''
            INSERT INTO users (username, password_hash, salt, company_name, role, created_at, failed_attempts)
            VALUES (?, ?, ?, ?, ?, ?, 0)
        ''', (clean_username, pwd_hash, salt, clean_company, role, created_at))
        conn.commit()
        conn.close()
        
        seed_financial_data_for_user(clean_username)
        log_audit(clean_username, "REGISTER", f"ลงทะเบียนผู้ใช้ใหม่ ({role})")
        return True, "ลงทะเบียนสำเร็จ! สามารถเข้าสู่ระบบได้ทันที"
    except Exception as e:
        conn.close()
        return False, f"เกิดข้อผิดพลาดในการลงทะเบียน: {e}"

def authenticate_user(username, password):
    clean_username = sanitize_input(username)
    
    is_locked, lock_msg = check_account_lockout(clean_username)
    if is_locked:
        return False, lock_msg
        
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT password_hash, salt, company_name, role, last_login FROM users WHERE username = ?", (clean_username,))
    row = c.fetchone()
    
    if row:
        stored_hash, stored_salt, company_name, role, last_login = row
        if verify_password(stored_hash, stored_salt, password):
            record_login_attempt(clean_username, is_success=True)
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            c.execute("UPDATE users SET last_login = ?, failed_attempts = 0, lockout_until = NULL WHERE username = ?", (now_str, clean_username))
            conn.commit()
            conn.close()
            log_audit(clean_username, "LOGIN", "เข้าสู่ระบบสำเร็จ")
            return True, {
                "username": clean_username,
                "company_name": company_name,
                "role": role,
                "last_login": last_login or now_str
            }
            
    conn.close()
    record_login_attempt(clean_username, is_success=False)
    log_audit(clean_username or "UNKNOWN", "LOGIN_FAILED", "พยายามเข้าสู่ระบบไม่สำเร็จ")
    return False, "ชื่อผู้ใช้งานหรือรหัสผ่านไม่ถูกต้อง"

def change_password(username, old_password, new_password):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT password_hash, salt FROM users WHERE username = ?", (username,))
    row = c.fetchone()
    if row:
        stored_hash, stored_salt = row
        if verify_password(stored_hash, stored_salt, old_password):
            new_hash, new_salt = hash_password(new_password)
            c.execute("UPDATE users SET password_hash = ?, salt = ? WHERE username = ?", (new_hash, new_salt, username))
            conn.commit()
            conn.close()
            log_audit(username, "CHANGE_PASSWORD", "เปลี่ยนรหัสผ่านสำเร็จ")
            return True, "เปลี่ยนรหัสผ่านเรียบร้อยแล้ว!"
        else:
            conn.close()
            return False, "รหัสผ่านเดิมไม่ถูกต้อง"
    conn.close()
    return False, "ไม่พบผู้ใช้งาน"

def create_default_demo_accounts():
    conn = get_connection()
    c = conn.cursor()
    
    c.execute("SELECT id FROM users WHERE username = ?", ("demo_admin",))
    if not c.fetchone():
        pw_hash, salt = hash_password("123456")
        c.execute('''
            INSERT INTO users (username, password_hash, salt, company_name, role, created_at, failed_attempts)
            VALUES (?, ?, ?, ?, ?, ?, 0)
        ''', ("demo_admin", pw_hash, salt, "Tech Studio Co., Ltd. (Admin)", "admin", datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        seed_financial_data_for_user("demo_admin")

    c.execute("SELECT id FROM users WHERE username = ?", ("demo_user",))
    if not c.fetchone():
        pw_hash, salt = hash_password("123456")
        c.execute('''
            INSERT INTO users (username, password_hash, salt, company_name, role, created_at, failed_attempts)
            VALUES (?, ?, ?, ?, ?, ?, 0)
        ''', ("demo_user", pw_hash, salt, "Siam Digital Agency Co., Ltd. (User)", "user", datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        seed_financial_data_for_user("demo_user")
        
    conn.close()
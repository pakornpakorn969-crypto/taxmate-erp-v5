from datetime import datetime
import json
from database import get_connection, hash_password, log_audit


def authenticate_user(username, password):
  conn = get_connection()
  c = conn.cursor()
  pass_h = hash_password(password)

  c.execute(
      "SELECT username, company, role, status, allowed_modules FROM users"
      " WHERE username = ? AND password_hash = ?",
      (username, pass_h),
  )
  row = c.fetchone()

  if row:
    u_name, company, role, status, allowed_mods = row
    if status == "suspended":
      conn.close()
      return False, "บัญชีของคุณถูกระงับการใช้งาน กรุณาติดต่อแอดมิน"

    # อัปเดตเวลาเข้าใช้งานล่าสุด
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute(
        "UPDATE users SET last_login = ? WHERE username = ?", (now_str, u_name)
    )
    conn.commit()
    conn.close()

    log_audit(u_name, "LOGIN", "Authentication", "เข้าสู่ระบบสำเร็จ")

    parsed_mods = "all"
    if allowed_mods and allowed_mods != "all":
      try:
        parsed_mods = json.loads(allowed_mods)
      except Exception:
        parsed_mods = "all"

    return True, {
        "username": u_name,
        "company": company,
        "role": role,
        "allowed_modules": parsed_mods,
    }

  conn.close()
  return False, "ชื่อผู้ใช้งานหรือรหัสผ่านไม่ถูกต้อง"


def register_user(username, password, company, role="user"):
  try:
    conn = get_connection()
    c = conn.cursor()
    pass_h = hash_password(password)
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    c.execute(
        """INSERT INTO users (username, password_hash, company, role, status, allowed_modules, created_at)
           VALUES (?, ?, ?, ?, 'active', 'all', ?)""",
        (username, pass_h, company, role, now_str),
    )
    conn.commit()
    conn.close()
    log_audit(
        username, "REGISTER", "Authentication", f"ลงทะเบียนบัญชีใหม่ ({role})"
    )
    return True, "ลงทะเบียนสำเร็จ!"
  except Exception as e:
    return False, f"ไม่สามารถลงทะเบียนได้: {e}"


def change_password(username, new_password):
  conn = get_connection()
  c = conn.cursor()
  pass_h = hash_password(new_password)
  c.execute(
      "UPDATE users SET password_hash = ? WHERE username = ?",
      (pass_h, username),
  )
  conn.commit()
  conn.close()
  log_audit(username, "CHANGE_PASSWORD", "Authentication", "เปลี่ยนรหัสผ่าน")
  return True, "เปลี่ยนรหัสผ่านเรียบร้อยแล้ว!"
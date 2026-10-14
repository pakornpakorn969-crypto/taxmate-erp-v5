from datetime import datetime
import hashlib
import json
import os
import sqlite3
import pandas as pd
import streamlit as st

DB_NAME = "taxmate.db"


def get_connection():
  """เชื่อมต่อฐานข้อมูล: ป้องกัน StreamlitSecretNotFoundError ด้วย try...except"""
  pg_uri = ""
  try:
    pg_uri = st.secrets.get("POSTGRES_URL", "")
  except Exception:
    pg_uri = os.environ.get("DATABASE_URL", "")

  if pg_uri:
    try:
      import psycopg2

      return psycopg2.connect(pg_uri)
    except Exception as e:
      print(f"PostgreSQL Connection Error: {e}")

  return sqlite3.connect(DB_NAME, check_same_thread=False)


def hash_password(password: str) -> str:
  """เข้ารหัสรหัสผ่านด้วย SHA-256"""
  return hashlib.sha256(password.encode("utf-8")).hexdigest()


def init_db():
  """สร้างโครงสร้างตารางระบบทั้งหมดพร้อมระบบ Auto-Migration"""
  conn = get_connection()
  c = conn.cursor()

  # 1. Users Table
  c.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        full_name TEXT,
        email TEXT,
        company TEXT,
        department TEXT DEFAULT 'General',
        role TEXT NOT NULL DEFAULT 'user',
        status TEXT DEFAULT 'active',
        allowed_modules TEXT DEFAULT 'all',
        last_login TEXT,
        created_at TEXT
    )""")

  # ⚙️ Auto-Migration: เพิ่มคอลัมน์ที่ขาดให้อัตโนมัติในกรณีที่มีตาราง users เดิมอยู่แล้ว
  for col_name, col_type in [
      ("full_name", "TEXT"),
      ("email", "TEXT"),
      ("company", "TEXT"),
      ("department", "TEXT DEFAULT 'General'"),
      ("role", "TEXT NOT NULL DEFAULT 'user'"),
      ("status", "TEXT DEFAULT 'active'"),
      ("allowed_modules", "TEXT DEFAULT 'all'"),
      ("last_login", "TEXT"),
      ("created_at", "TEXT"),
  ]:
    try:
      c.execute(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}")
    except Exception:
      pass

  # 2. Audit Logs
  c.execute("""CREATE TABLE IF NOT EXISTS audit_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        action TEXT NOT NULL,
        module TEXT,
        details TEXT,
        ip_address TEXT DEFAULT '127.0.0.1',
        timestamp TEXT
    )""")

  # 3. System Settings
  c.execute("""CREATE TABLE IF NOT EXISTS system_settings (
        key TEXT PRIMARY KEY,
        val TEXT,
        updated_at TEXT
    )""")

  # 4. Announcements
  c.execute("""CREATE TABLE IF NOT EXISTS announcements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        message TEXT NOT NULL,
        priority TEXT DEFAULT 'ปกติ',
        target_role TEXT DEFAULT 'all',
        created_by TEXT,
        created_at TEXT
    )""")

  # 5. Core ERP Tables
  c.execute("""CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL, date TEXT, type TEXT, title TEXT, 
        amount REAL, category TEXT, approval_status TEXT DEFAULT 'Approved'
    )""")

  c.execute("""CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL, doc_type TEXT, doc_number TEXT, issue_date TEXT, 
        client_name TEXT, client_tax_id TEXT, items_summary TEXT, 
        subtotal REAL, vat_amount REAL, grand_total REAL, 
        payment_status TEXT DEFAULT 'Unpaid', created_at TEXT
    )""")

  c.execute("""CREATE TABLE IF NOT EXISTS inventory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL, item_code TEXT, item_name TEXT, category TEXT, 
        qty REAL, unit TEXT, unit_price REAL, updated_at TEXT
    )""")

  c.execute("""CREATE TABLE IF NOT EXISTS clients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL, name TEXT, tax_id TEXT, client_type TEXT, 
        address TEXT, phone TEXT, created_at TEXT
    )""")

  c.execute("""CREATE TABLE IF NOT EXISTS employees (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL, emp_id TEXT, name TEXT, position TEXT, base_salary REAL
    )""")

  c.execute("""CREATE TABLE IF NOT EXISTS assets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL, asset_code TEXT, asset_name TEXT, purchase_date TEXT, 
        cost REAL, useful_life INTEGER, scrap_value REAL, annual_depreciation REAL
    )""")

  c.execute("""CREATE TABLE IF NOT EXISTS budgets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL, department TEXT, allocated_amount REAL, year_month TEXT
    )""")

  c.execute("""CREATE TABLE IF NOT EXISTS expense_claims (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL, claim_title TEXT, amount REAL, category TEXT, 
        status TEXT DEFAULT 'Pending', created_at TEXT
    )""")

  # Seed Demo Users
  admin_pass = hash_password("123456")
  user_pass = hash_password("123456")
  now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

  c.execute(
      """INSERT OR IGNORE INTO users 
        (username, password_hash, full_name, email, company, department, role, status, allowed_modules, created_at) 
        VALUES ('demo_admin', ?, 'Super Administrator', 'admin@company.com', 'Tech Studio Co., Ltd.', 'Management', 'admin', 'active', 'all', ?)""",
      (admin_pass, now_str),
  )

  c.execute(
      """INSERT OR IGNORE INTO users 
        (username, password_hash, full_name, email, company, department, role, status, allowed_modules, created_at) 
        VALUES ('demo_user', ?, 'General Staff', 'user@company.com', 'Tech Studio Co., Ltd.', 'Accounting', 'user', 'active', 'all', ?)""",
      (user_pass, now_str),
  )

  conn.commit()
  conn.close()


def get_all_users():
  conn = get_connection()
  df = pd.read_sql_query(
      """SELECT id, username, full_name, email, company, department, role, status, allowed_modules, last_login, created_at 
         FROM users ORDER BY id ASC""",
      conn,
  )
  conn.close()
  return df


def add_new_user(
    username,
    password,
    full_name,
    email,
    company,
    department,
    role,
    allowed_modules,
):
  try:
    conn = get_connection()
    c = conn.cursor()
    pass_h = hash_password(password)
    mods_str = (
        json.dumps(allowed_modules, ensure_ascii=False)
        if isinstance(allowed_modules, list)
        else allowed_modules
    )
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    c.execute(
        """INSERT INTO users (username, password_hash, full_name, email, company, department, role, status, allowed_modules, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, 'active', ?, ?)""",
        (
            username,
            pass_h,
            full_name,
            email,
            company,
            department,
            role,
            mods_str,
            now_str,
        ),
    )
    conn.commit()
    conn.close()
    return True, "เพิ่มผู้ใช้งานสำเร็จ!"
  except sqlite3.IntegrityError:
    return False, "Username นี้มีอยู่ในระบบแล้ว"
  except Exception as e:
    return False, f"เกิดข้อผิดพลาด: {e}"


def update_user_status(username, status):
  conn = get_connection()
  c = conn.cursor()
  c.execute(
      "UPDATE users SET status = ? WHERE username = ?", (status, username)
  )
  conn.commit()
  conn.close()


def update_user_permissions(username, role, department, allowed_modules):
  conn = get_connection()
  c = conn.cursor()
  mods_str = (
      json.dumps(allowed_modules, ensure_ascii=False)
      if isinstance(allowed_modules, list)
      else allowed_modules
  )
  c.execute(
      """UPDATE users SET role = ?, department = ?, allowed_modules = ? WHERE username = ?""",
      (role, department, mods_str, username),
  )
  conn.commit()
  conn.close()


def admin_reset_password(username, new_password):
  conn = get_connection()
  c = conn.cursor()
  pass_h = hash_password(new_password)
  c.execute(
      "UPDATE users SET password_hash = ? WHERE username = ?",
      (pass_h, username),
  )
  conn.commit()
  conn.close()


def log_audit(
    username, action, module="System", details="", ip_address="127.0.0.1"
):
  try:
    conn = get_connection()
    c = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute(
        """INSERT INTO audit_logs (username, action, module, details, ip_address, timestamp)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (username, action, module, details, ip_address, now_str),
    )
    conn.commit()
    conn.close()
  except Exception:
    pass


def get_audit_logs(limit=300):
  conn = get_connection()
  df = pd.read_sql_query(
      f"SELECT * FROM audit_logs ORDER BY id DESC LIMIT {limit}", conn
  )
  conn.close()
  return df


def get_database_health_stats():
  conn = get_connection()
  c = conn.cursor()
  tables = [
      "users",
      "transactions",
      "documents",
      "inventory",
      "clients",
      "employees",
      "assets",
      "budgets",
      "expense_claims",
      "audit_logs",
  ]
  stats = {}
  for tbl in tables:
    try:
      c.execute(f"SELECT COUNT(*) FROM {tbl}")
      stats[tbl] = c.fetchone()[0]
    except Exception:
      stats[tbl] = 0
  conn.close()

  db_size_mb = 0.0
  if os.path.exists(DB_NAME):
    db_size_mb = os.path.getsize(DB_NAME) / (1024 * 1024)

  return stats, round(db_size_mb, 2)


def get_cover_settings():
  try:
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT val FROM system_settings WHERE key = 'cover_config'")
    row = c.fetchone()
    conn.close()
    if row and row[0]:
      return json.loads(row[0])
  except Exception:
    pass

  return {
      "badge": "GLOBAL COMPLIANCE & THAI TAX READY",
      "title": "🏛️ TaxMate Enterprise ERP Suite",
      "subtitle": "The Complete Financial Management & Compliance Solution",
      "description": (
          "ระบบศูนย์กลางบริหารการเงิน ภาษีไทย e-Tax สต็อก งบการเงินอัตโนมัติ และ"
          " HR สำหรับองค์กรยุคใหม่"
      ),
      "theme_color": "#2563EB",
  }


def save_cover_settings(config_dict):
  conn = get_connection()
  c = conn.cursor()
  now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  c.execute(
      """INSERT OR REPLACE INTO system_settings (key, val, updated_at) VALUES ('cover_config', ?, ?)""",
      (json.dumps(config_dict, ensure_ascii=False), now_str),
  )
  conn.commit()
  conn.close()


def get_db_bytes():
  if os.path.exists(DB_NAME):
    with open(DB_NAME, "rb") as f:
      return f.read()
  return b""


def restore_db_from_bytes(file_bytes):
  try:
    with open(DB_NAME, "wb") as f:
      f.write(file_bytes)
    return True, "กู้คืนฐานข้อมูลสำเร็จ!"
  except Exception as e:
    return False, f"เกิดข้อผิดพลาดในการกู้คืน: {e}"
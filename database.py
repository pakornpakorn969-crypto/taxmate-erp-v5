import sqlite3
from datetime import datetime, timedelta
import random

DB_NAME = "taxmate_enterprise_auth.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def log_audit(user_id, action, details=""):
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute('''INSERT INTO audit_logs (user_id, action, details, timestamp)
                     VALUES (?, ?, ?, ?)''', 
                  (user_id, action, details, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Audit log error: {e}")

def init_db():
    conn = get_connection()
    c = conn.cursor()
    
    # 1. ตารางผู้ใช้
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        salt TEXT NOT NULL,
        company_name TEXT NOT NULL,
        role TEXT DEFAULT 'user',
        created_at TEXT NOT NULL,
        last_login TEXT,
        failed_attempts INTEGER DEFAULT 0,
        lockout_until TEXT
    )''')

    # 2. ตารางธุรกรรม
    c.execute('''CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        date TEXT NOT NULL,
        type TEXT NOT NULL,
        title TEXT NOT NULL,
        amount REAL NOT NULL,
        wht_amount REAL DEFAULT 0,
        wht_rate REAL DEFAULT 0,
        vat_amount REAL DEFAULT 0,
        is_vat INTEGER DEFAULT 0,
        category TEXT NOT NULL,
        account_name TEXT DEFAULT 'SCB Primary',
        status TEXT DEFAULT 'Paid',
        due_date TEXT,
        client_name TEXT,
        client_tax_id TEXT,
        approval_status TEXT DEFAULT 'Approved',
        attachment_file TEXT
    )''')

    # 3. ตารางตั้งค่าองค์กร
    c.execute('''CREATE TABLE IF NOT EXISTS company_settings (
        id INTEGER PRIMARY KEY,
        company_name TEXT,
        tax_id TEXT,
        doc_prefix TEXT,
        approval_threshold REAL DEFAULT 50000.0
    )''')

    c.execute("SELECT COUNT(*) FROM company_settings")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO company_settings (id, company_name, tax_id, doc_prefix, approval_threshold) VALUES (1, 'บริษัท สยามพาร์ทเนอร์ จำกัด', '0105550000000', 'INV-', 50000.0)")

    # 4. ตารางสมุดรายชื่อลูกค้า / คู่ค้า (Client & Vendor Directory)
    c.execute('''CREATE TABLE IF NOT EXISTS clients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        name TEXT NOT NULL,
        tax_id TEXT,
        client_type TEXT DEFAULT 'Customer',
        address TEXT,
        phone TEXT,
        created_at TEXT NOT NULL
    )''')

    # 5. ตารางล็อกงบการเงินประจำเดือน (Period Lock)
    c.execute('''CREATE TABLE IF NOT EXISTS period_locks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        year_month TEXT UNIQUE NOT NULL,
        is_locked INTEGER DEFAULT 1,
        locked_by TEXT NOT NULL,
        locked_at TEXT NOT NULL
    )''')

    # 6. ตารางระบบอื่นๆ
    c.execute('''CREATE TABLE IF NOT EXISTS accounts (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT NOT NULL, account_name TEXT NOT NULL, account_type TEXT NOT NULL, balance REAL NOT NULL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        user_id TEXT NOT NULL, 
        doc_type TEXT NOT NULL, 
        doc_number TEXT NOT NULL, 
        issue_date TEXT NOT NULL, 
        due_date TEXT, 
        client_name TEXT NOT NULL, 
        client_tax_id TEXT, 
        items_summary TEXT NOT NULL, 
        subtotal REAL NOT NULL, 
        vat_amount REAL DEFAULT 0, 
        grand_total REAL NOT NULL, 
        status TEXT DEFAULT 'Completed', 
        payment_status TEXT DEFAULT 'Unpaid',
        created_at TEXT NOT NULL
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS audit_logs (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT NOT NULL, action TEXT NOT NULL, details TEXT, timestamp TEXT NOT NULL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS announcements (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, message TEXT NOT NULL, priority TEXT DEFAULT 'Normal', created_by TEXT NOT NULL, created_at TEXT NOT NULL)''')

    # Auto Migration
    c.execute("PRAGMA table_info(transactions)")
    cols = [column[1] for column in c.fetchall()]
    if 'attachment_file' not in cols:
        c.execute("ALTER TABLE transactions ADD COLUMN attachment_file TEXT")
    if 'approval_status' not in cols:
        c.execute("ALTER TABLE transactions ADD COLUMN approval_status TEXT DEFAULT 'Approved'")

    c.execute("PRAGMA table_info(documents)")
    doc_cols = [column[1] for column in c.fetchall()]
    if 'payment_status' not in doc_cols:
        c.execute("ALTER TABLE documents ADD COLUMN payment_status TEXT DEFAULT 'Unpaid'")

    conn.commit()
    conn.close()

def seed_financial_data_for_user(username):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM transactions WHERE user_id = ?", (username,))
    
    # เพิ่มคู่ค้าตัวอย่าง
    c.execute("SELECT COUNT(*) FROM clients WHERE user_id = ?", (username,))
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO clients (user_id, name, tax_id, client_type, address, phone, created_at) VALUES (?, 'บริษัท สยามเทคโนโลยี จำกัด', '0105560000012', 'Customer', '123 ถนนสุขุมวิท กทม.', '02-123-4567', ?)", (username, datetime.now().strftime("%Y-%m-%d")))
        c.execute("INSERT INTO clients (user_id, name, tax_id, client_type, address, phone, created_at) VALUES (?, 'หจก. การตลาดออนไลน์ ซัพพลาย', '0103550000099', 'Vendor', '456 ถนนพหลโยธิน กทม.', '02-987-6543', ?)", (username, datetime.now().strftime("%Y-%m-%d")))

    c.execute("SELECT approval_threshold FROM company_settings WHERE id = 1")
    row = c.fetchone()
    threshold = row[0] if row else 50000.0
    
    today = datetime.today()
    cats_inc = ["40(2) ค่าจ้างทั่วไป", "40(6) วิชาชีพอิสระ", "40(8) ค้าขาย/บริการ"]
    cats_exp = ["อุปกรณ์/ซอฟต์แวร์", "การตลาด/โฆษณา", "เดินทาง/ที่พัก", "ค่าใช้จ่ายทั่วไป"]
    
    for i in range(15):
        days_ago = random.randint(0, 30)
        t_date = today - timedelta(days=days_ago)
        t_type = random.choice(["Income", "Income", "Expense"])
        amt = random.choice([5000, 15000, 35000, 60000, 120000])
        app_status = 'Pending' if (t_type == "Expense" and amt > threshold) else 'Approved'
        cat = random.choice(cats_inc if t_type == "Income" else cats_exp)
        
        c.execute('''
            INSERT INTO transactions (user_id, date, type, title, amount, category, approval_status, is_vat, wht_amount, wht_rate)
            VALUES (?, ?, ?, ?, ?, ?, ?, 1, ?, 0.03)
        ''', (username, t_date.strftime("%Y-%m-%d"), t_type, f"รายการพัฒนาระบบและที่ปรึกษา #{i+1}", amt, cat, app_status, amt*0.03))
        
    conn.commit()
    conn.close()

def get_audit_logs(user_id=None, is_admin=False):
    conn = get_connection()
    c = conn.cursor()
    if is_admin:
        c.execute("SELECT user_id, action, details, timestamp FROM audit_logs ORDER BY id DESC LIMIT 100")
    else:
        c.execute("SELECT user_id, action, details, timestamp FROM audit_logs WHERE user_id = ? ORDER BY id DESC LIMIT 50", (user_id,))
    rows = c.fetchall()
    conn.close()
    return rows
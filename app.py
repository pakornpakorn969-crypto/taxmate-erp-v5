import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import sqlite3
import hashlib
import json
from datetime import datetime, timedelta

# ==========================================
# 1. ADVANCED PAGE CONFIG & MODERN ENTERPRISE THEME
# ==========================================
st.set_page_config(
    page_title="TaxMate Enterprise ERP Suite v3.0",
    page_icon="🖥️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom High-End Ultra Clean Light Theme CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;500;600;700;800&family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Sarabun', 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .stApp {
        background-color: #F8FAFC;
        color: #0F172A;
    }

    /* Landing Hero Banner */
    .hero-container-3d {
        background: #EFF6FF;
        border: 1px solid #BFDBFE;
        border-radius: 24px;
        padding: 40px 30px;
        text-align: center;
        margin-bottom: 25px;
        box-shadow: 0 10px 30px rgba(37, 99, 235, 0.05);
    }
    .hero-badge-pill {
        display: inline-block;
        background: #1D4ED8;
        color: #FFFFFF;
        font-size: 11.5px;
        font-weight: 800;
        padding: 6px 18px;
        border-radius: 9999px;
        letter-spacing: 0.8px;
        margin-bottom: 18px;
        box-shadow: 0 4px 12px rgba(29, 78, 216, 0.25);
    }
    .hero-title-main {
        font-size: 34px;
        font-weight: 800;
        color: #0F172A;
        margin: 0 0 10px 0;
        letter-spacing: -0.5px;
    }
    .hero-subtitle-blue {
        font-size: 16px;
        font-weight: 700;
        color: #2563EB;
        margin-bottom: 12px;
    }
    .hero-desc-text {
        font-size: 13.5px;
        color: #475569;
        max-width: 820px;
        margin: 0 auto;
        line-height: 1.6;
    }

    /* 3D Cube Canvas Styling */
    .cube-stage {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 260px;
        margin: 20px 0 30px 0;
        perspective: 900px;
    }
    .orbit-ellipse {
        position: absolute;
        width: 320px;
        height: 120px;
        border: 3px solid #2563EB;
        border-radius: 50%;
        transform: rotateX(72deg) rotateY(-18deg);
        box-shadow: 0 0 20px rgba(37, 99, 235, 0.4), inset 0 0 20px rgba(37, 99, 235, 0.3);
        animation: spinOrbit 10s linear infinite;
    }
    .cube-box-3d {
        width: 110px;
        height: 110px;
        position: relative;
        transform-style: preserve-3d;
        animation: rotateCube3D 14s infinite linear;
    }
    .cube-side {
        position: absolute;
        width: 110px;
        height: 110px;
        background: rgba(59, 130, 246, 0.35);
        border: 2px solid #0284C7;
        box-shadow: 0 0 15px rgba(2, 132, 199, 0.4);
    }
    .side-front  { transform: rotateY(0deg) translateZ(55px); }
    .side-back   { transform: rotateY(180deg) translateZ(55px); }
    .side-right  { transform: rotateY(90deg) translateZ(55px); }
    .side-left   { transform: rotateY(-90deg) translateZ(55px); }
    .side-top    { transform: rotateX(90deg) translateZ(55px); }
    .side-bottom { transform: rotateX(-90deg) translateZ(55px); }

    @keyframes rotateCube3D {
        0% { transform: rotateX(15deg) rotateY(0deg); }
        100% { transform: rotateX(15deg) rotateY(360deg); }
    }
    @keyframes spinOrbit {
        0% { transform: rotateX(72deg) rotateZ(0deg); }
        100% { transform: rotateX(72deg) rotateZ(360deg); }
    }

    /* Sidebar Overrides */
    section[data-testid="stSidebar"] {
        background-color: #F8FAFC !important;
        border-right: 1px solid #E2E8F0 !important;
    }
    
    /* Authentication Card Styling */
    .login-card-light {
        background: #FFFFFF;
        padding: 32px 36px;
        border-radius: 20px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.04);
        margin-top: 10px;
    }
    
    /* Primary Coral Red Buttons */
    .stButton>button[kind="primary"], .stFormSubmitButton>button[kind="primary"] {
        background-color: #FF4B4B !important;
        border-color: #FF4B4B !important;
        color: #FFFFFF !important;
        border-radius: 10px;
        font-weight: 700;
        padding: 10px 24px;
    }
    .stButton>button[kind="primary"]:hover, .stFormSubmitButton>button[kind="primary"]:hover {
        background-color: #E03E3E !important;
        border-color: #E03E3E !important;
    }

    .stDataFrame {
        border-radius: 14px;
        overflow: hidden;
        border: 1px solid #E2E8F0;
        background-color: #FFFFFF;
    }
</style>
""", unsafe_allow_html=True)


# ==========================================
# 2. AUTO-REPAIRING FAIL-SAFE DATABASE ENGINE
# ==========================================
DB_FILE = "taxmate_erp_v3.db"

def get_db_connection():
    conn = sqlite3.connect(DB_FILE, timeout=15)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def ensure_table_columns(cursor, table_name, required_cols):
    """Auto-repair schema by dynamically injecting missing columns."""
    cursor.execute(f"PRAGMA table_info({table_name})")
    existing_cols = [row['name'] for row in cursor.fetchall()]
    for col_name, col_type in required_cols.items():
        if col_name not in existing_cols:
            cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col_type}")

def init_db_v3():
    """Fail-safe DB initialization with complete schema validation."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 1. Users Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT NOT NULL,
            role TEXT NOT NULL,
            department TEXT NOT NULL,
            email TEXT,
            status TEXT DEFAULT 'Active'
        )
        """)
        ensure_table_columns(cursor, "users", {
            "full_name": "TEXT DEFAULT 'ผู้ใช้งาน'",
            "role": "TEXT DEFAULT 'Executive'",
            "department": "TEXT DEFAULT 'ทั่วไป'",
            "email": "TEXT DEFAULT 'user@taxmate.co.th'",
            "status": "TEXT DEFAULT 'Active'"
        })
        
        # 2. Sales Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            doc_no TEXT UNIQUE NOT NULL,
            customer TEXT NOT NULL,
            amount REAL NOT NULL,
            tax REAL NOT NULL,
            total REAL NOT NULL,
            status TEXT NOT NULL,
            branch TEXT DEFAULT 'สำนักงานใหญ่',
            payment_method TEXT DEFAULT 'โอนเงินผ่านธนาคาร',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # 3. Products Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sku TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            stock INTEGER NOT NULL,
            category TEXT NOT NULL,
            branch TEXT DEFAULT 'สำนักงานใหญ่',
            min_stock INTEGER DEFAULT 10
        )
        """)

        # 4. Employees Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            emp_code TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            position TEXT NOT NULL,
            salary REAL NOT NULL,
            department TEXT NOT NULL,
            status TEXT DEFAULT 'Active'
        )
        """)

        # 5. Audit Logs Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_name TEXT NOT NULL,
            action TEXT NOT NULL,
            ip_address TEXT DEFAULT '127.0.0.1',
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # 6. Announcements Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS announcements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            priority TEXT DEFAULT 'Normal',
            target_role TEXT DEFAULT 'All',
            status TEXT DEFAULT 'Active',
            created_by TEXT DEFAULT 'ฝ่ายบริหาร',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # 7. Journal Entries Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS journal_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entry_date TEXT NOT NULL,
            account_code TEXT NOT NULL,
            account_name TEXT NOT NULL,
            debit REAL DEFAULT 0.0,
            credit REAL DEFAULT 0.0,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # Seed Default Users
        default_users = [
            ("admin", hash_password("admin123"), "ผู้บริหารสูงสุด (CEO / Admin)", "Executive", "บริหารและจัดการ (Executive)", "ceo@taxmate.co.th"),
            ("accountant", hash_password("acc123"), "หัวหน้าแผนกบัญชี", "Accounting", "บัญชีและการเงิน", "accounting@taxmate.co.th"),
            ("pos_staff", hash_password("pos123"), "พนักงานขาย POS", "POS", "หน้าร้าน/การขาย", "pos@taxmate.co.th"),
            ("hr_manager", hash_password("hr123"), "ผู้จัดการฝ่ายบุคคล", "HR", "ทรัพยากรบุคคล", "hr@taxmate.co.th")
        ]
        for username, pwd, name, role, dept, email in default_users:
            cursor.execute("""
            INSERT OR IGNORE INTO users (username, password_hash, full_name, role, department, email) 
            VALUES (?, ?, ?, ?, ?, ?)
            """, (username, pwd, name, role, dept, email))

        # Seed Demo Sales Data
        cursor.execute("SELECT COUNT(*) FROM sales")
        if cursor.fetchone()[0] == 0:
            demo_sales = [
                ("INV-202610-001", "บริษัท สยามเทคโนโลยี จำกัด", 150000.0, 10500.0, 160500.0, "ชำระแล้ว", "สำนักงานใหญ่", "โอนเงินผ่านธนาคาร"),
                ("INV-202610-002", "บจก. กิจการร่วมค้าไทย", 85000.0, 5950.0, 90950.0, "รอชำระ", "สาขาเชียงใหม่", "เครดิต 30 วัน"),
                ("INV-202610-003", "ห้างหุ้นส่วนจำกัด โกลบอลการค้า", 240000.0, 16800.0, 256800.0, "ชำระแล้ว", "สาขาภูเก็ต", "บัตรเครดิต"),
                ("INV-202610-004", "บมจ. อุตสาหกรรมก้าวหน้า", 320000.0, 22400.0, 342400.0, "ชำระแล้ว", "สำนักงานใหญ่", "โอนเงินผ่านธนาคาร"),
                ("INV-202610-005", "บจก. ดิจิทัล โซลูชันส์", 95000.0, 6650.0, 101650.0, "รอชำระ", "สาขาเชียงใหม่", "เครดิต 30 วัน")
            ]
            for doc, cust, amt, tax, tot, status, branch, pay_m in demo_sales:
                cursor.execute("""
                INSERT OR IGNORE INTO sales (doc_no, customer, amount, tax, total, status, branch, payment_method) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (doc, cust, amt, tax, tot, status, branch, pay_m))

        # Seed Demo Products Data
        cursor.execute("SELECT COUNT(*) FROM products")
        if cursor.fetchone()[0] == 0:
            demo_products = [
                ("SKU-001", "ระบบซอฟต์แวร์ ERP Enterprise v3.0", 150000.0, 50, "Software", "สำนักงานใหญ่", 5),
                ("SKU-002", "เครื่องสแกนบาร์โค้ด High Speed POS 2D", 4500.0, 120, "Hardware", "สำนักงานใหญ่", 15),
                ("SKU-003", "เครื่องพิมพ์ใบเสร็จความร้อน Thermal 80mm", 3200.0, 85, "Hardware", "สาขาเชียงใหม่", 10),
                ("SKU-004", "ลิขสิทธิ์ระบบบัญชี Cloud ERP (รายปี)", 25000.0, 200, "License", "สำนักงานใหญ่", 20),
                ("SKU-005", "เครื่องรูดบัตร Smart EDC Wireless 4G", 8900.0, 40, "Hardware", "สาขาภูเก็ต", 8)
            ]
            for sku, p_name, price, stock, cat, branch, min_s in demo_products:
                cursor.execute("""
                INSERT OR IGNORE INTO products (sku, name, price, stock, category, branch, min_stock) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (sku, p_name, price, stock, cat, branch, min_s))

        # Seed Demo Employees Data
        cursor.execute("SELECT COUNT(*) FROM employees")
        if cursor.fetchone()[0] == 0:
            demo_emps = [
                ("EMP-001", "นายสมชาย ใจดี", "Chief Executive Officer (CEO)", 150000.0, "ผู้บริหาร"),
                ("EMP-002", "นางสาววิภาดา เงินงาม", "Senior Accountant", 45000.0, "บัญชีและการเงิน"),
                ("EMP-003", "นายธนกร ขายดี", "POS Sales Manager", 38000.0, "หน้าร้าน/การขาย"),
                ("EMP-004", "นางสาวกานดา รักดี", "HR Director", 55000.0, "ทรัพยากรบุคคล")
            ]
            for code, e_name, pos, sal, dept in demo_emps:
                cursor.execute("""
                INSERT OR IGNORE INTO employees (emp_code, name, position, salary, department) 
                VALUES (?, ?, ?, ?, ?)
                """, (code, e_name, pos, sal, dept))

        # Seed Demo Announcements Data
        cursor.execute("SELECT COUNT(*) FROM announcements")
        if cursor.fetchone()[0] == 0:
            demo_announcements = [
                ("📢 แจ้งอัปเดตระบบ TaxMate Enterprise ERP v3.0", "ระบบได้ทำการปรับปรุงหน้าจอ Light Mode และเพิ่มประสิทธิภาพฐานข้อมูลเรียบร้อยแล้ว", "Normal", "All", "Active", "ฝ่ายไอทีและระบบ"),
                ("🔴 กำหนดการส่งงบการเงินและยื่นภาษีประจำเดือน", "ขอให้ฝ่ายบัญชีตรวจสอบและสรุปรายงานภาษีมูลค่าเพิ่ม ภ.พ.30 ภายในวันที่ 15 ของเดือนนี้อย่างเคร่งครัด", "Urgent", "All", "Active", "ผู้บริหารสูงสุด (CEO)")
            ]
            for title, content, priority, target, status, author in demo_announcements:
                cursor.execute("""
                INSERT INTO announcements (title, content, priority, target_role, status, created_by) 
                VALUES (?, ?, ?, ?, ?, ?)
                """, (title, content, priority, target, status, author))

        # Seed Demo Journal Entries Data
        cursor.execute("SELECT COUNT(*) FROM journal_entries")
        if cursor.fetchone()[0] == 0:
            demo_journals = [
                ("15/10/2026", "111000", "เงินฝากกระแสรายวัน (ธ.กสิกรไทย)", 160500.0, 0.0, "รับชำระค่าบริการซอฟต์แวร์ ERP"),
                ("15/10/2026", "411000", "รายได้จากการขายซอฟต์แวร์ ERP", 0.0, 150000.0, "รับชำระค่าบริการซอฟต์แวร์ ERP"),
                ("15/10/2026", "213100", "ภาษีขายรอส่ง (VAT Output)", 0.0, 10500.0, "ภาษีขาย VAT 7%"),
                ("14/10/2026", "511000", "ค่าใช้จ่ายซอฟต์แวร์และฮาร์ดแวร์", 45000.0, 0.0, "ซื้ออุปกรณ์ไอทีประจำสำนักงาน"),
                ("14/10/2026", "111000", "เงินฝากกระแสรายวัน", 0.0, 45000.0, "จ่ายชำระค่าอุปกรณ์ไอที")
            ]
            for dt, code, name, deb, cred, desc in demo_journals:
                cursor.execute("""
                INSERT INTO journal_entries (entry_date, account_code, account_name, debit, credit, description)
                VALUES (?, ?, ?, ?, ?, ?)
                """, (dt, code, name, deb, cred, desc))

        conn.commit()
        conn.close()
    except Exception as e:
        st.error(f"❌ ระบบเกิดข้อผิดพลาดในการเริ่มต้นฐานข้อมูล: {str(e)}")

def log_audit_action(user_name, action):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO audit_logs (user_name, action) VALUES (?, ?)", (user_name, action))
        conn.commit()
        conn.close()
    except Exception:
        pass

# Initialize DB
init_db_v3()


# ==========================================
# 3. ANNOUNCEMENT CARD COMPONENT (SHARED)
# ==========================================
def render_landing_announcements():
    """ดึงรายการประกาศสำคัญมาแสดงผลด้วยการ์ดขอบสี (ใช้ร่วมกันได้ทั้งหน้าแรก และ หน้า Admin)"""
    try:
        conn = get_db_connection()
        query = "SELECT * FROM announcements WHERE status = 'Active' AND target_role = 'All' ORDER BY id DESC"
        df_anc = pd.read_sql_query(query, conn)
        conn.close()
        
        if not df_anc.empty:
            st.markdown("<h4 style='color: #1E293B; font-weight: 800; margin-top: 20px; margin-bottom: 15px;'>📢 ประกาศสำคัญจากองค์กร (Latest Announcements)</h4>", unsafe_allow_html=True)
            for idx, row in df_anc.iterrows():
                p = row.get("priority", "Normal")
                card_style = "background: #FFFFFF; border-left: 6px solid #2563EB; border-top: 1px solid #E2E8F0; border-right: 1px solid #E2E8F0; border-bottom: 1px solid #E2E8F0;"
                badge = "ℹ️ ประกาศทั่วไป"
                icon_title = "📢"
                if p == "Urgent":
                    card_style = "background: #FEF2F2; border-left: 6px solid #EF4444; border-top: 1px solid #FCA5A5; border-right: 1px solid #FCA5A5; border-bottom: 1px solid #FCA5A5;"
                    badge = "🚨 ประกาศด่วนที่สุด"
                    icon_title = "🔴"
                elif p == "High":
                    card_style = "background: #FFFBEB; border-left: 6px solid #F59E0B; border-top: 1px solid #FDE68A; border-right: 1px solid #FDE68A; border-bottom: 1px solid #FDE68A;"
                    badge = "⚠️ ประกาศสำคัญ"
                    icon_title = "⚠️"
                
                st.markdown(f"""
                <div style="{card_style} border-radius: 14px; padding: 18px 24px; margin-bottom: 16px; box-shadow: 0 4px 15px rgba(0,0,0,0.03);">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                        <strong style="font-size: 16px; color: #0F172A;">{icon_title} {row['title']}</strong>
                        <span style="font-size: 12px; font-weight: 700; color: #475569;">{badge} • โดย {row['created_by']} ({row['created_at']})</span>
                    </div>
                    <div style="font-size: 14px; color: #334155; line-height: 1.6;">{row['content']}</div>
                </div>
                """, unsafe_allow_html=True)
    except Exception:
        pass


# ==========================================
# 4. LANDING PAGE & AUTHENTICATION CENTER
# ==========================================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.user = None

if not st.session_state.authenticated:
    # Sidebar Navigation for Unauthenticated Visitors
    with st.sidebar:
        st.markdown("""
        <div style="padding: 10px 0 15px 0;">
            <div style="font-size: 38px; margin-bottom: 4px;">🌐🔑</div>
            <h3 style="margin: 0; color: #0F172A; font-weight: 800; font-size: 20px;">TaxMate ERP</h3>
        </div>
        """, unsafe_allow_html=True)
        
        init_nav = st.radio(
            "📍 เมนูเริ่มต้น:",
            ["🏠 หน้าแรก (หน้าต้อนรับ 3 มิติ)", "🔑 เข้าสู่ระบบ / ลงทะเบียน"]
        )
        
        st.divider()
        st.markdown("""
        <div style="font-size: 13px; color: #475569; line-height: 1.8;">
            🟢 <b>สถานะเซิร์ฟเวอร์:</b> ออนไลน์ 24/7<br>
            ☁️ <b>ผู้ให้บริการ:</b> Render Cloud
        </div>
        """, unsafe_allow_html=True)

    # Page 1: 3D Landing Page
    if init_nav == "🏠 หน้าแรก (หน้าต้อนรับ 3 มิติ)":
        st.markdown("""
        <div class="hero-container-3d">
            <span class="hero-badge-pill">🥷 NEXT-GEN 3D ENTERPRISE ERP ENGINE</span>
            <div class="hero-title-main">🏛️ TaxMate Enterprise ERP Suite</div>
            <div class="hero-subtitle-blue">The Interactive 3D Cloud Financial & Compliance Platform</div>
            <div class="hero-desc-text">
                ศูนย์กลางบริหารจัดการบัญชี ภาษีไทย e-Tax สต็อกหลายสาขา การผลิต CRM และทรัพยากรมนุษย์ ด้วยสถาปัตยกรรมระดับองค์กรชั้นนำ
            </div>
        </div>
        
        <!-- 3D Cube Canvas -->
        <div class="cube-stage">
            <div class="orbit-ellipse"></div>
            <div class="cube-box-3d">
                <div class="cube-side side-front"></div>
                <div class="cube-side side-back"></div>
                <div class="cube-side side-right"></div>
                <div class="cube-side side-left"></div>
                <div class="cube-side side-top"></div>
                <div class="cube-side side-bottom"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        render_landing_announcements()

    # Page 2: AUTHENTICATION CENTER (ศูนย์ยืนยันตัวตน)
    else:
        st.markdown("""
        <div style="margin-bottom: 25px;">
            <h2 style="color: #0F172A; font-size: 30px; font-weight: 800; margin: 0; display: flex; align-items: center; gap: 8px;">
                🔑 ศูนย์ยืนยันตัวตน (Authentication Center)
            </h2>
            <p style="color: #64748B; font-size: 14px; margin-top: 5px;">ระบบเข้าสู่ระบบ ลงทะเบียน และกู้คืนรหัสผ่านสำหรับพนักงานและผู้ดูแลระบบ</p>
        </div>
        """, unsafe_allow_html=True)
        
        tab_login, tab_signup, tab_forgot = st.tabs([
            "🔑 เข้าสู่ระบบ (Login)", 
            "📝 ลงทะเบียนผู้ใช้ใหม่ (Register)", 
            "🔑 ลืมรหัสผ่าน (Forgot Password)"
        ])
        
        # TAB 1: LOGIN (SIGN IN)
        with tab_login:
            col1, col2, col3 = st.columns([1, 1.4, 1])
            with col2:
                st.markdown('<div class="login-card-light">', unsafe_allow_html=True)
                with st.form("login_form_v3"):
                    st.markdown("<h3 style='color: #0F172A; font-weight: 800; font-size: 26px; margin-bottom: 22px;'>ลงชื่อเข้าใช้งานระบบ (Sign In)</h3>", unsafe_allow_html=True)
                    login_user = st.text_input("ชื่อผู้ใช้งาน (Username)", value="admin")
                    login_pwd = st.text_input("รหัสผ่าน (Password)", type="password", value="admin123")
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    submit_login = st.form_submit_button("เข้าสู่ระบบประมวลผล", use_container_width=True, type="primary")
                    
                    if submit_login:
                        try:
                            conn = get_db_connection()
                            cursor = conn.cursor()
                            cursor.execute("SELECT * FROM users WHERE username = ? AND password_hash = ?", 
                                           (login_user, hash_password(login_pwd)))
                            user = cursor.fetchone()
                            conn.close()
                            
                            if user:
                                user_dict = dict(user)
                                if user_dict.get("status") == "Inactive":
                                    st.error("บัญชีผู้ใช้งานนี้ถูกระงับการใช้งานชั่วคราว")
                                else:
                                    st.session_state.authenticated = True
                                    st.session_state.user = user_dict
                                    log_audit_action(user_dict.get('full_name', 'User'), "เข้าสู่ระบบสำเร็จ (Login)")
                                    st.success(f"ยินดีต้อนรับคุณ {user_dict.get('full_name', 'User')} เข้าสู่ระบบ")
                                    st.rerun()
                            else:
                                st.error("ชื่อผู้ใช้งานหรือรหัสผ่านไม่ถูกต้อง")
                        except Exception as e:
                            st.error(f"เกิดข้อผิดพลาดในการตรวจสอบสิทธิ์: {str(e)}")
                st.markdown('</div>', unsafe_allow_html=True)

        # TAB 2: REGISTER (SIGN UP - MATCHING IMAGE 1)
        with tab_signup:
            st.markdown('<div class="login-card-light">', unsafe_allow_html=True)
            st.markdown("<h3 style='color: #0F172A; font-weight: 800; font-size: 24px; margin-bottom: 20px;'>ลงทะเบียนผู้ใช้งานใหม่</h3>", unsafe_allow_html=True)
            
            with st.form("signup_form_v3"):
                col_reg1, col_reg2 = st.columns(2)
                
                with col_reg1:
                    reg_name = st.text_input("ชื่อ-นามสกุล ผู้ใช้งาน:")
                    reg_user = st.text_input("ชื่อผู้ใช้งาน (Username):")
                    reg_email = st.text_input("อีเมลองครค์:")
                    
                with col_reg2:
                    role_options = [
                        "Super Admin (ผู้ดูแลระบบสูงสุด)",
                        "👑 Executive (ผู้บริหาร)", 
                        "💰 Accounting (ฝ่ายบัญชี)", 
                        "🛒 POS Staff (พนักงานขายหน้าร้าน)", 
                        "👥 HR Manager (ผู้จัดการฝ่ายบุคคล)"
                    ]
                    role_map = {
                        "Super Admin (ผู้ดูแลระบบสูงสุด)": "Executive",
                        "👑 Executive (ผู้บริหาร)": "Executive",
                        "💰 Accounting (ฝ่ายบัญชี)": "Accounting",
                        "🛒 POS Staff (พนักงานขายหน้าร้าน)": "POS",
                        "👥 HR Manager (ผู้จัดการฝ่ายบุคคล)": "HR"
                    }
                    selected_role_label = st.selectbox("🔑 สิทธิ์การใช้งานในระบบ (Role):", role_options)
                    reg_role = role_map[selected_role_label]
                    
                    reg_dept = st.selectbox("แผนก/ฝ่ายงาน:", ["บริหารและจัดการ (Executive)", "บัญชีและการเงิน", "หน้าร้าน/การขาย", "ทรัพยากรบุคคล", "ทั่วไป"])
                    reg_pwd1 = st.text_input("รหัสผ่าน:", type="password")
                    reg_pwd2 = st.text_input("ยืนยันรหัสผ่าน:", type="password")
                
                st.markdown("<br>", unsafe_allow_html=True)
                auto_login = st.checkbox("⚡ ล็อกอินเข้าสู่ระบบทันทีหลังสร้างบัญชีสำเร็จ", value=True)
                
                submit_signup = st.form_submit_button("📝 บันทึกสร้างบัญชีผู้ใช้ใหม่", type="primary")
                
                if submit_signup:
                    if not reg_name or not reg_email or not reg_user or not reg_pwd1:
                        st.warning("กรุณากรอกข้อมูลให้ครบถ้วนทุกช่อง")
                    elif reg_pwd1 != reg_pwd2:
                        st.error("รหัสผ่านและการยืนยันรหัสผ่านไม่ตรงกัน")
                    else:
                        try:
                            conn = get_db_connection()
                            cursor = conn.cursor()
                            cursor.execute("SELECT id FROM users WHERE username = ?", (reg_user,))
                            if cursor.fetchone():
                                st.error(f"Username '{reg_user}' มีอยู่ในระบบแล้ว กรุณาใช้ชื่ออื่น")
                                conn.close()
                            else:
                                cursor.execute("""
                                INSERT INTO users (username, password_hash, full_name, role, department, email, status)
                                VALUES (?, ?, ?, ?, ?, ?, 'Active')
                                """, (reg_user, hash_password(reg_pwd1), reg_name, reg_role, reg_dept, reg_email))
                                conn.commit()
                                
                                # Fetch newly created user object
                                cursor.execute("SELECT * FROM users WHERE username = ?", (reg_user,))
                                new_user = cursor.fetchone()
                                conn.close()
                                
                                new_user_dict = dict(new_user)
                                log_audit_action(reg_name, f"ลงทะเบียนบัญชีใหม่ ({reg_user}) - สิทธิ์ {reg_role}")
                                
                                if auto_login:
                                    st.session_state.authenticated = True
                                    st.session_state.user = new_user_dict
                                    st.success(f"สร้างบัญชีสำเร็จ! ยินดีต้อนรับคุณ {reg_name} เข้าสู่ระบบ")
                                    st.rerun()
                                else:
                                    st.success("สร้างบัญชีผู้ใช้งานสำเร็จ! สามารถสลับไปแท็บ [เข้าสู่ระบบ] ได้ทันที")
                        except Exception as e:
                            st.error(f"เกิดข้อผิดพลาดในการสร้างบัญชี: {str(e)}")

            st.markdown('</div>', unsafe_allow_html=True)

        # TAB 3: FORGOT PASSWORD
        with tab_forgot:
            col1, col2, col3 = st.columns([1, 1.4, 1])
            with col2:
                st.markdown('<div class="login-card-light">', unsafe_allow_html=True)
                with st.form("forgot_form_v3"):
                    st.markdown("<h3 style='color: #0F172A; font-weight: 800; font-size: 24px; margin-bottom: 20px;'>กู้คืน/ตั้งรหัสผ่านใหม่ (Forgot Password)</h3>", unsafe_allow_html=True)
                    fg_user = st.text_input("ชื่อผู้ใช้งาน (Username)")
                    fg_email = st.text_input("อีเมลที่ลงทะเบียนไว้")
                    
                    c_fp1, c_fp2 = st.columns(2)
                    with c_fp1:
                        new_pwd1 = st.text_input("รหัสผ่านใหม่", type="password")
                    with c_fp2:
                        new_pwd2 = st.text_input("ยืนยันรหัสผ่านใหม่", type="password")
                    
                    submit_forgot = st.form_submit_button("รีเซ็ตรหัสผ่านใหม่", use_container_width=True, type="primary")
                    
                    if submit_forgot:
                        if not fg_user or not fg_email or not new_pwd1:
                            st.warning("กรุณากรอกข้อมูลยืนยันตัวตนให้ครบถ้วน")
                        elif new_pwd1 != new_pwd2:
                            st.error("รหัสผ่านใหม่และการยืนยันไม่ตรงกัน")
                        else:
                            try:
                                conn = get_db_connection()
                                cursor = conn.cursor()
                                cursor.execute("SELECT id, full_name FROM users WHERE username = ? AND email = ?", (fg_user, fg_email))
                                matched_user = cursor.fetchone()
                                
                                if matched_user:
                                    cursor.execute("UPDATE users SET password_hash = ? WHERE id = ?", (hash_password(new_pwd1), matched_user["id"]))
                                    conn.commit()
                                    conn.close()
                                    log_audit_action(matched_user["full_name"], "รีเซ็ตรหัสผ่านใหม่สำเร็จ")
                                    st.success("รีเซ็ตรหัสผ่านสำเร็จ! กรุณาใช้รหัสผ่านใหม่เข้าสู่ระบบ")
                                else:
                                    conn.close()
                                    st.error("ไม่พบข้อมูลผู้ใช้ที่ตรงกับ Username และ Email ดังกล่าว")
                            except Exception as e:
                                st.error(f"เกิดข้อผิดพลาดในการรีเซ็ตรหัสผ่าน: {str(e)}")

                st.markdown('</div>', unsafe_allow_html=True)

    st.stop()


# ==========================================
# 5. AUTHENTICATED BACK-OFFICE DASHBOARD (20 MODULES)
# ==========================================
user_info = st.session_state.user
user_role = user_info.get("role", "Executive")
user_name = user_info.get("full_name", "ผู้ใช้งาน")
user_dept = user_info.get("department", "ทั่วไป")

ALL_MODULES = [
    {"id": "exec", "title": "📊 ผู้บริหาร (Executive Dashboard)", "roles": ["Executive"]},
    {"id": "acc", "title": "💰 บัญชีและการเงิน (Accounting & Finance)", "roles": ["Executive", "Accounting"]},
    {"id": "tax_inv", "title": "🧾 ออกใบกำกับภาษี/ใบเสร็จ (Tax Invoices)", "roles": ["Executive", "Accounting", "POS"]},
    {"id": "pos", "title": "🛒 ระบบหน้าร้าน (POS System)", "roles": ["Executive", "POS"]},
    {"id": "inv", "title": "📦 บริหารคลังสินค้า (Inventory Management)", "roles": ["Executive", "Accounting", "POS"]},
    {"id": "hr", "title": "👥 ทรัพยากรบุคคลและเงินเดือน (HR & Payroll)", "roles": ["Executive", "HR"]},
    {"id": "fin_ana", "title": "📈 วิเคราะห์งบการเงิน (Financial Analytics)", "roles": ["Executive", "Accounting"]},
    {"id": "tax_alert", "title": "🔔 ระบบแจ้งเตือนภาษี (Tax Alerts & LINE)", "roles": ["Executive", "Accounting"]},
    {"id": "logistics", "title": "🚚 ระบบขนส่งและโลจิสติกส์ (Logistics)", "roles": ["Executive", "POS"]},
    {"id": "mfg", "title": "🏭 ระบบการผลิต (Manufacturing ERP)", "roles": ["Executive", "Accounting"]},
    {"id": "crm", "title": "🤝 บริหารความสัมพันธ์ลูกค้า (CRM)", "roles": ["Executive", "POS"]},
    {"id": "procurement", "title": "📑 จัดซื้อและบริหารสัญญา (Procurement)", "roles": ["Executive", "Accounting"]},
    {"id": "audit", "title": "🛡️ การจัดการความเสี่ยงและตรวจสอบ (Audit)", "roles": ["Executive", "Accounting"]},
    {"id": "arap", "title": "🏦 บริหารลูกหนี้/เจ้าหนี้ (AR/AP System)", "roles": ["Executive", "Accounting"]},
    {"id": "asset", "title": "🏢 บริหารสินทรัพย์คงทน (Asset Management)", "roles": ["Executive", "Accounting"]},
    {"id": "edoc", "title": "📂 เอกสารอิเล็กทรอนิกส์ (e-Document Archive)", "roles": ["Executive", "Accounting", "HR"]},
    {"id": "vat", "title": "📊 รายงานภาษีมูลค่าเพิ่ม (VAT Report)", "roles": ["Executive", "Accounting"]},
    {"id": "wht", "title": "📑 รายงานภาษีหัก ณ ที่จ่าย (WHT Report)", "roles": ["Executive", "Accounting"]},
    {"id": "branch", "title": "🌐 บริหารหลายสาขา (Multi-Branch)", "roles": ["Executive"]},
    {"id": "setting", "title": "⚙️ ตั้งค่าระบบและประกาศ (System Settings)", "roles": ["Executive"]}
]

# Dynamic Sequential Renumbering per Role
allowed_list = [m for m in ALL_MODULES if user_role == "Executive" or user_role in m["roles"]]
if not allowed_list:
    allowed_list = ALL_MODULES

menu_options = [f"{i+1}. {m['title']}" for i, m in enumerate(allowed_list)]
menu_map = {f"{i+1}. {m['title']}": m for i, m in enumerate(allowed_list)}

with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 10px 0 16px 0;">
        <h2 style="margin:0; font-size: 22px; color: #2563EB; font-weight: 800;">⚡ TaxMate Light</h2>
        <span style="background: #DCFCE7; color: #15803D; padding: 3px 10px; border-radius: 999px; font-size: 11px; font-weight: 700;">v3.0 Enterprise Live</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"👤 **{user_name}**")
    role_display_name = "Admin / ผู้บริหารสูงสุด" if user_role == "Executive" else user_role
    st.caption(f"ตำแหน่ง: **{role_display_name}** | แผนก: **{user_dept}**")
    st.divider()
    
    selected_label = st.radio(f"📌 เมนูการทำงาน ({len(allowed_list)} โมดูล):", menu_options)
    selected_module = menu_map[selected_label]
    selected_id = selected_module["id"]
    
    st.divider()
    if st.button("🚪 ออกจากระบบ (Logout)", use_container_width=True):
        log_audit_action(user_name, "ออกจากระบบ (Logout)")
        st.session_state.authenticated = False
        st.session_state.user = None
        st.rerun()

# Header Banner
st.markdown(f"""
<div style="background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%); padding: 22px 30px; border-radius: 18px; color: #FFFFFF; margin-bottom: 20px;">
    <h2 style="margin: 0; font-size: 26px; font-weight: 800;">{selected_label}</h2>
    <div style="font-size: 13.5px; opacity: 0.9; margin-top: 4px;">TaxMate Enterprise ERP v3.0 • ระบบบริหารจัดการองค์กร บัญชี และภาษีแบบนิเวศน์ดิจิทัล</div>
</div>
""", unsafe_allow_html=True)


# MODULE 1: EXECUTIVE DASHBOARD
if selected_id == "exec":
    try:
        conn = get_db_connection()
        df_sales = pd.read_sql_query("SELECT * FROM sales", conn)
        df_products = pd.read_sql_query("SELECT * FROM products", conn)
        conn.close()

        total_revenue = df_sales["total"].sum() if not df_sales.empty else 0.0
        total_vat = df_sales["tax"].sum() if not df_sales.empty else 0.0
        net_sales = df_sales["amount"].sum() if not df_sales.empty else 0.0
        total_products = df_products["stock"].sum() if not df_products.empty else 0

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("ยอดขายรวมสุทธิ", f"฿{total_revenue:,.2f}", "+21.5%")
        c2.metric("รายได้ก่อนภาษี", f"฿{net_sales:,.2f}", "+18.2%")
        c3.metric("ภาษีขายรอส่ง (VAT)", f"฿{total_vat:,.2f}", "ภ.พ.30")
        c4.metric("สินค้าคงคลังรวม", f"{total_products:,} ชิ้น", "3 สาขา")

        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2 = st.columns([2.2, 1])
        with col1:
            st.subheader("📈 วิเคราะห์แนวโน้มรายได้ (Revenue Trend)")
            months = ["ม.ค.", "ก.พ.", "มี.ค.", "เม.ย.", "พ.ค.", "มิ.ย.", "ก.ค.", "ส.ค.", "ก.ย.", "ต.ค."]
            rev_data = [150000, 210000, 180000, 260000, 340000, 370000, 320000, 390000, 450000, net_sales if net_sales > 0 else 520000]
            fig_line = px.area(x=months, y=rev_data, labels={'x': 'เดือน', 'y': 'ยอดขาย (บาท)'}, color_discrete_sequence=['#2563EB'])
            st.plotly_chart(fig_line, use_container_width=True)

        with col2:
            st.subheader("🍰 สัดส่วนเอกสารการค้า")
            if not df_sales.empty:
                fig_pie = px.pie(df_sales, names="status", values="total", hole=0.5, color_discrete_sequence=['#16A34A', '#D97706'])
                st.plotly_chart(fig_pie, use_container_width=True)
                
        st.divider()
        render_landing_announcements()

    except Exception as e:
        st.error(f"ข้อผิดพลาดในโมดูลผู้บริหาร: {str(e)}")


# MODULE 2: ACCOUNTING & FINANCE (WITH DELETE SYSTEM)
elif selected_id == "acc":
    tab1, tab2 = st.tabs(["📒 สมุดรายวันทั่วไป", "➕ บันทึกรายการ บัญชีเดบิต/เครดิต"])
    
    with tab1:
        st.subheader("📒 สมุดรายวันทั่วไป (General Journal Ledger)")
        try:
            conn = get_db_connection()
            df_journal = pd.read_sql_query("SELECT id as 'ID', entry_date as 'วันที่', account_code as 'รหัสบัญชี', account_name as 'ชื่อบัญชี', debit as 'เดบิต (บาท)', credit as 'เครดิต (บาท)', description as 'คำอธิบาย' FROM journal_entries ORDER BY id DESC", conn)
            conn.close()
            st.dataframe(df_journal, use_container_width=True)
            
            if not df_journal.empty:
                with st.expander("🗑️ ลบรายการบัญชีจากสมุดรายวัน"):
                    del_j_id = st.selectbox("เลือก ID รายการบัญชีที่ต้องการลบ:", df_journal["ID"].tolist(), key="del_j_sel")
                    if st.button("❌ ยืนยันลบรายการบัญชีนี้", type="primary", key="btn_del_j"):
                        conn = get_db_connection()
                        cursor = conn.cursor()
                        cursor.execute("DELETE FROM journal_entries WHERE id = ?", (del_j_id,))
                        conn.commit()
                        conn.close()
                        log_audit_action(user_name, f"ลบรายการลงสมุดรายวัน ID {del_j_id}")
                        st.success(f"ลบรายการบัญชี ID {del_j_id} เรียบร้อยแล้ว!")
                        st.rerun()
                        
        except Exception as e:
            st.error(f"เกิดข้อผิดพลาดในการดึงข้อมูลสมุดรายวัน: {str(e)}")
            
        st.divider()
        st.subheader("💵 การบริหารกระแสเงินสด (Cash Flow Analysis)")
        c1, c2, c3 = st.columns(3)
        c1.metric("กระแสเงินสดรับ (Cash Inflow)", "฿985,000.00", "+22.4%")
        c2.metric("กระแสเงินสดจ่าย (Cash Outflow)", "฿275,000.00", "-1.8%")
        c3.metric("เงินสดคงเหลือสุทธิ (Net Cash)", "฿710,000.00", "+28.5%")

    with tab2:
        st.subheader("📝 บันทึกรายการลงสมุดรายวันทั่วไป")
        with st.form("add_journal_form"):
            c1, c2, c3 = st.columns(3)
            acc_code = c1.text_input("รหัสบัญชี", value="111000")
            acc_name = c2.text_input("ชื่อบัญชี", value="เงินฝากกระแสรายวัน")
            entry_type = c3.selectbox("ประเภทรายการ", ["เดบิต (Debit)", "เครดิต (Credit)"])
            
            c_a1, c_a2 = st.columns(2)
            amount_val = c_a1.number_input("จำนวนเงิน (บาท)", min_value=0.0, value=10000.0, step=1000.0)
            entry_desc = c_a2.text_input("รายละเอียดประกอบรายการ", value="บันทึกรายการบัญชีประจำวัน")
            
            if st.form_submit_button("💾 บันทึกรายการลงสมุดรายวัน", type="primary"):
                try:
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    d_val = amount_val if "เดบิต" in entry_type else 0.0
                    c_val = amount_val if "เครดิต" in entry_type else 0.0
                    curr_dt = datetime.now().strftime("%d/%m/%Y")
                    
                    cursor.execute("""
                    INSERT INTO journal_entries (entry_date, account_code, account_name, debit, credit, description)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """, (curr_dt, acc_code, acc_name, d_val, c_val, entry_desc))
                    conn.commit()
                    conn.close()
                    log_audit_action(user_name, f"บันทึกบัญชี {acc_name} ({entry_type}) ฿{amount_val:,.2f}")
                    st.success(f"บันทึกรายการ {acc_name} จำนวน ฿{amount_val:,.2f} ลงสมุดรายวันเรียบร้อยแล้ว!")
                    st.rerun()
                except Exception as e:
                    st.error(f"เกิดข้อผิดพลาดในการบันทึกบัญชี: {str(e)}")


# MODULE 3: TAX INVOICES (WITH DELETE SYSTEM)
elif selected_id == "tax_inv":
    tab1, tab2 = st.tabs(["📝 สร้างใบกำกับภาษีใหม่", "📋 คลังเอกสาร & พิมพ์ e-Tax Invoice"])
    with tab1:
        with st.form("new_inv_form_v3"):
            c1, c2 = st.columns(2)
            doc_no = c1.text_input("เลขที่เอกสาร", value=f"INV-{datetime.now().strftime('%Y%m%d')}-{np.random.randint(1000,9999)}")
            customer_name = c1.text_input("ชื่อลูกค้า / บริษัท", value="บริษัท สยามนวัตกรรม จำกัด")
            amount = c2.number_input("มูลค่าสินค้าก่อนภาษี (บาท)", min_value=0.0, value=75000.0)
            status = c2.selectbox("สถานะการชำระเงิน", ["ชำระแล้ว", "รอชำระ"])
            tax = amount * 0.07
            total = amount + tax
            st.info(f"ภาษี VAT 7%: **฿{tax:,.2f}** | ยอดรวมทั้งสิ้น: **฿{total:,.2f}**")
            if st.form_submit_button("💾 บันทึกเอกสาร", type="primary"):
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("INSERT OR REPLACE INTO sales (doc_no, customer, amount, tax, total, status) VALUES (?, ?, ?, ?, ?, ?)",
                               (doc_no, customer_name, amount, tax, total, status))
                conn.commit()
                conn.close()
                log_audit_action(user_name, f"ออกใบกำกับภาษี {doc_no}")
                st.success(f"บันทึกใบกำกับภาษี {doc_no} เรียบร้อยแล้ว!")

    with tab2:
        conn = get_db_connection()
        df_docs = pd.read_sql_query("SELECT * FROM sales ORDER BY id DESC", conn)
        conn.close()
        st.dataframe(df_docs, use_container_width=True)
        
        if not df_docs.empty:
            with st.expander("🗑️ ลบเอกสารใบกำกับภาษี"):
                del_doc_no = st.selectbox("เลือกเลขที่เอกสารที่ต้องการลบ:", df_docs["doc_no"].tolist(), key="del_inv_sel")
                if st.button("❌ ยืนยันลบเอกสารนี้", type="primary", key="btn_del_inv"):
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM sales WHERE doc_no = ?", (del_doc_no,))
                    conn.commit()
                    conn.close()
                    log_audit_action(user_name, f"ลบใบกำกับภาษี {del_doc_no}")
                    st.success(f"ลบเอกสาร {del_doc_no} ออกจากระบบเรียบร้อยแล้ว!")
                    st.rerun()


# MODULE 4: POS SYSTEM
elif selected_id == "pos":
    col1, col2 = st.columns([1.8, 1.2])
    conn = get_db_connection()
    df_p = pd.read_sql_query("SELECT * FROM products", conn)
    conn.close()
    
    with col1:
        st.subheader("🛍️ รายการสินค้าหน้าร้าน POS")
        if not df_p.empty:
            cols = st.columns(3)
            for idx, row in df_p.iterrows():
                with cols[idx % 3]:
                    st.markdown(f"""
                    <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 14px; padding: 16px; margin-bottom: 12px; text-align: center;">
                        <div style="font-size: 32px;">💻</div>
                        <strong style="font-size: 14px; color: #0F172A;">{row['name']}</strong><br>
                        <span style="color: #2563EB; font-weight: 800; font-size: 16px;">฿{row['price']:,.2f}</span><br>
                        <small style="color: #64748B;">คงเหลือ: {row['stock']} ชิ้น</small>
                    </div>
                    """, unsafe_allow_html=True)

    with col2:
        st.subheader("💳 ชำระเงิน & ตัดสต็อก Real-time")
        items_list = df_p["name"].tolist() if not df_p.empty else ["ไม่มีสินค้า"]
        sel_item = st.selectbox("เลือกรายการสินค้าสั่งซื้อ", items_list)
        qty = st.number_input("จำนวนที่ต้องการ", min_value=1, value=1)
        pay_type = st.radio("ช่องทางชำระเงิน", ["PromptPay QR", "เงินสด", "บัตรเครดิต EDC"])
        
        if not df_p.empty and sel_item in df_p["name"].values:
            matched_prod = df_p[df_p["name"] == sel_item].iloc[0]
            unit_p = matched_prod["price"]
            curr_stock = matched_prod["stock"]
            prod_id = matched_prod["id"]
            
            subtotal = unit_p * qty
            vat_val = subtotal * 0.07
            grand_total = subtotal + vat_val
            
            st.divider()
            st.write(f"มูลค่าสินค้า: **฿{subtotal:,.2f}**")
            st.write(f"ภาษี VAT 7%: **฿{vat_val:,.2f}**")
            st.markdown(f"### ยอดชำระสุทธิ: <span style='color: #2563EB;'>฿{grand_total:,.2f}</span>", unsafe_allow_html=True)
            
            if st.button("✅ ยืนยันชำระเงิน & ตัดสต็อก", type="primary", use_container_width=True):
                if qty > curr_stock:
                    st.error(f"สินค้าในสต็อกมีไม่พอ (คงเหลือเพียง {curr_stock} ชิ้น)")
                else:
                    try:
                        conn = get_db_connection()
                        cursor = conn.cursor()
                        cursor.execute("UPDATE products SET stock = stock - ? WHERE id = ?", (qty, prod_id))
                        pos_doc_no = f"POS-{datetime.now().strftime('%Y%m%d')}-{np.random.randint(1000,9999)}"
                        cursor.execute("""
                        INSERT INTO sales (doc_no, customer, amount, tax, total, status, branch, payment_method)
                        VALUES (?, 'ลูกค้าหน้าร้าน POS', ?, ?, ?, 'ชำระแล้ว', 'สำนักงานใหญ่', ?)
                        """, (pos_doc_no, subtotal, vat_val, grand_total, pay_type))
                        conn.commit()
                        conn.close()
                        
                        log_audit_action(user_name, f"ขาย POS {sel_item} x{qty} ({pos_doc_no})")
                        st.balloons()
                        st.success(f"ชำระเงินสำเร็จผ่าน {pay_type}! ตัดสต็อกสินค้า {sel_item} จำนวน {qty} ชิ้นเรียบร้อยแล้ว")
                        st.rerun()
                    except Exception as e:
                        st.error(f"เกิดข้อผิดพลาดในการตัดสต็อก: {str(e)}")


# MODULE 5: INVENTORY MANAGEMENT (WITH DELETE SYSTEM)
elif selected_id == "inv":
    conn = get_db_connection()
    df_products = pd.read_sql_query("SELECT * FROM products", conn)
    conn.close()
    
    st.subheader("📊 รายการสินค้าคงคลังปัจจุบัน")
    st.dataframe(df_products, use_container_width=True)
    
    c_add, c_del = st.columns([1.5, 1])
    
    with c_add:
        with st.expander("➕ เพิ่มสินค้าใหม่เข้าสู่คลังสินค้า"):
            with st.form("add_product_form_v3"):
                p_sku = st.text_input("รหัสสินค้า (SKU)", value=f"SKU-00{len(df_products)+1}")
                p_name = st.text_input("ชื่อสินค้า")
                p_price = st.number_input("ราคาต่อหน่วย (บาท)", min_value=0.0, value=3500.0)
                p_stock = st.number_input("จำนวนสต็อกเริ่มต้น", min_value=1, value=50)
                p_cat = st.selectbox("หมวดหมู่สินค้า", ["Software", "Hardware", "License", "Service"])
                p_branch = st.selectbox("สาขาจัดเก็บ", ["สำนักงานใหญ่", "สาขาเชียงใหม่", "สาขาภูเก็ต"])
                
                if st.form_submit_button("บันทึกสินค้าใหม่เข้าสู่คลัง"):
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute("""
                    INSERT INTO products (sku, name, price, stock, category, branch) 
                    VALUES (?, ?, ?, ?, ?, ?)
                    """, (p_sku, p_name, p_price, p_stock, p_cat, p_branch))
                    conn.commit()
                    conn.close()
                    log_audit_action(user_name, f"เพิ่มสินค้าใหม่ {p_name}")
                    st.success(f"เพิ่มสินค้า {p_name} เข้าสู่คลังเรียบร้อยแล้ว!")
                    st.rerun()

    with c_del:
        if not df_products.empty:
            with st.expander("🗑️ ลบสินค้าออกจากคลัง"):
                del_p_sku = st.selectbox("เลือกสินค้าที่ต้องการลบ:", [f"{r['sku']} - {r['name']}" for idx, r in df_products.iterrows()], key="del_prod_sel")
                target_sku = del_p_sku.split(" - ")[0]
                if st.button("❌ ยืนยันลบสินค้านี้", type="primary", key="btn_del_prod"):
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM products WHERE sku = ?", (target_sku,))
                    conn.commit()
                    conn.close()
                    log_audit_action(user_name, f"ลบสินค้าออกจากคลัง SKU: {target_sku}")
                    st.success(f"ลบสินค้า SKU {target_sku} เรียบร้อยแล้ว!")
                    st.rerun()


# MODULE 6: HR & PAYROLL (WITH DELETE SYSTEM)
elif selected_id == "hr":
    conn = get_db_connection()
    df_emp = pd.read_sql_query("SELECT * FROM employees", conn)
    conn.close()
    
    st.subheader("📋 ทะเบียนพนักงานและโครงสร้างเงินเดือน")
    st.dataframe(df_emp, use_container_width=True)
    
    if not df_emp.empty:
        with st.expander("🗑️ ลบข้อมูลพนักงานออกจากระบบ"):
            del_emp_code = st.selectbox("เลือกพนักงานที่ต้องการลบ:", [f"{r['emp_code']} - {r['name']}" for idx, r in df_emp.iterrows()], key="del_emp_sel")
            target_emp_code = del_emp_code.split(" - ")[0]
            if st.button("❌ ยืนยันลบพนักงานรายนี้", type="primary", key="btn_del_emp"):
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM employees WHERE emp_code = ?", (target_emp_code,))
                conn.commit()
                conn.close()
                log_audit_action(user_name, f"ลบข้อมูลพนักงาน รหัส {target_emp_code}")
                st.success(f"ลบข้อมูลพนักงาน {target_emp_code} เรียบร้อยแล้ว!")
                st.rerun()

    st.divider()
    st.subheader("💸 สรุปงบประมาณการจ่ายเงินเดือนและภาษีหัก ณ ที่จ่าย (ภ.ง.ด.1)")
    total_payroll = df_emp["salary"].sum() if not df_emp.empty else 0.0
    wht1_est = total_payroll * 0.03
    
    c1, c2, c3 = st.columns(3)
    c1.metric("ยอดจ่ายเงินเดือนรวมทั้งองค์กร", f"฿{total_payroll:,.2f}")
    c2.metric("จำนวนพนักงานปฏิบัติการ", f"{len(df_emp)} คน")
    c3.metric("ประมาณการ ภ.ง.ด.1 นำส่ง", f"฿{wht1_est:,.2f}")


# MODULE 7: FINANCIAL ANALYTICS
elif selected_id == "fin_ana":
    st.subheader("📊 วิเคราะห์งบกำไรขาดทุน (Income Statement Deep-Dive)")
    conn = get_db_connection()
    df_sales = pd.read_sql_query("SELECT * FROM sales", conn)
    conn.close()
    
    tot_rev = df_sales["amount"].sum() if not df_sales.empty else 985000.0
    cogs = tot_rev * 0.35
    gross_p = tot_rev - cogs
    sga = tot_rev * 0.20
    ebit = gross_p - sga
    
    inc_df = pd.DataFrame([
        {"รายการงบการเงิน": "1. รายได้จากการขายและบริการ", "จำนวนเงิน (บาท)": tot_rev, "สัดส่วน (%)": "100.0%"},
        {"รายการงบการเงิน": "2. ต้นทุนขายและบริการ (COGS)", "จำนวนเงิน (บาท)": -cogs, "สัดส่วน (%)": "35.0%"},
        {"รายการงบการเงิน": "กำไรขั้นต้น (Gross Profit)", "จำนวนเงิน (บาท)": gross_p, "สัดส่วน (%)": "65.0%"},
        {"รายการงบการเงิน": "3. ค่าใช้จ่ายในการขายและบริหาร (SG&A)", "จำนวนเงิน (บาท)": -sga, "สัดส่วน (%)": "20.0%"},
        {"รายการงบการเงิน": "กำไรก่อนหักภาษี (EBIT)", "จำนวนเงิน (บาท)": ebit, "สัดส่วน (%)": "45.0%"}
    ])
    st.table(inc_df)


# MODULE 8: TAX ALERTS & LINE
elif selected_id == "tax_alert":
    st.subheader("📅 ปฏิทินกำหนดส่งภาษีสรรพากร (Tax Compliance Schedule)")
    tax_sched = pd.DataFrame([
        {"รายการภาษี": "ภ.พ.30 (ภาษีมูลค่าเพิ่ม VAT)", "กำหนดส่ง": "วันที่ 15 ของทุกเดือน", "ช่องทาง": "e-Filing สรรพากร", "สถานะ": "🟢 พร้อมยื่น"},
        {"รายการภาษี": "ภ.ง.ด.3 / ภ.ง.ด.53 (หัก ณ ที่จ่าย)", "กำหนดส่ง": "วันที่ 15 ของทุกเดือน", "ช่องทาง": "e-Filing สรรพากร", "สถานะ": "🟡 รอนำส่ง"},
        {"รายการภาษี": "ภ.ง.ด.50 (ภาษีเงินได้นิติบุคคลประจำปี)", "กำหนดส่ง": "ภายใน 150 วันหลังปิดบัญชี", "ช่องทาง": "e-Filing สรรพากร", "สถานะ": "🟢 เรียบร้อย"}
    ])
    st.table(tax_sched)
    
    st.divider()
    st.subheader("💬 ตั้งค่า LINE Notify แจ้งเตือนผู้บริหารอัตโนมัติ")
    line_token = st.text_input("LINE Token Key:", type="password", value="demo_line_token_v3_xyz")
    if st.button("🚀 ทดสอบส่งข้อความแจ้งเตือนยอดภาษีเข้า LINE"):
        st.success("ข้อความทดสอบส่งเข้ากลุ่ม LINE ผู้บริหารเรียบร้อยแล้ว!")


# MODULE 9: LOGISTICS
elif selected_id == "logistics":
    st.subheader("📦 ตารางติดตามสถานะการจัดส่งพัสดุ (Tracking Engine)")
    logi_df = pd.DataFrame([
        {"Tracking ID": "TH202699101", "ชื่อลูกค้า": "บริษัท สยามเทคโนโลยี จำกัด", "สถานะ": "🚚 อยู่ระหว่างการจัดส่ง", "บริษัทขนส่ง": "Flash Express"},
        {"Tracking ID": "TH202699102", "ชื่อลูกค้า": "บจก. กิจการร่วมค้าไทย", "สถานะ": "✅ จัดส่งสำเร็จแล้ว", "บริษัทขนส่ง": "Kerry Express"}
    ])
    st.table(logi_df)


# MODULE 10: MANUFACTURING ERP
elif selected_id == "mfg":
    st.subheader("🛠️ สูตรโครงสร้างการผลิต (Bill of Materials - BOM)")
    bom_df = pd.DataFrame([
        {"รหัสวัตถุดิบ": "MAT-001", "รายการวัตถุดิบ": "หน้าจอสัมผัส POS 15 นิ้ว", "จำนวนใช้": 1, "หน่วย": "ชุด"},
        {"รหัสวัตถุดิบ": "MAT-002", "รายการวัตถุดิบ": "สายเคเบิลเชื่อมต่อ High Speed", "จำนวนใช้": 2, "หน่วย": "เส้น"}
    ])
    st.table(bom_df)


# MODULE 11: CRM
elif selected_id == "crm":
    st.subheader("🎯 ไปป์ไลน์โอกาสทางการขาย (Sales Pipeline)")
    crm_df = pd.DataFrame([
        {"ชื่อลูกค้า/บริษัท": "บริษัท ไทยนวัตกรรม จำกัด", "ผู้ติดต่อหลัก": "คุณสมศักดิ์", "มูลค่าดีล": "฿350,000.00", "สถานะขั้นตอน": "เสนอราคาแล้ว"},
        {"ชื่อลูกค้า/บริษัท": "โรงแรม แกรนด์ พลาซ่า", "ผู้ติดต่อหลัก": "คุณกานดา", "มูลค่าดีล": "฿750,000.00", "สถานะขั้นตอน": "เจรจาสัญญา"}
    ])
    st.table(crm_df)


# MODULE 12: PROCUREMENT
elif selected_id == "procurement":
    st.subheader("🛒 ใบสั่งซื้อสินค้า (Purchase Orders - PO)")
    po_df = pd.DataFrame([
        {"เลขที่ PO": "PO-202610-001", "ชื่อซัพพลายเออร์": "บริษัท ไอที ดิสทริบิวชั่น จำกัด", "ยอดเงินรวม": "฿180,000.00", "ผู้อนุมัติ": "ผู้บริหาร"}
    ])
    st.table(po_df)


# MODULE 13: AUDIT TRAIL
elif selected_id == "audit":
    conn = get_db_connection()
    df_logs = pd.read_sql_query("SELECT * FROM audit_logs ORDER BY id DESC LIMIT 50", conn)
    conn.close()
    st.subheader("📜 ประวัติการใช้งานและบันทึกความปลอดภัย (System Audit Log)")
    st.dataframe(df_logs, use_container_width=True)


# MODULE 14: AR/AP SYSTEM
elif selected_id == "arap":
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("📥 ลูกหนี้การค้าค้างชำระ (Accounts Receivable)")
        st.metric("ยอดลูกหนี้รอนำส่งชำระ", "฿192,600.00")
    with c2:
        st.subheader("📤 เจ้าหนี้การค้าต้องชำระ (Accounts Payable)")
        st.metric("ยอดเจ้าหนี้ถึงกำหนดชำระ", "฿65,000.00")


# MODULE 15: ASSET MANAGEMENT
elif selected_id == "asset":
    st.subheader("💻 ทะเบียนสินทรัพย์คงทนและการคำนวณค่าเสื่อมราคา")
    asset_df = pd.DataFrame([
        {"รหัสสินทรัพย์": "AST-001", "รายการสินทรัพย์": "เครื่องเซิร์ฟเวอร์สำนักงานใหญ่", "ราคาซื้อ": "฿150,000.00", "ค่าเสื่อมสะสม": "฿30,000.00"}
    ])
    st.table(asset_df)


# MODULE 16: E-DOCUMENT ARCHIVE
elif selected_id == "edoc":
    st.subheader("📤 ระบบจัดเก็บเอกสารสำคัญอิเล็กทรอนิกส์")
    up_f = st.file_uploader("เลือกไฟล์สแกนใบเสร็จ/สัญญาเพื่อแนบเข้าคลังระบบ", type=["pdf", "png", "jpg"])
    if up_f:
        st.success(f"จัดเก็บเอกสาร {up_f.name} เข้าสู่ระบบฐานข้อมูลเรียบร้อยแล้ว!")


# MODULE 17: VAT REPORT
elif selected_id == "vat":
    conn = get_db_connection()
    df_sales = pd.read_sql_query("SELECT * FROM sales", conn)
    conn.close()
    vat_sale = df_sales["tax"].sum() if not df_sales.empty else 0.0
    vat_buy = vat_sale * 0.35
    net_vat = vat_sale - vat_buy
    
    st.subheader("📊 รายงานสรุปภาษีมูลค่าเพิ่ม ภ.พ.30 ประจำเดือน")
    c1, c2, c3 = st.columns(3)
    c1.metric("1. ภาษีขาย (Output VAT)", f"฿{vat_sale:,.2f}")
    c2.metric("2. ภาษีซื้อ (Input VAT)", f"฿{vat_buy:,.2f}")
    c3.metric("3. ภาษีที่ต้องนำส่งสุทธิ", f"฿{net_vat:,.2f}")


# MODULE 18: WHT REPORT
elif selected_id == "wht":
    st.subheader("📑 สรุปภาษีหัก ณ ที่จ่าย (ภ.ง.ด.3 / ภ.ง.ด.53)")
    wht_df = pd.DataFrame([
        {"ประเภทเงินได้": "ค่าบริการวิชาชีพ (3%)", "ฐานภาษี": "฿150,000.00", "ภาษีหักไว้": "฿4,500.00"},
        {"ประเภทเงินได้": "ค่าเช่าอาคาร (5%)", "ฐานภาษี": "฿50,000.00", "ภาษีหักไว้": "฿2,500.00"}
    ])
    st.table(wht_df)


# MODULE 19: MULTI-BRANCH
elif selected_id == "branch":
    conn = get_db_connection()
    df_branch = pd.read_sql_query("SELECT branch, SUM(total) as total_sales FROM sales GROUP BY branch", conn)
    conn.close()
    st.subheader("🏢 รายได้เปรียบเทียบแยกตามสาขา")
    st.dataframe(df_branch, use_container_width=True)


# MODULE 20: SYSTEM SETTINGS, ANNOUNCEMENTS & AUDIT LOGS
elif selected_id == "setting":
    tab_users, tab_announcements, tab_audit_history = st.tabs([
        "👤 จัดการผู้ใช้งานระบบ", 
        "📢 ศูนย์จัดการประกาศสำคัญองค์กร", 
        "📜 ประวัติการใช้งานระบบทั้งหมด (Audit Logs)"
    ])
    
    # TAB 1: USER MANAGEMENT
    with tab_users:
        st.subheader("⚙️ รายชื่อผู้ใช้งานในระบบ (User Management)")
        try:
            conn = get_db_connection()
            df_users = pd.read_sql_query("SELECT id, username, full_name, role, department, email, status FROM users", conn)
            conn.close()
            st.dataframe(df_users, use_container_width=True)
            
            if not df_users.empty:
                with st.expander("🗑️ ลบบัญชีผู้ใช้งานระบบ"):
                    user_options = [f"{r['id']} - {r['username']} ({r['full_name']})" for idx, r in df_users.iterrows()]
                    sel_user_str = st.selectbox("เลือกบัญชีผู้ใช้ที่ต้องการลบ:", user_options, key="del_u_sel")
                    target_u_id = int(sel_user_str.split(" - ")[0])
                    target_u_name = sel_user_str.split(" - ")[1].split(" ")[0]
                    
                    if st.button("❌ ยืนยันลบบัญชีผู้ใช้งานนี้", type="primary", key="btn_del_user"):
                        if target_u_name == user_info.get("username"):
                            st.error("⚠️ ไม่สามารถลบบัญชีผู้ใช้งานที่คุณกำลังล็อกอินอยู่ได้!")
                        else:
                            conn = get_db_connection()
                            cursor = conn.cursor()
                            cursor.execute("DELETE FROM users WHERE id = ?", (target_u_id,))
                            conn.commit()
                            conn.close()
                            log_audit_action(user_name, f"ลบบัญชีผู้ใช้งาน {target_u_name} (ID: {target_u_id})")
                            st.success(f"ลบบัญชีผู้ใช้งาน {target_u_name} เรียบร้อยแล้ว!")
                            st.rerun()

            st.divider()
            if st.button("🔄 รีเซ็ตและซ่อมแซมโครงสร้างฐานข้อมูลอัตโนมัติ (Force Auto-Repair Engine)"):
                init_db_v3()
                st.success("ซ่อมแซมและตรวจสอบโครงสร้างฐานข้อมูล SQLite v3.0 สำเร็จ 100%!")
        except Exception as e:
            st.error(f"เกิดข้อผิดพลาดในการตั้งค่าระบบ: {str(e)}")

    # TAB 2: ANNOUNCEMENTS MANAGEMENT
    with tab_announcements:
        st.subheader("📢 สร้างและจัดการประกาศองค์กร (Announcement Management Center)")
        
        with st.expander("➕ สร้างประกาศสำคัญใหม่ (Publish New Announcement)", expanded=True):
            with st.form("new_announcement_form"):
                anc_title = st.text_input("หัวข้อประกาศ", value="แจ้งปิดปรับปรุงระบบเซิร์ฟเวอร์ประจำเดือน")
                anc_content = st.text_area("รายละเอียดประกาศ (ข้อความนี้จะแสดงบนหน้าปกเว็บและหน้า Admin ทันที)", value="ขอแจ้งให้พนักงานและผู้ใช้งานทุกท่านทราบ ระบบจะทำการสำรองข้อมูลและอัปเดตแพตช์ความปลอดภัยในวันเสาร์นี้ เวลา 22:00 - 23:00 น.")
                
                c1, c2, c3 = st.columns(3)
                with c1:
                    anc_priority = st.selectbox("ระดับความสำคัญ", ["Normal (ปกติ)", "High (สำคัญ)", "Urgent (ด่วนที่สุด)"])
                with c2:
                    anc_target = st.selectbox("กลุ่มผู้รับประกาศ", ["All (แสดงหน้าปกเว็บ & ทุกแผนก)", "Executive (ผู้บริหาร/Admin)", "Accounting (บัญชี)", "POS (หน้าร้าน)", "HR (บุคคล)"])
                with c3:
                    anc_status = st.selectbox("สถานะประกาศ", ["Active (เปิดแสดงผล)", "Inactive (ซ่อนประกาศ)"])
                
                if st.form_submit_button("🚀 บันทึกและส่งประกาศทันที", type="primary"):
                    p_code = anc_priority.split(" ")[0]
                    t_code = "All" if "All" in anc_target else anc_target.split(" ")[0]
                    s_code = anc_status.split(" ")[0]
                    
                    try:
                        conn = get_db_connection()
                        cursor = conn.cursor()
                        cursor.execute("""
                        INSERT INTO announcements (title, content, priority, target_role, status, created_by)
                        VALUES (?, ?, ?, ?, ?, ?)
                        """, (anc_title, anc_content, p_code, t_code, s_code, user_name))
                        conn.commit()
                        conn.close()
                        log_audit_action(user_name, f"สร้างประกาศใหม่: {anc_title}")
                        st.success("บันทึกประกาศเรียบร้อย! ประกาศจะถูกนำไปแสดงทันที")
                        st.rerun()
                    except Exception as e:
                        st.error(f"เกิดข้อผิดพลาดในการสร้างประกาศ: {str(e)}")

        st.divider()
        render_landing_announcements()

        st.divider()
        st.subheader("📋 ตารางรายการประกาศทั้งหมดในระบบ")
        try:
            conn = get_db_connection()
            df_all_anc = pd.read_sql_query("SELECT * FROM announcements ORDER BY id DESC", conn)
            conn.close()
            st.dataframe(df_all_anc, use_container_width=True)
            
            if not df_all_anc.empty:
                with st.expander("🗑️ ลบประกาศออกจากระบบ"):
                    sel_anc_id = st.selectbox("เลือก ID ประกาศที่ต้องการลบ:", df_all_anc["id"].tolist(), key="del_anc_sel")
                    if st.button("❌ ยืนยันลบประกาศที่เลือก", type="primary", key="btn_del_anc"):
                        conn = get_db_connection()
                        cursor = conn.cursor()
                        cursor.execute("DELETE FROM announcements WHERE id = ?", (sel_anc_id,))
                        conn.commit()
                        conn.close()
                        log_audit_action(user_name, f"ลบประกาศ ID {sel_anc_id}")
                        st.success(f"ลบประกาศ ID {sel_anc_id} เรียบร้อยแล้ว!")
                        st.rerun()
        except Exception as e:
            st.error(f"เกิดข้อผิดพลาดในการโหลดตารางประกาศ: {str(e)}")

    # TAB 3: FULL SYSTEM AUDIT LOGS HISTORY
    with tab_audit_history:
        st.subheader("📜 ประวัติการใช้งานและกิจกรรมในระบบทั้งหมด (Full System Audit Logs)")
        try:
            conn = get_db_connection()
            df_all_logs = pd.read_sql_query("""
                SELECT 
                    id as 'ID',
                    timestamp as 'วัน-เวลา',
                    user_name as 'ผู้ใช้งาน',
                    action as 'กิจกรรม/การทำรายการ',
                    ip_address as 'IP Address'
                FROM audit_logs 
                ORDER BY id DESC
            """, conn)
            conn.close()
            
            c_s1, c_s2 = st.columns([2, 1])
            search_query = c_s1.text_input("🔍 ค้นหาประวัติการใช้งาน (พิมพ์ชื่อผู้ใช้ หรือการกระทำ):")
            
            if search_query:
                filtered_df = df_all_logs[
                    df_all_logs['ผู้ใช้งาน'].astype(str).str.contains(search_query, case=False) |
                    df_all_logs['กิจกรรม/การทำรายการ'].astype(str).str.contains(search_query, case=False)
                ]
                st.caption(f"พบข้อมูลทั้งหมด {len(filtered_df)} รายการ")
                st.dataframe(filtered_df, use_container_width=True)
            else:
                st.caption(f"บันทึกกิจกรรมทั้งหมดในระบบ {len(df_all_logs)} รายการ")
                st.dataframe(df_all_logs, use_container_width=True)
            
            if not df_all_logs.empty:
                with st.expander("🗑️ ล้างประวัติความปลอดภัย (Clear Audit Logs)"):
                    st.warning("⚠️ การล้างประวัติจะลบบันทึกกิจกรรมย้อนหลังทั้งหมดออกจากระบบ")
                    if st.button("❌ ยืนยันล้างประวัติทั้งหมด", type="primary", key="btn_clear_logs"):
                        conn = get_db_connection()
                        cursor = conn.cursor()
                        cursor.execute("DELETE FROM audit_logs")
                        conn.commit()
                        conn.close()
                        log_audit_action(user_name, "ล้างประวัติความปลอดภัยทั้งหมด (Clear All Audit Logs)")
                        st.success("ล้างประวัติการใช้งานระบบเรียบร้อยแล้ว!")
                        st.rerun()
                
        except Exception as e:
            st.error(f"เกิดข้อผิดพลาดในการดึงประวัติการใช้งาน: {str(e)}")
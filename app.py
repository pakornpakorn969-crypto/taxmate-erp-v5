import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import sqlite3
import hashlib
import json
import io
import urllib.parse
import requests
from datetime import datetime, timedelta

# ==========================================
# 1. LIGHT MODE & 3D VISUAL ENTERPRISE THEME
# ==========================================
st.set_page_config(
    page_title="TaxMate Enterprise ERP Suite v5.0 Next-Gen",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Bright & Crisp 3D Glassmorphism Style
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;500;600;700;800&family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Sarabun', 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        -webkit-tap-highlight-color: transparent;
    }
    
    .stApp {
        background-color: #F8FAFC;
        color: #0F172A;
    }

    /* 3D Light Hero Banner Cover */
    .hero-container-3d-light {
        background: linear-gradient(135deg, #FFFFFF 0%, #EFF6FF 50%, #DBEAFE 100%);
        border: 1px solid #CBD5E1;
        border-radius: 28px;
        padding: 44px 32px;
        text-align: center;
        margin-bottom: 28px;
        color: #0F172A;
        box-shadow: 0 20px 40px -15px rgba(37, 99, 235, 0.12), 0 10px 20px -10px rgba(0, 0, 0, 0.04);
        position: relative;
        overflow: hidden;
    }
    .hero-badge-pill-3d {
        display: inline-block;
        background: #FFFFFF;
        color: #2563EB;
        font-size: 13px;
        font-weight: 800;
        padding: 8px 24px;
        border-radius: 9999px;
        letter-spacing: 1.5px;
        margin-bottom: 16px;
        box-shadow: 0 4px 14px rgba(37, 99, 235, 0.15);
        border: 1px solid #BFDBFE;
    }
    .hero-title-main-light {
        font-size: 38px;
        font-weight: 800;
        color: #1E3A8A;
        margin: 0 0 12px 0;
        letter-spacing: -0.5px;
        line-height: 1.25;
    }
    .hero-subtitle-light {
        font-size: 18px;
        font-weight: 700;
        color: #2563EB;
        margin-bottom: 16px;
    }
    .hero-desc-text-light {
        font-size: 15.5px;
        color: #475569;
        max-width: 900px;
        margin: 0 auto 24px auto;
        line-height: 1.7;
    }

    /* 3D Visual Cards Grid */
    .feature-grid-3d {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
        gap: 20px;
        margin-top: 20px;
    }
    .feature-card-3d {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        padding: 22px;
        border-radius: 22px;
        text-align: left;
        color: #0F172A;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05), 0 8px 10px -6px rgba(0, 0, 0, 0.01);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .feature-card-3d:hover {
        transform: translateY(-6px);
        box-shadow: 0 20px 30px -10px rgba(37, 99, 235, 0.15);
        border-color: #93C5FD;
    }
    .feature-card-link,
    .feature-card-link:visited {
        display: block;
        color: inherit;
        text-decoration: none;
    }
    .feature-card-link:focus-visible {
        outline: 3px solid #2563EB;
        outline-offset: 4px;
        border-radius: 22px;
    }
    .feature-card-3d b {
        color: #1D4ED8;
        display: block;
        margin-bottom: 6px;
        font-size: 16.5px;
    }

    /* Metric Cards Light 3D */
    [data-testid="stMetricValue"] {
        font-size: 26px !important;
        font-weight: 800 !important;
        color: #1E3A8A !important;
    }

    /* Sidebar Customization */
    section[data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 1px solid #E2E8F0 !important;
    }

    /* Printable Tax Receipt Paper View */
    .receipt-paper {
        background-color: #FFFFFF;
        border: 1px dashed #94A3B8;
        padding: 24px;
        border-radius: 16px;
        font-family: 'Courier New', Courier, monospace;
        color: #0F172A;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03);
    }
    
    /* Touch-Friendly Primary & Form Buttons */
    .stButton>button, .stFormSubmitButton>button {
        border-radius: 14px !important;
        font-weight: 700 !important;
        min-height: 48px !important;
        font-size: 15px !important;
    }
    .stButton>button[kind="primary"], .stFormSubmitButton>button[kind="primary"] {
        background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%) !important;
        border: none !important;
        color: #FFFFFF !important;
        width: 100%;
        box-shadow: 0 6px 18px rgba(37, 99, 235, 0.25);
    }

    .stDataFrame {
        border-radius: 14px;
        overflow-x: auto !important;
        border: 1px solid #E2E8F0;
        background-color: #FFFFFF;
        -webkit-overflow-scrolling: touch;
    }

    @media (max-width: 768px) {
        .hero-container-3d-light { 
            padding: 28px 18px !important; 
            border-radius: 20px !important;
        }
        .hero-title-main-light { font-size: 24px !important; }
        .hero-subtitle-light { font-size: 15px !important; }
        .hero-desc-text-light { font-size: 13.5px !important; }
        .feature-grid-3d { grid-template-columns: 1fr !important; }
        
        [data-testid="column"] {
            width: 100% !important;
            flex: 1 1 100% !important;
            min-width: 100% !important;
            margin-bottom: 10px;
        }

        input[type="text"], input[type="password"], select, div[data-baseweb="select"] {
            font-size: 16px !important;
        }
    }
</style>
""", unsafe_allow_html=True)


# ==========================================
# 2. FAIL-SAFE DATABASE ENGINE & INITIALIZER
# ==========================================
DB_FILE = "taxmate_erp_v5.db"

def get_db_connection():
    conn = sqlite3.connect(DB_FILE, timeout=15)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def send_line_notification(message: str, token: str = None):
    if token and token.strip():
        try:
            url = 'https://notify-api.line.me/api/notify'
            headers = {'content-type': 'application/x-www-form-urlencoded', 'Authorization': 'Bearer ' + token}
            requests.post(url, headers=headers, data={'message': message}, timeout=5)
        except Exception:
            pass

def generate_promptpay_payload(target_id: str, amount: float = None) -> str:
    target = target_id.replace('-', '').strip()
    target_type = "01" if len(target) == 10 else ("02" if len(target) == 13 else "03")
    target_fmt = ("0066" + target[1:]) if target_type == "01" else target

    tag29 = f"0016A000000677010111{target_type}{len(target_fmt):02d}{target_fmt}"
    payload = f"00020101021229{len(tag29):02d}{tag29}5303764"
    if amount and amount > 0:
        amt_str = f"{amount:.2f}"
        payload += f"54{len(amt_str):02d}{amt_str}"
    payload += "5802TH5911TaxMate ERP6304"

    crc = 0xFFFF
    for char in payload.encode('ascii'):
        crc ^= (char << 8)
        for _ in range(8):
            crc = ((crc << 1) ^ 0x1021) & 0xFFFF if crc & 0x8000 else (crc << 1) & 0xFFFF
    return payload + f"{crc:04X}"

def init_db():
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 1. Users
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT NOT NULL,
            role TEXT NOT NULL,
            department TEXT NOT NULL,
            email TEXT,
            status TEXT DEFAULT 'Active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # 2. Sales
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

        # 3. Products
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

        # 4. Employees
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

        # 5. Audit Logs
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_name TEXT NOT NULL,
            action TEXT NOT NULL,
            ip_address TEXT DEFAULT '127.0.0.1',
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # 6. Announcements
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS announcements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            priority TEXT DEFAULT 'Normal',
            created_by TEXT DEFAULT 'ฝ่ายบริหาร',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # 7. Journal Entries
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

        # 8. Approvals
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS approvals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            doc_type TEXT NOT NULL,
            title TEXT NOT NULL,
            amount REAL NOT NULL,
            requested_by TEXT NOT NULL,
            status TEXT DEFAULT 'Pending Approval',
            approved_by TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # Seed Users
        default_users = [
            ("admin", hash_password("admin123"), "ผู้ดูแลระบบสูงสุด (Super Admin)", "Admin", "บริหารและจัดการ (Executive)", "admin@taxmate.co.th", "Active"),
            ("ceo", hash_password("ceo123"), "ผู้บริหารสูงสุด (CEO)", "Executive", "บริหารและจัดการ (Executive)", "ceo@taxmate.co.th", "Active"),
            ("accountant", hash_password("acc123"), "หัวหน้าแผนกบัญชี", "Accounting", "บัญชีและการเงิน (Accounting)", "accounting@taxmate.co.th", "Active"),
            ("pos_staff", hash_password("pos123"), "พนักงานขาย POS", "POS", "หน้าร้าน/การขาย (POS)", "pos@taxmate.co.th", "Active"),
            ("hr_manager", hash_password("hr123"), "ผู้จัดการฝ่ายบุคคล", "HR", "ทรัพยากรบุคคล (HR)", "hr@taxmate.co.th", "Active")
        ]
        for username, pwd, name, role, dept, email, st_val in default_users:
            cursor.execute("""
            INSERT OR IGNORE INTO users (username, password_hash, full_name, role, department, email, status) 
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (username, pwd, name, role, dept, email, st_val))

        # Seed Sales
        cursor.execute("SELECT COUNT(*) FROM sales")
        if cursor.fetchone()[0] == 0:
            demo_sales = [
                ("INV-202610-001", "บริษัท สยามเทคโนโลยี จำกัด", 150000.0, 10500.0, 160500.0, "ชำระแล้ว", "สำนักงานใหญ่", "โอนเงินผ่านธนาคาร"),
                ("INV-202610-002", "บจก. กิจการร่วมค้าไทย", 85000.0, 5950.0, 90950.0, "รอชำระ", "สาขาเชียงใหม่", "เครดิต 30 วัน"),
                ("INV-202610-003", "ห้างหุ้นส่วนจำกัด โกลบอลการค้า", 240000.0, 16800.0, 256800.0, "ชำระแล้ว", "สาขาภูเก็ต", "บัตรเครดิต")
            ]
            for doc, cust, amt, tax, tot, status, branch, pay_m in demo_sales:
                cursor.execute("""
                INSERT OR IGNORE INTO sales (doc_no, customer, amount, tax, total, status, branch, payment_method) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (doc, cust, amt, tax, tot, status, branch, pay_m))

        # Seed Products
        cursor.execute("SELECT COUNT(*) FROM products")
        if cursor.fetchone()[0] == 0:
            demo_products = [
                ("SKU-001", "ระบบซอฟต์แวร์ ERP Enterprise v5.0", 150000.0, 50, "Software", "สำนักงานใหญ่", 5),
                ("SKU-002", "เครื่องสแกนบาร์โค้ด High Speed POS 2D", 4500.0, 120, "Hardware", "สำนักงานใหญ่", 15),
                ("SKU-003", "เครื่องพิมพ์ใบเสร็จความร้อน Thermal 80mm", 3200.0, 85, "Hardware", "สาขาเชียงใหม่", 10)
            ]
            for sku, p_name, price, stock, cat, branch, min_s in demo_products:
                cursor.execute("""
                INSERT OR IGNORE INTO products (sku, name, price, stock, category, branch, min_stock) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (sku, p_name, price, stock, cat, branch, min_s))

        # Seed Employees
        cursor.execute("SELECT COUNT(*) FROM employees")
        if cursor.fetchone()[0] == 0:
            demo_emps = [
                ("EMP-001", "นายสมชาย ใจดี", "Chief Executive Officer (CEO)", 150000.0, "บริหารและจัดการ"),
                ("EMP-002", "นางสาววิภาดา เงินงาม", "Senior Accountant", 45000.0, "บัญชีและการเงิน"),
                ("EMP-003", "นายธนกร ขายดี", "POS Sales Manager", 38000.0, "หน้าร้าน/การขาย"),
                ("EMP-004", "นางสาวกานดา รักดี", "HR Director", 55000.0, "ทรัพยากรบุคคล")
            ]
            for code, e_name, pos, sal, dept in demo_emps:
                cursor.execute("""
                INSERT OR IGNORE INTO employees (emp_code, name, position, salary, department) 
                VALUES (?, ?, ?, ?, ?)
                """, (code, e_name, pos, sal, dept))

        # Seed Journal Entries
        cursor.execute("SELECT COUNT(*) FROM journal_entries")
        if cursor.fetchone()[0] == 0:
            demo_journals = [
                ("2026-10-01", "11100", "เงินสด/เงินฝากธนาคาร", 160500.0, 0.0, "รับชำระเงินตามใบกำกับภาษี INV-202610-001"),
                ("2026-10-01", "41100", "รายได้จากการขายบริการ", 0.0, 150000.0, "รายได้ขายซอฟต์แวร์ ERP"),
                ("2026-10-01", "21300", "ภาษีขายรอส่ง (VAT)", 0.0, 10500.0, "ภาษีขาย 7%")
            ]
            for edate, acode, aname, deb, cred, desc in demo_journals:
                cursor.execute("""
                INSERT INTO journal_entries (entry_date, account_code, account_name, debit, credit, description)
                VALUES (?, ?, ?, ?, ?, ?)
                """, (edate, acode, aname, deb, cred, desc))

        # Seed Approvals
        cursor.execute("SELECT COUNT(*) FROM approvals")
        if cursor.fetchone()[0] == 0:
            demo_apps = [
                ("PO", "จัดซื้อเซิร์ฟเวอร์สำรองข้อมูล Cloud Server", 120000.0, "นายสมชาย ใจดี", "Approved", "ผู้ดูแลระบบสูงสุด (Super Admin)"),
                ("EXPENSE", "เบิกงบจัดอบรมพนักงานประจำปี 2026", 45000.0, "นางสาวกานดา รักดี", "Pending Approval", None)
            ]
            for dtype, title, amt, req_by, st_val, app_by in demo_apps:
                cursor.execute("""
                INSERT INTO approvals (doc_type, title, amount, requested_by, status, approved_by)
                VALUES (?, ?, ?, ?, ?, ?)
                """, (dtype, title, amt, req_by, st_val, app_by))

        conn.commit()
    except Exception as e:
        st.error(f"❌ เกิดข้อผิดพลาดในการตั้งค่าฐานข้อมูล: {str(e)}")
    finally:
        if conn:
            conn.close()

def log_audit_action(user_name, action):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO audit_logs (user_name, action) VALUES (?, ?)", (user_name, action))
        conn.commit()
    except Exception:
        pass
    finally:
        if conn:
            conn.close()

init_db()


# ==========================================
# 3. ANNOUNCEMENTS COMPONENT
# ==========================================
def render_announcements():
    conn = None
    try:
        conn = get_db_connection()
        query = "SELECT * FROM announcements ORDER BY id DESC"
        df_anc = pd.read_sql_query(query, conn)
        
        if not df_anc.empty:
            st.markdown("<h3 style='color: #0F172A; font-weight: 800; margin-top: 24px; margin-bottom: 14px; font-size: 19px;'>📢 ประกาศข่าวสารสำคัญ (Announcements)</h3>", unsafe_allow_html=True)
            for idx, row in df_anc.iterrows():
                p = row.get("priority", "Normal")
                card_style = "background: #FFFFFF; border-left: 5px solid #2563EB;"
                if p == "Urgent":
                    card_style = "background: #FEF2F2; border-left: 5px solid #EF4444;"
                elif p == "High":
                    card_style = "background: #FFFBEB; border-left: 5px solid #F59E0B;"
                
                st.markdown(f"""
                <div style="{card_style} border-radius: 16px; padding: 18px 20px; margin-bottom: 14px; box-shadow: 0 4px 12px rgba(0,0,0,0.03);">
                    <strong style="font-size: 15.5px; color: #0F172A;">📢 {row['title']}</strong>
                    <div style="font-size: 14px; color: #334155; margin-top: 4px; line-height: 1.5;">{row['content']}</div>
                    <div style="font-size: 11.5px; color: #64748B; margin-top: 6px;">โดย {row['created_by']} | {row['created_at']}</div>
                </div>
                """, unsafe_allow_html=True)
    except Exception:
        pass
    finally:
        if conn:
            conn.close()


# ==========================================
# 4. FRONT-END AUTHENTICATION CENTER
# ==========================================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.user = None

COVER_MODULE_IDS = {"exec", "tax_inv", "branch", "inv", "hr", "approval"}


def get_cover_module_request():
    if hasattr(st, "query_params"):
        module_id = st.query_params.get("module")
    else:
        module_values = st.experimental_get_query_params().get("module", [])
        module_id = module_values[0] if module_values else None
    return module_id if module_id in COVER_MODULE_IDS else None


def clear_cover_module_request():
    if hasattr(st, "query_params"):
        if "module" in st.query_params:
            del st.query_params["module"]
    else:
        params = st.experimental_get_query_params()
        if "module" in params:
            params.pop("module")
            st.experimental_set_query_params(**params)


requested_module_id = get_cover_module_request()

if not st.session_state.authenticated:
    with st.sidebar:
        st.markdown("""
        <div style="padding: 10px 0 10px 0;">
            <div style="font-size: 40px; margin-bottom: 2px;">🏛️</div>
            <h2 style="margin: 0; color: #0F172A; font-weight: 800; font-size: 21px;">TaxMate ERP v5.0</h2>
        </div>
        """, unsafe_allow_html=True)
        
        init_nav = st.radio(
            "📍 เมนูระบบ:",
            ["🏠 หน้าแรก (Overview)", "🔑 เข้าสู่ระบบ"],
            index=1 if requested_module_id else 0,
            key=f"radio_init_nav_{requested_module_id or 'default'}",
        )
        st.divider()
        st.caption("🟢 สถานะเซิร์ฟเวอร์: ออนไลน์ 24/7 (Cloud Engine)")

    if init_nav == "🏠 หน้าแรก (Overview)":
        # LIGHT 3D HERO COVER BANNER
        st.markdown("""
        <div class="hero-container-3d-light">
            <span class="hero-badge-pill-3d">🏛️ NEXT-GEN LIGHT 3D ERP v5.0</span>
            <div class="hero-title-main-light">TaxMate Enterprise ERP Suite</div>
            <div class="hero-subtitle-light">High-Speed Financial & Compliance Management Platform</div>
            <div class="hero-desc-text-light">ศูนย์กลางบริหารจัดการบัญชี ภาษีไทย e-Tax สต็อกหลายสาขา การผลิต CRM และทรัพยากรมนุษย์ พร้อมระบบ AI พยากรณ์ทางการเงินและกราฟิก 3D แสดงผล Real-Time</div>
        </div>
        """, unsafe_allow_html=True)

        # FULL-SYSTEM 3D VISUAL ILLUSTRATION CARDS (6 CORE MODULES)
        st.markdown("### 🧊 ฟีเจอร์หลักและสถาปัตยกรรม 3D ERP (เต็มระบบ)")
        
        # Row 1
        col3d_1, col3d_2, col3d_3 = st.columns(3)
        with col3d_1:
            st.markdown("""
            <a class="feature-card-link" href="?module=exec" aria-label="เปิดระบบ AI Financial Forecast" title="เปิดระบบ AI Financial Forecast">
                <div class="feature-card-3d">
                    <div style="text-align: center; margin-bottom: 12px; height: 85px; display: flex; align-items: center; justify-content: center;">
                        <img src="https://img.icons8.com/isometric/120/bar-chart.png" width="80" style="filter: drop-shadow(0 10px 15px rgba(37,99,235,0.2));" alt="AI Forecast">
                    </div>
                    <b>📊 AI Financial Forecast</b>
                    <span style="font-size: 13.5px; color: #475569;">วิเคราะห์แนวโน้มรายได้ คาดการณ์สุขภาพทางการเงิน 6 เดือนข้างหน้าด้วย Plotly Interactive Engine</span>
                </div>
            </a>
            """, unsafe_allow_html=True)
            
        with col3d_2:
            st.markdown("""
            <a class="feature-card-link" href="?module=tax_inv" aria-label="เปิดระบบ e-Tax" title="เปิดระบบ e-Tax">
                <div class="feature-card-3d">
                    <div style="text-align: center; margin-bottom: 12px; height: 85px; display: flex; align-items: center; justify-content: center;">
                        <img src="https://img.icons8.com/isometric/120/qr-code.png" width="80" style="filter: drop-shadow(0 10px 15px rgba(37,99,235,0.2));" alt="e-Tax QR">
                    </div>
                    <b>🧾 e-Tax & Dynamic QR</b>
                    <span style="font-size: 13.5px; color: #475569;">ออกใบกำกับภาษีมาตรฐานกรมสรรพากร และสร้าง Dynamic PromptPay QR Code รับชำระเงินทันที</span>
                </div>
            </a>
            """, unsafe_allow_html=True)
            
        with col3d_3:
            st.markdown("""
            <a class="feature-card-link" href="?module=branch" aria-label="เปิดระบบ Multi-Branch Matrix" title="เปิดระบบ Multi-Branch Matrix">
                <div class="feature-card-3d">
                    <div style="text-align: center; margin-bottom: 12px; height: 85px; display: flex; align-items: center; justify-content: center;">
                        <img src="https://img.icons8.com/isometric/120/organization.png" width="80" style="filter: drop-shadow(0 10px 15px rgba(37,99,235,0.2));" alt="Multi-Branch">
                    </div>
                    <b>🌐 Multi-Branch Matrix</b>
                    <span style="font-size: 13.5px; color: #475569;">เชื่อมโยงข้อมูลหลายสาขา โอนย้ายสต็อกข้ามสาขา และจัดหมวดหมู่พนักงานแบบ Centralized View</span>
                </div>
            </a>
            """, unsafe_allow_html=True)

        # Row 2
        col3d_4, col3d_5, col3d_6 = st.columns(3)
        with col3d_4:
            st.markdown("""
            <a class="feature-card-link" href="?module=inv" aria-label="เปิดระบบ Smart Inventory WMS" title="เปิดระบบ Smart Inventory WMS">
                <div class="feature-card-3d">
                    <div style="text-align: center; margin-bottom: 12px; height: 85px; display: flex; align-items: center; justify-content: center;">
                        <img src="https://img.icons8.com/isometric/120/box.png" width="80" style="filter: drop-shadow(0 10px 15px rgba(37,99,235,0.2));" alt="Inventory WMS">
                    </div>
                    <b>📦 Smart Inventory WMS</b>
                    <span style="font-size: 13.5px; color: #475569;">บริหารคลังสินค้า ตรวจสอบ SKU แจ้งเตือนสินค้าใกล้หมดสต็อก และติดตามการเคลื่อนย้ายสินค้า</span>
                </div>
            </a>
            """, unsafe_allow_html=True)

        with col3d_5:
            st.markdown("""
            <a class="feature-card-link" href="?module=hr" aria-label="เปิดระบบ HR & Payroll" title="เปิดระบบ HR & Payroll">
                <div class="feature-card-3d">
                    <div style="text-align: center; margin-bottom: 12px; height: 85px; display: flex; align-items: center; justify-content: center;">
                        <img src="https://img.icons8.com/isometric/120/user-male-circle.png" width="80" style="filter: drop-shadow(0 10px 15px rgba(37,99,235,0.2));" alt="HR Payroll">
                    </div>
                    <b>👥 HR & Payroll Automation</b>
                    <span style="font-size: 13.5px; color: #475569;">จัดการข้อมูลบุคลากร คำนวณเงินเดือน เงินปันผล และสวัสดิการพนักงานในระบบอัตโนมัติ</span>
                </div>
            </a>
            """, unsafe_allow_html=True)

        with col3d_6:
            st.markdown("""
            <a class="feature-card-link" href="?module=approval" aria-label="เปิดระบบ E-Approval" title="เปิดระบบ E-Approval">
                <div class="feature-card-3d">
                    <div style="text-align: center; margin-bottom: 12px; height: 85px; display: flex; align-items: center; justify-content: center;">
                        <img src="https://img.icons8.com/isometric/120/shield.png" width="80" style="filter: drop-shadow(0 10px 15px rgba(37,99,235,0.2));" alt="Security Approval">
                    </div>
                    <b>🛡️ E-Approval & Audit Trail</b>
                    <span style="font-size: 13.5px; color: #475569;">ระบบขออนุมัติเอกสารสั่งซื้อ (PO) และบันทึก Audit Logs ตรวจสอบกิจกรรมผู้ใช้อย่างเข้มงวด</span>
                </div>
            </a>
            """, unsafe_allow_html=True)

        render_announcements()

    else:
        st.markdown("""
        <div style="margin-bottom: 16px;">
            <h1 style="color: #0F172A; font-size: 26px; font-weight: 800; margin: 0;">🔑 ศูนย์ยืนยันตัวตน (Authentication Center)</h1>
            <p style="color: #64748B; font-size: 14px; margin-top: 4px;">ลงชื่อเข้าใช้งาน สมัครสมาชิกพนักงานใหม่ หรือรีเซ็ตรหัสผ่าน</p>
        </div>
        """, unsafe_allow_html=True)
        
        tab_login, tab_register, tab_forgot = st.tabs([
            "🔑 เข้าสู่ระบบ (Sign In)", 
            "📝 ลงทะเบียนผู้ใช้งานใหม่ (Sign Up)", 
            "🔑 ลืมรหัสผ่าน (Forgot Password)"
        ])
        
        # TAB 1: LOGIN
        with tab_login:
            col1, col2, col3 = st.columns([1, 1.4, 1])
            with col2:
                with st.form("login_form_v5_clean"):
                    st.markdown("<h2 style='color: #0F172A; font-weight: 800; font-size: 20px; text-align: center; margin-bottom: 14px;'>ลงชื่อเข้าใช้งานระบบ</h2>", unsafe_allow_html=True)
                    login_user = st.text_input("ชื่อผู้ใช้งาน (Username)", value="", key="login_u_inp")
                    login_pwd = st.text_input("รหัสผ่าน (Password)", type="password", value="", key="login_p_inp")
                    st.markdown("<br>", unsafe_allow_html=True)
                    submit_login = st.form_submit_button("เข้าสู่ระบบประมวลผล", use_container_width=True, type="primary")
                    
                    if submit_login:
                        conn = None
                        try:
                            conn = get_db_connection()
                            cursor = conn.cursor()
                            cursor.execute("SELECT * FROM users WHERE username = ? AND password_hash = ?", (login_user, hash_password(login_pwd)))
                            user = cursor.fetchone()
                            
                            if user:
                                user_dict = dict(user)
                                st_val = user_dict.get("status", "Active")
                                if st_val == "Inactive":
                                    st.error("❌ บัญชีนี้ถูกระงับการใช้งานชั่วคราว กรุณาติดต่อ Admin")
                                else:
                                    st.session_state.authenticated = True
                                    st.session_state.user = user_dict
                                    if requested_module_id:
                                        st.session_state.cover_target_module = requested_module_id
                                        clear_cover_module_request()
                                    log_audit_action(user_dict.get('full_name'), "เข้าสู่ระบบสำเร็จ")
                                    st.success(f"ยินดีต้อนรับคุณ {user_dict.get('full_name')} เข้าสู่ระบบ")
                                    st.rerun()
                            else:
                                st.error("ชื่อผู้ใช้งานหรือรหัสผ่านไม่ถูกต้อง")
                        finally:
                            if conn:
                                conn.close()

        # TAB 2: REGISTER FORM
        with tab_register:
            st.markdown("<h2 style='color: #0F172A; font-weight: 800; font-size: 22px; margin-bottom: 16px;'>ลงทะเบียนผู้ใช้งานใหม่</h2>", unsafe_allow_html=True)
            
            with st.form("register_form_exact_spec_v5"):
                col_left, col_right = st.columns(2)
                
                with col_left:
                    reg_fullname = st.text_input("ชื่อ-นามสกุล ผู้ใช้งาน:", key="reg_fn")
                    reg_username = st.text_input("ชื่อผู้ใช้งาน (Username):", key="reg_un")
                    reg_email = st.text_input("อีเมลองค์กร:", key="reg_em")
                    
                with col_right:
                    role_options_display = [
                        "Super Admin (ผู้ดูแลระบบสูงสุด)",
                        "👑 Executive (ผู้บริหาร)",
                        "💰 Accounting (ฝ่ายบัญชี)",
                        "🛒 POS Staff (พนักงานขายหน้าร้าน)",
                        "👥 HR Manager (ผู้จัดการฝ่ายบุคคล)"
                    ]
                    reg_role_str = st.selectbox("🔑 สิทธิ์การใช้งานในระบบ (Role):", role_options_display, key="reg_rl")
                    
                    dept_options_display = [
                        "บริหารและจัดการ (Executive)",
                        "บัญชีและการเงิน (Accounting)",
                        "หน้าร้าน/การขาย (POS)",
                        "ทรัพยากรบุคคล (HR)",
                        "ไอทีและระบบ (IT System)",
                        "ทั่วไป (General)"
                    ]
                    reg_dept_str = st.selectbox("แผนก/ฝ่ายงาน:", dept_options_display, key="reg_dp")
                    
                    reg_pwd1 = st.text_input("รหัสผ่าน:", type="password", key="reg_p1")
                    reg_pwd2 = st.text_input("ยืนยันรหัสผ่าน:", type="password", key="reg_p2")
                
                auto_login = st.checkbox("⚡ ล็อกอินเข้าระบบทันทีหลังสร้างบัญชีสำเร็จ", value=True, key="reg_al")
                
                st.markdown("<br>", unsafe_allow_html=True)
                submit_reg = st.form_submit_button("📑 บันทึกสร้างบัญชีผู้ใช้ใหม่", type="primary")
                
                if submit_reg:
                    if not reg_username or not reg_fullname or not reg_email or not reg_pwd1:
                        st.warning("กรุณากรอกข้อมูลสำคัญให้ครบถ้วนทุกช่อง")
                    elif reg_pwd1 != reg_pwd2:
                        st.error("รหัสผ่านและการยืนยันรหัสผ่านไม่ตรงกัน")
                    else:
                        role_mapping = {
                            "Super Admin (ผู้ดูแลระบบสูงสุด)": "Admin",
                            "👑 Executive (ผู้บริหาร)": "Executive",
                            "💰 Accounting (ฝ่ายบัญชี)": "Accounting",
                            "🛒 POS Staff (พนักงานขายหน้าร้าน)": "POS",
                            "👥 HR Manager (ผู้จัดการฝ่ายบุคคล)": "HR"
                        }
                        mapped_role = role_mapping.get(reg_role_str, "Executive")
                        
                        conn = None
                        try:
                            conn = get_db_connection()
                            cursor = conn.cursor()
                            cursor.execute("""
                            INSERT INTO users (username, password_hash, full_name, role, department, email, status) 
                            VALUES (?, ?, ?, ?, ?, ?, 'Active')
                            """, (reg_username, hash_password(reg_pwd1), reg_fullname, mapped_role, reg_dept_str, reg_email))
                            conn.commit()
                            
                            cursor.execute("SELECT * FROM users WHERE username = ?", (reg_username,))
                            new_user_row = cursor.fetchone()
                            
                            log_audit_action(reg_fullname, f"สมัครสมาชิกใหม่: {reg_username} (สิทธิ์: {mapped_role})")
                            
                            if auto_login and new_user_row:
                                st.session_state.authenticated = True
                                st.session_state.user = dict(new_user_row)
                                st.success(f"สร้างบัญชีสำเร็จ! กำลังเข้าสู่ระบบเป็นคุณ {reg_fullname}...")
                                st.rerun()
                            else:
                                st.success("สร้างบัญชีสำเร็จเรียบร้อย! กรุณาสลับไปที่แท็บ 'เข้าสู่ระบบ' เพื่อล็อกอิน")
                        except sqlite3.IntegrityError:
                            st.error("ชื่อผู้ใช้งาน (Username) นี้มีผู้ใช้งานในระบบแล้ว กรุณาเลือกชื่ออื่น")
                        except Exception as e:
                            st.error(f"เกิดข้อผิดพลาดในการลงทะเบียน: {str(e)}")
                        finally:
                            if conn:
                                conn.close()

        # TAB 3: FORGOT PASSWORD
        with tab_forgot:
            col1, col2, col3 = st.columns([1, 1.4, 1])
            with col2:
                with st.form("forgot_form_public_v5"):
                    st.markdown("<h2 style='color: #0F172A; font-weight: 800; font-size: 20px; text-align: center; margin-bottom: 14px;'>รีเซ็ตรหัสผ่าน</h2>", unsafe_allow_html=True)
                    fg_user = st.text_input("ชื่อผู้ใช้งาน (Username)", key="fg_u")
                    fg_email = st.text_input("อีเมลที่ลงทะเบียน", key="fg_e")
                    new_p1 = st.text_input("รหัสผ่านใหม่", type="password", key="fg_p1")
                    new_p2 = st.text_input("ยืนยันรหัสผ่านใหม่", type="password", key="fg_p2")
                    submit_fg = st.form_submit_button("ตั้งรหัสผ่านใหม่", use_container_width=True, type="primary")
                    
                    if submit_fg:
                        if new_p1 != new_p2 or not new_p1:
                            st.error("รหัสผ่านไม่ถูกต้องหรือไม่อนุญาตให้เป็นค่าว่าง")
                        else:
                            conn = None
                            try:
                                conn = get_db_connection()
                                cursor = conn.cursor()
                                cursor.execute("SELECT id FROM users WHERE username = ? AND email = ?", (fg_user, fg_email))
                                row = cursor.fetchone()
                                if row:
                                    cursor.execute("UPDATE users SET password_hash = ? WHERE id = ?", (hash_password(new_p1), row['id']))
                                    conn.commit()
                                    st.success("รีเซ็ตรหัสผ่านเรียบร้อยแล้ว!")
                                else:
                                    st.error("ข้อมูล Username หรือ Email ไม่ตรงในระบบ")
                            finally:
                                if conn:
                                    conn.close()

    st.stop()


# ==========================================
# 5. AUTHENTICATED ROLE-BASED DASHBOARD
# ==========================================
user_info = st.session_state.user
user_role = user_info.get("role", "POS")
user_name = user_info.get("full_name", "ผู้ใช้งาน")
user_dept = user_info.get("department", "ทั่วไป")

ALL_MODULES = [
    {"id": "exec", "title": "📊 ผู้บริหาร (Executive Dashboard & AI Forecast)", "roles": ["Admin", "Executive"]},
    {"id": "approval", "title": "📑 ระบบอนุมัติเอกสาร (E-Approval Workflow)", "roles": ["Admin", "Executive", "Accounting"]},
    {"id": "acc", "title": "💰 บัญชีและการเงิน (General Journal & Ledger)", "roles": ["Admin", "Executive", "Accounting"]},
    {"id": "tax_inv", "title": "🧾 ออกใบกำกับภาษี/ใบเสร็จ (e-Tax Invoice)", "roles": ["Admin", "Executive", "Accounting", "POS"]},
    {"id": "pos", "title": "🛒 ระบบหน้าร้าน (POS & PromptPay QR)", "roles": ["Admin", "POS"]},
    {"id": "inv", "title": "📦 บริหารคลังสินค้า (Stock & Inventory)", "roles": ["Admin", "Accounting", "POS"]},
    {"id": "hr", "title": "👥 ทรัพยากรบุคคลและเงินเดือน (HR & Payroll)", "roles": ["Admin", "HR"]},
    {"id": "fin_ana", "title": "📈 วิเคราะห์งบและสุขภาพการเงิน (Financial Health Ratios)", "roles": ["Admin", "Executive", "Accounting"]},
    {"id": "tax_alert", "title": "🔔 ระบบแจ้งเตือนกำหนดภาษี (Tax Alerts)", "roles": ["Admin", "Accounting"]},
    {"id": "branch", "title": "🌐 บริหารหลายสาขา (Multi-Branch Matrix)", "roles": ["Admin", "Executive"]},
    {"id": "audit", "title": "🛡️ ตรวจสอบกิจกรรมระบบ (Audit Logs)", "roles": ["Admin", "Accounting"]},
    {"id": "setting", "title": "⚙️ ตั้งค่าระบบและจัดการผู้ใช้ (Admin Panel)", "roles": ["Admin"]}
]

allowed_list = [m for m in ALL_MODULES if user_role in ["Admin", "Super Admin"] or user_role in m["roles"]]
if not allowed_list:
    allowed_list = [ALL_MODULES[4]]

cover_target_module = st.session_state.pop("cover_target_module", None)
cover_target = next(
    (module for module in allowed_list if module["id"] == cover_target_module),
    None,
)
if cover_target:
    st.session_state["radio_module_nav"] = cover_target["title"]
elif cover_target_module:
    st.session_state.cover_target_denied = True

if st.session_state.pop("cover_target_denied", False):
    st.warning("บัญชีนี้ไม่มีสิทธิ์ใช้โมดูลที่เลือกจากหน้าปก กรุณาเลือกโมดูลจากเมนูที่ได้รับสิทธิ์")

with st.sidebar:
    st.markdown(f"""
    <div style="background-color: #EFF6FF; border: 1px solid #BFDBFE; border-radius: 14px; padding: 14px; margin-bottom: 16px;">
        <div style="font-size: 11px; color: #1D4ED8; font-weight: 700; text-transform: uppercase;">👤 ผู้ใช้ปัจจุบัน</div>
        <div style="font-size: 16px; font-weight: 800; color: #0F172A;">{user_name}</div>
        <div style="font-size: 12px; color: #475569;">สิทธิ์: <b style="color:#2563EB;">{user_role}</b> | แผนก: {user_dept}</div>
    </div>
    """, unsafe_allow_html=True)
    
    module_titles = [m["title"] for m in allowed_list]
    selected_title = st.radio("📌 เมนูการใช้งานที่ได้รับสิทธิ์:", module_titles, key="radio_module_nav")
    selected_module_id = next(m["id"] for m in allowed_list if m["title"] == selected_title)
    
    st.divider()
    if st.button("🚪 ออกจากระบบ (Logout)", use_container_width=True, key="btn_logout"):
        log_audit_action(user_name, "ออกจากระบบ")
        st.session_state.authenticated = False
        st.session_state.user = None
        st.rerun()

st.markdown(f"## {selected_title}")


# ==========================================
# 6. MODULE CONTENTS IMPLEMENTATION
# ==========================================

# 1. Executive Dashboard
if selected_module_id == "exec":
    conn = get_db_connection()
    df_s = pd.read_sql_query("SELECT * FROM sales", conn)
    conn.close()
    
    c1, c2, c3, c4 = st.columns(4)
    tot_rev = df_s['total'].sum() if not df_s.empty else 0.0
    tot_vat = df_s['tax'].sum() if not df_s.empty else 0.0
    c1.metric("ยอดขายรวม", f"฿{tot_rev:,.2f}", "+14.2%")
    c2.metric("ภาษีขายรอส่ง (VAT)", f"฿{tot_vat:,.2f}", "+7.0%")
    c3.metric("รายการเอกสารขาย", f"{len(df_s)} รายการ")
    c4.metric("สถานะระบบ ERP", "Online", "100%")
    
    st.divider()
    st.subheader("📈 AI Financial Revenue Forecast (พยากรณ์รายได้ 6 เดือน)")
    months = ["พ.ย. 2026", "ธ.ค. 2026", "ม.ค. 2027", "ก.พ. 2027", "มี.ค. 2027", "เม.ย. 2027"]
    forecast_vals = [tot_rev * (1 + i * 0.05) for i in range(1, 7)]
    fig = go.Figure(data=go.Scatter(x=months, y=forecast_vals, mode='lines+markers', line=dict(color='#2563EB', width=4)))
    fig.update_layout(template="plotly_white", height=320, margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)

# 2. E-Approval Workflow Module
elif selected_module_id == "approval":
    st.subheader("📑 รายการขออนุมัติเอกสาร (E-Approval Center)")
    tab_app1, tab_app2 = st.tabs(["📋 รายการรออนุมัติ", "➕ สร้างคำขออนุมัติใหม่"])
    
    with tab_app1:
        conn = get_db_connection()
        df_apps = pd.read_sql_query("SELECT id as 'ID', doc_type as 'ประเภท', title as 'หัวข้อ', amount as 'จำนวนเงิน (฿)', requested_by as 'ผู้ขออนุมัติ', status as 'สถานะ', approved_by as 'ผู้อนุมัติ' FROM approvals ORDER BY id DESC", conn)
        conn.close()
        st.dataframe(df_apps, use_container_width=True)
        
        st.divider()
        st.write("##### ⚡ จัดการการอนุมัติเอกสาร")
        pending_apps = df_apps[df_apps['สถานะ'] == 'Pending Approval']
        if not pending_apps.empty:
            app_dict_opts = {f"ID #{r['ID']} - {r['หัวข้อ']} (฿{r['จำนวนเงิน (฿)']:,.2f})": r['ID'] for _, r in pending_apps.iterrows()}
            selected_app_str = st.selectbox("เลือกเอกสารที่ต้องการอนุมัติ:", list(app_dict_opts.keys()), key="sb_app_list")
            target_app_id = app_dict_opts[selected_app_str]
            
            ca1, ca2 = st.columns(2)
            if ca1.button("✅ อนุมัติเอกสาร (Approve)", type="primary", key="btn_app_yes"):
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("UPDATE approvals SET status = 'Approved', approved_by = ? WHERE id = ?", (user_name, target_app_id))
                conn.commit()
                conn.close()
                log_audit_action(user_name, f"อนุมัติเอกสาร ID #{target_app_id}")
                st.success("อนุมัติเอกสารเรียบร้อยแล้ว!")
                st.rerun()
            if ca2.button("❌ ไม่อนุมัติ (Reject)", type="secondary", key="btn_app_no"):
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("UPDATE approvals SET status = 'Rejected', approved_by = ? WHERE id = ?", (user_name, target_app_id))
                conn.commit()
                conn.close()
                log_audit_action(user_name, f"ปฏิเสธเอกสาร ID #{target_app_id}")
                st.warning("ปฏิเสธเอกสารเรียบร้อยแล้ว!")
                st.rerun()
        else:
            st.info("🎉 ไม่มีรายการเอกสารค้างอนุมัติในขณะนี้")

    with tab_app2:
        with st.form("form_create_approval_v5"):
            st.write("##### ✍️ แบบฟอร์มขออนุมัติสั่งซื้อ / เบิกงบประมาณ")
            new_app_type = st.selectbox("ประเภทเอกสาร:", ["PO (ใบสั่งซื้อ)", "EXPENSE (เบิกค่าใช้จ่าย)", "BUDGET (ขอกรอบงบประมาณ)"], key="f_app_t")
            new_app_title = st.text_input("หัวข้อรายการขออนุมัติ:", key="f_app_tit")
            new_app_amt = st.number_input("จำนวนเงินรวม (฿):", value=10000.0, key="f_app_a")
            
            sub_create_app = st.form_submit_button("ส่งคำขออนุมัติ", type="primary")
            if sub_create_app and new_app_title:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("INSERT INTO approvals (doc_type, title, amount, requested_by) VALUES (?, ?, ?, ?)",
                               (new_app_type, new_app_title, new_app_amt, user_name))
                conn.commit()
                conn.close()
                log_audit_action(user_name, f"ส่งคำขออนุมัติใหม่: {new_app_title} (฿{new_app_amt:,.2f})")
                send_line_notification(f"📑 มีคำขออนุมัติใหม่เข้ามา: {new_app_title} ยอดเงิน ฿{new_app_amt:,.2f} โดย {user_name}")
                st.success("ส่งคำขออนุมัติเรียบร้อยแล้ว!")
                st.rerun()

# 3. Accounting
elif selected_module_id == "acc":
    st.subheader("📖 สมุดรายวันทั่วไป (General Journal)")
    conn = get_db_connection()
    df_j = pd.read_sql_query("SELECT entry_date as 'วันที่', account_code as 'รหัส', account_name as 'บัญชี', debit as 'เดบิต', credit as 'เครดิต', description as 'รายละเอียด' FROM journal_entries", conn)
    conn.close()
    st.dataframe(df_j, use_container_width=True)

# 4. e-Tax Invoice
elif selected_module_id == "tax_inv":
    col1, col2 = st.columns([1, 1.2])
    with col1:
        st.subheader("📝 ออกใบกำกับภาษี")
        inv_c = st.text_input("ชื่อบริษัทลูกค้า", "บริษัท สยามเทคโนโลยี จำกัด", key="ti_c")
        inv_t = st.text_input("เลขผู้เสียภาษี", "0105560012345", key="ti_t")
        inv_a = st.number_input("จำนวนเงินก่อนภาษี (฿)", value=10000.0, key="ti_a")
        inv_v = inv_a * 0.07
        inv_tot = inv_a + inv_v
        st.write(f"**VAT 7%:** ฿{inv_v:,.2f}")
        st.write(f"**ยอดรวมสุทธิ:** ฿{inv_tot:,.2f}")
    with col2:
        st.markdown(f"""
        <div class="receipt-paper">
            <h3 style="text-align:center;margin:0;">ใบกำกับภาษี / ใบเสร็จรับเงิน</h3>
            <p style="text-align:center;font-size:12px;color:#64748B;">TAX INVOICE (e-Tax)</p>
            <hr>
            <b>ผู้ซื้อ:</b> {inv_c}<br>
            <b>เลขผู้เสียภาษี:</b> {inv_t}<br>
            <b>วันที่:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}<hr>
            <b>ยอดก่อน VAT:</b> ฿{inv_a:,.2f}<br>
            <b>ภาษีมูลค่าเพิ่ม 7%:</b> ฿{inv_v:,.2f}
            <h4>ยอดชำระสุทธิ: ฿{inv_tot:,.2f}</h4>
        </div>
        """, unsafe_allow_html=True)

# 5. POS & PromptPay
elif selected_module_id == "pos":
    st.subheader("🛒 ระบบขายหน้าร้าน POS")
    c_p1, c_p2 = st.columns([1.2, 1])
    with c_p1:
        conn = get_db_connection()
        df_p = pd.read_sql_query("SELECT sku, name, price, stock FROM products", conn)
        conn.close()
        st.dataframe(df_p, use_container_width=True)
        pos_amt = st.number_input("ยอดเงินที่ต้องชำระ (฿):", value=4500.0, key="pos_a")
    with c_p2:
        st.markdown("### 💳 Dynamic PromptPay QR")
        pp_num = st.text_input("หมายเลข PromptPay", "0105560012345", key="pos_pp")
        if st.button("กระตุ้นสร้าง QR Code", type="primary", key="btn_pp_gen"):
            payload = generate_promptpay_payload(pp_num, pos_amt)
            qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={urllib.parse.quote(payload)}"
            st.image(qr_url, caption=f"สแกนจ่าย ฿{pos_amt:,.2f}")

# 6. Inventory
elif selected_module_id == "inv":
    st.subheader("📦 ตรวจสอบสต็อกสินค้า")
    conn = get_db_connection()
    df_inv = pd.read_sql_query("SELECT sku as 'SKU', name as 'สินค้า', category as 'หมวด', price as 'ราคา', stock as 'คงเหลือ', branch as 'สาขา' FROM products", conn)
    conn.close()
    st.dataframe(df_inv, use_container_width=True)

# 7. HR
elif selected_module_id == "hr":
    st.subheader("👥 รายชื่อพนักงานและเงินเดือน")
    conn = get_db_connection()
    df_emp = pd.read_sql_query("SELECT emp_code as 'รหัส', name as 'ชื่อ-นามสกุล', position as 'ตำแหน่ง', salary as 'เงินเดือน', department as 'แผนก' FROM employees", conn)
    conn.close()
    st.dataframe(df_emp, use_container_width=True)

# 8. Financial Analysis
elif selected_module_id == "fin_ana":
    st.subheader("📈 วิเคราะห์งบและสุขภาพการเงิน (Financial Ratios)")
    col_f1, col_f2, col_f3 = st.columns(3)
    col_f1.metric("Current Ratio (สภาพคล่อง)", "2.45", "เกณฑ์ดีมาก (>1.5)")
    col_f2.metric("Net Profit Margin", "18.2%", "+2.5% YoY")
    col_f3.metric("Debt-to-Equity (D/E)", "0.42", "ความเสี่ยงต่ำ (<1.0)")
    st.success("✅ สุขภาพทางการเงินอยู่ในระดับแข็งแกร่ง (A+ Grade)")

# 9. Tax Alerts
elif selected_module_id == "tax_alert":
    st.subheader("🔔 ระบบแจ้งเตือนกำหนดภาษี (Tax Alerts Calendar)")
    st.warning("⏰ ภ.พ.30 (ภาษีมูลค่าเพิ่ม) ประจำเดือน: กำหนด ยื่นภายในวันที่ 15 ของเดือนถัดไป")
    st.info("ℹ️ ภ.ง.ด.1 (ภาษีหัก ณ ที่จ่าย เงินเดือน): กำหนดยื่นภายในวันที่ 7 ของเดือนถัดไป")

# 10. Multi-Branch
elif selected_module_id == "branch":
    st.subheader("🌐 ระบบบริหารหลายสาขาและการโอนย้ายสต็อก (Multi-Branch Matrix)")
    tab_b1, tab_b2 = st.tabs(["📊 สรุปภาพรวมรายสาขา", "🔄 โอนย้ายสต็อกข้ามสาขา"])
    with tab_b1:
        conn = get_db_connection()
        df_branch_p = pd.read_sql_query("SELECT sku as 'SKU', name as 'สินค้า', stock as 'สต็อกคงเหลือ', branch as 'สาขา' FROM products", conn)
        conn.close()
        st.dataframe(df_branch_p, use_container_width=True)
    with tab_b2:
        with st.form("form_branch_transfer_v5"):
            conn = get_db_connection()
            products_rows = pd.read_sql_query("SELECT sku, name, branch, stock FROM products", conn)
            conn.close()
            prod_dict_opts = {f"{r['sku']} - {r['name']} ({r['branch']})": r['sku'] for _, r in products_rows.iterrows()}
            if prod_dict_opts:
                selected_prod_str = st.selectbox("เลือกสินค้า:", list(prod_dict_opts.keys()), key="bt_p_sel")
                target_sku = prod_dict_opts[selected_prod_str]
                dest_branch = st.selectbox("สาขาปลายทาง:", ["สำนักงานใหญ่", "สาขาเชียงใหม่", "สาขาภูเก็ต"], key="bt_d_sel")
                submit_tr = st.form_submit_button("🚚 โอนย้ายสต็อก", type="primary")
                if submit_tr:
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute("UPDATE products SET branch = ? WHERE sku = ?", (dest_branch, target_sku))
                    conn.commit()
                    conn.close()
                    st.success("โอนย้ายสต็อกเรียบร้อยแล้ว!")
                    st.rerun()

# 11. Audit Logs
elif selected_module_id == "audit":
    st.subheader("🛡️ บันทึกกิจกรรมในระบบ (Audit Trail)")
    conn = get_db_connection()
    df_a = pd.read_sql_query("SELECT user_name as 'ผู้ใช้งาน', action as 'กิจกรรม', ip_address as 'IP', timestamp as 'เวลา' FROM audit_logs ORDER BY id DESC", conn)
    conn.close()
    st.dataframe(df_a, use_container_width=True)

# 12. ADMIN PANEL & USER MANAGEMENT WITH DELETE USER FEATURE
elif selected_module_id == "setting":
    if user_role not in ["Admin", "Super Admin"]:
        st.error("❌ คุณไม่มีสิทธิ์เข้าถึงศูนย์ควบคุมผู้ดูแลระบบ (Admin Panel Only)")
    else:
        st.subheader("⚙️ ศูนย์ตั้งค่าระบบและจัดการผู้ใช้งาน (Admin Control Panel)")
        
        tab_a1, tab_a2 = st.tabs([
            "👥 จัดการบัญชีผู้ใช้ทั้งหมด (User Management)", 
            "📢 ประกาศข่าวสารองค์กร (Announcements)"
        ])
        
        # SUB-TAB 1: User Management & Deletion
        with tab_a1:
            st.write("#### 📋 รายชื่อผู้ใช้งานทั้งหมด")
            conn = get_db_connection()
            df_users = pd.read_sql_query("SELECT id as 'ID', username as 'Username', full_name as 'ชื่อ-นามสกุล', role as 'สิทธิ์', status as 'สถานะ' FROM users", conn)
            conn.close()
            st.dataframe(df_users, use_container_width=True)
            
            st.divider()
            st.write("#### 🛠️ แก้ไขสิทธิ์ / สถานะ / รหัสผ่าน / ลบบัญชีผู้ใช้งาน")
            
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id, username, full_name, role, status FROM users")
            all_users_rows = cursor.fetchall()
            conn.close()
            
            user_dict_opts = {f"ID #{u['id']} - {u['username']} ({u['full_name']}) [{u['role']}]": u['id'] for u in all_users_rows}
            
            if user_dict_opts:
                selected_user_str = st.selectbox("เลือกบัญชีผู้ใช้ที่ต้องการจัดการ:", list(user_dict_opts.keys()), key="adm_u_sel")
                target_user_id = user_dict_opts[selected_user_str]
                
                with st.form("form_admin_edit_user_v5"):
                    col_e1, col_e2 = st.columns(2)
                    edit_role = col_e1.selectbox("กำหนดสิทธิ์ใหม่ (Role):", ["Admin", "Executive", "Accounting", "POS", "HR"], key="adm_r_sel")
                    edit_status = col_e2.selectbox("สถานะการใช้งาน (Status):", ["Active", "Inactive", "Pending"], key="adm_st_sel")
                    
                    edit_reset_pwd = st.text_input("รีเซ็ตรหัสผ่านใหม่ (เว้นว่างหากไม่ต้องการเปลี่ยน):", type="password", key="adm_p_reset")
                    
                    btn_col1, btn_col2 = st.columns(2)
                    sub_update = btn_col1.form_submit_button("💾 บันทึกการเปลี่ยนแปลง", type="primary")
                    sub_delete = btn_col2.form_submit_button("🗑️ ลบบัญชีผู้ใช้คนนี้ออกจากระบบ", type="secondary")
                    
                    if sub_update:
                        conn = get_db_connection()
                        cursor = conn.cursor()
                        if edit_reset_pwd.strip():
                            cursor.execute("UPDATE users SET role = ?, status = ?, password_hash = ? WHERE id = ?",
                                           (edit_role, edit_status, hash_password(edit_reset_pwd.strip()), target_user_id))
                        else:
                            cursor.execute("UPDATE users SET role = ?, status = ? WHERE id = ?",
                                           (edit_role, edit_status, target_user_id))
                        conn.commit()
                        conn.close()
                        log_audit_action(user_name, f"Admin อัปเดตผู้ใช้ ID #{target_user_id} -> {edit_role}/{edit_status}")
                        st.success("อัปเดตข้อมูลผู้ใช้งานสำเร็จ!")
                        st.rerun()

                    if sub_delete:
                        if target_user_id == 1:
                            st.error("❌ ไม่สามารถลบบัญชี Super Admin หลัก (ID #1) ออกจากระบบได้")
                        else:
                            conn = get_db_connection()
                            cursor = conn.cursor()
                            cursor.execute("DELETE FROM users WHERE id = ?", (target_user_id,))
                            conn.commit()
                            conn.close()
                            log_audit_action(user_name, f"Admin ลบบัญชีผู้ใช้ ID #{target_user_id}")
                            st.success("ลบบัญชีผู้ใช้งานออกจากระบบเรียบร้อยแล้ว!")
                            st.rerun()

        # SUB-TAB 2: Announcements
        with tab_a2:
            st.write("#### 📢 ลงประกาศข่าวสารองค์กร")
            with st.form("form_admin_anc_v5"):
                anc_t = st.text_input("หัวข้อประกาศ:", key="anc_t_inp")
                anc_c = st.text_area("เนื้อหาประกาศ:", key="anc_c_inp")
                anc_p = st.selectbox("ระดับความสำคัญ:", ["Normal", "High", "Urgent"], key="anc_p_sel")
                submit_anc = st.form_submit_button("ลงประกาศ", type="primary")
                if submit_anc and anc_t:
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO announcements (title, content, priority, created_by) VALUES (?, ?, ?, ?)",
                                   (anc_t, anc_c, anc_p, user_name))
                    conn.commit()
                    conn.close()
                    log_audit_action(user_name, f"ลงประกาศ: {anc_t}")
                    st.success("ลงประกาศเรียบร้อยแล้ว!")
                    st.rerun()
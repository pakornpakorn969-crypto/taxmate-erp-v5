import io
import json
import os
import re
from datetime import datetime, timedelta

import numpy as np
import openpyxl
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

import streamlit as st
from auth import authenticate_user, change_password, hash_password, register_user
from database import (
    DB_NAME,
    get_audit_logs,
    get_connection,
    get_cover_settings,
    get_db_bytes,
    log_audit,
    restore_db_from_bytes,
    save_cover_settings,
)

UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)


# ==========================================
# 📄 PDF Generation Engine (Invoices & Payslips)
# ==========================================
def generate_pdf_document(doc_data):
    """สร้างไฟล์ PDF เอกสารการเงินมาตรฐานองค์กร"""
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Header Ribbon
    p.setFillColor(colors.HexColor("#2563EB"))
    p.rect(0, height - 80, width, 80, fill=True, stroke=False)

    p.setFillColor(colors.white)
    p.setFont("Helvetica-Bold", 20)
    p.drawString(40, height - 45, "TAX MATE ENTERPRISE ERP SUITE")

    p.setFont("Helvetica", 10)
    p.drawString(40, height - 65, "Official Financial Statement & Document")

    # Document Type & Details
    p.setFillColor(colors.HexColor("#0F172A"))
    p.setFont("Helvetica-Bold", 16)
    doc_type = str(doc_data.get("doc_type", "INVOICE")).upper()
    p.drawString(40, height - 120, doc_type)

    p.setFont("Helvetica", 10)
    p.drawString(40, height - 140, f"Doc Number: {doc_data.get('doc_number')}")
    p.drawString(40, height - 155, f"Date: {doc_data.get('issue_date')}")

    p.drawRightString(
        width - 40, height - 120, f"Client: {doc_data.get('client_name')}"
    )
    p.drawRightString(
        width - 40,
        height - 140,
        f"Client Tax ID: {doc_data.get('client_tax_id')}",
    )

    # Line Separator
    p.setStrokeColor(colors.HexColor("#CBD5E1"))
    p.setLineWidth(1)
    p.line(40, height - 170, width - 40, height - 170)

    # Items Box
    p.setFont("Helvetica-Bold", 11)
    p.drawString(50, height - 200, "Description / Items Summary")
    p.drawRightString(width - 50, height - 200, "Amount (THB)")

    p.setFont("Helvetica", 10)
    p.drawString(50, height - 225, str(doc_data.get("items_summary"))[:65])
    subtotal = float(doc_data.get("subtotal", 0.0))
    p.drawRightString(width - 50, height - 225, f"{subtotal:,.2f}")

    p.line(40, height - 245, width - 40, height - 245)

    # Calculation Summary
    vat = float(doc_data.get("vat_amount", 0.0))
    grand = float(doc_data.get("grand_total", 0.0))

    p.drawRightString(width - 150, height - 270, "Subtotal:")
    p.drawRightString(width - 50, height - 270, f"฿{subtotal:,.2f}")

    p.drawRightString(width - 150, height - 290, "VAT (7%):")
    p.drawRightString(width - 50, height - 290, f"฿{vat:,.2f}")

    p.setFont("Helvetica-Bold", 12)
    p.setFillColor(colors.HexColor("#1D4ED8"))
    p.drawRightString(width - 150, height - 315, "Grand Total:")
    p.drawRightString(width - 50, height - 315, f"฿{grand:,.2f}")

    # Signatures
    p.setFillColor(colors.HexColor("#64748B"))
    p.setFont("Helvetica", 9)
    p.drawString(60, 100, "___________________________")
    p.drawString(70, 85, "Authorized Signature")

    p.drawString(width - 200, 100, "___________________________")
    p.drawString(width - 180, 85, "Customer Signature")

    p.drawCentredString(
        width / 2, 40, "Generated automatically by TaxMate Enterprise ERP Suite"
    )

    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer.getvalue()


def generate_payslip_pdf(emp_data):
    """สร้างไฟล์ PDF สลิปเงินเดือนพนักงาน"""
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    p.setFillColor(colors.HexColor("#059669"))
    p.rect(0, height - 80, width, 80, fill=True, stroke=False)

    p.setFillColor(colors.white)
    p.setFont("Helvetica-Bold", 20)
    p.drawString(40, height - 45, "TAX MATE ENTERPRISE ERP - PAYSLIP")

    p.setFont("Helvetica", 10)
    p.drawString(40, height - 65, "Confidential Salary Slip")

    p.setFillColor(colors.HexColor("#0F172A"))
    p.setFont("Helvetica-Bold", 14)
    p.drawString(40, height - 120, f"Employee Name: {emp_data.get('name')}")

    p.setFont("Helvetica", 10)
    p.drawString(40, height - 140, f"Employee ID: {emp_data.get('emp_id')}")
    p.drawString(40, height - 155, f"Position: {emp_data.get('position')}")

    p.drawRightString(
        width - 40,
        height - 120,
        f"Pay Period: {datetime.now().strftime('%B %Y')}",
    )
    p.drawRightString(
        width - 40,
        height - 140,
        f"Date Issued: {datetime.now().strftime('%Y-%m-%d')}",
    )

    p.setStrokeColor(colors.HexColor("#CBD5E1"))
    p.setLineWidth(1)
    p.line(40, height - 175, width - 40, height - 175)

    base_sal = float(emp_data.get("base_salary", 0.0))
    sso_deduct = min(base_sal * 0.05, 750.0)
    tax_deduct = base_sal * 0.03
    net_pay = base_sal - sso_deduct - tax_deduct

    p.setFont("Helvetica-Bold", 11)
    p.drawString(50, height - 200, "Earnings (รายรับ)")
    p.drawRightString(width / 2 - 20, height - 200, f"{base_sal:,.2f} THB")

    p.drawString(width / 2 + 20, height - 200, "Deductions (รายการหัก)")
    p.drawString(width / 2 + 20, height - 225, "Social Security (5%)")
    p.drawRightString(width - 50, height - 225, f"{sso_deduct:,.2f} THB")

    p.drawString(width / 2 + 20, height - 245, "Withholding Tax (3%)")
    p.drawRightString(width - 50, height - 245, f"{tax_deduct:,.2f} THB")

    p.line(40, height - 270, width - 40, height - 270)

    p.setFont("Helvetica-Bold", 14)
    p.setFillColor(colors.HexColor("#059669"))
    p.drawString(50, height - 300, "Net Payable (เงินสุทธิได้รับ):")
    p.drawRightString(width - 50, height - 300, f"฿{net_pay:,.2f}")

    p.setFillColor(colors.HexColor("#64748B"))
    p.setFont("Helvetica", 9)
    p.drawString(60, 100, "___________________________")
    p.drawString(70, 85, "Employer Signature")

    p.drawString(width - 200, 100, "___________________________")
    p.drawString(width - 180, 85, "Employee Signature")

    p.drawCentredString(
        width / 2,
        40,
        "TaxMate Enterprise ERP - Payroll System (Strictly Confidential)",
    )

    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer.getvalue()


# ==========================================
# 📢 Helper Functions & Enterprise Light Theme
# ==========================================
def render_html(html_str):
    clean_html = "\n".join([line.lstrip() for line in html_str.splitlines()])
    st.markdown(clean_html, unsafe_allow_html=True)


def display_active_broadcasts():
    try:
        conn = get_connection()
        ann_df = pd.read_sql_query(
            "SELECT * FROM announcements ORDER BY id DESC LIMIT 1", conn
        )
        conn.close()
        if not ann_df.empty:
            latest = ann_df.iloc[0]
            p_type = latest.get("priority", "ปกติ")
            msg_str = (
                f"📢 **ประกาศระบบ [{latest.get('created_at', '')}]:"
                f" {latest.get('title', '')}**\n\n{latest.get('message', '')}"
            )
            if p_type == "ด่วนที่สุด (Urgent)":
                st.error(msg_str)
            elif p_type == "สำคัญ (High)":
                st.warning(msg_str)
            else:
                st.info(msg_str)
    except Exception:
        pass


def apply_enterprise_theme():
    light_css = """<style>
    @import url('https://fonts.googleapis.com/css2?family=Prompt:wght@300;400;500;600;700&family=Sarabun:wght@300;400;500;600;700&display=swap');
    *, ::before, ::after { box-sizing: border-box !important; }

    .stApp {
        background-color: #f8fafc !important;
        color: #0f172a !important;
    }

    p, label, h1, h2, h3, h4, h5, h6, .stMarkdown, .stText, div[data-testid="stMarkdownContainer"] p {
        font-family: 'Prompt', 'Sarabun', -apple-system, sans-serif !important;
        line-height: 1.55 !important;
        color: #0f172a !important;
    }

    [data-testid="stIconMaterial"], [data-testid="collapsedControl"], [data-testid="stSidebarCollapseButton"],
    [data-testid="stSidebarNavLink"], [data-baseweb="icon"], .stIcon, button[kind="header"] span,
    span[class*="material-symbols"], span[class*="icon"], i, svg {
        font-family: 'Material Symbols Rounded', 'Material Icons', sans-serif !important;
        white-space: nowrap !important; word-break: normal !important;
        display: inline-block !important; width: auto !important;
    }

    div[data-testid="stMetric"] {
        background-color: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        padding: 14px 16px !important;
        border-radius: 14px !important;
        box-shadow: 0 2px 6px rgba(0,0,0,0.02) !important;
    }

    .stButton > button {
        width: 100% !important;
        border-radius: 10px !important;
        font-weight: 500 !important;
    }

    section[data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 1px solid #e2e8f0 !important;
    }

    @media (max-width: 768px) {
        .block-container { padding: 0.8rem 0.5rem !important; }
        [data-testid="stHorizontalBlock"] { flex-direction: column !important; gap: 12px !important; }
        [data-testid="column"] { width: 100% !important; min-width: 100% !important; }
    }
    </style>"""
    render_html(light_css)


def safe_dataframe_display(df, required_cols):
    if df.empty:
        empty_df = pd.DataFrame(columns=required_cols)
        st.dataframe(empty_df, use_container_width=True)
        return
    for col in required_cols:
        if col not in df.columns:
            df[col] = ""
    st.dataframe(df[required_cols], use_container_width=True)


# ==========================================
# 🏠 1. Landing & Auth Views
# ==========================================
def render_landing_page():
    try:
        apply_enterprise_theme()
        display_active_broadcasts()

        cfg = get_cover_settings()

        hero_html = f"""
        <div style="
            background: linear-gradient(135deg, #ffffff 0%, #f1f5f9 50%, #e0f2fe 100%);
            padding: 42px 32px;
            border-radius: 18px;
            box-shadow: 0 10px 30px rgba(37, 99, 235, 0.08);
            border: 1px solid #cbd5e1;
            text-align: center;
            margin-bottom: 28px;
        ">
            <div style="
                display: inline-block;
                background: #eff6ff;
                color: {cfg.get('theme_color', '#1d4ed8')};
                padding: 6px 20px;
                border-radius: 20px;
                font-size: 0.85rem;
                font-weight: 700;
                letter-spacing: 0.5px;
                margin-bottom: 14px;
                border: 1px solid #bfdbfe;
            ">
                {cfg.get('badge')}
            </div>
            <h1 style="
                color: #0f172a; 
                font-size: 2.5rem; 
                font-weight: 800; 
                margin-bottom: 12px;
                letter-spacing: -0.5px;
            ">
                {cfg.get('title')}
            </h1>
            <p style="
                color: {cfg.get('theme_color', '#2563eb')}; 
                font-size: 1.15rem; 
                font-weight: 600; 
                margin-bottom: 18px;
            ">
                {cfg.get('subtitle')}
            </p>
            <p style="
                color: #334155; 
                font-size: 1.05rem; 
                max-width: 820px; 
                margin: 0 auto 25px auto; 
                line-height: 1.6;
            ">
                {cfg.get('description')}
            </p>
            <div style="
                display: inline-block;
                background: #ffffff;
                padding: 10px 24px;
                border-radius: 30px;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
                border: 1px solid #cbd5e1;
                color: #0284c7;
                font-size: 0.95rem;
                font-weight: 600;
            ">
                💡 เลือกเมนู <span style="color: #0f172a; font-weight: 700;">'🔑 เข้าสู่ระบบ / ลงทะเบียน'</span> ที่แถบด้านซ้าย เพื่อเริ่มต้นใช้งาน
            </div>
        </div>
        """
        render_html(hero_html)

        col1, col2, col3 = st.columns(3)
        with col1:
            render_html("""
            <div style="background: #ffffff; padding: 22px; border-radius: 14px; border: 1px solid #e2e8f0; text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.03);">
                <h3 style="color: #2563eb; margin-bottom: 10px; font-weight: 700;">📊 Thai Tax & e-Tax</h3>
                <p style="color: #475569; font-size: 0.92rem; line-height: 1.5;">คำนวณ ภ.พ.30, 50 ทวิ และสร้างไฟล์ e-Tax Invoice ตามมาตรฐานกรมสรรพากร</p>
            </div>
            """)

        with col2:
            render_html("""
            <div style="background: #ffffff; padding: 22px; border-radius: 14px; border: 1px solid #e2e8f0; text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.03);">
                <h3 style="color: #059669; margin-bottom: 10px; font-weight: 700;">🤖 AI Financial Advisor</h3>
                <p style="color: #475569; font-size: 0.92rem; line-height: 1.5;">วิเคราะห์งบการเงิน ประเมินความเสี่ยง และสรุปรายงานการบริหารอัตโนมัติ</p>
            </div>
            """)

        with col3:
            render_html("""
            <div style="background: #ffffff; padding: 22px; border-radius: 14px; border: 1px solid #e2e8f0; text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.03);">
                <h3 style="color: #0284c7; margin-bottom: 10px; font-weight: 700;">📦 Inventory & HR</h3>
                <p style="color: #475569; font-size: 0.92rem; line-height: 1.5;">จัดการสต็อกสินค้า ตัดสต็อกอัตโนมัติ พร้อมระบบบริหารเงินเดือนพนักงาน</p>
            </div>
            """)
    except Exception as e:
        st.error(f"Error in Landing Page: {e}")


def render_auth_page():
    try:
        apply_enterprise_theme()
        st.title("🔑 ศูนย์ยืนยันตัวตน (Authentication Center)")
        st.caption(
            "ระบบเข้าสู่ระบบ ลงทะเบียน"
            " และกู้คืนรหัสผ่านสำหรับพนักงานและผู้บริหาร"
        )

        tab_login, tab_register, tab_forgot = st.tabs([
            "🔑 เข้าสู่ระบบ (Login)",
            "📝 ลงทะเบียนผู้ใช้ใหม่ (Register)",
            "🔓 ลืมรหัสผ่าน (Forgot Password)",
        ])

        with tab_login:
            st.subheader("เข้าสู่ระบบด้วยบัญชีองค์กร")
            with st.form("login_form"):
                username = st.text_input("ชื่อผู้ใช้งาน (Username):")
                password = st.text_input("รหัสผ่าน (Password):", type="password")
                submit_login = st.form_submit_button(
                    "🔑 เข้าสู่ระบบ", type="primary", use_container_width=True
                )

                if submit_login:
                    if username and password:
                        success, result = authenticate_user(username, password)
                        if success:
                            st.session_state.authenticated = True
                            st.session_state.user_info = result
                            st.session_state.current_page = (
                                "📊 [Admin] Dashboard ผู้บริหาร"
                                if result.get("role") == "admin"
                                else "📊 ภาพรวม & เพิ่มรายการ"
                            )
                            st.success("เข้าสู่ระบบสำเร็จ!")
                            st.rerun()
                        else:
                            st.error(f"❌ {result}")
                    else:
                        st.warning(
                            "⚠️ กรุณากรอกชื่อผู้ใช้งานและรหัสผ่านให้ครบถ้วน"
                        )

            st.divider()
            st.subheader(
                "⚡ เข้าใช้งานด่วนด้วย บัญชีทดสอบ (Quick Demo Access)"
            )
            c_admin, c_user = st.columns(2)
            if c_admin.button(
                "🛡️ เข้าใช้งานด่วน: Super Admin (demo_admin)",
                type="secondary",
                use_container_width=True,
            ):
                success, result = authenticate_user("demo_admin", "123456")
                if success:
                    st.session_state.authenticated = True
                    st.session_state.user_info = result
                    st.session_state.current_page = (
                        "📊 [Admin] Dashboard ผู้บริหาร"
                    )
                    st.rerun()

            if c_user.button(
                "👤 เข้าใช้งานด่วน: General User (demo_user)",
                type="secondary",
                use_container_width=True,
            ):
                success, result = authenticate_user("demo_user", "123456")
                if success:
                    st.session_state.authenticated = True
                    st.session_state.user_info = result
                    st.session_state.current_page = "📊 ภาพรวม & เพิ่มรายการ"
                    st.rerun()

        with tab_register:
            st.subheader("ลงทะเบียนสร้างบัญชีผู้ใช้ใหม่")
            with st.form("register_form"):
                reg_username = st.text_input(
                    "ชื่อผู้ใช้งานที่ต้องการ (Username):"
                )
                reg_company = st.text_input(
                    "ชื่อบริษัท / องค์กร:", value="Tech Studio Co., Ltd."
                )
                reg_role = st.selectbox("สิทธิ์การใช้งาน (Role):", [
                    "user (พนักงานทั่วไป)",
                    "admin (ผู้ดูแลระบบ)",
                ])
                reg_pass = st.text_input("กำหนดรหัสผ่าน:", type="password")
                reg_pass_confirm = st.text_input(
                    "ยืนยันรหัสผ่าน:", type="password"
                )
                submit_reg = st.form_submit_button(
                    "📝 สมัครสมาชิก", type="primary", use_container_width=True
                )

                if submit_reg:
                    if not reg_username or not reg_pass:
                        st.warning("⚠️ กรุณากรอกข้อมูลให้ครบทุกช่อง")
                    elif reg_pass != reg_pass_confirm:
                        st.error("❌ รหัสผ่านทั้งสองช่องไม่ตรงกัน")
                    else:
                        role_code = "admin" if "admin" in reg_role else "user"
                        success, msg = register_user(
                            reg_username, reg_pass, reg_company, role_code
                        )
                        if success:
                            st.success(
                                "✅ ลงทะเบียนสำเร็จ!"
                                " สามารถเข้าสู่ระบบได้ทันที"
                            )
                        else:
                            st.error(f"❌ {msg}")

        with tab_forgot:
            st.subheader("กู้คืนหรือตั้งรหัสผ่านใหม่ (Reset Password)")
            with st.form("forgot_password_form"):
                fg_username = st.text_input(
                    "ระบุชื่อผู้ใช้งาน (Username) ที่ต้องการรีเซ็ต:"
                )
                fg_new_pass = st.text_input(
                    "ตั้งรหัสผ่านใหม่ (New Password):", type="password"
                )
                fg_confirm_pass = st.text_input(
                    "ยืนยันรหัสผ่านใหม่:", type="password"
                )
                submit_forgot = st.form_submit_button(
                    "🔓 รีเซ็ตรหัสผ่าน",
                    type="primary",
                    use_container_width=True,
                )

                if submit_forgot:
                    if not fg_username or not fg_new_pass:
                        st.warning(
                            "⚠️ กรุณากรอกชื่อผู้ใช้งานและรหัสผ่านใหม่"
                        )
                    elif fg_new_pass != fg_confirm_pass:
                        st.error("❌ รหัสผ่านใหม่ทั้งสองช่องไม่ตรงกัน")
                    else:
                        success, msg = change_password(
                            fg_username, fg_new_pass
                        )
                        if success:
                            st.success(
                                "✅ เปลี่ยนรหัสผ่านสำหรับ"
                                f" '{fg_username}' เรียบร้อยแล้ว!"
                            )
                        else:
                            st.error(f"❌ {msg}")

    except Exception as e:
        st.error(f"Error in Auth Page: {e}")


# ==========================================
# 📊 2. General User Core Modules
# ==========================================
def render_financial_overview():
    try:
        apply_enterprise_theme()
        st.title("📊 ศูนย์บริหารการเงินและบันทึกบัญชี")
        user = (
            st.session_state.user_info.get("username", "user")
            if st.session_state.user_info
            else "user"
        )

        with st.expander("➕ เพิ่มรายการ บัญชี รายรับ / รายจ่าย ใหม่", expanded=False):
            with st.form("add_tx_form"):
                col_a, col_b, col_c = st.columns(3)
                tx_date = col_a.date_input("วันที่:", datetime.now())
                tx_type = col_b.selectbox("ประเภท:", ["Income", "Expense"])
                tx_cat = col_c.selectbox("หมวดหมู่:", [
                    "ขายสินค้า/บริการ",
                    "ค่าเช่าออฟฟิศ",
                    "เงินเดือน",
                    "ค่าซอฟต์แวร์",
                    "ค่าน้ำ/ค่าไฟ",
                    "อื่นๆ",
                ])

                col_d, col_e = st.columns([2, 1])
                tx_title = col_d.text_input("รายละเอียดรายการ:")
                tx_amount = col_e.number_input(
                    "จำนวนเงิน (บาท):", min_value=0.0, value=1000.0
                )

                if st.form_submit_button("💾 บันทึกรายการลงระบบ"):
                    conn = get_connection()
                    c = conn.cursor()
                    c.execute(
                        """INSERT INTO transactions (user_id, date, type, title, amount, category, approval_status)
                                  VALUES (?, ?, ?, ?, ?, ?, 'Approved')""",
                        (
                            user,
                            tx_date.strftime("%Y-%m-%d"),
                            tx_type,
                            tx_title,
                            tx_amount,
                            tx_cat,
                        ),
                    )
                    conn.commit()
                    conn.close()
                    log_audit(
                        user,
                        "ADD_TX",
                        f"บันทึก {tx_type} {tx_title} ฿{tx_amount}",
                    )
                    st.success("บันทึกรายการสำเร็จ!")
                    st.rerun()

        conn = get_connection()
        df = pd.read_sql_query(
            "SELECT id, date, type, title, amount, category, approval_status"
            " FROM transactions WHERE user_id = ? ORDER BY id DESC",
            conn,
            params=(user,),
        )
        conn.close()

        inc = (
            df[
                (df["type"] == "Income")
                & (df.get("approval_status", "Approved") == "Approved")
            ]["amount"].sum()
            if not df.empty and "amount" in df.columns
            else 0.0
        )
        exp = (
            df[
                (df["type"] == "Expense")
                & (df.get("approval_status", "Approved") == "Approved")
            ]["amount"].sum()
            if not df.empty and "amount" in df.columns
            else 0.0
        )

        c1, c2, c3 = st.columns(3)
        c1.metric("รายรับรวม", f"฿{inc:,.2f}")
        c2.metric("รายจ่ายรวม", f"฿{exp:,.2f}")
        c3.metric("คงเหลือสุทธิ", f"฿{(inc - exp):,.2f}")

        # 📊 เพิ่มกราฟวิเคราะห์รายรับ-รายจ่ายตามหมวดหมู่
        if not df.empty and "category" in df.columns:
            st.divider()
            st.subheader("📈 กราฟสรุปสัดส่วนตามหมวดหมู่ (Category Analysis)")
            cat_summary = (
                df.groupby(["category", "type"])["amount"].sum().unstack().fillna(0)
            )
            st.bar_chart(cat_summary)

        # 🔱 เพิ่มเครื่องมือแปลงสกุลเงินต่างประเทศ
        with st.expander("🔱 เครื่องมือคำนวณและแปลงสกุลเงิน (Currency Converter)", expanded=False):
            col_curr1, col_curr2, col_curr3 = st.columns(3)
            foreign_amt = col_curr1.number_input(
                "จำนวนเงินต่างประเทศ:", min_value=0.0, value=100.0
            )
            currency = col_curr2.selectbox(
                "สกุลเงิน:", ["USD ($)", "EUR (€)", "JPY (¥)", "CNY (¥)", "SGD ($)"]
            )
            rates = {
                "USD ($)": 35.5,
                "EUR (€)": 38.2,
                "JPY (¥)": 0.24,
                "CNY (¥)": 4.9,
                "SGD ($)": 26.2,
            }
            converted_thb = foreign_amt * rates.get(currency, 35.5)
            col_curr3.metric(
                "คิดเป็นเงินบาท (THB ประมาณการ):", f"฿{converted_thb:,.2f}"
            )

        st.divider()
        safe_dataframe_display(
            df,
            [
                "id",
                "date",
                "type",
                "title",
                "amount",
                "category",
                "approval_status",
            ],
        )

        if not df.empty:
            with st.expander("🗑️ จัดการลบข้อมูล (Delete Options)", expanded=False):
                col_del1, col_del2 = st.columns(2)
                with col_del1:
                    st.markdown("##### 🗑️ ลบเฉพาะรายการ")
                    del_id = st.selectbox(
                        "เลือก ID ที่ต้องการลบ:",
                        df["id"].tolist(),
                        key="del_tx_id",
                    )
                    if st.button("🔴 ลบรายการนี้", key="btn_del_tx_single"):
                        conn = get_connection()
                        c = conn.cursor()
                        c.execute(
                            "DELETE FROM transactions WHERE id = ? AND user_id = ?",
                            (del_id, user),
                        )
                        conn.commit()
                        conn.close()
                        log_audit(user, "DELETE_TX", f"ลบรายการ ID: {del_id}")
                        st.success(f"ลบรายการ ID {del_id} เรียบร้อยแล้ว!")
                        st.rerun()

                with col_del2:
                    st.markdown("##### ⚠️ ลบข้อมูลทั้งหมด")
                    chk_confirm = st.checkbox(
                        "ยืนยันว่าต้องการลบข้อมูลรายรับ-รายจ่ายทั้งหมด",
                        key="chk_del_tx_all",
                    )
                    if st.button(
                        "💥 ลบข้อมูลทั้งหมดในหน้านี้",
                        type="primary",
                        key="btn_del_tx_all",
                    ):
                        if chk_confirm:
                            conn = get_connection()
                            c = conn.cursor()
                            c.execute(
                                "DELETE FROM transactions WHERE user_id = ?",
                                (user,),
                            )
                            conn.commit()
                            conn.close()
                            log_audit(
                                user, "DELETE_ALL_TX", "ลบข้อมูลธุรกรรมทั้งหมด"
                            )
                            st.success("ลบข้อมูลทั้งหมดเรียบร้อยแล้ว!")
                            st.rerun()
                        else:
                            st.warning(
                                "⚠️ กรุณาติ๊กถูกที่กล่องยืนยันก่อนกดลบทั้งหมด"
                            )

    except Exception as e:
        st.error(f"Error in Financial Overview: {e}")


def render_client_directory():
    try:
        apply_enterprise_theme()
        st.title("📇 สมุดรายนามคู่ค้า/ลูกค้า (Client Directory)")
        user = (
            st.session_state.user_info.get("username", "user")
            if st.session_state.user_info
            else "user"
        )

        with st.expander("➕ เพิ่มข้อมูลลูกค้า / คู่ค้าใหม่", expanded=False):
            with st.form("add_client_form"):
                col1, col2 = st.columns(2)
                c_name = col1.text_input("ชื่อบริษัท / ลูกค้า:")
                c_tax = col2.text_input(
                    "เลขประจำตัวผู้เสียภาษี (13 หลัก):",
                    value="0105500000000",
                )
                col3, col4 = st.columns(2)
                c_type = col3.selectbox("ประเภท:", [
                    "Customer (ลูกค้า)",
                    "Vendor (คู่ค้า/ผู้ขาย)",
                ])
                c_phone = col4.text_input("เบอร์โทรศัพท์:")
                c_addr = st.text_area("ที่อยู่:")

                if st.form_submit_button("💾 บันทึกข้อมูลคู่ค้า"):
                    conn = get_connection()
                    c = conn.cursor()
                    c.execute(
                        "INSERT INTO clients (user_id, name, tax_id, client_type, address, phone, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                        (
                            user,
                            c_name,
                            c_tax,
                            c_type,
                            c_addr,
                            c_phone,
                            datetime.now().strftime("%Y-%m-%d"),
                        ),
                    )
                    conn.commit()
                    conn.close()
                    st.success("บันทึกข้อมูลคู่ค้าเรียบร้อย!")
                    st.rerun()

        conn = get_connection()
        clients_df = pd.read_sql_query(
            "SELECT id, name, tax_id, client_type, phone, address FROM clients WHERE user_id = ?",
            conn,
            params=(user,),
        )
        conn.close()
        safe_dataframe_display(
            clients_df,
            ["id", "name", "tax_id", "client_type", "phone", "address"],
        )

        if not clients_df.empty:
            with st.expander("🗑️ จัดการลบข้อมูล (Delete Options)", expanded=False):
                col_del1, col_del2 = st.columns(2)
                with col_del1:
                    st.markdown("##### 🗑️ ลบเฉพาะรายการ")
                    del_id = st.selectbox(
                        "เลือก ID คู่ค้าที่ต้องการลบ:",
                        clients_df["id"].tolist(),
                        key="del_client_id",
                    )
                    if st.button("🔴 ลบคู่ค้ารายนี้", key="btn_del_client_single"):
                        conn = get_connection()
                        c = conn.cursor()
                        c.execute(
                            "DELETE FROM clients WHERE id = ? AND user_id = ?",
                            (del_id, user),
                        )
                        conn.commit()
                        conn.close()
                        log_audit(
                            user, "DELETE_CLIENT", f"ลบคู่ค้า ID: {del_id}"
                        )
                        st.success(f"ลบคู่ค้า ID {del_id} เรียบร้อยแล้ว!")
                        st.rerun()

                with col_del2:
                    st.markdown("##### ⚠️ ลบข้อมูลทั้งหมด")
                    chk_confirm = st.checkbox(
                        "ยืนยันว่าต้องการลบรายชื่อคู่ค้าทั้งหมด",
                        key="chk_del_client_all",
                    )
                    if st.button(
                        "💥 ลบข้อมูลคู่ค้าทั้งหมด",
                        type="primary",
                        key="btn_del_client_all",
                    ):
                        if chk_confirm:
                            conn = get_connection()
                            c = conn.cursor()
                            c.execute(
                                "DELETE FROM clients WHERE user_id = ?", (user,)
                            )
                            conn.commit()
                            conn.close()
                            log_audit(
                                user,
                                "DELETE_ALL_CLIENTS",
                                "ลบข้อมูลคู่ค้าทั้งหมด",
                            )
                            st.success("ลบข้อมูลคู่ค้าทั้งหมดเรียบร้อยแล้ว!")
                            st.rerun()
                        else:
                            st.warning(
                                "⚠️ กรุณาติ๊กถูกที่กล่องยืนยันก่อนกดลบทั้งหมด"
                            )

    except Exception as e:
        st.error(f"Error in Client Directory: {e}")


def render_documents_module():
    try:
        apply_enterprise_theme()
        st.title("📑 ออกเอกสาร & ตัดรับชำระเงิน (Invoicing & Documents)")
        user = (
            st.session_state.user_info.get("username", "user")
            if st.session_state.user_info
            else "user"
        )

        with st.expander("📄 สร้างเอกสารใบแจ้งหนี้ / ใบเสร็จรับเงินใหม่", expanded=False):
            with st.form("create_doc_form"):
                col1, col2, col3 = st.columns(3)
                doc_type = col1.selectbox("ประเภทเอกสาร:", [
                    "ใบแจ้งหนี้ (Invoice)",
                    "ใบเสร็จรับเงิน (Receipt)",
                    "ใบเสนอราคา (Quotation)",
                    "ใบสั่งซื้อ (PO)",
                ])
                doc_num = col2.text_input(
                    "เลขที่เอกสาร:",
                    value=f"INV-{datetime.now().strftime('%Y%m%d%H%M')}",
                )
                issue_date = col3.date_input("วันที่ออกเอกสาร:", datetime.now())

                c1, c2 = st.columns(2)
                client_name = c1.text_input("ชื่อลูกค้า/บริษัทผู้รับ:")
                client_tax = c2.text_input(
                    "เลขผู้เสียภาษีลูกค้า:", value="0105500000000"
                )

                items_summary = st.text_input(
                    "รายการสินค้า/บริการ:",
                    value="ค่าบริการที่ปรึกษาระบบซอฟต์แวร์ประจำเดือน",
                )
                subtotal = st.number_input(
                    "จำนวนเงินก่อน VAT (บาท):", min_value=0.0, value=10000.0
                )
                vat_amount = subtotal * 0.07
                grand_total = subtotal + vat_amount

                st.caption(
                    f"VAT (7%): ฿{vat_amount:,.2f} | **ยอดรวมสุทธิ:"
                    f" ฿{grand_total:,.2f}**"
                )

                if st.form_submit_button("💾 สร้างและบันทึกเอกสาร"):
                    conn = get_connection()
                    c = conn.cursor()
                    c.execute(
                        """INSERT INTO documents (user_id, doc_type, doc_number, issue_date, client_name, client_tax_id, items_summary, subtotal, vat_amount, grand_total, payment_status, created_at)
                                  VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Unpaid', ?)""",
                        (
                            user,
                            doc_type,
                            doc_num,
                            issue_date.strftime("%Y-%m-%d"),
                            client_name,
                            client_tax,
                            items_summary,
                            subtotal,
                            vat_amount,
                            grand_total,
                            datetime.now().strftime("%Y-%m-%d"),
                        ),
                    )
                    conn.commit()
                    conn.close()
                    st.success("สร้างเอกสารสำเร็จ!")
                    st.rerun()

        conn = get_connection()
        docs_df = pd.read_sql_query(
            "SELECT * FROM documents WHERE user_id = ? ORDER BY id DESC",
            conn,
            params=(user,),
        )
        conn.close()

        # 🚨 แจ้งเตือนเอกสารยังไม่ได้ชำระเงิน
        if not docs_df.empty and "payment_status" in docs_df.columns:
            unpaid_count = len(docs_df[docs_df["payment_status"] == "Unpaid"])
            if unpaid_count > 0:
                st.warning(
                    f"⚠️ คุณมีเอกสารที่ยังไม่ได้ชำระเงินค้างอยู่ทั้งหมด"
                    f" **{unpaid_count} รายการ**"
                )

        safe_dataframe_display(
            docs_df,
            [
                "id",
                "doc_number",
                "doc_type",
                "issue_date",
                "client_name",
                "grand_total",
                "payment_status",
            ],
        )

        # 📄 ปุ่มดาวน์โหลดเอกสาร PDF
        if not docs_df.empty:
            st.divider()
            st.subheader("📄 ดาวน์โหลดเอกสารรูปแบบ PDF")
            selected_doc_id = st.selectbox(
                "เลือกเอกสารที่ต้องการพิมพ์ PDF:",
                docs_df["id"].tolist(),
                format_func=lambda x: (
                    f"ID: {x} |"
                    f" {docs_df[docs_df['id']==x]['doc_number'].values[0]} -"
                    f" {docs_df[docs_df['id']==x]['client_name'].values[0]}"
                ),
            )
            doc_row = docs_df[docs_df["id"] == selected_doc_id].iloc[0].to_dict()
            pdf_bytes = generate_pdf_document(doc_row)

            st.download_button(
                label=f"📥 ดาวน์โหลด PDF ({doc_row['doc_number']})",
                data=pdf_bytes,
                file_name=f"{doc_row['doc_number']}.pdf",
                mime="application/pdf",
                type="primary",
            )

        if not docs_df.empty:
            with st.expander("🗑️ จัดการลบข้อมูล (Delete Options)", expanded=False):
                col_del1, col_del2 = st.columns(2)
                with col_del1:
                    st.markdown("##### 🗑️ ลบเฉพาะรายการ")
                    del_id = st.selectbox(
                        "เลือก ID เอกสารที่ต้องการลบ:",
                        docs_df["id"].tolist(),
                        key="del_doc_id",
                    )
                    if st.button("🔴 ลบเอกสารฉบับนี้", key="btn_del_doc_single"):
                        conn = get_connection()
                        c = conn.cursor()
                        c.execute(
                            "DELETE FROM documents WHERE id = ? AND user_id = ?",
                            (del_id, user),
                        )
                        conn.commit()
                        conn.close()
                        log_audit(user, "DELETE_DOC", f"ลบเอกสาร ID: {del_id}")
                        st.success(f"ลบเอกสาร ID {del_id} เรียบร้อยแล้ว!")
                        st.rerun()

                with col_del2:
                    st.markdown("##### ⚠️ ลบข้อมูลทั้งหมด")
                    chk_confirm = st.checkbox(
                        "ยืนยันว่าต้องการลบเอกสารทั้งหมด", key="chk_del_doc_all"
                    )
                    if st.button(
                        "💥 ลบเอกสารทั้งหมด",
                        type="primary",
                        key="btn_del_doc_all",
                    ):
                        if chk_confirm:
                            conn = get_connection()
                            c = conn.cursor()
                            c.execute(
                                "DELETE FROM documents WHERE user_id = ?",
                                (user,),
                            )
                            conn.commit()
                            conn.close()
                            log_audit(
                                user, "DELETE_ALL_DOCS", "ลบเอกสารทั้งหมด"
                            )
                            st.success("ลบเอกสารทั้งหมดเรียบร้อยแล้ว!")
                            st.rerun()
                        else:
                            st.warning(
                                "⚠️ กรุณาติ๊กถูกที่กล่องยืนยันก่อนกดลบทั้งหมด"
                            )

    except Exception as e:
        st.error(f"Error in Documents Module: {e}")


def render_inventory_module():
    try:
        apply_enterprise_theme()
        st.title("📦 บริหารสต็อกสินค้าคงคลัง (Inventory Management)")
        user = (
            st.session_state.user_info.get("username", "user")
            if st.session_state.user_info
            else "user"
        )

        with st.expander("➕ เพิ่มสินค้าเข้าสต็อกใหม่", expanded=False):
            with st.form("add_inv_form"):
                col1, col2, col3 = st.columns(3)
                code = col1.text_input("รหัสสินค้า:", value="SKU-001")
                name = col2.text_input("ชื่อสินค้า:")
                cat = col3.selectbox("หมวดหมู่:", [
                    "วัตถุดิบ",
                    "สินค้าพร้อมขาย",
                    "อุปกรณ์สำนักงาน",
                ])

                c1, c2, c3 = st.columns(3)
                qty = c1.number_input(
                    "จำนวน:", min_value=0.0, value=100.0
                )
                unit = c2.text_input("หน่วยนับ:", value="ชิ้น")
                price = c3.number_input(
                    "ราคาต่อหน่วย (บาท):", min_value=0.0, value=250.0
                )

                if st.form_submit_button("💾 บันทึกสินค้าเข้าคลัง"):
                    conn = get_connection()
                    c = conn.cursor()
                    c.execute(
                        "INSERT INTO inventory (user_id, item_code, item_name, category, qty, unit, unit_price, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                        (
                            user,
                            code,
                            name,
                            cat,
                            qty,
                            unit,
                            price,
                            datetime.now().strftime("%Y-%m-%d"),
                        ),
                    )
                    conn.commit()
                    conn.close()
                    st.success("เพิ่มสินค้าเข้าสต็อกสำเร็จ!")
                    st.rerun()

        conn = get_connection()
        inv_df = pd.read_sql_query(
            "SELECT id, item_code, item_name, category, qty, unit, unit_price FROM inventory WHERE user_id = ?",
            conn,
            params=(user,),
        )
        conn.close()

        # 🚨 แจ้งเตือนสินค้าใกล้หมดสต็อก
        if not inv_df.empty and "qty" in inv_df.columns:
            low_stock = inv_df[inv_df["qty"] <= 10]
            if not low_stock.empty:
                st.error(
                    f"⚠️ มีสินค้าใกล้หมดสต็อก (ต่ำกว่า 10 ชิ้น) จำนวน"
                    f" **{len(low_stock)} รายการ**"
                )

        safe_dataframe_display(
            inv_df,
            [
                "id",
                "item_code",
                "item_name",
                "category",
                "qty",
                "unit",
                "unit_price",
            ],
        )

        if not inv_df.empty:
            with st.expander("🗑️ จัดการลบข้อมูล (Delete Options)", expanded=False):
                col_del1, col_del2 = st.columns(2)
                with col_del1:
                    st.markdown("##### 🗑️ ลบเฉพาะรายการ")
                    del_id = st.selectbox(
                        "เลือก ID สินค้าที่ต้องการลบ:",
                        inv_df["id"].tolist(),
                        key="del_inv_id",
                    )
                    if st.button("🔴 ลบสินค้าชิ้นนี้", key="btn_del_inv_single"):
                        conn = get_connection()
                        c = conn.cursor()
                        c.execute(
                            "DELETE FROM inventory WHERE id = ? AND user_id = ?",
                            (del_id, user),
                        )
                        conn.commit()
                        conn.close()
                        log_audit(
                            user, "DELETE_INVENTORY", f"ลบสินค้า ID: {del_id}"
                        )
                        st.success(f"ลบสินค้า ID {del_id} เรียบร้อยแล้ว!")
                        st.rerun()

                with col_del2:
                    st.markdown("##### ⚠️ ลบข้อมูลทั้งหมด")
                    chk_confirm = st.checkbox(
                        "ยืนยันว่าต้องการลบสต็อกสินค้าทั้งหมด",
                        key="chk_del_inv_all",
                    )
                    if st.button(
                        "💥 ลบสต็อกสินค้าทั้งหมด",
                        type="primary",
                        key="btn_del_inv_all",
                    ):
                        if chk_confirm:
                            conn = get_connection()
                            c = conn.cursor()
                            c.execute(
                                "DELETE FROM inventory WHERE user_id = ?",
                                (user,),
                            )
                            conn.commit()
                            conn.close()
                            log_audit(
                                user,
                                "DELETE_ALL_INVENTORY",
                                "ลบสินค้าในคลังทั้งหมด",
                            )
                            st.success("ลบสต็อกสินค้าทั้งหมดเรียบร้อยแล้ว!")
                            st.rerun()
                        else:
                            st.warning(
                                "⚠️ กรุณาติ๊กถูกที่กล่องยืนยันก่อนกดลบทั้งหมด"
                            )

    except Exception as e:
        st.error(f"Error in Inventory Module: {e}")


def render_budgeting_module():
    try:
        apply_enterprise_theme()
        st.title("🎯 วางแผนงบประมาณ (Departmental Budgeting)")
        user = (
            st.session_state.user_info.get("username", "user")
            if st.session_state.user_info
            else "user"
        )

        with st.form("set_budget_form"):
            col1, col2 = st.columns(2)
            dept = col1.selectbox("แผนก/ฝ่าย:", [
                "ฝ่ายการตลาด",
                "ฝ่ายไอที/ซอฟต์แวร์",
                "ฝ่ายบริหาร",
                "ฝ่ายขาย",
            ])
            alloc = col2.number_input(
                "งบประมาณที่จัดสรร (บาท):",
                min_value=1000.0,
                value=100000.0,
            )
            if st.form_submit_button("💾 ตั้งค่าวงเงินงบประมาณ"):
                conn = get_connection()
                c = conn.cursor()
                c.execute(
                    "INSERT INTO budgets (user_id, department, allocated_amount, year_month) VALUES (?, ?, ?, ?)",
                    (user, dept, alloc, datetime.now().strftime("%Y-%m")),
                )
                conn.commit()
                conn.close()
                st.success("บันทึกงบประมาณสำเร็จ!")
                st.rerun()

        conn = get_connection()
        b_df = pd.read_sql_query(
            "SELECT id, department, allocated_amount, year_month FROM budgets WHERE user_id = ?",
            conn,
            params=(user,),
        )
        conn.close()
        safe_dataframe_display(
            b_df, ["id", "department", "allocated_amount", "year_month"]
        )

        if not b_df.empty:
            with st.expander("🗑️ จัดการลบข้อมูล (Delete Options)", expanded=False):
                col_del1, col_del2 = st.columns(2)
                with col_del1:
                    st.markdown("##### 🗑️ ลบเฉพาะรายการ")
                    del_id = st.selectbox(
                        "เลือก ID งบประมาณที่ต้องการลบ:",
                        b_df["id"].tolist(),
                        key="del_budget_id",
                    )
                    if st.button(
                        "🔴 ลบงบประมาณรายการนี้", key="btn_del_budget_single"
                    ):
                        conn = get_connection()
                        c = conn.cursor()
                        c.execute(
                            "DELETE FROM budgets WHERE id = ? AND user_id = ?",
                            (del_id, user),
                        )
                        conn.commit()
                        conn.close()
                        log_audit(
                            user, "DELETE_BUDGET", f"ลบงบประมาณ ID: {del_id}"
                        )
                        st.success(f"ลบงบประมาณ ID {del_id} เรียบร้อยแล้ว!")
                        st.rerun()

                with col_del2:
                    st.markdown("##### ⚠️ ลบข้อมูลทั้งหมด")
                    chk_confirm = st.checkbox(
                        "ยืนยันว่าต้องการลบข้อมูลงบประมาณทั้งหมด",
                        key="chk_del_budget_all",
                    )
                    if st.button(
                        "💥 ลบข้อมูลงบประมาณทั้งหมด",
                        type="primary",
                        key="btn_del_budget_all",
                    ):
                        if chk_confirm:
                            conn = get_connection()
                            c = conn.cursor()
                            c.execute(
                                "DELETE FROM budgets WHERE user_id = ?", (user,)
                            )
                            conn.commit()
                            conn.close()
                            log_audit(
                                user,
                                "DELETE_ALL_BUDGETS",
                                "ลบข้อมูลงบประมาณทั้งหมด",
                            )
                            st.success("ลบข้อมูลงบประมาณทั้งหมดเรียบร้อยแล้ว!")
                            st.rerun()
                        else:
                            st.warning(
                                "⚠️ กรุณาติ๊กถูกที่กล่องยืนยันก่อนกดลบทั้งหมด"
                            )

    except Exception as e:
        st.error(f"Error in Budgeting Module: {e}")


def render_thai_tax_module():
    try:
        apply_enterprise_theme()
        st.title(
            "🇹🇭 ระบบภาษีไทย (VAT 7% & ภาษีหัก ณ ที่จ่าย 50 ทวิ)"
        )

        tab1, tab2 = st.tabs([
            "📋 คำนวณ ภ.พ. 30 (VAT)",
            "📑 ออกหนังสือรับรอง 50 ทวิ (WHT)",
        ])

        with tab1:
            st.subheader("คำนวณภาษีมูลค่าเพิ่ม (VAT 7%)")
            sales = st.number_input(
                "ยอดขายรวมก่อน VAT (บาท):", value=100000.0
            )
            purchases = st.number_input(
                "ยอดซื้อรวมก่อน VAT (บาท):", value=60000.0
            )
            sales_vat = sales * 0.07
            purch_vat = purchases * 0.07
            net_vat = sales_vat - purch_vat
            st.info(
                f"ภาษีขาย: ฿{sales_vat:,.2f} | ภาษีซื้อ: ฿{purch_vat:,.2f} |"
                f" **ภาษีต้องชำระสุทธิ: ฿{net_vat:,.2f}**"
            )

        with tab2:
            st.subheader("คำนวณภาษีหัก ณ ที่จ่าย (Withholding Tax)")
            rate = st.selectbox("ประเภทเงินได้ / อัตราภาษี:", [
                "3% - ค่าบริการ / จ้างทำของ",
                "5% - ค่าเช่าสถานที่",
                "1% - ค่าขนส่ง / ยานพาหนะ",
                "2% - ค่าโฆษณา",
            ])
            amt = st.number_input("จำนวนเงินเต็ม (บาท):", value=10000.0)
            pct = (
                0.03
                if "3%" in rate
                else (0.05 if "5%" in rate else (0.01 if "1%" in rate else 0.02))
            )
            wht_val = amt * pct
            st.success(
                f"ภาษีหัก ณ ที่จ่ายที่ต้องหักไว้: **฿{wht_val:,.2f}**"
                f" (จ่ายจริงให้ผู้รับ: ฿{(amt - wht_val):,.2f})"
            )
    except Exception as e:
        st.error(f"Error in Thai Tax Module: {e}")


def render_bank_reconciliation():
    try:
        apply_enterprise_theme()
        st.title("🏦 กระทบยอดธนาคาร (Bank Statement Reconciliation)")
        user = (
            st.session_state.user_info.get("username", "user")
            if st.session_state.user_info
            else "user"
        )

        uploaded_file = st.file_uploader(
            "อัปโหลดไฟล์ Bank Statement (.csv / .xlsx):", type=["csv", "xlsx"]
        )
        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith(".csv"):
                    stmt_df = pd.read_csv(uploaded_file)
                else:
                    stmt_df = pd.read_excel(uploaded_file)
                st.success(
                    f"อ่านไฟล์สำเร็จ! พบทั้งหมด {len(stmt_df)} รายการ"
                )
                st.dataframe(stmt_df, use_container_width=True)
            except Exception as ex:
                st.error(f"อ่านไฟล์ไม่สำเร็จ: {ex}")

        conn = get_connection()
        tx_df = pd.read_sql_query(
            "SELECT id, date, title, amount, type FROM transactions WHERE user_id = ?",
            conn,
            params=(user,),
        )
        conn.close()

        st.subheader("📋 รายการในสมุดบัญชีองค์กร")
        safe_dataframe_display(tx_df, ["id", "date", "title", "amount", "type"])
    except Exception as e:
        st.error(f"Error in Bank Reconciliation: {e}")


def render_expense_claims_module():
    try:
        apply_enterprise_theme()
        st.title(
            "💳 เบิกเงินสดย่อย & เคลมค่าใช้จ่าย (Petty Cash Claims)"
        )
        user = (
            st.session_state.user_info.get("username", "user")
            if st.session_state.user_info
            else "user"
        )

        with st.form("claim_form"):
            title = st.text_input(
                "รายการที่ต้องการเบิก (เช่น ค่าเดินทางพบลูกค้า):"
            )
            amount = st.number_input(
                "จำนวนเงิน (บาท):", min_value=1.0, value=500.0
            )
            cat = st.selectbox("หมวดหมู่:", [
                "ค่าเดินทาง",
                "ค่ารับรองลูกค้า",
                "ค่าอุปกรณ์สำนักงาน",
            ])
            if st.form_submit_button("📤 ส่งคำขอเบิกเงินสดย่อย"):
                conn = get_connection()
                c = conn.cursor()
                c.execute(
                    "INSERT INTO expense_claims (user_id, claim_title, amount, category, status, created_at) VALUES (?, ?, ?, ?, 'Pending', ?)",
                    (
                        user,
                        title,
                        amount,
                        cat,
                        datetime.now().strftime("%Y-%m-%d"),
                    ),
                )
                conn.commit()
                conn.close()
                st.success("ส่งคำขอเบิกเงินสดย่อยเรียบร้อย!")
                st.rerun()

        conn = get_connection()
        c_df = pd.read_sql_query(
            "SELECT id, claim_title, amount, category, status, created_at FROM expense_claims WHERE user_id = ?",
            conn,
            params=(user,),
        )
        conn.close()
        safe_dataframe_display(
            c_df,
            [
                "id",
                "claim_title",
                "amount",
                "category",
                "status",
                "created_at",
            ],
        )

        if not c_df.empty:
            with st.expander("🗑️ จัดการลบข้อมูล (Delete Options)", expanded=False):
                col_del1, col_del2 = st.columns(2)
                with col_del1:
                    st.markdown("##### 🗑️ ลบเฉพาะรายการ")
                    del_id = st.selectbox(
                        "เลือก ID รายการเคลมที่ต้องการลบ:",
                        c_df["id"].tolist(),
                        key="del_claim_id",
                    )
                    if st.button("🔴 ลบรายการเคลมนี้", key="btn_del_claim_single"):
                        conn = get_connection()
                        c = conn.cursor()
                        c.execute(
                            "DELETE FROM expense_claims WHERE id = ? AND user_id = ?",
                            (del_id, user),
                        )
                        conn.commit()
                        conn.close()
                        log_audit(
                            user, "DELETE_CLAIM", f"ลบรายการเคลม ID: {del_id}"
                        )
                        st.success(f"ลบรายการเคลม ID {del_id} เรียบร้อยแล้ว!")
                        st.rerun()

                with col_del2:
                    st.markdown("##### ⚠️ ลบข้อมูลทั้งหมด")
                    chk_confirm = st.checkbox(
                        "ยืนยันว่าต้องการลบรายการเคลมเงินสดย่อยทั้งหมด",
                        key="chk_del_claim_all",
                    )
                    if st.button(
                        "💥 ลบรายการเคลมทั้งหมด",
                        type="primary",
                        key="btn_del_claim_all",
                    ):
                        if chk_confirm:
                            conn = get_connection()
                            c = conn.cursor()
                            c.execute(
                                "DELETE FROM expense_claims WHERE user_id = ?",
                                (user,),
                            )
                            conn.commit()
                            conn.close()
                            log_audit(
                                user,
                                "DELETE_ALL_CLAIMS",
                                "ลบรายการเบิกเงินสดย่อยทั้งหมด",
                            )
                            st.success(
                                "ลบรายการเบิกเงินสดย่อยทั้งหมดเรียบร้อยแล้ว!"
                            )
                            st.rerun()
                        else:
                            st.warning(
                                "⚠️ กรุณาติ๊กถูกที่กล่องยืนยันก่อนกดลบทั้งหมด"
                            )

    except Exception as e:
        st.error(f"Error in Expense Claims: {e}")


def render_slip_ocr_module():
    try:
        apply_enterprise_theme()
        st.title("🤖 AI สแกนสลิป/ใบเสร็จรับเงิน (Smart Receipt OCR)")
        user = (
            st.session_state.user_info.get("username", "user")
            if st.session_state.user_info
            else "user"
        )

        uploaded_file = st.file_uploader(
            "อัปโหลดรูปภาพสลิปโอนเงิน / ใบเสร็จ:",
            type=["png", "jpg", "jpeg"],
        )
        if uploaded_file is not None:
            st.image(uploaded_file, caption="สลิปที่อัปโหลด", width=300)
            st.subheader("🤖 ข้อมูลที่ AI สแกนได้ (ตรวจสอบและแก้ไขได้):")

            with st.form("ocr_save_form"):
                col1, col2 = st.columns(2)
                ocr_title = col1.text_input(
                    "ชื่อรายการ:", value="ค่าบริการ/สินค้าจากสลิปโอนเงิน"
                )
                ocr_amount = col2.number_input(
                    "จำนวนเงินสุทธิ (บาท):", min_value=1.0, value=1500.0
                )
                col3, col4 = st.columns(2)
                ocr_type = col3.selectbox("ประเภท:", ["Expense", "Income"])
                ocr_cat = col4.selectbox("หมวดหมู่:", [
                    "ค่าซอฟต์แวร์",
                    "ค่าน้ำ/ค่าไฟ",
                    "ค่าอุปกรณ์สำนักงาน",
                    "ขายสินค้า/บริการ",
                ])

                if st.form_submit_button(
                    "💾 บันทึกลงสมุดบัญชีทันที", type="primary"
                ):
                    conn = get_connection()
                    c = conn.cursor()
                    c.execute(
                        """INSERT INTO transactions (user_id, date, type, title, amount, category, approval_status)
                                  VALUES (?, ?, ?, ?, ?, ?, 'Approved')""",
                        (
                            user,
                            datetime.now().strftime("%Y-%m-%d"),
                            ocr_type,
                            ocr_title,
                            ocr_amount,
                            ocr_cat,
                        ),
                    )
                    conn.commit()
                    conn.close()
                    log_audit(
                        user,
                        "OCR_ADD_TX",
                        f"สแกนสลิปบันทึก {ocr_type} {ocr_title} ฿{ocr_amount}",
                    )
                    st.success(
                        "บันทึกรายการจากสลิปเข้าสมุดบัญชีเรียบร้อยแล้ว!"
                    )
                    st.rerun()
    except Exception as e:
        st.error(f"Error in Slip OCR Module: {e}")


def render_ai_financial_health_module():
    try:
        apply_enterprise_theme()
        st.title(
            "🧠 AI วิเคราะห์สุขภาพการเงิน (Financial Health Check Scorecard)"
        )
        user = (
            st.session_state.user_info.get("username", "user")
            if st.session_state.user_info
            else "user"
        )

        conn = get_connection()
        tx_df = pd.read_sql_query(
            "SELECT * FROM transactions WHERE user_id = ? AND approval_status = 'Approved'",
            conn,
            params=(user,),
        )
        conn.close()

        rev = (
            tx_df[tx_df["type"] == "Income"]["amount"].sum()
            if not tx_df.empty and "amount" in tx_df.columns
            else 0.0
        )
        exp = (
            tx_df[tx_df["type"] == "Expense"]["amount"].sum()
            if not tx_df.empty and "amount" in tx_df.columns
            else 0.0
        )
        net = rev - exp

        score = 85
        if rev > 0:
            margin = (net / rev) * 100
            score = min(100, max(40, int(margin + 50)))

        st.success(
            f"📊 **คะแนนสุขภาพทางการเงินองค์กรของคุณ: {score}/100**"
        )
        col1, col2 = st.columns(2)
        col1.info(
            f"💵 **รายได้รวม:** ฿{rev:,.2f} | **รายจ่ายรวม:** ฿{exp:,.2f}"
        )
        col2.warning(f"📈 **กำไรสุทธิคงเหลือ:** ฿{net:,.2f}")
    except Exception as e:
        st.error(f"Error in Financial Health Check: {e}")


def render_ai_cfo_advisor():
    try:
        apply_enterprise_theme()
        st.title("💬 AI CFO Virtual Advisor (ผู้ช่วยบริหารการเงิน 24 ชม.)")
        q = st.text_input(
            "สอบถามคำแนะนำด้านภาษี การเงิน หรือวางแผนงบประมาณ:"
        )
        if q:
            q_lower = q.lower()
            if "ภาษี" in q_lower or "vat" in q_lower:
                reply = (
                    "สำหรับภาษีมูลค่าเพิ่ม (VAT 7%) ควรเตรียมยื่นแบบ ภ.พ. 30"
                    " ภายในวันที่ 15 ของเดือนถัดไปครับ"
                )
            elif "งบ" in q_lower or "กำไร" in q_lower:
                reply = (
                    "การวางแผนงบประมาณแนะนำให้รักษาสัดส่วนค่าใช้จ่ายไม่เกิน 70%"
                    " ของรายรับรวมเพื่อสร้างกระแสเงินสดสำรอง"
                )
            else:
                reply = (
                    f"คำแนะนำสำหรับคำถาม '{q}':"
                    " ควรตรวจสอบสถานะกระแสเงินสดและสัดส่วนหนี้สินอย่างน้อยสัปดาห์ละ"
                    " 1 ครั้งครับ"
                )
            st.markdown(f"**🤖 AI CFO ตอบ:** {reply}")
    except Exception as e:
        st.error(f"Error in AI CFO Advisor: {e}")


def render_import_export_module():
    try:
        apply_enterprise_theme()
        st.title(
            "📈 ศูนย์รายงานการเงิน Multi-Tab Excel & CSV Export"
        )
        user = (
            st.session_state.user_info.get("username", "user")
            if st.session_state.user_info
            else "user"
        )

        conn = get_connection()
        tx_df = pd.read_sql_query(
            "SELECT * FROM transactions WHERE user_id = ?", conn, params=(user,)
        )
        doc_df = pd.read_sql_query(
            "SELECT * FROM documents WHERE user_id = ?", conn, params=(user,)
        )
        client_df = pd.read_sql_query(
            "SELECT * FROM clients WHERE user_id = ?", conn, params=(user,)
        )
        conn.close()

        col1, col2 = st.columns(2)
        if not tx_df.empty:
            csv_data = tx_df.to_csv(index=False).encode("utf-8-sig")
            col1.download_button(
                "📥 ดาวน์โหลดรายงานธุรกรรม (.CSV)",
                data=csv_data,
                file_name=f"Transactions_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
            )

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            (
                tx_df
                if not tx_df.empty
                else pd.DataFrame([{"info": "ไม่มีข้อมูล"}])
            ).to_excel(writer, sheet_name="Transactions", index=False)
            (
                doc_df
                if not doc_df.empty
                else pd.DataFrame([{"info": "ไม่มีข้อมูล"}])
            ).to_excel(writer, sheet_name="Documents", index=False)
            (
                client_df
                if not client_df.empty
                else pd.DataFrame([{"info": "ไม่มีข้อมูล"}])
            ).to_excel(writer, sheet_name="Clients", index=False)
        excel_data = output.getvalue()

        col2.download_button(
            label="📊 ดาวน์โหลดรายงานครบถ้วน Multi-Tab (.XLSX)",
            data=excel_data,
            file_name=f"TaxMate_Full_Report_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime=(
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            ),
            type="primary",
        )
    except Exception as e:
        st.error(f"Error in Import/Export Module: {e}")


def render_hr_payroll():
    try:
        apply_enterprise_theme()
        st.title("👥 จัดการเงินเดือนและประกันสังคม (HR & Payroll)")
        user = (
            st.session_state.user_info.get("username", "user")
            if st.session_state.user_info
            else "user"
        )

        with st.expander("➕ เพิ่มข้อมูลพนักงานใหม่", expanded=False):
            with st.form("add_emp_form"):
                col1, col2 = st.columns(2)
                e_id = col1.text_input("รหัสพนักงาน:", value="EMP-001")
                e_name = col2.text_input("ชื่อ-นามสกุล พนักงาน:")
                col3, col4 = st.columns(2)
                e_pos = col3.text_input(
                    "ตำแหน่ง:", value="Accounting Manager"
                )
                e_sal = col4.number_input(
                    "เงินเดือนฐาน (บาท):", min_value=0.0, value=35000.0
                )

                if st.form_submit_button("💾 บันทึกข้อมูลพนักงาน"):
                    conn = get_connection()
                    c = conn.cursor()
                    c.execute(
                        "INSERT INTO employees (user_id, emp_id, name, position, base_salary) VALUES (?, ?, ?, ?, ?)",
                        (user, e_id, e_name, e_pos, e_sal),
                    )
                    conn.commit()
                    conn.close()
                    st.success("เพิ่มข้อมูลพนักงานสำเร็จ!")
                    st.rerun()

        conn = get_connection()
        emp_df = pd.read_sql_query(
            "SELECT id, emp_id, name, position, base_salary FROM employees WHERE user_id = ?",
            conn,
            params=(user,),
        )
        conn.close()
        safe_dataframe_display(
            emp_df, ["id", "emp_id", "name", "position", "base_salary"]
        )

        # 📄 พิมพ์สลิปเงินเดือนพนักงาน PDF
        if not emp_df.empty:
            st.divider()
            st.subheader("📄 พิมพ์สลิปเงินเดือนพนักงาน (Payslip PDF)")
            selected_emp_id = st.selectbox(
                "เลือกพนักงานที่ต้องการพิมพ์สลิปเงินเดือน:",
                emp_df["id"].tolist(),
                format_func=lambda x: (
                    f"ID: {x} | {emp_df[emp_df['id']==x]['emp_id'].values[0]} -"
                    f" {emp_df[emp_df['id']==x]['name'].values[0]}"
                ),
            )
            emp_row = emp_df[emp_df["id"] == selected_emp_id].iloc[0].to_dict()
            payslip_bytes = generate_payslip_pdf(emp_row)

            st.download_button(
                label=f"📥 ดาวน์โหลดสลิปเงินเดือน PDF ({emp_row['name']})",
                data=payslip_bytes,
                file_name=f"Payslip_{emp_row['emp_id']}.pdf",
                mime="application/pdf",
                type="primary",
            )

        if not emp_df.empty:
            with st.expander("🗑️ จัดการลบข้อมูล (Delete Options)", expanded=False):
                col_del1, col_del2 = st.columns(2)
                with col_del1:
                    st.markdown("##### 🗑️ ลบเฉพาะรายการ")
                    del_id = st.selectbox(
                        "เลือก ID พนักงานที่ต้องการลบ:",
                        emp_df["id"].tolist(),
                        key="del_emp_id",
                    )
                    if st.button("🔴 ลบพนักงานคนนี้", key="btn_del_emp_single"):
                        conn = get_connection()
                        c = conn.cursor()
                        c.execute(
                            "DELETE FROM employees WHERE id = ? AND user_id = ?",
                            (del_id, user),
                        )
                        conn.commit()
                        conn.close()
                        log_audit(
                            user, "DELETE_EMP", f"ลบข้อมูลพนักงาน ID: {del_id}"
                        )
                        st.success(f"ลบพนักงาน ID {del_id} เรียบร้อยแล้ว!")
                        st.rerun()

                with col_del2:
                    st.markdown("##### ⚠️ ลบข้อมูลทั้งหมด")
                    chk_confirm = st.checkbox(
                        "ยืนยันว่าต้องการลบข้อมูลพนักงานทั้งหมด",
                        key="chk_del_emp_all",
                    )
                    if st.button(
                        "💥 ลบข้อมูลพนักงานทั้งหมด",
                        type="primary",
                        key="btn_del_emp_all",
                    ):
                        if chk_confirm:
                            conn = get_connection()
                            c = conn.cursor()
                            c.execute(
                                "DELETE FROM employees WHERE user_id = ?",
                                (user,),
                            )
                            conn.commit()
                            conn.close()
                            log_audit(
                                user,
                                "DELETE_ALL_EMPS",
                                "ลบข้อมูลพนักงานทั้งหมด",
                            )
                            st.success("ลบข้อมูลพนักงานทั้งหมดเรียบร้อยแล้ว!")
                            st.rerun()
                        else:
                            st.warning(
                                "⚠️ กรุณาติ๊กถูกที่กล่องยืนยันก่อนกดลบทั้งหมด"
                            )

    except Exception as e:
        st.error(f"Error in HR Payroll Module: {e}")


def render_assets():
    try:
        apply_enterprise_theme()
        st.title(
            "💻 ทะเบียนสินทรัพย์และคำนวณค่าเสื่อมราคา (Fixed Assets)"
        )
        user = (
            st.session_state.user_info.get("username", "user")
            if st.session_state.user_info
            else "user"
        )

        with st.expander("➕ เพิ่มสินทรัพย์ใหม่", expanded=False):
            with st.form("add_asset_form"):
                col1, col2 = st.columns(2)
                a_code = col1.text_input("รหัสสินทรัพย์:", value="AST-001")
                a_name = col2.text_input("ชื่อสินทรัพย์:")

                c1, c2, c3 = st.columns(3)
                p_date = c1.date_input("วันที่ซื้อ:", datetime.now())
                cost = c2.number_input(
                    "มูลค่าทุนซื้อ (บาท):", min_value=0.0, value=50000.0
                )
                useful_life = c3.number_input(
                    "อายุการใช้งาน (ปี):", min_value=1, value=5
                )

                c4, c5 = st.columns(2)
                scrap_val = c4.number_input(
                    "ราคาซาก (บาท):", min_value=0.0, value=1.0
                )
                deprec_year = (
                    (cost - scrap_val) / useful_life if useful_life > 0 else 0
                )
                c5.text_input(
                    "ค่าเสื่อมราคาต่อปี (ประมาณการ):",
                    value=f"฿{deprec_year:,.2f}",
                    disabled=True,
                )

                if st.form_submit_button("💾 บันทึกสินทรัพย์"):
                    conn = get_connection()
                    c = conn.cursor()
                    c.execute(
                        """INSERT INTO assets (user_id, asset_code, asset_name, purchase_date, cost, useful_life, scrap_value, annual_depreciation) 
                                     VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                        (
                            user,
                            a_code,
                            a_name,
                            p_date.strftime("%Y-%m-%d"),
                            cost,
                            useful_life,
                            scrap_val,
                            deprec_year,
                        ),
                    )
                    conn.commit()
                    conn.close()
                    st.success("บันทึกสินทรัพย์สำเร็จ!")
                    st.rerun()

        conn = get_connection()
        assets_df = pd.read_sql_query(
            "SELECT id, asset_code, asset_name, purchase_date, cost, useful_life, scrap_value, annual_depreciation FROM assets WHERE user_id = ?",
            conn,
            params=(user,),
        )
        conn.close()
        safe_dataframe_display(
            assets_df,
            [
                "id",
                "asset_code",
                "asset_name",
                "purchase_date",
                "cost",
                "useful_life",
                "scrap_value",
                "annual_depreciation",
            ],
        )

        if not assets_df.empty:
            with st.expander("🗑️ จัดการลบข้อมูล (Delete Options)", expanded=False):
                col_del1, col_del2 = st.columns(2)
                with col_del1:
                    st.markdown("##### 🗑️ ลบเฉพาะรายการ")
                    del_id = st.selectbox(
                        "เลือก ID สินทรัพย์ที่ต้องการลบ:",
                        assets_df["id"].tolist(),
                        key="del_asset_id",
                    )
                    if st.button("🔴 ลบสินทรัพย์ชิ้นนี้", key="btn_del_asset_single"):
                        conn = get_connection()
                        c = conn.cursor()
                        c.execute(
                            "DELETE FROM assets WHERE id = ? AND user_id = ?",
                            (del_id, user),
                        )
                        conn.commit()
                        conn.close()
                        log_audit(
                            user, "DELETE_ASSET", f"ลบสินทรัพย์ ID: {del_id}"
                        )
                        st.success(f"ลบสินทรัพย์ ID {del_id} เรียบร้อยแล้ว!")
                        st.rerun()

                with col_del2:
                    st.markdown("##### ⚠️ ลบข้อมูลทั้งหมด")
                    chk_confirm = st.checkbox(
                        "ยืนยันว่าต้องการลบทรัพย์สินทั้งหมด",
                        key="chk_del_asset_all",
                    )
                    if st.button(
                        "💥 ลบทรัพย์สินทั้งหมด",
                        type="primary",
                        key="btn_del_asset_all",
                    ):
                        if chk_confirm:
                            conn = get_connection()
                            c = conn.cursor()
                            c.execute(
                                "DELETE FROM assets WHERE user_id = ?", (user,)
                            )
                            conn.commit()
                            conn.close()
                            log_audit(
                                user,
                                "DELETE_ALL_ASSETS",
                                "ลบข้อมูลสินทรัพย์ทั้งหมด",
                            )
                            st.success("ลบข้อมูลสินทรัพย์ทั้งหมดเรียบร้อยแล้ว!")
                            st.rerun()
                        else:
                            st.warning(
                                "⚠️ กรุณาติ๊กถูกที่กล่องยืนยันก่อนกดลบทั้งหมด"
                            )

    except Exception as e:
        st.error(f"Error in Assets Module: {e}")


# ==========================================
# 🛡️ 3. Admin Management Dashboard
# ==========================================
def render_admin_dashboard():
    try:
        apply_enterprise_theme()
        st.title("🛡️ [Admin] ศูนย์ควบคุมและบริหารจัดการระบบ")
        current_admin = (
            st.session_state.user_info.get("username", "admin")
            if st.session_state.user_info
            else "admin"
        )

        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📢 ประกาศข่าวระบบ",
            "📜 Audit Logs",
            "👥 จัดการผู้ใช้งาน & สิทธิ์",
            "💾 สำรอง & กู้คืน DB",
            "🖼️ จัดการหน้าปกระบบ",
        ])

        with tab1:
            st.subheader("สร้างประกาศข่าวสารระบบ (System Broadcast)")
            with st.form("broadcast_form"):
                title = st.text_input("หัวข้อประกาศ:")
                msg = st.text_area("เนื้อหาประกาศ:")
                priority = st.selectbox("ระดับความสำคัญ:", [
                    "ปกติ (Normal)",
                    "สำคัญ (High)",
                    "ด่วนที่สุด (Urgent)",
                ])
                if st.form_submit_button("📢 ส่งประกาศทันที"):
                    conn = get_connection()
                    c = conn.cursor()
                    c.execute(
                        "INSERT INTO announcements (title, message, priority, created_at) VALUES (?, ?, ?, ?)",
                        (
                            title,
                            msg,
                            priority,
                            datetime.now().strftime("%Y-%m-%d %H:%M"),
                        ),
                    )
                    conn.commit()
                    conn.close()
                    st.success("ส่งประกาศข่าวสารเรียบร้อยแล้ว!")
                    st.rerun()

            st.divider()
            st.subheader("📋 ประกาศข่าวทั้งหมดในระบบ")
            conn = get_connection()
            ann_df = pd.read_sql_query(
                "SELECT id, title, message, priority, created_at FROM announcements ORDER BY id DESC",
                conn,
            )
            conn.close()
            safe_dataframe_display(
                ann_df, ["id", "title", "message", "priority", "created_at"]
            )

            if not ann_df.empty:
                with st.expander("🗑️ จัดการลบประกาศ (Delete Options)", expanded=False):
                    col_del1, col_del2 = st.columns(2)
                    with col_del1:
                        del_id = st.selectbox(
                            "เลือก ID ประกาศที่ต้องการลบ:",
                            ann_df["id"].tolist(),
                            key="del_ann_id",
                        )
                        if st.button(
                            "🔴 ลบประกาศนี้", key="btn_del_ann_single"
                        ):
                            conn = get_connection()
                            c = conn.cursor()
                            c.execute(
                                "DELETE FROM announcements WHERE id = ?",
                                (del_id,),
                            )
                            conn.commit()
                            conn.close()
                            log_audit(
                                current_admin,
                                "DELETE_ANNOUNCEMENT",
                                f"ลบประกาศ ID: {del_id}",
                            )
                            st.success(
                                f"ลบประกาศ ID {del_id} เรียบร้อยแล้ว!"
                            )
                            st.rerun()

                    with col_del2:
                        chk_confirm = st.checkbox(
                            "ยืนยันว่าต้องการลบประกาศข่าวสารทั้งหมด",
                            key="chk_del_ann_all",
                        )
                        if st.button(
                            "💥 ลบประกาศทั้งหมด",
                            type="primary",
                            key="btn_del_ann_all",
                        ):
                            if chk_confirm:
                                conn = get_connection()
                                c = conn.cursor()
                                c.execute("DELETE FROM announcements")
                                conn.commit()
                                conn.close()
                                log_audit(
                                    current_admin,
                                    "DELETE_ALL_ANNOUNCEMENTS",
                                    "ลบประกาศข่าวสารทั้งหมด",
                                )
                                st.success(
                                    "ลบประกาศข่าวสารทั้งหมดเรียบร้อยแล้ว!"
                                )
                                st.rerun()
                            else:
                                st.warning(
                                    "⚠️"
                                    " กรุณาติ๊กถูกที่กล่องยืนยันก่อนกดลบทั้งหมด"
                                )

        with tab2:
            st.subheader("ประวัติการใช้งานและ Audit Logs")
            logs_df = get_audit_logs()
            safe_dataframe_display(
                logs_df, ["id", "username", "action", "details", "timestamp"]
            )

            if not logs_df.empty:
                with st.expander(
                    "🗑️ จัดการลบ Audit Logs (Delete Options)", expanded=False
                ):
                    col_del1, col_del2 = st.columns(2)
                    with col_del1:
                        del_id = st.selectbox(
                            "เลือก ID บันทึกที่ต้องการลบ:",
                            logs_df["id"].tolist(),
                            key="del_audit_id",
                        )
                        if st.button("🔴 ลบบันทึกนี้", key="btn_del_audit_single"):
                            conn = get_connection()
                            c = conn.cursor()
                            c.execute(
                                "DELETE FROM audit_logs WHERE id = ?", (del_id,)
                            )
                            conn.commit()
                            conn.close()
                            st.success(f"ลบบันทึก ID {del_id} เรียบร้อยแล้ว!")
                            st.rerun()

                    with col_del2:
                        chk_confirm = st.checkbox(
                            "ยืนยันว่าต้องการลบประวัติการใช้งานทั้งหมด",
                            key="chk_del_audit_all",
                        )
                        if st.button(
                            "💥 ลบประวัติ Audit Log ทั้งหมด",
                            type="primary",
                            key="btn_del_audit_all",
                        ):
                            if chk_confirm:
                                conn = get_connection()
                                c = conn.cursor()
                                c.execute("DELETE FROM audit_logs")
                                conn.commit()
                                conn.close()
                                st.success(
                                    "ลบประวัติการใช้งานทั้งหมดเรียบร้อยแล้ว!"
                                )
                                st.rerun()
                            else:
                                st.warning(
                                    "⚠️"
                                    " กรุณาติ๊กถูกที่กล่องยืนยันก่อนกดลบทั้งหมด"
                                )

        with tab3:
            st.subheader("รายชื่อผู้ใช้งานทั้งหมด")
            conn = get_connection()
            users_df = pd.read_sql_query(
                "SELECT id, username, company, role, allowed_modules, created_at FROM users",
                conn,
            )
            conn.close()
            safe_dataframe_display(
                users_df,
                [
                    "id",
                    "username",
                    "company",
                    "role",
                    "allowed_modules",
                    "created_at",
                ],
            )

            st.divider()
            st.subheader("⚙️ กำหนดสิทธิ์การเข้าถึงเมนูย่อยของพนักงาน")
            if not users_df.empty:
                selected_u = st.selectbox(
                    "เลือกผู้ใช้ที่ต้องการแก้ไขสิทธิ์:",
                    users_df["username"].tolist(),
                )
                all_possible_modules = [
                    "📊 ภาพรวม & เพิ่มรายการ",
                    "📇 สมุดรายนามคู่ค้า/ลูกค้า",
                    "📑 ออกเอกสาร & ตัดรับชำระ",
                    "📦 บริหารสต็อกสินค้า",
                    "🎯 วางแผนงบประมาณ",
                    "🇹🇭 ระบบภาษีไทย (VAT/WHT)",
                    "🏦 กระทบยอดธนาคาร",
                    "💳 เบิกเงินสดย่อย",
                    "🤖 AI สแกนสลิป (OCR)",
                    "🧠 AI วิเคราะห์สุขภาพการเงิน",
                    "💬 AI CFO Virtual Advisor",
                    "📈 รายงาน Multi-Tab Export",
                    "👥 จัดการเงินเดือน (HR)",
                    "💻 ทะเบียนสินทรัพย์ (Assets)",
                ]

                chosen_mods = st.multiselect(
                    f"เลือกเมนูที่อนุญาตให้ '{selected_u}' เข้าถึง:",
                    all_possible_modules,
                    default=all_possible_modules,
                )

                if st.button("💾 บันทึกสิทธิ์การใช้งาน"):
                    conn = get_connection()
                    c = conn.cursor()
                    mod_str = json.dumps(chosen_mods)
                    c.execute(
                        "UPDATE users SET allowed_modules = ? WHERE username = ?",
                        (mod_str, selected_u),
                    )
                    conn.commit()
                    conn.close()
                    log_audit(
                        current_admin,
                        "UPDATE_PERMISSIONS",
                        f"ปรับสิทธิ์ {selected_u}",
                    )
                    st.success(f"อัปเดตสิทธิ์สำหรับ '{selected_u}' เรียบร้อยแล้ว!")
                    st.rerun()

            if not users_df.empty:
                with st.expander(
                    "🗑️ จัดการลบผู้ใช้งาน (Delete User Options)",
                    expanded=False,
                ):
                    col_del1, col_del2 = st.columns(2)
                    with col_del1:
                        deletable_users = users_df[
                            users_df["username"] != current_admin
                        ]
                        if not deletable_users.empty:
                            del_user_id = st.selectbox(
                                "เลือก ID ผู้ใช้ที่ต้องการลบ:",
                                deletable_users["id"].tolist(),
                                key="del_user_id",
                            )
                            if st.button(
                                "🔴 ลบบัญชีผู้ใช้คนนี้",
                                key="btn_del_user_single",
                            ):
                                conn = get_connection()
                                c = conn.cursor()
                                c.execute(
                                    "DELETE FROM users WHERE id = ?",
                                    (del_user_id,),
                                )
                                conn.commit()
                                conn.close()
                                log_audit(
                                    current_admin,
                                    "DELETE_USER",
                                    f"ลบผู้ใช้ ID: {del_user_id}",
                                )
                                st.success(
                                    f"ลบผู้ใช้ ID {del_user_id}"
                                    " เรียบร้อยแล้ว!"
                                )
                                st.rerun()
                        else:
                            st.info("ไม่มีผู้ใช้งานอื่นให้ลบ")

                    with col_del2:
                        chk_confirm = st.checkbox(
                            "ยืนยันลบบัญชีผู้ใช้ทั่วไป (Role: user) ทั้งหมด",
                            key="chk_del_user_all",
                        )
                        if st.button(
                            "💥 ลบบัญชีผู้ใช้ทั่วไปทั้งหมด",
                            type="primary",
                            key="btn_del_user_all",
                        ):
                            if chk_confirm:
                                conn = get_connection()
                                c = conn.cursor()
                                c.execute(
                                    "DELETE FROM users WHERE role = 'user'"
                                )
                                conn.commit()
                                conn.close()
                                log_audit(
                                    current_admin,
                                    "DELETE_ALL_USERS",
                                    "ลบบัญชีผู้ใช้งานทั่วไปทั้งหมด",
                                )
                                st.success(
                                    "ลบบัญชีผู้ใช้งานทั่วไปทั้งหมดเรียบร้อยแล้ว!"
                                )
                                st.rerun()
                            else:
                                st.warning(
                                    "⚠️"
                                    " กรุณาติ๊กถูกที่กล่องยืนยันก่อนกดลบทั้งหมด"
                                )

        with tab4:
            st.subheader("💾 สำรองและกู้คืนฐานข้อมูล (Database Backup)")
            col_b1, col_b2 = st.columns(2)

            with col_b1:
                st.markdown("##### 📥 ดาวน์โหลดไฟล์สำรองข้อมูล")
                db_bytes = get_db_bytes()
                st.download_button(
                    label="📥 ดาวน์โหลดไฟล์สำรอง taxmate.db",
                    data=db_bytes,
                    file_name=f"taxmate_backup_{datetime.now().strftime('%Y%m%d_%H%M')}.db",
                    mime="application/x-sqlite3",
                    type="primary",
                )

            with col_b2:
                st.markdown("##### 📤 กู้คืนฐานข้อมูลจากไฟล์สำรอง")
                uploaded_db = st.file_uploader(
                    "อัปโหลดไฟล์ .db สำรอง:", type=["db", "sqlite3"]
                )
                chk_confirm_restore = st.checkbox("ยืนยันการเขียนทับฐานข้อมูลเดิม")
                if (
                    st.button("💥 เริ่มกู้คืนฐานข้อมูล", type="primary")
                    and uploaded_db
                ):
                    if chk_confirm_restore:
                        res, msg = restore_db_from_bytes(uploaded_db.read())
                        if res:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)
                    else:
                        st.warning("⚠️ กรุณาติ๊กยืนยันความเสี่ยงก่อนกู้คืน")

        with tab5:
            st.subheader("🖼️ จัดการข้อความและดีไซน์หน้าปกหลัก (Landing Page Cover)")
            curr_cfg = get_cover_settings()

            with st.form("edit_cover_form"):
                new_badge = st.text_input(
                    "ข้อความป้ายกำกับ (Badge Text):", value=curr_cfg.get("badge", "")
                )
                new_title = st.text_input(
                    "ชื่อหลักระบบ (Main Title):", value=curr_cfg.get("title", "")
                )
                new_subtitle = st.text_input(
                    "สโลแกนระบบ (Subtitle):", value=curr_cfg.get("subtitle", "")
                )
                new_desc = st.text_area(
                    "คำอธิบายรายละเอียด (Description):",
                    value=curr_cfg.get("description", ""),
                )
                new_color = st.color_picker(
                    "สีเน้นองค์กร (Accent Color):",
                    value=curr_cfg.get("theme_color", "#2563EB"),
                )

                if st.form_submit_button("💾 บันทึกการเปลี่ยนแปลงหน้าปก", type="primary"):
                    updated_cfg = {
                        "badge": new_badge,
                        "title": new_title,
                        "subtitle": new_subtitle,
                        "description": new_desc,
                        "theme_color": new_color,
                    }
                    save_cover_settings(updated_cfg)
                    st.success("อัปเดตข้อมูลหน้าปกเรียบร้อยแล้ว!")
                    st.rerun()

    except Exception as e:
        st.error(f"Error in Admin Dashboard: {e}")
import json
from database import init_db
import streamlit as st
import views

st.set_page_config(
    page_title="TaxMate Enterprise ERP Suite",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 1. Initialize DB
init_db()

# 2. Session States
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_info" not in st.session_state:
    st.session_state.user_info = None
if "current_page" not in st.session_state:
    st.session_state.current_page = "🏠 หน้าแรก (Landing Page)"
if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = "light"

views.apply_enterprise_theme()

st.sidebar.title("🏛️ TaxMate ERP")

# API Key Setting for Real AI Integration
with st.sidebar.expander("🔑 ตั้งค่า AI API Key", expanded=False):
    api_key_input = st.text_input(
        "Gemini API Key:",
        type="password",
        value=st.session_state.get("gemini_api_key", ""),
    )
    if api_key_input:
        st.session_state.gemini_api_key = api_key_input

if st.session_state.authenticated:
    user = st.session_state.user_info.get("username", "User")
    role = st.session_state.user_info.get("role", "user")
    company = st.session_state.user_info.get("company", "Organization")
    allowed_mods_raw = st.session_state.user_info.get("allowed_modules", "all")

    st.sidebar.success(f"👤 **{user}** ({role.upper()})\n🏢 {company}")

    all_user_pages = [
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

    if role == "admin":
        pages = ["📊 [Admin] Dashboard ผู้บริหาร"] + all_user_pages
    else:
        if allowed_mods_raw == "all":
            pages = all_user_pages
        else:
            try:
                allowed_list = json.loads(allowed_mods_raw)
                pages = [p for p in all_user_pages if p in allowed_list]
                if not pages:
                    pages = all_user_pages
            except Exception:
                pages = all_user_pages

    if st.session_state.current_page not in pages:
        st.session_state.current_page = pages[0]

    selected_page = st.sidebar.radio(
        "📍 เมนูการใช้งาน:",
        pages,
        index=pages.index(st.session_state.current_page),
    )
    st.session_state.current_page = selected_page

    if st.sidebar.button(
        "🚪 ออกจากระบบ (Logout)", type="secondary", use_container_width=True
    ):
        st.session_state.authenticated = False
        st.session_state.user_info = None
        st.session_state.current_page = "🏠 หน้าแรก (Landing Page)"
        st.rerun()

else:
    pages = ["🏠 หน้าแรก (Landing Page)", "🔑 เข้าสู่ระบบ / ลงทะเบียน"]
    if st.session_state.current_page not in pages:
        st.session_state.current_page = pages[0]
    selected_page = st.sidebar.radio(
        "📍 เมนูเริ่มต้น:",
        pages,
        index=pages.index(st.session_state.current_page),
    )
    st.session_state.current_page = selected_page

# Page Router
page = st.session_state.current_page

if page == "🏠 หน้าแรก (Landing Page)":
    views.render_landing_page()
elif page == "🔑 เข้าสู่ระบบ / ลงทะเบียน":
    views.render_auth_page()
elif page == "📊 [Admin] Dashboard ผู้บริหาร":
    views.render_admin_dashboard()
elif page == "📊 ภาพรวม & เพิ่มรายการ":
    views.render_financial_overview()
elif page == "📇 สมุดรายนามคู่ค้า/ลูกค้า":
    views.render_client_directory()
elif page == "📑 ออกเอกสาร & ตัดรับชำระ":
    views.render_documents_module()
elif page == "📦 บริหารสต็อกสินค้า":
    views.render_inventory_module()
elif page == "🎯 วางแผนงบประมาณ":
    views.render_budgeting_module()
elif page == "🇹🇭 ระบบภาษีไทย (VAT/WHT)":
    views.render_thai_tax_module()
elif page == "🏦 กระทบยอดธนาคาร":
    views.render_bank_reconciliation()
elif page == "💳 เบิกเงินสดย่อย":
    views.render_expense_claims_module()
elif page == "🤖 AI สแกนสลิป (OCR)":
    views.render_slip_ocr_module()
elif page == "🧠 AI วิเคราะห์สุขภาพการเงิน":
    views.render_ai_financial_health_module()
elif page == "💬 AI CFO Virtual Advisor":
    views.render_ai_cfo_advisor()
elif page == "📈 รายงาน Multi-Tab Export":
    views.render_import_export_module()
elif page == "👥 จัดการเงินเดือน (HR)":
    views.render_hr_payroll()
elif page == "💻 ทะเบียนสินทรัพย์ (Assets)":
    views.render_assets()
else:
    views.render_landing_page()
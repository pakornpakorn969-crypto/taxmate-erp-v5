import streamlit as st
from database import init_db
from auth import create_default_demo_accounts
import views

st.set_page_config(page_title="TaxMate Enterprise ERP", page_icon="🏦", layout="wide")

init_db()
create_default_demo_accounts()

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_info" not in st.session_state:
    st.session_state.user_info = None
if "current_page" not in st.session_state:
    st.session_state.current_page = "🏠 หน้าแรก (Landing Page)"

st.sidebar.title("🏦 TaxMate ERP Suite")

if st.session_state.authenticated:
    is_admin = st.session_state.user_info.get('role') == 'admin'
    
    st.sidebar.success(f"{'🛡️ SUPER ADMIN' if is_admin else '👤 USER'}\n\n**{st.session_state.user_info['company_name']}**")
    st.sidebar.divider()

    if is_admin:
        nav_options = [
            "📊 [Admin] Dashboard ผู้บริหาร",
            "🔒 [Admin] ล็อกงบประจำเดือน (Period Closing)",
            "✅ [Admin] ศูนย์อนุมัติรายการ (Maker-Checker)",
            "🔍 [Admin] ตรวจสอบธุรกรรมทั้งหมด",
            "⚙️ [Admin] ตั้งค่าองค์กร (Company Settings)",
            "👥 [Admin] จัดการผู้ใช้งานระบบ",
            "📢 [Admin] ส่งประกาศข่าวสาร",
            "🛠️ [Admin] สำรองฐานข้อมูล"
        ]
    else:
        nav_options = [
            "📊 ภาพรวม & เพิ่มรายการ",
            "📇 สมุดรายนามคู่ค้า/ลูกค้า (Directory)",
            "📑 ออกเอกสาร & ตัดรับชำระเงิน",
            "🇹🇭 ระบบภาษีไทย (VAT & 50 ทวิ)",
            "🤖 AI สแกนสลิป/ใบเสร็จ",
            "📤 นำเข้า/ส่งออกข้อมูล (CSV)",
            "👥 จัดการเงินเดือน (HR & Payroll)",
            "💻 ทะเบียนสินทรัพย์ (Assets)",
            "🛡️ โปรไฟล์ & ประวัติการใช้งาน"
        ]

    if st.session_state.current_page not in nav_options:
        st.session_state.current_page = nav_options[0]

    selected_page = st.sidebar.radio("📍 เมนูนำทาง:", nav_options, index=nav_options.index(st.session_state.current_page))
    st.session_state.current_page = selected_page
    
    st.sidebar.divider()
    if st.sidebar.button("🚪 ออกจากระบบ (Logout)", type="primary", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.user_info = None
        st.session_state.current_page = "🏠 หน้าแรก (Landing Page)"
        st.rerun()

    # Routing Admin
    if selected_page == "📊 [Admin] Dashboard ผู้บริหาร": 
        views.render_admin_overview()
    elif selected_page == "🔒 [Admin] ล็อกงบประจำเดือน (Period Closing)":
        views.render_admin_period_lock()
    elif selected_page == "✅ [Admin] ศูนย์อนุมัติรายการ (Maker-Checker)": 
        views.render_admin_approval_center()
    elif selected_page == "🔍 [Admin] ตรวจสอบธุรกรรมทั้งหมด": 
        views.render_admin_audit()
    elif selected_page == "⚙️ [Admin] ตั้งค่าองค์กร (Company Settings)": 
        views.render_admin_settings()
    elif selected_page == "👥 [Admin] จัดการผู้ใช้งานระบบ": 
        views.render_admin_users()
    elif selected_page == "📢 [Admin] ส่งประกาศข่าวสาร": 
        views.render_admin_broadcast()
    elif selected_page == "🛠️ [Admin] สำรองฐานข้อมูล": 
        views.render_admin_db_tools()
        
    # Routing User
    elif selected_page == "📊 ภาพรวม & เพิ่มรายการ": 
        views.render_financial_overview()
    elif selected_page == "📇 สมุดรายนามคู่ค้า/ลูกค้า (Directory)":
        views.render_client_directory()
    elif selected_page == "📑 ออกเอกสาร & ตัดรับชำระเงิน": 
        views.render_documents_module()
    elif selected_page == "🇹🇭 ระบบภาษีไทย (VAT & 50 ทวิ)": 
        views.render_thai_tax_module()
    elif selected_page == "🤖 AI สแกนสลิป/ใบเสร็จ": 
        views.render_slip_ocr_module()
    elif selected_page == "📤 นำเข้า/ส่งออกข้อมูล (CSV)": 
        views.render_import_export_module()
    elif selected_page == "👥 จัดการเงินเดือน (HR & Payroll)": 
        views.render_hr_payroll()
    elif selected_page == "💻 ทะเบียนสินทรัพย์ (Assets)": 
        views.render_assets()
    elif selected_page == "🛡️ โปรไฟล์ & ประวัติการใช้งาน": 
        views.render_security_audit_module()

else:
    guest_pages = ["🏠 หน้าแรก (Landing Page)", "🔑 เข้าสู่ระบบ / ลงทะเบียน"]
    if st.session_state.current_page not in guest_pages:
        st.session_state.current_page = guest_pages[0]
        
    selected_page = st.sidebar.radio("📍 เมนูเริ่มต้น:", guest_pages, index=guest_pages.index(st.session_state.current_page))
    st.session_state.current_page = selected_page

    if selected_page == "🏠 หน้าแรก (Landing Page)":
        views.render_landing_page()
    elif selected_page == "🔑 เข้าสู่ระบบ / ลงทะเบียน":
        views.render_auth_page()
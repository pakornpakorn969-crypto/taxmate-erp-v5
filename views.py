import streamlit as st
import pandas as pd
import os
from datetime import datetime
import random
from database import get_connection, log_audit, get_audit_logs, DB_NAME
from auth import authenticate_user, register_user, change_password, hash_password

UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

def display_active_broadcasts():
    try:
        conn = get_connection()
        ann_df = pd.read_sql_query("SELECT * FROM announcements ORDER BY id DESC LIMIT 1", conn)
        conn.close()
        if not ann_df.empty:
            latest = ann_df.iloc[0]
            p_type = latest['priority']
            msg_str = f"📢 **ประกาศจากระบบ [{latest['created_at']}]: {latest['title']}**\n\n{latest['message']}"
            if p_type == "ด่วนที่สุด (Urgent)":
                st.error(msg_str)
            elif p_type == "สำคัญ (High)":
                st.warning(msg_str)
            else:
                st.info(msg_str)
    except Exception:
        pass

def is_period_locked(date_str):
    try:
        ym = date_str[:7]
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT is_locked FROM period_locks WHERE year_month = ?", (ym,))
        row = c.fetchone()
        conn.close()
        return row[0] == 1 if row else False
    except Exception:
        return False

# ==========================================
# 🏠 1. Landing & Auth Page
# ==========================================
def render_landing_page():
    display_active_broadcasts()
    st.markdown("""
    <style>
        .hero-cover-3d {
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #2563eb 100%);
            border-radius: 24px; padding: 55px 35px; text-align: center; color: #ffffff;
            box-shadow: 0 20px 40px -15px rgba(15, 23, 42, 0.35); margin-bottom: 35px;
        }
        .hero-title-3d { font-size: 3.2rem; font-weight: 900; margin-bottom: 12px; }
        .card-3d {
            background: #ffffff; border-radius: 22px; padding: 25px; border: 1px solid #e2e8f0;
            box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.06); transition: all 0.3s;
        }
        .card-3d:hover { transform: translateY(-8px); box-shadow: 0 20px 30px -10px rgba(37, 99, 235, 0.2); }
    </style>
    <div class="hero-cover-3d">
        <div class="hero-title-3d">🔐 TaxMate Enterprise ERP</div>
        <p style="font-size: 1.2rem; color: #94a3b8;">ระบบบริหารการเงิน ภาษีไทย ออกเอกสาร และอนุมัติงบการเงินระดับองค์กร</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="card-3d"><h3>🇹🇭 ระบบภาษีไทย & 50 ทวิ</h3><p>รองรับ VAT 7%, ภ.พ. 30 และ หัก ณ ที่จ่าย 1%/3%/5%</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="card-3d"><h3>🔒 ล็อกงบประจำเดือน & Maker-Checker</h3><p>ป้องกันการแก้ไขบัญชีย้อนหลัง และระบบควบคุมเพดานเงินอนุมัติ</p></div>', unsafe_allow_html=True)

def render_auth_page():
    display_active_broadcasts()
    st.title("🔑 เข้าสู่ระบบ / ลงทะเบียนผู้ใช้")
    tab1, tab2 = st.tabs(["🔐 เข้าสู่ระบบ (Login)", "📝 ลงทะเบียน (Register)"])
    
    with tab1:
        with st.form("login_form"):
            username = st.text_input("ชื่อผู้ใช้ (Username):")
            password = st.text_input("รหัสผ่าน (Password):", type="password")
            if st.form_submit_button("เข้าสู่ระบบ"):
                success, result = authenticate_user(username, password)
                if success:
                    st.session_state.authenticated = True
                    st.session_state.user_info = result
                    st.session_state.current_page = "📊 ภาพรวม & เพิ่มรายการ" if result['role'] != 'admin' else "📊 [Admin] Dashboard ผู้บริหาร"
                    st.success("เข้าสู่ระบบสำเร็จ!")
                    st.rerun()
                else:
                    st.error(result)

    with tab2:
        with st.form("register_form"):
            reg_username = st.text_input("ชื่อผู้ใช้ใหม่:")
            reg_password = st.text_input("รหัสผ่าน:", type="password")
            reg_company = st.text_input("ชื่อบริษัท / ร้านค้า:")
            reg_role = st.selectbox("บทบาท:", ["user", "admin"])
            if st.form_submit_button("ลงทะเบียน"):
                if not reg_username or not reg_password or not reg_company:
                    st.error("กรุณากรอกข้อมูลให้ครบถ้วน")
                else:
                    success, msg = register_user(reg_username, reg_password, reg_company, reg_role)
                    if success: st.success(msg)
                    else: st.error(msg)

# ==========================================
# 📊 2. User Modules
# ==========================================
def render_financial_overview():
    display_active_broadcasts()
    st.title("📊 ภาพรวมการเงิน & เพิ่มรายการ (User)")
    user = st.session_state.user_info['username']

    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT approval_threshold FROM company_settings WHERE id = 1")
        threshold = c.fetchone()[0]
        conn.close()
    except: threshold = 50000.0

    with st.expander("➕ เพิ่มรายการธุรกรรมใหม่", expanded=False):
        with st.form("add_tx"):
            col1, col2 = st.columns(2)
            t_date = col1.date_input("วันที่ทำรายการ:", datetime.now())
            t_type = col2.selectbox("ประเภท:", ["Expense", "Income"])
            
            title = st.text_input("ชื่อรายการ / รายละเอียด:")
            col3, col4 = st.columns(2)
            amount = col3.number_input("จำนวนเงิน (บาท):", min_value=0.0, step=100.0)
            category = col4.selectbox("หมวดหมู่:", ["อุปกรณ์/ซอฟต์แวร์", "การตลาด/โฆษณา", "ค่าใช้จ่ายทั่วไป", "รายได้ค่าบริการ", "เดินทาง/ที่พัก"])
            
            uploaded_file = st.file_uploader("📎 แนบไฟล์สลิป / ใบเสร็จรับเงิน (Optional):", type=["png", "jpg", "jpeg", "pdf"])
            
            st.info(f"💡 รายการจ่ายเกิน ฿{threshold:,.2f} ต้องรออนุมัติจาก Admin")
            if st.form_submit_button("💾 บันทึก"):
                date_str = t_date.strftime("%Y-%m-%d")
                if is_period_locked(date_str):
                    st.error(f"🔒 ไม่สามารถเพิ่มรายการในเดือน {date_str[:7]} ได้เนื่องจาก Admin ได้ทำการ 'ล็อกงบการเงินประจำเดือน' แล้ว")
                elif not title or amount <= 0:
                    st.error("กรุณากรอกข้อมูลให้ถูกต้อง")
                else:
                    saved_filename = None
                    if uploaded_file is not None:
                        saved_filename = f"{user}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uploaded_file.name}"
                        with open(os.path.join(UPLOAD_DIR, saved_filename), "wb") as f:
                            f.write(uploaded_file.getbuffer())

                    app_status = 'Pending' if (t_type == 'Expense' and amount > threshold) else 'Approved'
                    conn = get_connection()
                    c = conn.cursor()
                    c.execute('''INSERT INTO transactions (user_id, date, type, title, amount, category, approval_status, attachment_file)
                                 VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', 
                              (user, date_str, t_type, title, amount, category, app_status, saved_filename))
                    conn.commit()
                    conn.close()
                    log_audit(user, "ADD_TX", f"เพิ่มรายการ {title} ยอด {amount}")
                    st.success("บันทึกรายการสำเร็จ!")
                    st.rerun()

    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM transactions WHERE user_id = ? ORDER BY id DESC", conn, params=(user,))
    conn.close()

    inc = df[(df['type'] == 'Income') & (df['approval_status'] == 'Approved')]['amount'].sum() if not df.empty else 0
    exp = df[(df['type'] == 'Expense') & (df['approval_status'] == 'Approved')]['amount'].sum() if not df.empty else 0
    
    c1, c2, c3 = st.columns(3)
    c1.metric("รายรับรวม (อนุมัติแล้ว)", f"฿{inc:,.2f}")
    c2.metric("รายจ่ายรวม (อนุมัติแล้ว)", f"฿{exp:,.2f}")
    c3.metric("คงเหลือสุทธิ", f"฿{(inc - exp):,.2f}")

    st.divider()
    st.subheader("📋 ประวัติรายการของคุณ")
    if not df.empty:
        st.dataframe(df[['date', 'type', 'title', 'amount', 'category', 'approval_status', 'attachment_file']], use_container_width=True)
    else: st.info("ยังไม่มีข้อมูลรายการธุรกรรม")

def render_client_directory():
    st.title("📇 สมุดรายนามคู่ค้า/ลูกค้า (Client Directory)")
    user = st.session_state.user_info['username']

    with st.expander("➕ เพิ่มข้อมูลคู่ค้า / ลูกค้าใหม่", expanded=False):
        with st.form("client_form"):
            col1, col2 = st.columns(2)
            c_name = col1.text_input("ชื่อบริษัท / ลูกค้า:")
            c_tax_id = col2.text_input("เลขประจำตัวผู้เสียภาษี (13 หลัก):")
            
            col3, col4 = st.columns(2)
            c_type = col3.selectbox("ประเภท:", ["Customer (ลูกค้า)", "Vendor (ผู้ขาย/คู่ค้า)"])
            c_phone = col4.text_input("เบอร์โทรศัพท์:")
            c_address = st.text_area("ที่อยู่ตามภ.พ. 20:")
            
            if st.form_submit_button("💾 บันทึกคู่ค้า"):
                if not c_name:
                    st.error("กรุณากรอกชื่อบริษัท/ลูกค้า")
                else:
                    conn = get_connection()
                    c = conn.cursor()
                    c.execute('''INSERT INTO clients (user_id, name, tax_id, client_type, address, phone, created_at)
                                 VALUES (?, ?, ?, ?, ?, ?, ?)''',
                              (user, c_name, c_tax_id, c_type.split()[0], c_address, c_phone, datetime.now().strftime("%Y-%m-%d")))
                    conn.commit()
                    conn.close()
                    log_audit(user, "ADD_CLIENT", f"เพิ่มคู่ค้า {c_name}")
                    st.success("บันทึกคู่ค้าสำเร็จ!")
                    st.rerun()

    conn = get_connection()
    clients_df = pd.read_sql_query("SELECT name, tax_id, client_type, phone, address FROM clients WHERE user_id = ?", conn, params=(user,))
    conn.close()

    if not clients_df.empty:
        st.dataframe(clients_df, use_container_width=True)
    else:
        st.info("ยังไม่มีรายชื่อคู่ค้าในระบบ")

def render_documents_module():
    st.title("📑 ออกเอกสารการเงิน & ติดตามหนี้")
    user = st.session_state.user_info['username']
    
    conn = get_connection()
    clients_df = pd.read_sql_query("SELECT name, tax_id FROM clients WHERE user_id = ?", conn, params=(user,))
    conn.close()
    
    client_list = clients_df['name'].tolist() if not clients_df.empty else ["ลูกค้าทั่วไป"]

    tab1, tab2 = st.tabs(["➕ ออกเอกสารใหม่", "📂 รายการเอกสาร & ตัดรับชำระเงิน"])

    with tab1:
        with st.form("doc_form"):
            col1, col2 = st.columns(2)
            doc_type = col1.selectbox("ประเภท:", ["ใบเสนอราคา", "ใบแจ้งหนี้", "ใบเสร็จรับเงิน/ใบกำกับภาษี"])
            doc_num = col2.text_input("เลขที่เอกสาร:", f"DOC-{datetime.now().strftime('%Y%m%d%H%M')}")
            
            selected_client = st.selectbox("เลือกลูกค้าจากสมุดรายนาม:", client_list)
            client_tax_id = ""
            if not clients_df.empty and selected_client in clients_df['name'].values:
                client_tax_id = clients_df[clients_df['name'] == selected_client]['tax_id'].values[0]

            subtotal = st.number_input("จำนวนเงินก่อน VAT (บาท):", min_value=0.0, value=10000.0)
            
            if st.form_submit_button("💾 บันทึกและสร้างเอกสาร"):
                conn = get_connection()
                c = conn.cursor()
                c.execute('''INSERT INTO documents (user_id, doc_type, doc_number, issue_date, client_name, client_tax_id, items_summary, subtotal, vat_amount, grand_total, payment_status, created_at)
                             VALUES (?, ?, ?, ?, ?, ?, 'ค่าบริการวิชาชีพและที่ปรึกษา', ?, ?, ?, 'Unpaid', ?)''', 
                          (user, doc_type, doc_num, datetime.now().strftime("%Y-%m-%d"), selected_client, client_tax_id, subtotal, subtotal*0.07, subtotal*1.07, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                conn.commit()
                conn.close()
                st.success("บันทึกเอกสารสำเร็จ!")
                st.rerun()

    with tab2:
        conn = get_connection()
        docs_df = pd.read_sql_query("SELECT * FROM documents WHERE user_id = ? ORDER BY id DESC", conn, params=(user,))
        conn.close()
        
        if not docs_df.empty:
            st.dataframe(docs_df[['doc_number', 'doc_type', 'issue_date', 'client_name', 'grand_total', 'payment_status']], use_container_width=True)
            
            st.divider()
            st.subheader("💰 ตัดรับชำระเงิน (Mark Invoice as Paid)")
            unpaid_docs = docs_df[docs_df['payment_status'] == 'Unpaid']
            if not unpaid_docs.empty:
                doc_options = {f"{row['doc_number']} | ลูกค้า: {row['client_name']} (฿{row['grand_total']:,.2f})": row['id'] for _, row in unpaid_docs.iterrows()}
                selected_doc = st.selectbox("เลือกเอกสารที่ได้รับชำระเงินแล้ว:", list(doc_options.keys()))
                target_id = doc_options[selected_doc]
                
                if st.button("✅ ยืนยันว่าชำระเงินแล้ว (Mark as Paid)", type="primary"):
                    conn = get_connection()
                    c = conn.cursor()
                    c.execute("UPDATE documents SET payment_status = 'Paid' WHERE id = ?", (target_id,))
                    conn.commit()
                    conn.close()
                    log_audit(user, "MARK_PAID", f"ตัดรับชำระเงินเอกสาร ID {target_id}")
                    st.success("ตัดรับชำระเงินเรียบร้อยแล้ว!")
                    st.rerun()
            else:
                st.success("🎉 เอกสารทั้งหมดได้รับการชำระเงินครบถ้วนแล้ว")

def render_thai_tax_module():
    st.title("🇹🇭 ระบบจัดการภาษีไทย (VAT & 50 ทวิ)")
    user = st.session_state.user_info['username']
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM transactions WHERE user_id = ? AND approval_status = 'Approved'", conn, params=(user,))
    conn.close()

    tab1, tab2 = st.tabs(["📑 ใบหัก ณ ที่จ่าย (50 ทวิ)", "📊 ภาษีมูลค่าเพิ่ม (VAT 7%)"])
    with tab1:
        wht_df = df[df['wht_amount'] > 0] if not df.empty and 'wht_amount' in df.columns else pd.DataFrame()
        st.metric("ภาษีหัก ณ ที่จ่าย สะสมรวม", f"฿{(wht_df['wht_amount'].sum() if not wht_df.empty else 0):,.2f}")
        if not wht_df.empty:
            st.dataframe(wht_df[['date', 'title', 'amount', 'wht_amount']], use_container_width=True)
    with tab2:
        if not df.empty and 'is_vat' in df.columns:
            df['vat_val'] = df['amount'] * 0.07 * df['is_vat']
            vat_sale = df[df['type'] == 'Income']['vat_val'].sum()
            vat_buy = df[df['type'] == 'Expense']['vat_val'].sum()
            st.metric("ภาษีที่ต้องชำระเพิ่มสุทธิ (ภ.พ.30)", f"฿{abs(vat_sale - vat_buy):,.2f}")

def render_slip_ocr_module():
    st.title("🤖 AI OCR สแกนสลิป/ใบเสร็จ")
    st.file_uploader("เลือกรูปภาพสลิป:", type=["jpg", "png", "jpeg"])
    st.info("จำลองสแกนข้อมูลเข้าสู่ระบบเรียบร้อยแล้ว")

def render_import_export_module():
    st.title("📤 นำเข้า/ส่งออกข้อมูล (CSV)")
    user = st.session_state.user_info['username']
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM transactions WHERE user_id = ?", conn, params=(user,))
    conn.close()
    if not df.empty:
        st.download_button("📥 ดาวน์โหลดไฟล์ CSV", df.to_csv(index=False).encode('utf-8-sig'), file_name=f"export_{user}.csv")

def render_hr_payroll():
    st.title("👥 ระบบจัดการเงินเดือน (HR & Payroll)")
    st.dataframe(pd.DataFrame({"รหัสพนักงาน": ["EMP01", "EMP02"], "ชื่อ-สกุล": ["สมชาย ใจดี", "สมหญิง รักงาน"], "ตำแหน่ง": ["Sale Executive", "Developer"], "เงินเดือน": ["฿25,000", "฿40,000"]}), use_container_width=True)

def render_assets():
    st.title("💻 ทะเบียนสินทรัพย์ (Assets)")
    st.dataframe(pd.DataFrame({"รหัสสินทรัพย์": ["FA-2026-01", "FA-2026-02"], "ชื่อสินทรัพย์": ["MacBook Pro", "โต๊ะทำงาน"], "ราคาทุน": ["฿79,000", "฿5,000"]}), use_container_width=True)

def render_security_audit_module():
    st.title("🛡️ โปรไฟล์ & ประวัติการใช้งาน")
    user = st.session_state.user_info['username']
    logs = get_audit_logs(user_id=user, is_admin=False)
    if logs: st.dataframe(pd.DataFrame(logs, columns=["ผู้ใช้งาน", "กิจกรรม", "รายละเอียด", "วัน-เวลา"]), use_container_width=True)

# ==========================================
# 🛡️ 3. Admin Modules
# ==========================================
def render_admin_overview():
    st.title("📊 [Admin] Dashboard ผู้บริหาร")
    conn = get_connection()
    tx_df = pd.read_sql_query("SELECT * FROM transactions", conn)
    c_set = pd.read_sql_query("SELECT approval_threshold FROM company_settings WHERE id = 1", conn).iloc[0]
    conn.close()
    
    inc = tx_df[(tx_df['type'] == 'Income') & (tx_df['approval_status'] == 'Approved')]['amount'].sum() if not tx_df.empty else 0
    exp = tx_df[(tx_df['type'] == 'Expense') & (tx_df['approval_status'] == 'Approved')]['amount'].sum() if not tx_df.empty else 0
    pending_count = len(tx_df[tx_df['approval_status'] == 'Pending']) if not tx_df.empty else 0
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("รายรับรวม", f"฿{inc:,.2f}")
    m2.metric("รายจ่ายรวม", f"฿{exp:,.2f}")
    m3.metric("กำไรสุทธิ", f"฿{(inc - exp):,.2f}")
    m4.metric("🔔 รออนุมัติ", f"{pending_count} รายการ", delta_color="inverse")
    st.divider()
    if pending_count > 0: st.warning(f"มีรายการขอเบิกจ่ายที่เกินเกณฑ์ (฿{c_set['approval_threshold']:,.2f}) จำนวน {pending_count} รายการ รออนุมัติ")

def render_admin_period_lock():
    st.title("🔒 [Admin] ปิดงบประจำเดือน (Period Closing)")
    admin_user = st.session_state.user_info['username']
    
    st.info("💡 เมื่อทำการล็อกงบการเงินในเดือนใดแล้ว User จะไม่สามารถเพิ่ม แก้ไข หรือลบรายการในเดือนนั้นได้อีก")
    
    col1, col2 = st.columns(2)
    selected_ym = col1.text_input("ระบุงบประจำเดือน (รูปแบบ YYYY-MM):", value=datetime.now().strftime("%Y-%m"))
    
    conn = get_connection()
    locks_df = pd.read_sql_query("SELECT * FROM period_locks ORDER BY id DESC", conn)
    conn.close()
    
    is_already_locked = False
    if not locks_df.empty and selected_ym in locks_df['year_month'].values:
        is_already_locked = locks_df[locks_df['year_month'] == selected_ym]['is_locked'].values[0] == 1

    if is_already_locked:
        st.warning(f"🔒 งบประจำเดือน {selected_ym} ถูก 'ล็อก' อยู่ในขณะนี้")
        if st.button("🔓 ปดล็อกงบประจำเดือนนี้"):
            conn = get_connection()
            c = conn.cursor()
            c.execute("UPDATE period_locks SET is_locked = 0 WHERE year_month = ?", (selected_ym,))
            conn.commit()
            conn.close()
            log_audit(admin_user, "UNLOCK_PERIOD", f"ปลดล็อกงบประจำเดือน {selected_ym}")
            st.success(f"ปลดล็อกงบประจำเดือน {selected_ym} เรียบร้อย!")
            st.rerun()
    else:
        st.success(f"🔓 งบประจำเดือน {selected_ym} ยังเปิดให้คีย์ข้อมูลได้ปกติ")
        if st.button("🔒 ยืนยันล็อกงบประจำเดือนนี้", type="primary"):
            conn = get_connection()
            c = conn.cursor()
            c.execute("INSERT OR REPLACE INTO period_locks (year_month, is_locked, locked_by, locked_at) VALUES (?, 1, ?, ?)",
                      (selected_ym, admin_user, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            conn.commit()
            conn.close()
            log_audit(admin_user, "LOCK_PERIOD", f"ล็อกงบประจำเดือน {selected_ym}")
            st.success(f"ล็อกงบประจำเดือน {selected_ym} เรียบร้อยแล้ว!")
            st.rerun()

    st.divider()
    st.subheader("📋 ประวัติการล็อกงบการเงินทั้งหมด")
    if not locks_df.empty:
        st.dataframe(locks_df, use_container_width=True)

def render_admin_approval_center():
    st.title("✅ [Admin] ศูนย์อนุมัติรายการ (Maker-Checker)")
    admin_user = st.session_state.user_info['username']
    conn = get_connection()
    pending_df = pd.read_sql_query("SELECT * FROM transactions WHERE approval_status = 'Pending'", conn)
    conn.close()
    
    if pending_df.empty:
        st.success("🎉 ขณะนี้ไม่มีรายการรออนุมัติ")
    else:
        st.dataframe(pending_df[['id', 'date', 'user_id', 'title', 'amount', 'attachment_file']], use_container_width=True)
        app_options = {f"ID #{r['id']} | ผู้ขอ: {r['user_id']} | ฿{r['amount']:,.2f} - {r['title']}": r['id'] for _, r in pending_df.iterrows()}
        target_id = app_options[st.selectbox("เลือกรายการที่ต้องการดำเนินการ:", list(app_options.keys()))]
        
        col1, col2 = st.columns(2)
        if col1.button("✅ อนุมัติ (Approve)", type="primary", use_container_width=True):
            conn = get_connection()
            c = conn.cursor()
            c.execute("UPDATE transactions SET approval_status = 'Approved' WHERE id = ?", (target_id,))
            conn.commit()
            conn.close()
            log_audit(admin_user, "APPROVE_TX", f"อนุมัติ ID {target_id}")
            st.rerun()
            
        if col2.button("❌ ปฏิเสธ (Reject)", use_container_width=True):
            conn = get_connection()
            c = conn.cursor()
            c.execute("UPDATE transactions SET approval_status = 'Rejected' WHERE id = ?", (target_id,))
            conn.commit()
            conn.close()
            log_audit(admin_user, "REJECT_TX", f"ปฏิเสธ ID {target_id}")
            st.rerun()

def render_admin_audit():
    st.title("🔍 [Admin] ตรวจสอบและจัดการธุรกรรมทั้งหมด")
    admin_user = st.session_state.user_info['username']
    conn = get_connection()
    all_tx = pd.read_sql_query("SELECT * FROM transactions ORDER BY id DESC", conn)
    conn.close()
    if not all_tx.empty:
        st.dataframe(all_tx, use_container_width=True)
        if st.button("🔥 ลบรายการทั้งหมดในระบบ", type="primary"):
            conn = get_connection()
            c = conn.cursor()
            c.execute("DELETE FROM transactions")
            conn.commit()
            conn.close()
            log_audit(admin_user, "ADMIN_DEL_ALL", "ลบรายการทั้งหมด")
            st.rerun()

def render_admin_users():
    st.title("👥 [Admin] จัดการผู้ใช้งานระบบ")
    conn = get_connection()
    users_df = pd.read_sql_query("SELECT id, username, company_name, role FROM users", conn)
    conn.close()
    st.dataframe(users_df, use_container_width=True)

def render_admin_broadcast():
    st.title("📢 [Admin] ส่งประกาศข่าวสาร")
    with st.form("broadcast_form"):
        title = st.text_input("หัวข้อประกาศ:")
        msg = st.text_area("รายละเอียด:")
        if st.form_submit_button("🚀 ส่งประกาศ"):
            conn = get_connection()
            c = conn.cursor()
            c.execute("INSERT INTO announcements (title, message, created_by, created_at) VALUES (?, ?, 'admin', ?)", 
                      (title, msg, datetime.now().strftime("%Y-%m-%d %H:%M")))
            conn.commit()
            conn.close()
            st.success("ส่งประกาศเรียบร้อย!")

def render_admin_settings():
    st.title("⚙️ [Admin] ตั้งค่าองค์กร")
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM company_settings WHERE id = 1")
    settings = c.fetchone()
    conn.close()
    
    with st.form("settings_form"):
        comp_name = st.text_input("ชื่อบริษัท:", value=settings[1])
        threshold = st.number_input("เพดานอนุมัติธุรกรรม (บาท):", min_value=0.0, value=float(settings[4]))
        if st.form_submit_button("💾 บันทึก"):
            conn = get_connection()
            c = conn.cursor()
            c.execute("UPDATE company_settings SET company_name = ?, approval_threshold = ? WHERE id = 1", (comp_name, threshold))
            conn.commit()
            conn.close()
            st.success("บันทึกการตั้งค่าแล้ว!")

def render_admin_db_tools():
    st.title("🛠️ [Admin] สำรองและจัดการฐานข้อมูล")
    try:
        with open(DB_NAME, "rb") as f:
            st.download_button("📦 ดาวน์โหลด Backup DB (.db)", f.read(), file_name=f"backup_{datetime.now().strftime('%Y%m%d')}.db")
    except Exception as e:
        st.error(f"ไม่สามารถอ่านไฟล์ DB ได้: {e}")
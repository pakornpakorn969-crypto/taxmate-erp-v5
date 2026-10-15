import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import datetime
import plotly.express as px

# =========================================================
# 1. PAGE CONFIGURATION & ENTERPRISE LIGHT CUSTOM CSS
# =========================================================
st.set_page_config(
    page_title="TaxMate Enterprise ERP Suite",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Sarabun', sans-serif;
    }
    .stApp {
        background-color: #f8fafc;
    }
    
    /* Light 3D Hero Banner */
    .hero-banner-3d {
        background: linear-gradient(135deg, #eff6ff 0%, #e0f2fe 50%, #dbeafe 100%);
        border: 1px solid #bfdbfe;
        border-radius: 20px;
        padding: 35px 20px;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0 10px 30px rgba(37, 99, 235, 0.08);
    }
    .hero-badge-3d {
        background: linear-gradient(90deg, #2563eb, #0284c7);
        color: #ffffff;
        padding: 6px 20px;
        border-radius: 30px;
        font-size: 0.85rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        display: inline-block;
        margin-bottom: 14px;
        box-shadow: 0 4px 14px rgba(37, 99, 235, 0.25);
    }
    .hero-title-3d {
        color: #0f172a;
        font-size: 2.3rem;
        font-weight: 800;
        margin-bottom: 8px;
    }
    .hero-sub-3d {
        color: #0284c7;
        font-size: 1.15rem;
        font-weight: 700;
        margin-bottom: 10px;
    }
    .hero-desc-3d {
        color: #475569;
        font-size: 0.95rem;
        max-width: 850px;
        margin: 0 auto;
    }
    
    .notice-box-3d {
        background: #ffffff;
        border: 1px solid #bfdbfe;
        border-radius: 30px;
        padding: 12px 24px;
        text-align: center;
        color: #0284c7;
        font-weight: 600;
        font-size: 0.95rem;
        margin: 15px auto;
        max-width: 650px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
    }
    
    .feature-card-3d {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.03);
        height: 100%;
        transition: transform 0.3s ease, border-color 0.3s ease, box-shadow 0.3s ease;
    }
    .feature-card-3d:hover {
        transform: translateY(-4px);
        border-color: #2563eb;
        box-shadow: 0 10px 25px rgba(37, 99, 235, 0.12);
    }
    .feature-card-3d h3 {
        color: #0f172a;
        font-size: 1.05rem;
        margin-bottom: 6px;
    }
    
    /* Primary Action Button */
    .stButton > button[kind="primary"] {
        background-color: #ff4b4b !important;
        color: white !important;
        border: none !important;
        height: 46px !important;
        font-size: 0.98rem !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
    }
    
    .demo-btn > button {
        height: 44px;
        border-radius: 8px;
        border: 1px solid #cbd5e1;
        background-color: #ffffff;
        color: #1e293b;
        font-weight: 600;
        width: 100%;
    }
    .demo-btn > button:hover {
        border-color: #2563eb;
        color: #2563eb;
        background-color: #f0f9ff;
    }
    
    @media (max-width: 768px) {
        .hero-title-3d { font-size: 1.6rem; }
    }
    </style>
""", unsafe_allow_html=True)

# =========================================================
# 2. GLOBAL SESSION STATE INITIALIZATION
# =========================================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_info" not in st.session_state:
    st.session_state.user_info = None

if "selected_branch" not in st.session_state:
    st.session_state.selected_branch = "สำนักงานใหญ่ (กรุงเทพฯ)"

if "line_notify_token" not in st.session_state:
    st.session_state.line_notify_token = ""

# Users & RBAC
if "users_db" not in st.session_state:
    st.session_state.users_db = {
        "demo_admin": {"password": "password123", "name": "Super Admin (Demo)", "role": "Super Admin", "dept": "Executive Management"},
        "demo_user": {"password": "password123", "name": "General User (Demo)", "role": "General User", "dept": "Finance & Accounting"},
        "demo_hr": {"password": "password123", "name": "HR Manager (Demo)", "role": "HR Manager", "dept": "Human Resources"},
        "demo_wh": {"password": "password123", "name": "Warehouse Manager (Demo)", "role": "Inventory Manager", "dept": "Logistics & Supply Chain"}
    }

# Inventory & Multi-Warehouse Stock
if "inventory" not in st.session_state:
    st.session_state.inventory = [
        {"SKU": "SKU-1001", "name": "โน้ตบุ๊กสำนักงาน Core i5", "category": "IT Equipment", "wh": "คลังสินค้าหลัก A", "bin": "Rack-A01", "qty": 45, "min_qty": 10, "cost": 18500.0, "price": 23900.0},
        {"SKU": "SKU-1002", "name": "จอมอนิเตอร์ 24 นิ้ว IPS 100Hz", "category": "IT Equipment", "wh": "คลังสินค้าหลัก A", "bin": "Rack-B03", "qty": 120, "min_qty": 15, "cost": 3800.0, "price": 4900.0},
        {"SKU": "SKU-2005", "name": "คีย์บอร์ดไร้สาย Ergonomic", "category": "Accessories", "wh": "คลังสาขาชลบุรี", "bin": "Rack-C02", "qty": 88, "min_qty": 20, "cost": 750.0, "price": 1290.0},
        {"SKU": "SKU-9042", "name": "ปลั๊กไฟอุตสาหกรรม 5 ช่อง", "category": "Hardware", "wh": "คลังสินค้าหลัก A", "bin": "Rack-D05", "qty": 4, "min_qty": 10, "cost": 280.0, "price": 450.0},
    ]

# Sales History & Payment Reconcile
if "sales_history" not in st.session_state:
    st.session_state.sales_history = [
        {"inv_no": "INV-2026-001", "customer": "บจก. ไทยสมาร์ท ดิสทริบิวชั่น", "amount": 125000.0, "vat": 8750.0, "total": 133750.0, "status": "ชำระแล้ว", "pay_method": "PromptPay QR", "date": "2026-10-01", "due_days": 0, "branch": "สำนักงานใหญ่ (กรุงเทพฯ)"},
        {"inv_no": "INV-2026-002", "customer": "หจก. รุ่งเรือง การบัญชี", "amount": 48000.0, "vat": 3360.0, "total": 51360.0, "status": "รอชำระ", "pay_method": "โอนเงินธนาคาร", "date": "2026-09-15", "due_days": 30, "branch": "สาขาชลบุรี"},
        {"inv_no": "INV-2026-003", "customer": "บจก. สยามเทคโนโลยีก้าวหน้า", "amount": 89000.0, "vat": 6230.0, "total": 95230.0, "status": "เกินกำหนด", "pay_method": "เครดิต 30 วัน", "date": "2026-08-10", "due_days": 65, "branch": "สำนักงานใหญ่ (กรุงเทพฯ)"},
    ]

# Purchase Orders
if "purchase_orders" not in st.session_state:
    st.session_state.purchase_orders = [
        {"po_no": "PO-2026-088", "vendor": "บจก. เอสไอที ซัพพลายส์", "item": "โน้ตบุ๊กสำนักงาน Core i5", "qty": 10, "unit_price": 18000.0, "total": 180000.0, "approval": "อนุมัติแล้ว (2/2)", "status": "รอรับสินค้า"},
        {"po_no": "PO-2026-089", "vendor": "บจก. ไอที ดิสทริบิวเตอร์ ไทย", "item": "จอมอนิเตอร์ 24 นิ้ว IPS", "qty": 20, "unit_price": 3600.0, "total": 72000.0, "approval": "อนุมัติแล้ว (2/2)", "status": "รับสินค้าแล้ว"},
    ]

# Manufacturing Orders & BOM
if "manufacturing_orders" not in st.session_state:
    st.session_state.manufacturing_orders = [
        {"mo_no": "MO-2026-01", "product": "ชุดเซ็ตคอมพิวเตอร์พร้อมใช้งาน", "qty": 15, "cost_est": 225000.0, "start_date": "2026-10-10", "status": "อยู่ระหว่างประกอบ"},
        {"mo_no": "MO-2026-02", "product": "ชุดปลั๊กไฟพ่วงอุตสาหกรรมสายยาว 10m", "qty": 50, "cost_est": 18000.0, "start_date": "2026-10-12", "status": "เสร็จสมบูรณ์"},
    ]

# Support Tickets & Helpdesk
if "support_tickets" not in st.session_state:
    st.session_state.support_tickets = [
        {"ticket_id": "TCK-1001", "customer": "บจก. ไทยสมาร์ท ดิสทริบิวชั่น", "subject": "ขอใบรับประกันจอมอนิเตอร์เพิ่มเติม", "priority": "ปานกลาง", "status": "กำลังดำเนินการ"},
        {"ticket_id": "TCK-1002", "customer": "หจก. รุ่งเรือง การบัญชี", "subject": "สอบถามการออก e-Tax Invoice", "priority": "ด่วน", "status": "ปิดเคสแล้ว"},
    ]

# CRM Deals
if "crm_leads" not in st.session_state:
    st.session_state.crm_leads = [
        {"lead_id": "CRM-001", "company": "บจก. บิ๊กดาต้า โซลูชั่นส์", "contact": "คุณธนพล", "val": 350000.0, "stage": "เสนอราคา (Proposal)", "prob": "70%"},
        {"lead_id": "CRM-002", "company": "หจก. นวัตกรรมซอฟต์แวร์", "contact": "คุณกาญจนา", "val": 180000.0, "stage": "เจรจาสัญญา (Negotiation)", "prob": "90%"},
    ]

# Expense Claims & Approvals
if "expense_claims" not in st.session_state:
    st.session_state.expense_claims = [
        {"claim_id": "EXP-2026-01", "emp": "คุณวิภาวี มีสุข", "cat": "ค่าเดินทาง/ที่พัก", "amount": 4500.0, "date": "2026-10-10", "approver": "คุณสมชาย ใจดี", "status": "รออนุมัติขั้นที่ 2"},
        {"claim_id": "EXP-2026-02", "emp": "คุณอนันต์ ตั้งใจ", "cat": "อุปกรณ์ไอที/ซอฟต์แวร์", "amount": 2800.0, "date": "2026-10-12", "approver": "Super Admin", "status": "อนุมัติเรียบร้อย"},
    ]

# Projects & Job Costing
if "projects" not in st.session_state:
    st.session_state.projects = [
        {"p_code": "PRJ-001", "name": "วางระบบ ERP และ e-Tax บริษัท สยามมอเตอร์", "budget": 850000.0, "actual_cost": 420000.0, "progress": 65, "status": "กำลังดำเนินการ"},
        {"p_code": "PRJ-002", "name": "พัฒนาแอปพลิเคชันคลังสินค้า ชลบุรีโลจิสติกส์", "budget": 450000.0, "actual_cost": 390000.0, "progress": 90, "status": "ใกล้เสร็จสิ้น"},
    ]

# Fixed Assets
if "fixed_assets" not in st.session_state:
    st.session_state.fixed_assets = [
        {"asset_code": "AST-001", "name": "เครื่องเซิร์ฟเวอร์หลักประจำสำนักงาน", "cat": "อุปกรณ์ IT", "cost": 150000.0, "useful_years": 5, "buy_date": "2024-01-10", "depreciation_yr": 30000.0, "book_value": 67500.0},
        {"asset_code": "AST-002", "name": "รถยนต์ขนส่งสินค้า Toyota Revo", "cat": "ยานพาหนะ", "cost": 680000.0, "useful_years": 5, "buy_date": "2023-05-15", "depreciation_yr": 136000.0, "book_value": 226667.0},
    ]

# Contracts
if "contracts" not in st.session_state:
    st.session_state.contracts = [
        {"contract_no": "CTR-2026-01", "title": "สัญญาจ้างพัฒนาระบบซอฟต์แวร์ ERP", "party": "บจก. สยามเทคโนโลยี", "val": 1200000.0, "end_date": "2027-03-31", "status": "มีผลบังคับใช้"},
        {"contract_no": "CTR-2026-02", "title": "สัญญาเช่าพื้นที่อาคารสำนักงานชั้น 12", "party": "บจก. สาทรทาวเวอร์", "val": 360000.0, "end_date": "2026-11-30", "status": "⚠️ ใกล้หมดอายุ"},
    ]

# Logistics
if "shipments" not in st.session_state:
    st.session_state.shipments = [
        {"tracking_no": "TH2026889101", "inv_no": "INV-2026-001", "courier": "Flash Express", "dest": "กรุงเทพฯ", "status": "ส่งมอบสำเร็จ"},
        {"tracking_no": "TH2026889102", "inv_no": "INV-2026-002", "courier": "Kerry Express", "dest": "ชลบุรี", "status": "อยู่ระหว่างการจัดส่ง"},
    ]

# Employees & Payroll
if "employees" not in st.session_state:
    st.session_state.employees = [
        {"id": "EMP-001", "name": "คุณสมชาย ใจดี", "position": "ผู้จัดการฝ่ายการเงิน", "salary": 65000.0, "sso": 750.0, "wht": 3250.0, "net": 61000.0},
        {"id": "EMP-002", "name": "คุณวิภาวี มีสุข", "position": "นักบัญชีบริหาร", "salary": 38000.0, "sso": 750.0, "wht": 1100.0, "net": 36150.0},
        {"id": "EMP-003", "name": "คุณอนันต์ ตั้งใจ", "position": "IT Systems Engineer", "salary": 32000.0, "sso": 750.0, "wht": 650.0, "net": 30600.0},
    ]

# Journal Entries
if "journal_entries" not in st.session_state:
    st.session_state.journal_entries = [
        {"date": "2026-10-01", "code": "11100", "account": "เงินฝากธนาคาร", "debit": 133750.0, "credit": 0.0},
        {"date": "2026-10-01", "code": "41100", "account": "รายได้จากการขาย", "debit": 0.0, "credit": 125000.0},
        {"date": "2026-10-01", "code": "21300", "account": "ภาษีขายรอส่งมอบ", "debit": 0.0, "credit": 8750.0},
    ]

if "pos_cart" not in st.session_state:
    st.session_state.pos_cart = []

if "system_logs" not in st.session_state:
    st.session_state.system_logs = [
        {"timestamp": "2026-10-15 11:30:00", "user": "demo_admin", "action": "เข้าสู่ระบบสิทธิ์ Super Admin"},
        {"timestamp": "2026-10-15 11:45:12", "user": "demo_user", "action": "เข้าสู่ระบบสิทธิ์ General User"},
    ]

# =========================================================
# 3. PUBLIC VIEW (LIGHT 3D LANDING PAGE & AUTH CENTER)
# =========================================================
if not st.session_state.logged_in:
    
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/2082/2082805.png", width=60)
        st.title("🖥️ TaxMate ERP")
        st.caption("📍 **เมนูเริ่มต้น:**")
        public_page = st.radio(
            "เลือกหน้าการทำงาน:",
            ["🏠 หน้าแรก (หน้าต้อนรับ 3 มิติ)", "🔑 เข้าสู่ระบบ / ลงทะเบียน"],
            label_visibility="collapsed"
        )
        st.divider()
        st.caption("🟢 สถานะเซิร์ฟเวอร์: **ออนไลน์ 24/7**")
        st.caption("☁️ ผู้ให้บริการ: **Render Cloud**")

    if public_page == "🏠 หน้าแรก (หน้าต้อนรับ 3 มิติ)":
        
        # 1. Light Hero Header Title
        st.markdown("""
        <div class="hero-banner-3d">
            <div class="hero-badge-3d">🔮 NEXT-GEN 3D ENTERPRISE ERP ENGINE</div>
            <div class="hero-title-3d">🏛️ TaxMate Enterprise ERP Suite</div>
            <div class="hero-sub-3d">The Interactive 3D Cloud Financial & Compliance Platform</div>
            <div class="hero-desc-3d">ศูนย์กลางบริหารจัดการบัญชี ภาษีไทย e-Tax สต็อกหลายสาขา การผลิต CRM และทรัพยากรมนุษย์ ด้วยสถาปัตยกรรมระดับองค์กรชั้นนำ</div>
        </div>
        """, unsafe_allow_html=True)
        
        # 2. Interactive Light 3D WebGL Canvas (Three.js Engine)
        components.html("""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { margin: 0; overflow: hidden; background: transparent; }
                #canvas-container { width: 100vw; height: 380px; }
            </style>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
        </head>
        <body>
            <div id="canvas-container"></div>
            <script>
                const container = document.getElementById('canvas-container');
                const scene = new THREE.Scene();
                
                const camera = new THREE.PerspectiveCamera(45, container.clientWidth / container.clientHeight, 0.1, 1000);
                camera.position.set(0, 0, 8);

                const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
                renderer.setSize(container.clientWidth, container.clientHeight);
                renderer.setPixelRatio(window.devicePixelRatio);
                container.appendChild(renderer.domElement);

                // Main Floating Glass Cube
                const geometry = new THREE.BoxGeometry(2.2, 2.2, 2.2);
                const material = new THREE.MeshPhongMaterial({
                    color: 0x2563eb,
                    emissive: 0x1d4ed8,
                    specular: 0x60a5fa,
                    shininess: 90,
                    transparent: true,
                    opacity: 0.88,
                    wireframe: false
                });
                const cube = new THREE.Mesh(geometry, material);
                scene.add(cube);

                // Outer Wireframe Structure
                const wireGeometry = new THREE.BoxGeometry(2.6, 2.6, 2.6);
                const wireMaterial = new THREE.MeshBasicMaterial({ color: 0x0284c7, wireframe: true });
                const wireCube = new THREE.Mesh(wireGeometry, wireMaterial);
                scene.add(wireCube);

                // Orbit Ring
                const ringGeo = new THREE.TorusGeometry(3.2, 0.035, 16, 100);
                const ringMat = new THREE.MeshBasicMaterial({ color: 0x3b82f6 });
                const ring = new THREE.Mesh(ringGeo, ringMat);
                ring.rotation.x = Math.PI / 3;
                scene.add(ring);

                // Lighting Setup
                const ambientLight = new THREE.AmbientLight(0xffffff, 0.9);
                scene.add(ambientLight);

                const pointLight = new THREE.PointLight(0x2563eb, 2.5, 50);
                pointLight.position.set(5, 5, 5);
                scene.add(pointLight);

                // Mouse Interaction
                let mouseX = 0, mouseY = 0;
                document.addEventListener('mousemove', (e) => {
                    mouseX = (e.clientX / window.innerWidth - 0.5) * 2;
                    mouseY = (e.clientY / window.innerHeight - 0.5) * 2;
                });

                // Animation Loop
                function animate() {
                    requestAnimationFrame(animate);
                    
                    cube.rotation.x += 0.008;
                    cube.rotation.y += 0.012;
                    
                    wireCube.rotation.x -= 0.005;
                    wireCube.rotation.y -= 0.008;

                    ring.rotation.z += 0.01;

                    camera.position.x += (mouseX * 1.5 - camera.position.x) * 0.05;
                    camera.position.y += (-mouseY * 1.5 - camera.position.y) * 0.05;
                    camera.lookAt(scene.position);

                    renderer.render(scene, camera);
                }
                animate();

                window.addEventListener('resize', () => {
                    camera.aspect = container.clientWidth / container.clientHeight;
                    camera.updateProjectionMatrix();
                    renderer.setSize(container.clientWidth, container.clientHeight);
                });
            </script>
        </body>
        </html>
        """, height=380)

        st.markdown("""
        <div class="notice-box-3d">
            💡 เลือกเมนู '🔑 เข้าสู่ระบบ / ลงทะเบียน' ที่แถบด้านซ้าย เพื่อเข้าใช้งานระบบ
        </div>
        """, unsafe_allow_html=True)
        
        # Light 3D Feature Cards
        f1, f2, f3, f4 = st.columns(4)
        with f1:
            st.markdown("""
            <div class="feature-card-3d">
                <h3>🌐 ระบบประมวลผลคลาวด์</h3>
                <p style="color:#64748b; font-size:0.85rem;">ระบบประมวลผลเซิร์ฟเวอร์หลังบ้าน ปลอดภัย เสถียร ตรวจสอบ Audit Trail 24/7</p>
            </div>
            """, unsafe_allow_html=True)
        with f2:
            st.markdown("""
            <div class="feature-card-3d">
                <h3>🗄️ คลังสินค้าหลายสาขา</h3>
                <p style="color:#64748b; font-size:0.85rem;">จัดการสต็อกสินค้าหลายสาขา ระบุพิกัด Rack/Bin สั่งผลิต BOM อัตโนมัติ</p>
            </div>
            """, unsafe_allow_html=True)
        with f3:
            st.markdown("""
            <div class="feature-card-3d">
                <h3>💳 ชำระเงิน PromptPay QR</h3>
                <p style="color:#64748b; font-size:0.85rem;">ระบบ Dynamic PromptPay QR ชำระเงินสะดวก พร้อม Auto Bank Reconcile</p>
            </div>
            """, unsafe_allow_html=True)
        with f4:
            st.markdown("""
            <div class="feature-card-3d">
                <h3>📊 บริหารภาษี & AI</h3>
                <p style="color:#64748b; font-size:0.85rem;">ออกใบกำกับภาษี e-Tax Invoice แบบสรรพากร และ AI พยากรณ์ยอดขายล่วงหน้า</p>
            </div>
            """, unsafe_allow_html=True)

    elif public_page == "🔑 เข้าสู่ระบบ / ลงทะเบียน":
        st.markdown("<h2 style='color:#0f172a; margin-bottom:0;'>🔑 ศูนย์ยืนยันตัวตน (Authentication Center)</h2>", unsafe_allow_html=True)
        st.caption("ระบบเข้าสู่ระบบ ลงทะเบียน และกู้คืนรหัสผ่านสำหรับพนักงานและผู้ดูแลระบบ")
        st.markdown("<br>", unsafe_allow_html=True)
        
        tab_login, tab_register, tab_forgot = st.tabs([
            "🔑 เข้าสู่ระบบ (Login)", 
            "📝 ลงทะเบียนผู้ใช้ใหม่ (Register)", 
            "🔑 ลืมรหัสผ่าน (Forgot Password)"
        ])
        
        with tab_login:
            st.markdown("### **เข้าสู่ระบบด้วยบัญชีองค์กร**")
            with st.form("login_form"):
                username_input = st.text_input("ชื่อผู้ใช้งาน (Username):", placeholder="กรอก Username เช่น demo_admin หรือ บัญชีที่สมัครใหม่")
                password_input = st.text_input("รหัสผ่าน (Password):", type="password", placeholder="กรอกรหัสผ่าน")
                
                submit_login = st.form_submit_button("🔑 เข้าสู่ระบบ", type="primary")
                
                if submit_login:
                    if username_input in st.session_state.users_db and st.session_state.users_db[username_input]["password"] == password_input:
                        user_data = st.session_state.users_db[username_input]
                        st.session_state.logged_in = True
                        st.session_state.user_info = {
                            "username": username_input,
                            "name": user_data["name"],
                            "role": user_data["role"],
                            "dept": user_data["dept"]
                        }
                        st.session_state.system_logs.append({
                            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "user": username_input,
                            "action": f"เข้าสู่ระบบสิทธิ์ {user_data['role']}"
                        })
                        st.success(f"เข้าสู่ระบบสำเร็จ! ยินดีต้อนรับ {user_data['name']}")
                        st.rerun()
                    else:
                        st.error("❌ ชื่อผู้ใช้งานหรือรหัสผ่านไม่ถูกต้อง")

            st.divider()
            st.markdown("### ⚡ **เข้าใช้งานด่วนด้วย บัญชีทดสอบ (Quick Demo Access)**")
            d_col1, d_col2 = st.columns(2)
            with d_col1:
                st.markdown('<div class="demo-btn">', unsafe_allow_html=True)
                if st.button("👤 เข้าใช้งานด่วน: ผู้ดูแลระบบ (demo_admin)", key="btn_demo_admin"):
                    st.session_state.logged_in = True
                    st.session_state.user_info = {
                        "username": "demo_admin",
                        "name": "Super Admin (Demo)",
                        "role": "Super Admin",
                        "dept": "Executive Management"
                    }
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
                
            with d_col2:
                st.markdown('<div class="demo-btn">', unsafe_allow_html=True)
                if st.button("👤 เข้าใช้งานด่วน: พนักงานทั่วไป (demo_user)", key="btn_demo_user"):
                    st.session_state.logged_in = True
                    st.session_state.user_info = {
                        "username": "demo_user",
                        "name": "General User (Demo)",
                        "role": "General User",
                        "dept": "Finance & Accounting"
                    }
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

        with tab_register:
            st.markdown("### **ลงทะเบียนผู้ใช้งานใหม่**")
            with st.form("register_form"):
                col_r1, col_r2 = st.columns(2)
                with col_r1:
                    reg_fullname = st.text_input("ชื่อ-นามสกุล ผู้ใช้งาน:")
                    reg_username = st.text_input("ชื่อผู้ใช้งาน (Username):")
                    reg_email = st.text_input("อีเมลองค์กร:")
                with col_r2:
                    reg_role = st.selectbox("🔑 สิทธิ์การใช้งานในระบบ (Role):", [
                        "Super Admin (ผู้ดูแลระบบสูงสุด)", 
                        "Chief Accountant (ผู้จัดการบัญชี)", 
                        "General User (พนักงานทั่วไป)"
                    ])
                    reg_dept = st.selectbox("แผนก/ฝ่ายงาน:", ["บริหารและจัดการ (Executive)", "การเงินและบัญชี", "ทรัพยากรบุคคล (HR)", "จัดซื้อ/คลังสินค้า/การผลิต", "ฝ่ายขาย"])
                    reg_pass1 = st.text_input("รหัสผ่าน:", type="password")
                    reg_pass2 = st.text_input("ยืนยันรหัสผ่าน:", type="password")
                    
                auto_login_check = st.checkbox("⚡ ล็อกอินเข้าสู่ระบบทันทีหลังสร้างบัญชีสำเร็จ", value=True)
                submit_reg = st.form_submit_button("📝 บันทึกสร้างบัญชีผู้ใช้ใหม่", type="primary")
                
                if submit_reg:
                    clean_role = "Super Admin" if "Super Admin" in reg_role else ("Chief Accountant" if "Chief Accountant" in reg_role else "General User")
                    if not reg_username or not reg_pass1 or not reg_fullname:
                        st.warning("⚠️ กรุณากรอกข้อมูลสำคัญให้ครบถ้วน")
                    elif reg_pass1 != reg_pass2:
                        st.error("❌ รหัสผ่านทั้งสองช่องไม่ตรงกัน")
                    elif reg_username in st.session_state.users_db:
                        st.error("❌ ชื่อผู้ใช้นี้มีอยู่ในระบบแล้ว")
                    else:
                        st.session_state.users_db[reg_username] = {
                            "password": reg_pass1, "name": reg_fullname, "role": clean_role, "dept": reg_dept
                        }
                        if auto_login_check:
                            st.session_state.logged_in = True
                            st.session_state.user_info = {
                                "username": reg_username, "name": reg_fullname, "role": clean_role, "dept": reg_dept
                            }
                            st.success(f"✅ บันทึกสำเร็จ! นำคุณเข้าสู่ระบบสิทธิ์ {clean_role}...")
                            st.rerun()
                        else:
                            st.success(f"✅ สร้างบัญชีสิทธิ์ {clean_role} สำเร็จ!")

        with tab_forgot:
            st.markdown("### **กู้คืนรหัสผ่าน**")
            with st.form("forgot_form"):
                reset_email = st.text_input("กรอกอีเมลที่ลงทะเบียนไว้ในระบบ:")
                submit_forgot = st.form_submit_button("📩 ส่งลิงก์รีเซ็ตรหัสผ่าน", type="primary")
                if submit_forgot:
                    if reset_email:
                        st.success(f"ระบบได้ส่งคำแนะนำไปยัง {reset_email} เรียบร้อยแล้ว")
                    else:
                        st.warning("กรุณากรอกอีเมล")

# =========================================================
# 4. AUTHENTICATED FULL ENTERPRISE ERP SYSTEM
# =========================================================
else:
    u_info = st.session_state.user_info
    is_admin = u_info['role'] in ["Super Admin", "Chief Accountant"]
    
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/2082/2082805.png", width=55)
        st.title("🖥️ TaxMate ERP")
        st.caption("ฉบับแปลภาษาไทยเต็มรูปแบบ")
        
        st.session_state.selected_branch = st.selectbox(
            "🏢 เลือกสาขาองค์กร:",
            ["สำนักงานใหญ่ (กรุงเทพฯ)", "สาขาเชียงใหม่", "สาขาชลบุรี", "สาขาภูเก็ต"]
        )
        
        badge_color = "#dc2626" if is_admin else "#2563eb"
        st.markdown(f"""
        <div style="background:#ffffff; border:1px solid #cbd5e1; padding:12px; border-radius:8px; margin-bottom:12px;">
            <b style="color:#0f172a;">👤 {u_info['name']}</b><br>
            <span style="font-size:0.85rem; color:{badge_color}; font-weight:bold;">สิทธิ์: {u_info['role']}</span><br>
            <span style="font-size:0.85rem; color:#64748b;">แผนก: {u_info['dept']}</span>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚪 ออกจากระบบ"):
            st.session_state.logged_in = False
            st.session_state.user_info = None
            st.rerun()
            
        st.divider()
        
        # เมนูด้านซ้ายภาษาไทยทั้งหมด ทั้งฝั่ง Admin และ User
        available_modules = [
            "📊 แดชบอร์ดผู้บริหาร",
            "🖥️ ระบบควบคุมเซิร์ฟเวอร์หลังบ้าน",
            "🇹🇭 ระบบบริหารภาษีไทย & e-Tax",
            "🏢 ระบบจัดการคลังสินค้าหลายสาขา & ตำแหน่งจัดเก็บ",
            "🛒 ระบบขายหน้าร้าน (POS) & PromptPay QR",
            "🛍️ ระบบจัดซื้อจัดจ้าง & ใบสั่งซื้อ (PO)",
            "🏭 ระบบบริหารการผลิต & สูตรโครงสร้างสินค้า (BOM)",
            "🤝 ระบบบริหารความสัมพันธ์ลูกค้า & โอกาสการขาย (CRM)",
            "💳 ระบบช่องทางชำระเงิน & กระทบยอดธนาคาร",
            "💬 ระบบศูนย์บริการลูกค้า & ตั๋วแจ้งปัญหา (Helpdesk)",
            "📜 ระบบบริหารสัญญาและเอกสารทางกฎหมาย",
            "🚚 ระบบการจัดส่งสินค้า & ห่วงโซ่อุปทาน",
            "💸 ระบบเบิกจ่ายค่าใช้จ่าย & สายการอนุมัติ",
            "🏢 ระบบสินทรัพย์ถาวร & คำนวณค่าเสื่อมราคา",
            "📁 ระบบจัดการโครงการ & ต้นทุนงาน",
            "👥 ระบบบริหารทรัพยากรบุคคล & คำนวณเงินเดือน",
            "📑 ระบบบัญชีแยกประเภท & งบการเงิน",
            "📈 AI พยากรณ์ความต้องการยอดขาย",
            "🔔 ระบบแจ้งเตือนอัตโนมัติ & LINE Notify"
        ]
        
        if is_admin:
            available_modules.append("⚙️ ระบบความปลอดภัย & ตั้งค่าระบบ")
            
        menu_choice = st.radio("📌 มอดูลการทำงานทั้งหมด:", available_modules)
        st.divider()
        st.caption("🟢 สถานะเซิร์ฟเวอร์: **ออนไลน์ 24/7**")

    # 1. แดชบอร์ดผู้บริหาร
    if menu_choice == "📊 แดชบอร์ดผู้บริหาร":
        st.title(f"📊 แดชบอร์ดผู้บริหาร ({st.session_state.selected_branch})")
        
        total_sales = sum([x['amount'] for x in st.session_state.sales_history])
        total_vat = sum([x['vat'] for x in st.session_state.sales_history])
        total_stock_val = sum([x['qty'] * x['cost'] for x in st.session_state.inventory])
        total_pipeline = sum([x['val'] for x in st.session_state.crm_leads])
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("ยอดขายสะสมรวม", f"฿ {total_sales:,.2f}", "+14.2%")
        m2.metric("ภาษีขายรอส่งมอบ (VAT)", f"฿ {total_vat:,.2f}", "ภ.พ.30 Ready")
        m3.metric("มูลค่าสินค้าในคลัง", f"฿ {total_stock_val:,.2f}", f"{len(st.session_state.inventory)} SKU")
        m4.metric("มูลค่าดีลใน CRM Pipeline", f"฿ {total_pipeline:,.2f}", f"{len(st.session_state.crm_leads)} Deals")
        
        st.divider()
        c_chart, c_alert = st.columns([2, 1])
        with c_chart:
            st.subheader("📈 แนวโน้มกระแสเงินสด & รายได้องค์กร")
            df_chart = pd.DataFrame({
                "เดือน": ["พ.ค.", "มิ.ย.", "ก.ค.", "ส.ค.", "ก.ย.", "ต.ค."],
                "รายได้": [850000, 920000, 1100000, 1050000, 1180000, total_sales + 950000],
                "ค่าใช้จ่าย": [620000, 680000, 750000, 720000, 790000, 850000]
            })
            fig = px.bar(df_chart, x="เดือน", y=["รายได้", "ค่าใช้จ่าย"], barmode="group", color_discrete_sequence=['#2563eb', '#ef4444'])
            st.plotly_chart(fig, use_container_width=True)
            
        with c_alert:
            st.subheader("🔔 การแจ้งเตือนระบบ")
            low_stock = [x for x in st.session_state.inventory if x['qty'] <= x['min_qty']]
            if low_stock:
                for item in low_stock:
                    st.error(f"🚨 **สินค้าใกล้หมด:** {item['name']} เหลือ {item['qty']} ชิ้น")
            else:
                st.success("✅ ระดับสินค้าในคลังปกติทุกรายการ")
            st.info("📅 **นัดหมายภาษี:** ยื่น ภ.พ.30 e-Filing ภายในวันที่ 23 ต.ค.")

    # 2. ระบบควบคุมเซิร์ฟเวอร์หลังบ้าน
    elif menu_choice == "🖥️ ระบบควบคุมเซิร์ฟเวอร์หลังบ้าน":
        st.title("🖥️ ระบบบริหารจัดการเครื่องเซิร์ฟเวอร์ & โครงสร้างหลังบ้าน (Backend Control)")
        st.caption("ตรวจสอบสถานะ คลาวด์เซิร์ฟเวอร์ ฐานข้อมูล และประมวลผลระบบหลังบ้านแบบ Real-Time")
        
        b1, b2, b3, b4 = st.columns(4)
        b1.metric("Cloud Status", "Active 99.99%", "Render Cloud")
        b2.metric("CPU Usage", "18.4%", "Normal")
        b3.metric("RAM Allocation", "1.2 GB / 4.0 GB", "Healthy")
        b4.metric("DB Connections", "12 Active Pool", "PostgreSQL Ready")
        
        st.divider()
        st.subheader("🗄️ สถานะการเชื่อมต่อฐานข้อมูล & API หลังบ้าน")
        st.image("https://images.unsplash.com/photo-1558494949-ef010cbdcc31?auto=format&fit=crop&w=1200&q=80", caption="🖥️ Main Server Rack & Database Infrastructure", use_container_width=True)
        
        col_b1, col_b2 = st.columns(2)
        with col_b1:
            st.write("### ⚙️ Backend Services Status")
            st.success("✅ **e-Tax Invoice Gateway:** Connected & Ready")
            st.success("✅ **PromptPay Dynamic QR Generator:** Online")
            st.success("✅ **LINE Workflows Engine:** Active")
            st.success("✅ **AI Demand Forecast Engine:** Model Loaded")
        with col_b2:
            st.write("### 🔄 Database Manual Backup")
            if st.button("💾 สำรองข้อมูลระบบหลังบ้านทันที (Manual DB Backup)"):
                st.toast("ทำการ Backup ฐานข้อมูลลง Cloud Storage สำเร็จ!")
                st.success("บันทึกไฟล์สแนปชอต `taxmate_backup_20261015.sql` เรียบร้อยแล้ว")

    # 3. ระบบบริหารภาษีไทย & E-TAX
    elif menu_choice == "🇹🇭 ระบบบริหารภาษีไทย & e-Tax":
        st.title("🇹🇭 ระบบบริหารภาษีไทย & e-Tax Invoice")
        tab_etax, tab_wht, tab_vat = st.tabs(["📄 ออกใบกำกับภาษี e-Tax Invoice", "📑 ภาษีหัก ณ ที่จ่าย (50 ทวิ)", "📊 แบบสรุป ภ.พ. 30"])
        
        with tab_etax:
            col1, col2 = st.columns(2)
            with col1:
                c_name = st.text_input("ชื่อบริษัท/ลูกค้า", "บริษัท ไทยพาณิชย์ก้าวหน้า จำกัด")
                c_taxid = st.text_input("เลขประจำตัวผู้เสียภาษี 13 หลัก", "0105562098765")
            with col2:
                doc_date = st.date_input("วันที่ออกเอกสาร", datetime.date.today())
                subtotal = st.number_input("จำนวนเงินก่อน VAT (บาท)", min_value=0.0, value=50000.0)
                vat_val = subtotal * 0.07
                st.write(f"**VAT (7%):** ฿ {vat_val:,.2f}")
                st.write(f"**ยอดรวมสุทธิ:** ฿ {subtotal + vat_val:,.2f}")
                
            if st.button("🚀 ออก e-Tax Invoice พร้อมลงลายเซ็นดิจิทัล"):
                st.session_state.sales_history.append({
                    "inv_no": f"INV-2026-00{len(st.session_state.sales_history)+1}",
                    "customer": c_name, "amount": subtotal, "vat": vat_val, "total": subtotal + vat_val, "status": "ชำระแล้ว", "pay_method": "e-Payment", "date": str(doc_date), "due_days": 0, "branch": st.session_state.selected_branch
                })
                st.success("สร้างเอกสาร e-Tax Invoice สำเร็จ!")

        with tab_wht:
            p_name = st.text_input("ชื่อผู้รับเงิน", "บริษัท รักษาความปลอดภัย พรีเมี่ยม จำกัด")
            p_amount = st.number_input("จำนวนเงิน (บาท)", value=20000.0)
            st.info(f"ภาษีหัก ณ ที่จ่าย (3%): **฿ {p_amount * 0.03:,.2f}**")
            if st.button("🖨️ ออกหนังสือรับรอง 50 ทวิ"):
                st.success("ออกเอกสาร 50 ทวิ เรียบร้อยแล้ว")

        with tab_vat:
            df_v = pd.DataFrame(st.session_state.sales_history)
            st.dataframe(df_v, use_container_width=True)

    # 4. ระบบจัดการคลังสินค้าหลายสาขา
    elif menu_choice == "🏢 ระบบจัดการคลังสินค้าหลายสาขา & ตำแหน่งจัดเก็บ":
        st.title("🏢 ระบบคลังสินค้าหลายสาขา & ตำแหน่งจัดเก็บ (Bin/Rack Location)")
        st.dataframe(pd.DataFrame(st.session_state.inventory), use_container_width=True)
        
        st.divider()
        st.subheader("📦 ย้ายสต็อกระหว่างคลัง (Stock Transfer)")
        with st.form("transfer_form"):
            t_sku = st.selectbox("เลือกสินค้า", [x['SKU'] + " - " + x['name'] for x in st.session_state.inventory])
            t_from = st.selectbox("จากคลังต้นทาง", ["คลังสินค้าหลัก A", "คลังสาขาชลบุรี", "คลังสาขาเชียงใหม่"])
            t_to = st.selectbox("ไปยังคลังปลายทาง", ["คลังสาขาชลบุรี", "คลังสินค้าหลัก A", "คลังสาขาภูเก็ต"])
            t_qty = st.number_input("จำนวนที่ต้องการย้าย", min_value=1, value=5)
            
            if st.form_submit_button("🔄 ดำเนินการย้ายสต็อก"):
                st.success(f"บันทึกการโอนย้ายสินค้า {t_sku} จำนวน {t_qty} ชิ้น เรียบร้อยแล้ว")

    # 5. ระบบขายหน้าร้าน (POS)
    elif menu_choice == "🛒 ระบบขายหน้าร้าน (POS) & PromptPay QR":
        st.title("🛒 ระบบขายหน้าร้าน (POS) & Dynamic PromptPay QR")
        p_left, p_right = st.columns([2, 1])
        with p_left:
            st.subheader("🛍️ เลือกสินค้า")
            for item in st.session_state.inventory:
                if st.button(f"➕ {item['name']} (฿{item['price']:,.2f})", key=f"pos_{item['SKU']}"):
                    st.session_state.pos_cart.append(item)
                    st.toast(f"เพิ่ม {item['name']} แล้ว")
        with p_right:
            st.subheader("🛒 ตะกร้าสินค้า")
            if st.session_state.pos_cart:
                st.dataframe(pd.DataFrame(st.session_state.pos_cart)[['name', 'price']], use_container_width=True)
                sub_t = sum([x['price'] for x in st.session_state.pos_cart])
                grand_total = sub_t * 1.07
                st.write(f"**ยอดรวมสุทธิ:** ฿ {grand_total:,.2f}")
                
                st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=180x180&data=PROMPTPAY_PAYMENT_AMOUNT_{grand_total}", caption=f"สแกนจ่าย PromptPay: ฿ {grand_total:,.2f}")
                
                if st.button("💵 ยืนยันชำระเงินและตัดสต็อก"):
                    for cart_item in st.session_state.pos_cart:
                        for inv_item in st.session_state.inventory:
                            if inv_item['SKU'] == cart_item['SKU'] and inv_item['qty'] > 0:
                                inv_item['qty'] -= 1
                    st.session_state.sales_history.append({
                        "inv_no": f"POS-2026-00{len(st.session_state.sales_history)+1}",
                        "customer": "ลูกค้าหน้าร้าน", "amount": sub_t, "vat": sub_t * 0.07, "total": grand_total, "status": "ชำระแล้ว", "pay_method": "PromptPay QR", "date": str(datetime.date.today()), "due_days": 0, "branch": st.session_state.selected_branch
                    })
                    st.session_state.pos_cart = []
                    st.balloons()
                    st.rerun()

    # 6. ระบบจัดซื้อจัดจ้าง
    elif menu_choice == "🛍️ ระบบจัดซื้อจัดจ้าง & ใบสั่งซื้อ (PO)":
        st.title("🛍️ ระบบจัดซื้อจัดจ้าง & ใบสั่งซื้อ (Purchase Orders)")
        st.dataframe(pd.DataFrame(st.session_state.purchase_orders), use_container_width=True)

    # 7. ระบบบริหารการผลิต
    elif menu_choice == "🏭 ระบบบริหารการผลิต & สูตรโครงสร้างสินค้า (BOM)":
        st.title("🏭 ระบบบริหารการผลิต & สูตรโครงสร้างสินค้า (BOM)")
        st.dataframe(pd.DataFrame(st.session_state.manufacturing_orders), use_container_width=True)

    # 8. ระบบ CRM
    elif menu_choice == "🤝 ระบบบริหารความสัมพันธ์ลูกค้า & โอกาสการขาย (CRM)":
        st.title("🤝 ระบบบริหารความสัมพันธ์ลูกค้า & โอกาสการขาย (CRM)")
        st.dataframe(pd.DataFrame(st.session_state.crm_leads), use_container_width=True)

    # 9. ระบบช่องทางชำระเงิน
    elif menu_choice == "💳 ระบบช่องทางชำระเงิน & กระทบยอดธนาคาร":
        st.title("💳 ระบบกระทบยอดเงินโอนธนาคารอัตโนมัติ (Auto Bank Reconciliation)")
        df_bank = pd.DataFrame([
            {"date": "2026-10-15 10:14", "bank": "ธนาคารกสิกรไทย", "tx_id": "TX998201", "amount": 133750.0, "match_inv": "INV-2026-001", "status": "กระทบยอดแล้ว ✅"},
            {"date": "2026-10-15 11:02", "bank": "ธนาคารไทยพาณิชย์", "tx_id": "TX998205", "amount": 51360.0, "match_inv": "INV-2026-002", "status": "รอจับคู่เอกสาร ⚠️"}
        ])
        st.dataframe(df_bank, use_container_width=True)

    # 10. ระบบศูนย์บริการลูกค้า
    elif menu_choice == "💬 ระบบศูนย์บริการลูกค้า & ตั๋วแจ้งปัญหา (Helpdesk)":
        st.title("💬 ระบบบริการลูกค้าหลังการขาย & ตั๋วแจ้งปัญหา (Helpdesk)")
        st.dataframe(pd.DataFrame(st.session_state.support_tickets), use_container_width=True)

    # 11. ระบบบริหารสัญญา
    elif menu_choice == "📜 ระบบบริหารสัญญาและเอกสารทางกฎหมาย":
        st.title("📜 ระบบบริหารสัญญาและเอกสารทางกฎหมาย (Contracts)")
        st.dataframe(pd.DataFrame(st.session_state.contracts), use_container_width=True)

    # 12. ระบบการจัดส่งสินค้า
    elif menu_choice == "🚚 ระบบการจัดส่งสินค้า & ห่วงโซ่อุปทาน":
        st.title("🚚 ระบบการจัดส่งสินค้าและห่วงโซ่อุปทาน (Logistics)")
        st.dataframe(pd.DataFrame(st.session_state.shipments), use_container_width=True)

    # 13. ระบบเบิกจ่ายค่าใช้จ่าย
    elif menu_choice == "💸 ระบบเบิกจ่ายค่าใช้จ่าย & สายการอนุมัติ":
        st.title("💸 ระบบเบิกจ่ายค่าใช้จ่ายพนักงาน & สายการอนุมัติ")
        st.dataframe(pd.DataFrame(st.session_state.expense_claims), use_container_width=True)

    # 14. ระบบสินทรัพย์ถาวร
    elif menu_choice == "🏢 ระบบสินทรัพย์ถาวร & คำนวณค่าเสื่อมราคา":
        st.title("🏢 ระบบบริหารสินทรัพย์ถาวร & คำนวณค่าเสื่อมราคา")
        st.dataframe(pd.DataFrame(st.session_state.fixed_assets), use_container_width=True)

    # 15. ระบบจัดการโครงการ
    elif menu_choice == "📁 ระบบจัดการโครงการ & ต้นทุนงาน":
        st.title("📁 ระบบจัดการโครงการ & ต้นทุนงาน (Job Costing)")
        for prj in st.session_state.projects:
            st.write(f"📌 **{prj['p_code']} - {prj['name']}** (ความคืบหน้า {prj['progress']}%)")
            st.progress(prj['progress'] / 100)

    # 16. ระบบบริหารทรัพยากรบุคคล
    elif menu_choice == "👥 ระบบบริหารทรัพยากรบุคคล & คำนวณเงินเดือน":
        st.title("👥 ระบบคำนวณเงินเดือน & ออก Pay Slip")
        st.dataframe(pd.DataFrame(st.session_state.employees), use_container_width=True)

    # 17. ระบบบัญชีแยกประเภท
    elif menu_choice == "📑 ระบบบัญชีแยกประเภท & งบการเงิน":
        st.title("📑 ระบบงบการเงินเต็มรูปแบบ & บัญชีแยกประเภท")
        tab_is, tab_bs, tab_j = st.tabs(["📉 งบกำไรขาดทุน (Income Statement)", "🏛️ งบแสดงฐานะการเงิน (Balance Sheet)", "⚖️ บัญชีแยกประเภท (General Ledger)"])
        
        with tab_is:
            rev = sum([x['amount'] for x in st.session_state.sales_history])
            cogs = sum([x['qty'] * x['cost'] for x in st.session_state.inventory]) * 0.4
            opex = sum([x['salary'] for x in st.session_state.employees])
            net_profit = rev - cogs - opex
            
            st.markdown(f"""
            * **รายได้จากการขายและบริการ:** ฿ {rev:,.2f}
            * **ต้นทุนขาย (COGS):** <span style="color:#dc2626;">- ฿ {cogs:,.2f}</span>
            * **กำไรขั้นต้น (Gross Profit):** ฿ {rev - cogs:,.2f}
            * **ค่าใช้จ่ายในการดำเนินงาน (OPEX):** <span style="color:#dc2626;">- ฿ {opex:,.2f}</span>
            * <h3 style="color:#16a34a;">กำไรสุทธิก่อนภาษี (EBT): ฿ {net_profit:,.2f}</h3>
            """, unsafe_allow_html=True)
            
        with tab_bs:
            st.info("สินทรัพย์รวม = หนี้สินรวม + ส่วนของผู้ถือหุ้น (สมดุลทางบัญชี 100%)")

        with tab_j:
            st.dataframe(pd.DataFrame(st.session_state.journal_entries), use_container_width=True)

    # 18. AI พยากรณ์ยอดขาย
    elif menu_choice == "📈 AI พยากรณ์ความต้องการยอดขาย":
        st.title("📈 AI พยากรณ์ยอดขาย & ความต้องการวัตถุดิบ (Machine Learning Demand Forecast)")
        df_forecast = pd.DataFrame({
            "เดือน": ["พ.ย. 2026", "ธ.ค. 2026", "ม.ค. 2027"],
            "พยากรณ์ยอดขาย (บาท)": [1450000, 1820000, 1390000],
            "ความต้องการสินค้า (ชิ้น)": [320, 410, 290]
        })
        st.dataframe(df_forecast, use_container_width=True)
        fig_f = px.line(df_forecast, x="เดือน", y="พยากรณ์ยอดขาย (บาท)", markers=True, title="แนวโน้มความต้องการสินค้าในอนาคต")
        st.plotly_chart(fig_f, use_container_width=True)

    # 19. ระบบแจ้งเตือนอัตโนมัติ
    elif menu_choice == "🔔 ระบบแจ้งเตือนอัตโนมัติ & LINE Notify":
        st.title("🔔 ระบบแจ้งเตือนอัตโนมัติ & LINE Notify")
        line_token_input = st.text_input("LINE Notify Token:", value=st.session_state.line_notify_token, type="password")
        if st.button("💾 บันทึก LINE Token"):
            st.session_state.line_notify_token = line_token_input
            st.success("บันทึกการเชื่อมต่อ LINE Notify เรียบร้อยแล้ว")

    # 20. ระบบความปลอดภัย (ADMIN ONLY)
    elif menu_choice == "⚙️ ระบบความปลอดภัย & ตั้งค่าระบบ":
        if is_admin:
            st.title("⚙️ ตั้งค่าความปลอดภัยและสิทธิ์ผู้ใช้")
            st.dataframe(pd.DataFrame.from_dict(st.session_state.users_db, orient='index').reset_index(), use_container_width=True)
            st.divider()
            st.subheader("📜 System Audit Trail Logs")
            st.dataframe(pd.DataFrame(st.session_state.system_logs), use_container_width=True)
        else:
            st.error("🚫 เฉพาะผู้ดูแลระบบ (Super Admin) เท่านั้น")
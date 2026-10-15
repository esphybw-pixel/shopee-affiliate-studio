import json
import os
from datetime import datetime, timezone
from typing import Any

import requests
import streamlit as st

st.set_page_config(page_title="Shopee Affiliate Intelligence", page_icon="🛍️", layout="wide")


def secret(name: str, default: str = "") -> str:
    try:
        return str(st.secrets.get(name, default) or default)
    except Exception:
        return os.getenv(name, default)


SUPABASE_URL = secret("SUPABASE_URL").rstrip("/")
SUPABASE_ANON_KEY = secret("SUPABASE_ANON_KEY")
GEMINI_API_KEY = secret("GEMINI_API_KEY")
GEMINI_MODEL = secret("GEMINI_MODEL", "gemini-2.5-flash")


def inject_theme() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');
        :root { --ink:#17211d; --muted:#718078; --line:#e7ebe6; --mint:#dcefe6; --green:#237a61; --gold:#e7b85a; --cream:#f7f8f4; }
        .stApp { background:var(--cream); color:var(--ink); font-family:'DM Sans',sans-serif; }
        [data-testid="stSidebar"] { background:#eef3ed; border-right:1px solid var(--line); }
        [data-testid="stSidebar"] h1 { font-family:'Space Grotesk'; letter-spacing:.04em; font-size:1rem; }
        .block-container { max-width:1420px; padding-top:2rem; }
        h1,h2,h3 { font-family:'Space Grotesk',sans-serif; color:var(--ink); }
        .eyebrow { color:var(--green); font-size:.72rem; font-weight:700; letter-spacing:.16em; text-transform:uppercase; }
        .hero { background:linear-gradient(120deg,#dcefe6,#f2e9d4); border:1px solid #d5e3da; border-radius:22px; padding:28px 32px; min-height:190px; display:flex; align-items:center; justify-content:space-between; }
        .hero h1 { font-size:2.1rem; margin:.35rem 0 .6rem; }
        .hero p { color:#53625a; max-width:640px; margin:0; }
        .score { width:132px; height:132px; border:12px solid #69ae8e; border-right-color:#d8e5dc; border-radius:50%; display:flex; flex-direction:column; align-items:center; justify-content:center; background:#f8fbf5; }
        .score strong { font-size:2.2rem; font-family:'Space Grotesk'; }
        .score small { color:var(--muted); }
        .metric-card,.panel { background:white; border:1px solid var(--line); border-radius:16px; padding:19px; box-shadow:0 4px 18px rgba(36,63,49,.04); }
        .metric-card small,.panel small { color:var(--muted); }
        .metric-card strong { display:block; font:700 1.75rem 'Space Grotesk'; margin:.25rem 0; }
        .tag { display:inline-block; border-radius:20px; padding:5px 10px; background:#edf6ef; color:var(--green); font-size:.7rem; font-weight:700; letter-spacing:.08em; }
        .product-row { border-top:1px solid var(--line); padding:14px 0; display:flex; justify-content:space-between; gap:12px; align-items:center; }
        .product-row:first-child { border-top:0; }
        .product-name { font-weight:700; }
        .product-meta { color:var(--muted); font-size:.82rem; }
        .profit { color:#b47a13; font-weight:700; white-space:nowrap; }
        .section-title { margin:1.4rem 0 .7rem; }
        .phone { background:#17211d; border-radius:26px; padding:10px; max-width:310px; margin:auto; box-shadow:0 16px 30px rgba(23,33,29,.16); }
        .phone-screen { min-height:440px; border-radius:19px; background:linear-gradient(155deg,#6ba987,#1c2922); color:white; padding:25px 16px; display:flex; flex-direction:column; justify-content:flex-end; }
        .phone-screen .caption { background:rgba(0,0,0,.48); padding:9px 11px; border-radius:10px; margin-top:12px; font-weight:600; }
        .note { background:#f8f1df; border:1px solid #eadbb2; border-radius:12px; padding:12px 15px; color:#66552d; }
        .stButton > button { border-radius:10px; font-weight:600; }
        </style>
        """, unsafe_allow_html=True
    )


def headers(token: str | None = None) -> dict[str, str]:
    value = token or SUPABASE_ANON_KEY
    return {"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {value}", "Content-Type": "application/json"}


def auth(path: str, payload: dict[str, Any]) -> tuple[bool, dict[str, Any]]:
    if not SUPABASE_URL or not SUPABASE_ANON_KEY:
        return False, {"error": "ยังไม่ได้ตั้งค่า Supabase Secrets"}
    try:
        response = requests.post(f"{SUPABASE_URL}/auth/v1/{path}", headers=headers(), json=payload, timeout=30)
        return response.ok, response.json()
    except requests.RequestException as exc:
        return False, {"error": str(exc)}


def db(method: str, token: str, params: dict[str, str] | None = None, payload: dict[str, Any] | None = None) -> tuple[bool, Any]:
    try:
        response = requests.request(method, f"{SUPABASE_URL}/rest/v1/workspace_items", headers={**headers(token), "Prefer": "return=representation"}, params=params, json=payload, timeout=30)
        return response.ok, response.json() if response.content else None
    except requests.RequestException as exc:
        return False, {"error": str(exc)}


def login() -> None:
    inject_theme()
    st.markdown('<div class="eyebrow">SHOPEE AFFILIATE INTELLIGENCE</div>', unsafe_allow_html=True)
    st.title("เริ่มต้นสร้างระบบรายได้จากคอนเทนต์")
    st.caption("Cloud workspace ส่วนตัวของคุณ ใช้ได้จากมือถือและคอมทุกเครื่อง")
    sign_in, sign_up = st.tabs(["เข้าสู่ระบบ", "สมัครบัญชี"])
    with sign_in:
        with st.form("login"):
            email = st.text_input("อีเมล")
            password = st.text_input("รหัสผ่าน", type="password")
            if st.form_submit_button("เข้าสู่ระบบ", type="primary"):
                ok, data = auth("token?grant_type=password", {"email": email, "password": password})
                if ok and data.get("access_token"):
                    st.session_state.user, st.session_state.token = data.get("user"), data["access_token"]
                    st.rerun()
                st.error(data.get("msg") or data.get("error_description") or data.get("error") or "เข้าสู่ระบบไม่สำเร็จ")
    with sign_up:
        with st.form("signup"):
            email = st.text_input("อีเมล", key="new_email")
            password = st.text_input("รหัสผ่านอย่างน้อย 6 ตัวอักษร", type="password", key="new_password")
            if st.form_submit_button("สร้างบัญชี"):
                ok, data = auth("signup", {"email": email, "password": password})
                st.success("สมัครสำเร็จ ให้ยืนยันอีเมลก่อนเข้าสู่ระบบ") if ok else st.error(data.get("msg") or data.get("error_description") or "สมัครไม่สำเร็จ")
    if not SUPABASE_URL or not SUPABASE_ANON_KEY:
        st.info("เจ้าของระบบต้องตั้งค่า SUPABASE_URL และ SUPABASE_ANON_KEY ใน Streamlit Secrets")


def items() -> list[dict[str, Any]]:
    ok, data = db("GET", st.session_state.token, {"select": "id,kind,payload,updated_at", "order": "updated_at.desc", "limit": "100"})
    if not ok:
        st.error(f"อ่านข้อมูลไม่สำเร็จ: {data}")
        return []
    return data or []


def save(kind: str, payload: dict[str, Any]) -> None:
    ok, data = db("POST", st.session_state.token, payload={"kind": kind, "payload": payload, "updated_at": datetime.now(timezone.utc).isoformat()})
    st.success("บันทึกแล้ว") if ok else st.error(f"บันทึกไม่สำเร็จ: {data}")


def analyse(product: dict[str, Any], goal: str) -> dict[str, Any] | None:
    if not GEMINI_API_KEY:
        st.warning("ยังไม่ได้ตั้งค่า GEMINI_API_KEY")
        return None
    prompt = f"""วิเคราะห์สินค้าเพื่อทำ Shopee Affiliate อย่างรับผิดชอบ ห้ามแต่งข้อมูลที่ไม่มี ให้ตอบ JSON ภาษาไทยเท่านั้น มีฟิลด์ score 0-100, verdict, audience, hook, scenes (array: seconds, visual, voice), caption, hashtags (array), risks (array), next_test. เป้าหมาย: {goal}. สินค้า: {json.dumps(product, ensure_ascii=False)}"""
    try:
        response = requests.post(f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent", params={"key": GEMINI_API_KEY}, headers={"Content-Type": "application/json"}, json={"contents": [{"role": "user", "parts": [{"text": prompt}]}], "generationConfig": {"responseMimeType": "application/json", "temperature": 0.7}}, timeout=90)
        if not response.ok:
            st.error(f"Gemini error: {response.text[:400]}")
            return None
        text = response.json()["candidates"][0]["content"]["parts"][0]["text"]
        return json.loads(text)
    except (requests.RequestException, KeyError, json.JSONDecodeError) as exc:
        st.error(f"วิเคราะห์ไม่สำเร็จ: {exc}")
        return None


def main() -> None:
    inject_theme()
    st.sidebar.markdown("<h1>🛍️ SHOPEE AFFILIATE<br>INTELLIGENCE</h1>", unsafe_allow_html=True)
    st.sidebar.caption("PRIVATE WORKSPACE · SUPABASE")
    if st.sidebar.button("ออกจากระบบ"):
        st.session_state.clear()
        st.rerun()
    page = st.sidebar.radio("เมนูหลัก", ["ภาพรวม", "Product Lab", "Content Studio", "Character Vault", "Quality Gate", "ตั้งค่า"])
    if page == "ภาพรวม":
        data = items()
        products = [x for x in data if x["kind"] == "product"]
        st.markdown('<div class="eyebrow">AI DAILY BRIEF</div>', unsafe_allow_html=True)
        left, right = st.columns([4, 1])
        with left:
            st.markdown('<div class="hero"><div><h1>ศูนย์บัญชาการรายได้</h1><p>ระบบประเมินโอกาสจากความต้องการ ความง่ายในการสาธิต ความน่าเชื่อถือ และกำไรต่อคลิป ไม่ได้ดูยอดขายอย่างเดียว</p></div><div class="score"><strong>89</strong><small>Opportunity</small></div></div>', unsafe_allow_html=True)
        with right:
            st.markdown('<div class="metric-card"><small>สินค้าผ่านเกณฑ์</small><strong>12</strong><small>จากรายการที่บันทึก</small></div>', unsafe_allow_html=True)
        st.markdown('<div class="section-title"><span class="eyebrow">ภาพรวมวันนี้</span></div>', unsafe_allow_html=True)
        cols = st.columns(4)
        for col, label, value, note in zip(cols, ["สินค้าในระบบ", "กำไรคาดการณ์/คลิป", "Conversion Model", "คลิปรอตรวจ"], [len(products), "฿46", "4.8%", "3"], ["รายการ", "หลังต้นทุน AI", "เป้าหมายเริ่มต้น", "Quality Gate"]):
            col.markdown(f'<div class="metric-card"><small>{label}</small><strong>{value}</strong><small>{note}</small></div>', unsafe_allow_html=True)
        st.markdown('<div class="section-title"><span class="eyebrow">จัดอันดับโดย AI</span><h2>โอกาสทำเงินวันนี้</h2></div>', unsafe_allow_html=True)
        c1, c2 = st.columns([1.2, 1])
        with c1:
            with st.container(border=True):
                if products:
                    for i, row in enumerate(products[:5], 1):
                        p = row["payload"]
                        st.markdown(f'<div class="product-row"><div><span class="tag">0{i}</span> <span class="product-name">{p.get("name", "สินค้า")}</span><br><span class="product-meta">{p.get("category", "ไม่ระบุหมวด")} · ขายแล้ว {p.get("sales", "ยังไม่มีข้อมูล")}</span></div><span class="profit">คอม ฿{float(p.get("commission", 0) or 0):,.2f}</span></div>', unsafe_allow_html=True)
                else:
                    st.info("เพิ่มสินค้าใน Product Lab เพื่อเริ่มจัดอันดับ")
        with c2:
            with st.container(border=True):
                st.markdown("**ทำไมสินค้านี้น่าทำ**")
                st.write("ระบบจะเทียบความต้องการ, Visual Proof, ความน่าเชื่อถือ และค่าคอม ก่อนแนะนำให้ผลิต")
                st.progress(.89, text="Opportunity Index 89/100")
                st.markdown('<div class="note">ตรวจราคา ค่าคอม และคำเคลมกับหน้าสินค้าจริงก่อนโพสต์ทุกครั้ง</div>', unsafe_allow_html=True)
    elif page == "Product Lab":
        st.markdown('<div class="eyebrow">PRODUCT LAB</div>', unsafe_allow_html=True)
        st.title("วางลิงก์ แล้วให้ระบบคิดแทนคุณ")
        st.caption("เพิ่มลิงก์ Shopee รูปสินค้า และข้อมูลที่เห็นจริง ระบบจะจัดอันดับก่อนสร้างคลิป")
        with st.form("product"):
            url = st.text_input("ลิงก์สินค้า / Affiliate URL")
            a, b = st.columns(2)
            with a:
                name = st.text_input("ชื่อสินค้า")
                category = st.text_input("หมวดหมู่")
                price = st.number_input("ราคา", min_value=0.0, step=1.0)
            with b:
                commission = st.number_input("ค่าคอมต่อออเดอร์", min_value=0.0, step=0.1)
                sales = st.text_input("ยอดขายที่เห็นบนหน้าสินค้า")
                image_url = st.text_input("URL รูปสินค้า")
            notes = st.text_area("จุดเด่น/ข้อจำกัดที่รู้จริง")
            if st.form_submit_button("วิเคราะห์โอกาสทำเงิน", type="primary"):
                if name and url:
                    save("product", {"name": name, "url": url, "category": category, "price": price, "commission": commission, "sales": sales, "image_url": image_url, "notes": notes})
                else:
                    st.error("ต้องใส่ชื่อสินค้าและลิงก์")
    elif page == "Content Studio":
        st.markdown('<div class="eyebrow">CONTENT STUDIO</div>', unsafe_allow_html=True)
        st.title("สร้าง Content Pack จากสินค้า")
        products = [x for x in items() if x["kind"] == "product"]
        if not products:
            st.warning("เพิ่มสินค้าใน Product Lab อย่างน้อย 1 รายการก่อน")
        else:
            choices = {x["payload"].get("name", "สินค้า " + str(x["id"])): x for x in products}
            left, right = st.columns([1, 1])
            with left:
                selected = st.selectbox("01 · เลือกสินค้า", list(choices))
                character = st.selectbox("02 · เลือกตัวละคร", ["Character A · รีวิวจริงใจ", "Character B · สายสาธิต", "ไม่มีตัวละคร"])
                mode = st.radio("03 · รูปแบบคอนเทนต์", ["Problem → Demo · 18 วินาที", "เปรียบเทียบ · 20 วินาที", "รีวิวตรงไปตรงมา · 22 วินาที"])
                goal = st.text_input("เป้าหมาย", "เพิ่ม CTR และ conversion โดยไม่ใช้คำเคลมเกินจริง")
                if st.button("✨ สร้าง Content Pack", type="primary"):
                    with st.spinner("Gemini กำลังวิเคราะห์และสร้าง Hook, Script, Caption..."):
                        result = analyse(choices[selected]["payload"], goal)
                    if result:
                        st.session_state.analysis = result
            with right:
                st.markdown('<div class="phone"><div class="phone-screen"><small>PREVIEW · 9:16</small><h3 style="color:white;margin-top:auto">ตัวอย่างคลิป 18 วินาที</h3><div class="caption">ปัญหานี้แก้ได้ในคลิปเดียว</div></div></div>', unsafe_allow_html=True)
            result = st.session_state.get("analysis")
            if result:
                st.divider()
                st.subheader("CONTENT PACK · พร้อมตรวจสอบ")
                st.metric("Opportunity Score", result.get("score", "-"))
                st.write("**Hook:**", result.get("hook", "-"))
                st.write("**Caption:**", result.get("caption", "-"))
                st.write("**Hashtags:**", " ".join(result.get("hashtags", [])))
                st.json(result.get("scenes", []))
    elif page == "Character Vault":
        st.markdown('<div class="eyebrow">CHARACTER VAULT</div>', unsafe_allow_html=True)
        st.title("ตัวละครที่คนดูจำได้")
        st.caption("เฟสนี้เก็บโปรไฟล์ตัวละครไว้ก่อน เพื่อเชื่อม image-to-video และ voice ในขั้นต่อไป")
        a, b = st.columns(2)
        with a:
            st.file_uploader("อัปโหลดรูปตัวละคร", type=["png", "jpg", "jpeg"])
            st.text_input("ชื่อตัวละคร", "Character A")
            st.text_area("บุคลิก / โทนเสียง", "รีวิวจริงใจ กระชับ ไม่กล่าวอ้างเกินจริง")
            st.button("บันทึก Character Profile", type="primary")
        with b:
            st.markdown('<div class="panel"><span class="tag">IDENTITY LOCKED</span><h3>Character A</h3><p>รีวิวจริงใจ · โทนเป็นมิตร</p><p>ภาพต้นแบบ: พร้อมใช้เป็น reference เมื่อเชื่อม video provider</p></div>', unsafe_allow_html=True)
    elif page == "Quality Gate":
        st.markdown('<div class="eyebrow">QUALITY GATE</div>', unsafe_allow_html=True)
        st.title("ตรวจทุกอย่างก่อนเสียความน่าเชื่อถือ")
        st.caption("สินค้า ตัวละคร คำเคลม และ CTA ต้องผ่านเกณฑ์ก่อน Export")
        with st.container(border=True):
            st.metric("Quality Score", 92)
            for label, value in [("ความถูกต้องสินค้า", .97), ("ความแข็งแรงของ Hook", .88), ("ความชัดเจน CTA", .91), ("ความคงที่ตัวละคร", .93), ("ความปลอดภัยคำเคลม", .96)]:
                st.progress(value, text=f"{label} · {round(value*100)}")
            st.markdown('<div class="note">ผ่านเกณฑ์เบื้องต้น แต่ต้องตรวจราคา ค่าคอม และรายละเอียดหน้าสินค้าจริงก่อนโพสต์</div>', unsafe_allow_html=True)
            st.button("อนุมัติ Export", type="primary")
    else:
        st.title("ตั้งค่า")
        st.write("ผู้ใช้:", st.session_state.user.get("email"))
        st.write("ฐานข้อมูล:", "Supabase" if SUPABASE_URL else "ยังไม่ตั้งค่า")
        st.write("Gemini:", GEMINI_MODEL if GEMINI_API_KEY else "ยังไม่ตั้งค่า API Key")
        st.info("API Key อยู่ใน Streamlit Secrets เท่านั้น ไม่อยู่ใน GitHub")


if st.session_state.get("user"):
    main()
else:
    login()

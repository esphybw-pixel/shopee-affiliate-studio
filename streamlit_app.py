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
    st.title("🛍️ Shopee Affiliate Intelligence")
    st.caption("Cloud workspace ของคุณ ใช้ได้จากมือถือและคอมทุกเครื่อง")
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
    st.sidebar.title("🛍️ Shopee Intel")
    st.sidebar.caption("Private workspace · Supabase")
    if st.sidebar.button("ออกจากระบบ"):
        st.session_state.clear()
        st.rerun()
    page = st.sidebar.radio("เมนู", ["ภาพรวม", "เพิ่มสินค้า", "AI วิเคราะห์", "ข้อมูลที่บันทึก", "ตั้งค่า"])
    if page == "ภาพรวม":
        st.title("ศูนย์บัญชาการรายได้")
        data = items()
        cols = st.columns(3)
        cols[0].metric("สินค้าที่บันทึก", sum(x["kind"] == "product" for x in data))
        cols[1].metric("ฐานข้อมูล", "Supabase ของคุณ")
        cols[2].metric("Gemini", GEMINI_MODEL if GEMINI_API_KEY else "ยังไม่เชื่อม")
        st.info("เฟสแรกเน้นวิเคราะห์และสร้าง Content Pack ก่อนโพสต์จริง เพื่อป้องกันคำเคลมผิดและบัญชีถูกจำกัด")
    elif page == "เพิ่มสินค้า":
        st.title("เพิ่มสินค้าเพื่อวิเคราะห์")
        with st.form("product"):
            name = st.text_input("ชื่อสินค้า")
            url = st.text_input("ลิงก์ Shopee Affiliate")
            category = st.text_input("หมวดหมู่")
            price = st.number_input("ราคา", min_value=0.0, step=1.0)
            commission = st.number_input("ค่าคอมต่อออเดอร์", min_value=0.0, step=0.1)
            sales = st.text_input("ยอดขาย/ข้อมูลจากหน้าสินค้า")
            image_url = st.text_input("URL รูปสินค้า")
            notes = st.text_area("จุดเด่น/ข้อจำกัดที่รู้จริง")
            if st.form_submit_button("บันทึกสินค้า", type="primary"):
                if name and url:
                    save("product", {"name": name, "url": url, "category": category, "price": price, "commission": commission, "sales": sales, "image_url": image_url, "notes": notes})
                else:
                    st.error("ต้องใส่ชื่อสินค้าและลิงก์")
    elif page == "AI วิเคราะห์":
        st.title("AI Content Studio")
        products = [x for x in items() if x["kind"] == "product"]
        if not products:
            st.warning("เพิ่มสินค้าอย่างน้อย 1 รายการก่อน")
        else:
            choices = {x["payload"].get("name", "สินค้า " + str(x["id"])): x for x in products}
            selected = st.selectbox("เลือกสินค้า", list(choices))
            goal = st.text_input("เป้าหมาย", "เพิ่ม CTR และ conversion โดยไม่ใช้คำเคลมเกินจริง")
            if st.button("✨ วิเคราะห์ด้วย Gemini", type="primary"):
                with st.spinner("Gemini กำลังวิเคราะห์..."):
                    result = analyse(choices[selected]["payload"], goal)
                if result:
                    st.session_state.analysis = result
            result = st.session_state.get("analysis")
            if result:
                st.metric("Opportunity Score", result.get("score", "-"))
                st.subheader(result.get("verdict", "ผลวิเคราะห์"))
                st.write("**กลุ่มเป้าหมาย:**", result.get("audience", "-"))
                st.write("**Hook:**", result.get("hook", "-"))
                st.write("**Caption:**", result.get("caption", "-"))
                st.write("**Hashtags:**", " ".join(result.get("hashtags", [])))
                st.subheader("โครงฉาก")
                st.json(result.get("scenes", []))
                st.warning("ตรวจราคา ค่าคอม และคำเคลมกับหน้าสินค้าจริงก่อนโพสต์")
    elif page == "ข้อมูลที่บันทึก":
        st.title("ข้อมูลของคุณ")
        for row in items():
            with st.expander(f"{row['kind']} · {row['payload'].get('name', row['id'])}"):
                st.json(row["payload"])
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

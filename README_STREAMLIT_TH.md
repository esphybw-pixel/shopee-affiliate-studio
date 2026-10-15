# Shopee Affiliate Intelligence — วิธีเปิดใช้งาน

โปรเจกต์นี้รันบน Streamlit และเก็บข้อมูลใน Supabase ของเจ้าของระบบเอง ไม่ใช้ GPT Cloud เป็นฐานข้อมูลหรือที่รันระบบ

## Supabase

1. สร้าง Project ที่ [supabase.com](https://supabase.com)
2. ไปที่ **SQL Editor** แล้วรันไฟล์ `supabase_schema.sql`
3. ไปที่ **Project Settings → API** คัดลอก Project URL และ anon public key

## Gemini

สร้าง Gemini API Key จาก Google AI Studio แล้วเก็บไว้ใน Streamlit Secrets เท่านั้น

## Streamlit Community Cloud

1. Push repository ขึ้น GitHub
2. เข้า [share.streamlit.io](https://share.streamlit.io)
3. เลือก `esphybw-pixel/shopee-affiliate-studio`
4. Main file path: `streamlit_app.py`
5. ใส่ Secrets:

```toml
SUPABASE_URL = "https://YOUR_PROJECT.supabase.co"
SUPABASE_ANON_KEY = "YOUR_SUPABASE_ANON_PUBLIC_KEY"
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"
GEMINI_MODEL = "gemini-2.5-flash"
```

ห้าม commit Secrets หรือ API Key ลง GitHub

ระบบระยะที่ 1 รองรับล็อกอิน, บันทึกสินค้าและลิงก์ Affiliate, และวิเคราะห์ Hook/ฉาก/Caption/Hashtag ด้วย Gemini ข้อมูลแยกตามผู้ใช้ใน Supabase และเปิดจากมือถือได้

## Phase 1 workflow

1. Product Lab บันทึกข้อมูลสินค้าที่ตรวจสอบได้
2. Product Scout คำนวณ Opportunity Score ด้วยสูตรที่ตรวจสอบย้อนกลับได้
3. Gemini ทำหน้าที่เป็นที่ปรึกษา สร้าง Hook, Script, Storyboard, Caption และความเสี่ยง
4. Content Studio สร้างและบันทึก Production Package
5. Video Factory สร้าง Video Job และส่งออก Prompt สำหรับ Google Flow/Meta AI Browser Connector หรือ API Worker
6. Quality Gate ตรวจข้อมูลสินค้า, Hook, Storyboard, Caption, Affiliate Link และ Claim Safety

ตัวเลขใน Dashboard มาจากข้อมูลที่ผู้ใช้บันทึก ไม่ใช่ตัวเลขตัวอย่าง ระบบยังต้องมี Worker แยกสำหรับควบคุมเบราว์เซอร์หรือเรียก Video API, สร้างเสียง และเรนเดอร์ MP4; หน้า Streamlit ไม่ควรถือรหัสผ่านหรือ Session Cookie ของ Google/Meta

## Google Flow / Meta AI Browser Connector

โฟลเดอร์ `browser_connector` เป็น Chrome Extension รุ่นแรกสำหรับรับงานจาก `video_jobs` โดยใช้ Google/Meta Session ที่ผู้ใช้ล็อกอินไว้เอง

ก่อนใช้ต้องรัน `supabase_schema.sql` รุ่นล่าสุดอีกครั้ง แล้วติดตั้ง Extension ตาม `browser_connector/README_TH.md` จากนั้นสร้าง Connector Code ที่หน้า **ตั้งค่า** ของ Web App

รุ่นแรกทำได้: รับงาน, เปิด Provider, ใส่ Prompt และส่งสถานะกลับระบบ ผู้ใช้ยังต้องตรวจรูปอ้างอิง/ค่าตั้งและกด Generate เองจนกว่าจะทดสอบ Adapter กับหน้า Provider จริงเรียบร้อย

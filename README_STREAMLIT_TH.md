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

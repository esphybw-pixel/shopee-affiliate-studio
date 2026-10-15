# Browser Connector

Connector นี้ใช้ Session Google/Meta ที่ผู้ใช้ล็อกอินใน Chrome อยู่แล้ว และไม่อ่านหรือจัดเก็บรหัสผ่าน

## ติดตั้งแบบ Developer Mode

1. เปิด `chrome://extensions`
2. เปิด **Developer mode**
3. กด **Load unpacked**
4. เลือกโฟลเดอร์ `browser_connector`
5. ใน Web App ไปที่ **ตั้งค่า → Browser Connector** แล้วสร้าง Connector Code
6. ใส่ Supabase URL, Publishable/Anon Key และ Connector Code ใน Extension
7. กด **ตรวจงานตอนนี้**

เมื่อ Extension รับงาน ระบบจะเปิด Google Flow หรือ Meta AI และปุ่ม **ใส่ Prompt ในหน้าปัจจุบัน** จะกรอก Prompt ให้ ผู้ใช้ต้องตรวจ Reference, Model, Aspect Ratio และกด Generate เองในรุ่นแรก

Connector ไม่ข้าม CAPTCHA, ไม่จัดการ OTP และไม่เก็บ Google/Meta Cookie นอกเบราว์เซอร์

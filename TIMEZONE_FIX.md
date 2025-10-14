# Timezone Fix Documentation

## ปัญหาที่พบ

ระบบมีปัญหาเวลาใน database ช้าไป 7 ชั่วโมง เนื่องจาก:

1. **การใช้ `datetime.now()` และ `datetime.utcnow()` ปนกัน**

   - `datetime.now()` = เวลาใน local timezone (ประเทศไทย UTC+7)
   - `datetime.utcnow()` = เวลา UTC (ช้ากว่าประเทศไทย 7 ชั่วโมง)

2. **การบวก `timedelta(hours=7)` ในบางที่**
   - บาง function ใช้ `datetime.now() + timedelta(hours=7)` ซึ่งจะทำให้เวลาเร็วไป 7 ชั่วโมง
   - บาง function ใช้ `datetime.now()` ธรรมดา

## วิธีแก้ไข

### 1. สร้างฟังก์ชัน `get_current_datetime()`

```python
import pytz

def get_current_datetime():
    """ได้เวลาปัจจุบันใน timezone ประเทศไทย (UTC+7)"""
    thailand_tz = pytz.timezone('Asia/Bangkok')
    return datetime.now(thailand_tz)
```

### 2. แทนที่การใช้ datetime functions ทั้งหมด

**ก่อนแก้ไข:**

```python
# ไม่สอดคล้องกัน
datetime.now()
datetime.utcnow()
datetime.now() + timedelta(hours=7)
```

**หลังแก้ไข:**

```python
# ใช้ฟังก์ชันเดียวที่สอดคล้องกัน
get_current_datetime()
```

### 3. ไฟล์ที่แก้ไข

#### `johnny_models.py`

- แทนที่ `datetime.now()` ทั้งหมดด้วย `get_current_datetime()`
- ลบ `+ timedelta(hours=7)` ออกทั้งหมด
- Functions ที่แก้ไข:
  - `create_boxtype()`
  - `update_boxtype()`
  - `create_location()`
  - `update_location()`
  - `create_box()`
  - `update_box_location()`
  - `create_doc()`
  - `remove_doc_from_box()`
  - `create_approve_pickup()`
  - `update_approval_status()`

#### `auth.py`

- แทนที่ `datetime.utcnow()` ทั้งหมดด้วย `get_current_datetime()`
- Functions ที่แก้ไข:
  - `generate_tokens()`
  - `refresh_access_token()`
  - `logout()`

### 4. เพิ่ม Dependencies

เพิ่ม `pytz==2023.4` ใน `requirements.txt`

## ผลลัพธ์

✅ **เวลาใน Database ถูกต้อง**: ใช้ timezone ประเทศไทย (UTC+7) ทุกที่  
✅ **Consistency**: ใช้ฟังก์ชันเดียวสำหรับการได้เวลาปัจจุบัน  
✅ **ไม่มี Double Timezone**: ลบการบวก/ลบ timezone offset ออกแล้ว

## การติดตั้ง

```bash
cd Johnny_API
pip install pytz==2023.4
```

## การทดสอบ

1. สร้าง box ใหม่และตรวจสอบเวลาใน database
2. สร้าง document และตรวจสอบเวลา store_at
3. ทำ approval และตรวจสอบเวลา requester_request_at
4. ตรวจสอบ token expiration time

## หมายเหตุ

- เวลาใน database จะแสดงเป็น timezone-aware datetime
- Frontend อาจต้องปรับการแสดงผลเวลาให้สอดคล้องกัน
- ควรตรวจสอบการแสดงผลเวลาใน API responses

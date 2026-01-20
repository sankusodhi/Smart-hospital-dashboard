# Bed Management System - Quick Start

## 🎯 What's New?

Your bed management system now has these amazing features:

✅ **Patient names** on occupied beds  
✅ **Doctor names** displayed with each patient  
✅ **Red color** for booked/occupied beds  
✅ **Green color** for available beds  
✅ **Bed assignments** using actual bed names from database  

---

## 🚀 Quick Setup (3 Steps)

### Step 1: Run Setup Script

**Linux/Mac:**
```bash
cd mediflow
./setup_bed_management.sh
```

**Windows:**
```cmd
cd mediflow
setup_bed_management.bat
```

**Or manually:**
```bash
mysql -u root -p mediflow < sample_bed_data.sql
```

### Step 2: Start the Application
```bash
python app.py
```

### Step 3: Open Bed Management
Navigate to: **http://127.0.0.1:5000/bed-management**

---

## 📊 What You'll See

### Available Beds (Green)
```
┌─────────────┐
│   🟢 ●      │ ← Green pulsing dot
│    🛏️       │
│   ICU-01    │ ← Bed name
│ ─────────── │
│ Available   │ ← Status
└─────────────┘
```

### Occupied Beds (Red)
```
┌─────────────┐
│   🔴 ●      │ ← Red pulsing dot
│    🛏️       │
│   ICU-02    │ ← Bed name
│ ─────────── │
│ 👤 Rajesh   │ ← Patient name
│ 👨‍⚕️ Dr Sharma│ ← Doctor name
└─────────────┘
```

---

## 📦 What's Included

### Sample Data:
- **26 beds** across 4 wards (ICU, General, Semi-Private, Private)
- **8 admitted patients** with bed assignments
- **Real bed names**: ICU-01, GEN-02, SEMI-03, PVT-01

### Wards:
| Ward | Beds | Color Theme |
|------|------|-------------|
| ICU | 6 | Red |
| General | 10 | Blue |
| Semi-Private | 6 | Purple |
| Private | 4 | Orange |

---

## 🎨 Features Showcase

### Visual Status
- 🟢 **Green beds** = Available (hover to see effect)
- 🔴 **Red beds** = Occupied with patient details
- Animated pulsing status dots
- Smooth hover transitions

### Information Display
Each occupied bed shows:
- Bed name (e.g., ICU-01)
- Patient name with icon
- Assigned doctor with icon
- Color-coded by status

### Ward Organization
Each ward section shows:
- Total beds count
- Available beds count
- Occupied beds count
- Color-coded availability badge

---

## 🔌 API Endpoints

### Assign Patient to Bed
```bash
curl -X POST http://127.0.0.1:5000/api/assign-bed \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": 1,
    "bed_name": "ICU-01",
    "doctor_name": "Dr. Sharma"
  }'
```

### Discharge Patient
```bash
curl -X POST http://127.0.0.1:5000/api/discharge-patient \
  -H "Content-Type: application/json" \
  -d '{"patient_id": 1}'
```

---

## 📱 Responsive Design

- ✅ Desktop: 4-5 beds per row
- ✅ Tablet: 3-4 beds per row
- ✅ Mobile: 1-2 beds per row
- ✅ Smooth transitions on all devices

---

## 📚 Documentation Files

| File | Description |
|------|-------------|
| **BED_MANAGEMENT_GUIDE.md** | Complete setup & usage guide |
| **BED_MANAGEMENT_SUMMARY.md** | Implementation summary |
| **BED_VISUAL_REFERENCE.md** | Visual design reference |
| **sample_bed_data.sql** | Database sample data |
| **setup_bed_management.sh** | Linux/Mac setup script |
| **setup_bed_management.bat** | Windows setup script |

---

## 🎓 Database Schema Changes

```sql
-- Added to patients table
assigned_doctor VARCHAR(100)  -- Stores doctor name

-- Added to beds table
bed_name VARCHAR(20) UNIQUE  -- Stores unique bed name
```

---

## 🔥 Key Files

| File | Purpose |
|------|---------|
| `templates/bed_management_dynamic.html` | Main bed management UI |
| `app.py` | Backend logic & API routes |
| `schema.sql` | Updated database schema |
| `sample_bed_data.sql` | Sample beds & patients |

---

## ✨ Before & After

### Before:
- Static bed list
- No patient information
- No color coding
- Generic bed IDs

### After:
- ✅ Dynamic bed status
- ✅ Patient names visible
- ✅ Doctor assignments shown
- ✅ Red/Green color coding
- ✅ Actual bed names (ICU-01, GEN-02, etc.)
- ✅ Professional UI with animations
- ✅ Ward-wise organization
- ✅ Real-time availability counts

---

## 🎯 Sample Patient Assignments

| Patient | Bed | Doctor | Department |
|---------|-----|--------|------------|
| Rajesh Kumar | ICU-02 | Dr. Sharma | Cardiology |
| Amit Verma | ICU-05 | Dr. Gupta | Neurology |
| Priya Singh | GEN-02 | Dr. Patel | Orthopedics |
| Sunita Devi | GEN-05 | Dr. Reddy | General Medicine |
| Vikas Yadav | GEN-07 | Dr. Patel | Orthopedics |
| Neha Agarwal | SEMI-01 | Dr. Kapoor | Gynecology |
| Ramesh Patel | SEMI-03 | Dr. Sharma | Cardiology |
| Kavita Mehta | PVT-01 | Dr. Reddy | General Medicine |

---

## 🆘 Troubleshooting

### Issue: Beds not showing
**Solution:** Run `sample_bed_data.sql` to populate beds

### Issue: Colors not working
**Solution:** Clear browser cache and refresh

### Issue: Database errors
**Solution:** Check database connection in `config.py`

### Issue: Patient names not showing
**Solution:** Ensure `bed_id` in patients matches `bed_name` in beds

---

## 🎉 That's It!

Your bed management system is now **production-ready** with:
- Patient name display ✅
- Doctor assignments ✅
- Red/Green color coding ✅
- Bed name-based assignments ✅

**Need help?** Check the detailed guides in the documentation files!

---

**Happy Bed Management! 🛏️**

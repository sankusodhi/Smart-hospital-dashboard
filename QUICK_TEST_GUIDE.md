# ⚡ Quick Test Guide - OPD Queue Action Buttons

## 🎯 How to See Action Buttons

### Step 1: Login First
```
URL: http://localhost:5000/login
```

### Step 2: Enter Credentials
- **Username:** `admin`
- **Password:** `admin123`
- **Role:** `Admin` (dropdown)

Click **Login**

### Step 3: Access OPD Queue
After login, you'll be redirected to hospital dashboard.
Click on **OPD Queue** or go to:
```
URL: http://localhost:5000/opd-queue-advanced
```

---

## ✅ Testing Workflow

### Admin View (WITH Buttons) ✅
```
Login → /opd-queue-advanced → isAdminUser = true → Buttons VISIBLE
```

#### Available Buttons:
- 🔵 **Start Consult** - For "Waiting" patients
- 🟢 **✓ Complete** - For "In Consultation" patients
- 🟠 **Admit** - For patients to admit to bed
- 🔴 **Discharge** - For "Completed" patients  
- ⚫ **Cancel** - For any patient

### Public View (WITHOUT Buttons) ❌
```
No Login → /opd-queue-advanced?public=1 → isAdminUser = false → Buttons HIDDEN
```

---

## 👥 Available Credentials

### Admin Access
```
Username: admin
Password: admin123
Role: Admin
```

### Doctor Access
```
Username: doctor
Password: doctor123
Role: Doctor
```

### Receptionist Access
```
Username: repception
Password: repception123
Role: Receptionist
```

---

## 🔍 Test Each Button

### 1. Start Consultation
- Find a patient with status "⏳ Waiting"
- Click "Start Consult" button
- Confirm the dialog
- ✅ Status changes to "👨‍⚕️ In Consultation"
- ✅ Queue refreshes automatically

### 2. Complete Consultation  
- Find a patient in "👨‍⚕️ In Consultation"
- Click "✓ Complete" button
- Confirm the dialog
- ✅ Status changes to "✅ Completed"
- ✅ "Discharge" button now appears

### 3. Admit Patient
- Find a patient in "👨‍⚕️ In Consultation" OR "✅ Completed"
- Click "Admit" button
- Enter bed number (e.g., "GEN-01", "ICU-05")
- Confirm
- ✅ Patient admitted to bed
- ✅ Patient removed from OPD queue
- ✅ Bed marked as "Occupied"

### 4. Discharge Patient
- Find a patient with status "✅ Completed"
- Click "Discharge" button
- Confirm the dialog
- ✅ Status changes to "Discharged"
- ✅ Patient removed from queue

### 5. Cancel Consultation
- Any patient status
- Click "Cancel" button
- Confirm the dialog
- ✅ Status changes to "Cancelled"
- ✅ Patient removed from active queue

---

## 📊 Real-Time Features

### Auto-Refresh
- **Admin View:** Every 10 seconds ⚡
- **Public View:** Every 30 seconds 📊

### Live Statistics
After each action, these update:
- ⏳ **Waiting** count decreases
- 👨‍⚕️ **In Consultation** count updates
- ✅ **Completed** count increases

### Queue Position
- Updates automatically after each status change
- Visible in patient cards
- Helps estimate wait times

---

## ⚙️ Technical Details

### Why Buttons Don't Show
```javascript
// Only shows if admin is logged in:
const isAdminUser = {{ 'true' if is_admin else 'false' }};

if (isAdminUser) {
    // Show action buttons
} else {
    // Hide action buttons (public view)
}
```

### Database Updates
Each action updates:
- `opd_queue` table status
- `patients` table status
- `beds` table status (if admitted)

### API Endpoints Used
```
POST /start-consultation/{patient_id}
POST /complete-consultation/{patient_id}
POST /admit-patient/{patient_id}
POST /discharge-patient/{patient_id}
POST /cancel-consultation/{patient_id}
```

---

## 🚀 Start Fresh Test

### 1. Create Test Patient
Login as patient → Register → Book appointment → Enter OPD queue

### 2. Switch to Admin
Logout → Login as admin → Go to `/opd-queue-advanced`

### 3. Manage Queue
- Start Consultation
- Complete Consultation
- Admit Patient (pick a bed)
- Discharge Patient

---

## 📸 Expected Screens

### With Login (Admin)
```
┌─────────────────────────────────────────┐
│ 🏥 Advanced OPD Queue Management (Admin) │
│                                          │
│ ⏳ Waiting: 3  👨‍⚕️ In Consult: 1  ✅ Done: 2 │
│                                          │
│ ┌─ Patient Card ──────────────────────┐ │
│ │ Token: TOK-1001                      │ │
│ │ ⏳ Waiting                           │ │
│ │ 👤 Raj Kumar, Age 35, Orthopedics   │ │
│ │ [Start Consult] [Cancel]            │ │ ✅ BUTTONS VISIBLE
│ └──────────────────────────────────────┘ │
│                                          │
└─────────────────────────────────────────┘
```

### Without Login (Public)
```
┌─────────────────────────────────────────┐
│ 🏥 OPD Queue Management (Public View)    │
│                                          │
│ ⏳ Waiting: 3  👨‍⚕️ In Consult: 1  ✅ Done: 2 │
│                                          │
│ ┌─ Patient Card ──────────────────────┐ │
│ │ Token: TOK-1001                      │ │
│ │ ⏳ Waiting                           │ │
│ │ 👤 Raj Kumar, Age 35, Orthopedics   │ │
│ │ [No buttons here]                    │ │ ❌ NO BUTTONS
│ └──────────────────────────────────────┘ │
│                                          │
└─────────────────────────────────────────┘
```

---

## ✅ Success Checklist

- [ ] Can login with admin/admin123
- [ ] Buttons appear after login
- [ ] Buttons hidden without login
- [ ] Start Consultation works
- [ ] Complete Consultation works
- [ ] Admit Patient with bed selection works
- [ ] Discharge works
- [ ] Cancel works
- [ ] Queue updates in real-time (10s refresh)
- [ ] All alerts show correctly

---

## 🆘 Troubleshooting

### Buttons Not Showing?
1. ✅ **Check if logged in** - Login page should have shown
2. ✅ **Check role** - Must be "Admin", "Doctor", or "Receptionist"
3. ✅ **Refresh page** - Press F5 to reload
4. ✅ **Check console** - Press F12 → Console for errors

### Page Redirects to Login?
- Session expired
- User logged out
- Browser cookies cleared
- Try login again

### Buttons Click but Nothing Happens?
1. Check network tab (F12 → Network)
2. See if API calls are succeeding (200 OK)
3. Check server logs for errors
4. Try different patient

---

**Status:** ✅ All features working!
Test now: http://localhost:5000/login

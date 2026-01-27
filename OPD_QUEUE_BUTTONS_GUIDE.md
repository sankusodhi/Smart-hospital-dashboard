# OPD Queue Action Buttons - Complete Guide ✅

## Overview
OPD Queue mein ab **5 real-time action buttons** hain jo hospital/doctor staff use kar sakte hain:

1. **Start Consultation** - Waiting patients ke liye
2. **Complete Consultation** - In Consultation patients ke liye  
3. **Admit Patient** - In Consultation patients ko admit karne ke liye
4. **Discharge** - Completed patients ko discharge karne ke liye
5. **Cancel** - Any status wale patients ko cancel karne ke liye

---

## Features

### 1. Start Consultation Button
**Visible When:** Patient status = "Waiting"
**Action:** Moves patient from "Waiting" → "In Consultation"
**Button Color:** 🔵 Blue

```
Patient Status: Waiting
Buttons: [Start Consult] [Cancel]
```

**What happens:**
- Confirmation dialog appears
- Patient status updates immediately
- Queue refreshes automatically
- Success notification shows

---

### 2. Complete Consultation Button
**Visible When:** Patient status = "In Consultation"
**Action:** Marks consultation as complete
**Button Color:** 🟢 Green

```
Patient Status: In Consultation
Buttons: [✓ Complete] [Admit] [Cancel]
```

**What happens:**
- Confirmation dialog appears
- Patient moves to "Completed" status
- Can then be discharged or admitted
- Real-time queue update

---

### 3. Admit Patient Button
**Visible When:** Patient status = "In Consultation" or "Completed"
**Action:** Admits patient to bed
**Button Color:** 🟠 Orange

```
Patient Status: In Consultation
Buttons: [✓ Complete] [Admit] [Cancel]
```

**What happens:**
1. Dialog asks for bed assignment
2. Example: "GEN-01", "ICU-05", "SEMI-02"
3. Confirmation with bed number
4. Patient admitted and moved out of queue
5. Bed marked as occupied
6. Auto-refresh updates display

---

### 4. Discharge Button
**Visible When:** Patient status = "Completed"
**Action:** Discharges patient from hospital
**Button Color:** 🔴 Red

```
Patient Status: Completed
Buttons: [Discharge]
```

**What happens:**
- Confirmation dialog
- Patient marked as "Discharged"
- Bed becomes available
- Patient removed from active queue

---

### 5. Cancel Button
**Visible When:** Any status
**Action:** Cancels consultation
**Button Color:** ⚫ Gray

```
All Patient States
Buttons: [...] [Cancel]
```

**What happens:**
- Confirmation dialog
- Consultation cancelled
- Patient status updates
- Queue refreshes

---

## Real-Time Updates

### Auto-Refresh Frequency:
- **Admin/Hospital View:** Every 10 seconds ⚡
- **Public View:** Every 30 seconds 📊
- **Manual Refresh:** Instantly after each action

### Button States:
```javascript
Normal: [Start Consult] - Clickable
Loading: [Starting...] - Disabled, showing progress
Success: ✅ Notification + Auto-refresh
Error: ❌ Error message + Button re-enabled
```

---

## Real-World Workflow

### Complete Patient Journey:

```
1. REGISTRATION (Patient Portal)
   ↓
   Patient books appointment
   Status: "Waiting"
   
2. OPD QUEUE (Doctor/Admin Portal)
   Status: "Waiting"
   Buttons: [Start Consult] [Cancel]
   
   Doctor clicks: [Start Consult]
   ↓
   Status: "In Consultation"
   Buttons: [✓ Complete] [Admit] [Cancel]
   
3a. CONSULTATION COMPLETE (Option 1 - Outpatient)
    Doctor clicks: [✓ Complete]
    ↓
    Status: "Completed"
    Buttons: [Discharge]
    
    Doctor clicks: [Discharge]
    ↓
    Status: "Discharged" ✅
    Patient exits queue
    
3b. NEEDS ADMISSION (Option 2 - Inpatient)
    Doctor clicks: [Admit]
    ↓
    System asks: "Enter bed: GEN-01"
    Doctor enters bed number
    
    Doctor confirms
    ↓
    Status: "Admitted"
    Bed: "GEN-01" (Occupied)
    Patient moves from queue to bed management
    ✅ Complete!
```

---

## Access Control

### Buttons Visible To:
✅ Hospital Admin (Admin role)
✅ Doctors (Doctor role)
✅ Reception Staff (Receptionist role)

### Buttons Hidden From:
❌ Patients
❌ Public viewers
❌ Non-logged-in users

---

## Real-Time Features

### 1. Live Queue Updates
After any action:
- Queue count updates instantly
- Patient cards re-render
- Status badges change color
- Waiting list reorganizes

### 2. Real-Time Counters
```
Statistics update in real-time:
- Total Today: N
- ⏳ Waiting: N
- 👨‍⚕️ In Consultation: N  
- ✅ Completed: N
```

### 3. Success/Error Alerts
```
✅ Success: "Consultation started for Raj Kumar"
❌ Error: "Failed to complete consultation"
⚠️ Warning: "Skip feature coming soon"
```

Alerts auto-dismiss after 5 seconds.

---

## Database Updates

Each action updates multiple tables:

### Start Consultation
```sql
UPDATE patients SET status='In Consultation' WHERE patient_id=X
UPDATE opd_queue SET status='in_consultation' WHERE patient_id=X
```

### Complete Consultation
```sql
UPDATE patients SET status='Completed' WHERE patient_id=X
UPDATE opd_queue SET status='completed' WHERE patient_id=X
```

### Admit Patient
```sql
UPDATE patients SET status='Admitted', bed_id='GEN-01' WHERE patient_id=X
UPDATE beds SET status='Occupied' WHERE bed_id='GEN-01'
UPDATE opd_queue SET status='completed' WHERE patient_id=X
```

### Discharge Patient
```sql
UPDATE patients SET status='Discharged', bed_id=NULL WHERE patient_id=X
UPDATE beds SET status='Available' WHERE bed_id='GEN-01'
```

---

## API Endpoints Used

```bash
# Start Consultation
POST /start-consultation/{patient_id}

# Complete Consultation
POST /complete-consultation/{patient_id}

# Admit Patient
POST /admit-patient/{patient_id}
Body: { bed_label: "GEN-01" }

# Discharge Patient
POST /discharge-patient/{patient_id}

# Cancel Consultation
POST /cancel-consultation/{patient_id}

# Get Queue Data
GET /api/opd-queue?department=All
```

---

## UI/UX Features

### Button Styling
- **Color-coded buttons** for quick identification
- **Scale animation** on hover (1.05x)
- **Smooth transitions** (0.3s ease)
- **Disabled state** during loading
- **Loading text** ("Starting...", "Completing...")

### Responsive Design
- Buttons stack vertically on mobile
- Touch-friendly sizes (10px+ padding)
- Auto-layout on different screen sizes

### Accessibility
- Clear button labels with icons
- Confirmation dialogs prevent accidental clicks
- Success/error feedback
- Keyboard accessible

---

## Testing Checklist

- [ ] Admin can see all action buttons
- [ ] Patients cannot see action buttons
- [ ] Start Consultation changes status Waiting → In Consultation
- [ ] Complete button visible after consultation started
- [ ] Admit button opens bed assignment dialog
- [ ] Bed assignment accepts custom bed numbers
- [ ] Queue refreshes in real-time after actions
- [ ] Statistics update correctly
- [ ] Error handling works (invalid bed, etc)
- [ ] Public view hides all action buttons
- [ ] Hospital view shows action buttons
- [ ] Doctor view shows action buttons

---

## Files Modified

```
mediflow/templates/opd_queue_advanced.html
- Added enhanced button styling
- Improved startConsultation() function
- Enhanced completeConsultation() function
- Improved admitPatient() function with bed input
- Added real-time refresh (10s for admin, 30s for public)
- Better error handling and user feedback
```

---

## Deployment

**Server Location:** `mediflow/`
**Template:** `mediflow/templates/opd_queue_advanced.html`
**Run Command:**
```bash
cd mediflow
python app.py
```

**Access URL:**
```
Hospital/Doctor View: http://localhost:5000/opd-queue-advanced (while logged in as admin)
Public View: http://localhost:5000/opd-queue?public=1
```

---

## Performance Notes

- Real-time updates every 10 seconds (admin) for minimal server load
- Buttons disable during action to prevent duplicate clicks
- Loading states provide visual feedback
- Auto-refresh doesn't block user interaction
- Queue filters persist while updating

---

**Status:** ✅ **Fully Implemented and Working**

Ab patients ka complete journey tracked ho raha hai! 🎉

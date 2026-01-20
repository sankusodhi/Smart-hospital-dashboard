# 🏥 MediFlow - Hospital OPD Queue Management System

## Overview

**MediFlow** is a modern hospital management system featuring a professional **OPD (Outpatient Department) Queue Management Dashboard** designed for doctors and hospital staff. The system provides real-time queue management, patient tracking, and bed allocation with an intuitive, beautiful interface.

---

## 🎯 Project Objectives

- ✅ Build a dual-dashboard system (Patient View + Hospital Staff View)
- ✅ Implement real-time queue management with 10-second polling
- ✅ Provide professional medical aesthetic with modern design
- ✅ Enable seamless patient workflow: Registration → Queue → Consultation → Admission
- ✅ Synchronize data across multiple tables for consistency
- ✅ Create responsive, mobile-friendly interfaces
- ✅ Deliver production-ready, secure system

---

## 📋 Key Features

### 1. **OPD Queue Management Dashboard** 🔥 NEW
- Real-time patient queue display with 10s auto-refresh
- Color-coded patient status (Waiting→In Consultation→Completed/Admitted)
- Department filtering
- Action buttons: Start Consultation, Complete, Admit to Bed
- Professional modal confirmations
- Status counters with badge indicators
- Responsive design for all devices

### 2. **Hospital Staff Dashboard**
- Real-time statistics (Patients Today, In Queue, Occupancy %)
- Bed utilization panel with progress bars
- Recent patients list with live updates
- Professional stats cards with icons

### 3. **Bed Management System**
- Visual bed grid by ward (ICU, General, Semi-Private)
- Click-to-assign workflow
- Live patient name display on beds
- One-click bed discharge

### 4. **Patient Registration**
- Simple registration form
- Auto-enrollment in OPD queue
- Token generation
- Success confirmation with token display

### 5. **Patient Dashboard**
- View registration status
- Check queue position
- See bed occupancy
- View recent patients

---

## 🎨 Design Highlights

### Modern Medical Aesthetic
- **Dark Professional Sidebar**: Navy gradient with cyan accents
- **Bold Typography**: 900-weight headings, clear hierarchy
- **Gradient Buttons**: Interactive effects with color-coded actions
- **Status Colors**:
  - 🟠 Orange: Waiting (action needed)
  - 🔵 Blue: In Consultation (active)
  - 🟢 Green: Completed (success)
  - 🟣 Purple: Admitted (hospitalized)

### Responsive Layout
- **Desktop**: Full sidebar + content
- **Tablet**: Optimized grid layout
- **Mobile**: Stacked layout with horizontal sidebar scroll

### Animation & Interaction
- Smooth hover effects on cards and buttons
- Modal slide-up animation with blur backdrop
- Pulsing status indicators
- Dropdown animations

---

## 🏗️ Architecture

### Technology Stack
- **Backend**: Flask (Python)
- **Database**: MySQL
- **Frontend**: HTML5 + CSS3 + Vanilla JavaScript
- **Real-Time**: Client-side polling (10s intervals)
- **Icons**: Font Awesome 6.4.0

### Database Schema
```
patients table:
├── id (PRIMARY KEY)
├── name
├── age
├── department
├── phone
├── status (Waiting, In Consultation, Completed, Admitted)
├── token (unique)
└── created_at

opd_queue table:
├── id (PRIMARY KEY)
├── patient_id (FOREIGN KEY)
├── status
├── assigned_doctor
└── created_at

beds table:
├── id (PRIMARY KEY)
├── bed_label
├── ward_name
├── status (Available, Occupied)
└── patient_name (if occupied)
```

### API Endpoints

#### Data Endpoints
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/dashboard-summary` | GET | Patient stats for dashboard |
| `/api/opd-queue?department=X` | GET | OPD queue data with counts |

#### Action Endpoints
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/start-consultation/<id>` | POST | Begin patient consultation |
| `/complete-consultation/<id>` | POST | End consultation |
| `/admit-patient/<id>` | POST | Admit to hospital bed |
| `/discharge-by-bed` | POST | Discharge from bed |

#### Page Routes
| Route | Purpose |
|-------|---------|
| `/` | Patient dashboard |
| `/hospital-dashboard` | Staff dashboard |
| `/opd-queue` | OPD queue management |
| `/bed-management` | Bed assignment |
| `/patient-registration` | New patient form |
| `/switch-role?role=X` | Role switching |

---

## 🚀 Getting Started

### Prerequisites
- Python 3.7+
- MySQL 5.7+
- pip (Python package manager)
- Modern web browser

### Installation

1. **Clone Repository**
```bash
cd /home/sanku-sodhi/mediflow
```

2. **Install Dependencies**
```bash
pip install -r requirements.txt
```

3. **Setup Database**
```bash
mysql -u root -p < db.sql
```

4. **Configure Settings**
Edit `config.py` with your database credentials:
```python
DATABASE = {
    'host': 'localhost',
    'user': 'your_user',
    'password': 'your_password',
    'database': 'mediflow'
}
```

5. **Run Application**
```bash
python app.py
```

6. **Access Dashboard**
- **Patient View**: http://localhost:5000
- **Staff Dashboard**: http://localhost:5000/hospital-dashboard
- **OPD Queue**: http://localhost:5000/opd-queue
- **Bed Management**: http://localhost:5000/bed-management
- **Registration**: http://localhost:5000/patient-registration

---

## 📊 Workflow Examples

### Patient Registration Workflow
```
1. Patient arrives at hospital
   ↓
2. Receptionist fills registration form (Name, Age, Dept, Phone)
   ↓
3. System generates unique token
   ↓
4. Patient auto-added to OPD queue (status='Waiting')
   ↓
5. Patient receives success page with token
   ↓
6. Patient views dashboard to see queue position
```

### Doctor Consultation Workflow
```
1. Doctor views OPD queue dashboard (/opd-queue)
   ↓
2. Sees waiting patients in card format with token, name, age, department
   ↓
3. Clicks "Start" on waiting patient
   ↓
4. Confirms action in modal
   ↓
5. Patient status changes: Waiting → In Consultation
   ↓
6. Card updates to show "Complete" and "Admit" buttons
   ↓
7. After consultation:
   - If Completed: Mark as done (patient discharged)
   - If Admitting: Click "Admit" → Patient moves to Admitted status
```

### Bed Assignment Workflow
```
1. Staff view bed management dashboard (/bed-management)
   ↓
2. See bed grid for each ward (ICU, General, Semi-Private)
   ↓
3. Click on available bed
   ↓
4. Enter patient ID or token
   ↓
5. Click "Assign"
   ↓
6. Bed card updates: Occupied status + patient name displayed
   ↓
7. Patient status synced: Admitted
```

---

## 📁 File Structure

```
mediflow/
│
├── app.py                          # Main Flask application (routes, APIs, business logic)
├── db.py                          # Database connection module
├── config.py                      # Configuration settings
├── requirements.txt               # Python dependencies
├── db.sql                         # Database schema
├── schema.sql                     # Alternative schema file
│
├── templates/                     # HTML Templates
│   ├── base.html                 # Base layout template
│   ├── index.html                # Patient dashboard
│   ├── hospital_dashboard.html    # Staff dashboard
│   ├── opd_queue.html           # ⭐ OPD Queue Management (579 lines, 36KB)
│   ├── bed_management_new.html   # Bed management interface
│   ├── patient_registration.html # Registration form
│   ├── registration_success.html # Success confirmation
│   └── [other templates]         # Additional pages
│
├── static/                       # Static Assets
│   ├── css/
│   │   ├── style.css            # Main stylesheet
│   │   ├── opd_queue.css        # Legacy (now embedded)
│   │   └── [other CSS files]
│   ├── js/
│   │   ├── main.js              # Shared JavaScript
│   │   └── script.js            # Additional scripts
│   └── images/                  # Image assets
│
├── Documentation/               # Project Documentation
│   ├── README.md                # This file
│   ├── OPD_QUEUE_DESIGN_SUMMARY.md
│   ├── DESIGN_SPECIFICATIONS.md
│   ├── IMPLEMENTATION_GUIDE.md
│   ├── OPD_QUEUE_COMPLETE_SUMMARY.md
│   ├── DESIGN_SPECIFICATIONS.md
│   └── OPD_QUEUE_DESIGN_SUMMARY.md
│
└── __pycache__/                # Python cache files

```

---

## 🎯 OPD Queue Dashboard - Key Components

### Sidebar Navigation
```
┌─────────────────────────────┐
│ 🏥 MediFlow                 │
│    Hospital Management      │
├─────────────────────────────┤
│ 👨‍⚕️ [Doctor/Admin Role]       │
│    [Switch Role ▼]          │
├─────────────────────────────┤
│ DEPARTMENT                  │
│ [General Medicine ▼]        │
├─────────────────────────────┤
│ 🏠 Home                      │
│ 🛏️ Bed Management           │
│ 📝 Registration             │
│ 📋 Queue Assignment (Active)│
├─────────────────────────────┤
│ 🟢 System Online            │
└─────────────────────────────┘
```

### Patient Card Example
```
┌────────────────────────────────────────────────┐
│ ┌────┐  Rajesh Kumar, 45y           [Waiting] │
│ │ 05 │                                         │
│ │Tok │  Department:        Registered:        │
│ │en  │  Cardiology         14:30               │
│ └────┘                                         │
│                                                │
│ Assigned Doctor: Dr. Sharma                    │
│                                                │
│ ⚕️ Symptoms: Chest pain, shortness of breath  │
│                                                │
│ [Start Consultation]                          │
└────────────────────────────────────────────────┘
```

### Status Badges
```
🟠 5 Waiting  |  🔵 2 In Consultation  |  🟢 8 Completed
```

---

## 💡 Key Features Explained

### 1. Real-Time Polling
- JavaScript fetches queue data every 10 seconds
- No page reload required
- Automatic DOM updates
- Efficient and lightweight

### 2. Status Synchronization
- All actions update both `patients` and `opd_queue` tables
- Prevents data inconsistency
- Ensures real-time accuracy

### 3. Department Filtering
- Doctors can filter by specialty
- Sidebar dropdown changes view instantly
- URL parameter updates for bookmarking

### 4. Modal Confirmations
- Prevent accidental actions
- Clear action details shown
- Smooth animations with backdrop blur

### 5. Token-Based Patient Lookup
- Flexible patient identification
- Supports both ID and token
- Fallback mechanism for reliability

---

## 🔒 Security Features

- ✅ **Session Management**: Role-based access control
- ✅ **Token System**: Secure patient identification
- ✅ **Input Validation**: Server-side form validation
- ✅ **SQL Injection Prevention**: Parameterized queries
- ✅ **CSRF Protection**: Flask form handling
- ✅ **Data Consistency**: Transaction handling

---

## 📈 Performance Optimization

| Aspect | Optimization |
|--------|-------------|
| CSS | Embedded in HTML (no external requests) |
| JavaScript | Vanilla JS (no framework overhead) |
| Polling | 10-second interval (balanced) |
| DOM Updates | Batch rendering via renderCards() |
| Animations | CSS-based (hardware-accelerated) |
| Database | Optimized queries with JOINs |
| Icons | Font Awesome CDN (minimal impact) |

---

## 🧪 Testing

### API Testing
```bash
# Get queue data
curl http://localhost:5000/api/opd-queue?department=All%20Departments

# Start consultation
curl -X POST http://localhost:5000/start-consultation/1

# Complete consultation
curl -X POST http://localhost:5000/complete-consultation/1

# Admit patient
curl -X POST http://localhost:5000/admit-patient/1?bed_label=ICU-01
```

### Browser Testing
- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+
- ✅ Mobile browsers (iOS Safari, Android Chrome)

---

## 🎓 Documentation Files

1. **README.md** (This file) - Project overview and usage
2. **OPD_QUEUE_DESIGN_SUMMARY.md** - Design overview and features
3. **DESIGN_SPECIFICATIONS.md** - Colors, typography, spacing
4. **IMPLEMENTATION_GUIDE.md** - Technical implementation details
5. **OPD_QUEUE_COMPLETE_SUMMARY.md** - Comprehensive project summary

---

## 🚀 Deployment Guide

### Local Testing
```bash
python app.py
# Access at http://localhost:5000
```

### Production Deployment
1. Use production WSGI server (Gunicorn, uWSGI)
2. Configure environment variables
3. Set up HTTPS
4. Configure database connection pooling
5. Enable logging and monitoring
6. Set up backup procedures

### Docker Deployment
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000"]
```

---

## 🔧 Configuration

### Database Connection (config.py)
```python
DATABASE = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', 'password'),
    'database': os.getenv('DB_NAME', 'mediflow')
}
```

### Flask Settings (app.py)
```python
app.secret_key = 'your-secret-key'
app.config['SESSION_TIMEOUT'] = 3600  # 1 hour
```

---

## 📊 Statistics

| Metric | Value |
|--------|-------|
| **Total Lines of Code** | ~500 (core app.py) |
| **OPD Queue Template** | 579 lines, 36KB |
| **CSS Classes** | 71 defined |
| **API Endpoints** | 6+ active |
| **Responsive Breakpoints** | 3 (Desktop, Tablet, Mobile) |
| **Animation Keyframes** | 4 defined |
| **Browser Support** | 5+ modern browsers |
| **Real-Time Polling** | Every 10 seconds |

---

## 🎯 Future Enhancements

1. **Advanced Analytics**: Doctor performance, patient satisfaction metrics
2. **Doctor Profiles**: Track assigned patients, consultation history
3. **Patient Feedback**: Rating system for consultations
4. **Appointment Scheduling**: Pre-book consultations
5. **SMS/Email Alerts**: Notify patients of status changes
6. **Report Generation**: Export queue data to PDF/Excel
7. **WebSocket Integration**: Replace polling with push notifications
8. **Multi-Hospital Support**: Manage multiple locations

---

## 🆘 Troubleshooting

### Issue: Queue not updating
**Solution**: Check browser console for errors, verify API endpoint is responding

### Issue: Patient not appearing in queue
**Solution**: Ensure patient was registered successfully, check database for records

### Issue: Styling looks off on mobile
**Solution**: Clear browser cache, verify responsive CSS is loaded

### Issue: Database connection error
**Solution**: Check config.py credentials, verify MySQL is running, check database exists

---

## 📞 Support

For issues or questions:
1. Check documentation files
2. Review code comments
3. Test API endpoints manually
4. Check browser console for errors
5. Verify database connections

---

## 📜 License

MediFlow Hospital Management System - Internal Use

---

## 👥 Contributors

- **Sanku Sodhi** - Project Lead & Developer
- MediFlow Development Team

---

## ✨ Summary

**MediFlow OPD Queue Management Dashboard** is a production-ready, modern hospital management system featuring:

- ✅ Professional medical aesthetic with dark sidebar branding
- ✅ Real-time queue management with 10s auto-refresh
- ✅ Color-coded patient status indicators
- ✅ Responsive design for all devices
- ✅ Smooth animations and interactive feedback
- ✅ Secure session management
- ✅ Database synchronization
- ✅ Clean, maintainable codebase

**The system is ready for immediate deployment and use in hospital environments.**

---

**Version**: 2.0 - Enhanced Modern Medical Theme  
**Last Updated**: January 8, 2025  
**Status**: ✅ Production Ready

---

*For technical questions or customization requests, contact the development team.*

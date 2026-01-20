from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import mysql.connector
from mysql.connector import Error
from datetime import datetime
import random
import string
import os

# Use project-level templates directory so app can render templates moved to repo root
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')
app = Flask(__name__, template_folder=TEMPLATES_DIR)
app.secret_key = 'mediflow-secret-key-2024'

# Database Configuration - Railway.app MySQL
from urllib.parse import urlparse

# Parse Railway MySQL URL: mysql://user:password@host:port/database
def build_db_config():
    """Support Railway vars (`${{ MySQL.MYSQL_URL }}`) and fall back to local."""
    db_url = os.getenv('MYSQL_URL') or os.getenv('DATABASE_URL')

    # Railway also exposes split vars (MYSQLHOST, MYSQLPORT, etc.)
    if not db_url:
        host = os.getenv('MYSQLHOST')
        user = os.getenv('MYSQLUSER')
        password = os.getenv('MYSQLPASSWORD')
        database = os.getenv('MYSQLDATABASE')
        port = os.getenv('MYSQLPORT', '3306')
        if all([host, user, password, database]):
            db_url = f"mysql://{user}:{password}@{host}:{port}/{database}"

    if not db_url:
        db_url = 'mysql://root:swati@localhost:3306/mediflow'

    parsed_url = urlparse(db_url)
    return {
        'host': parsed_url.hostname or 'localhost',
        'user': parsed_url.username or 'root',
        'password': parsed_url.password or 'swati',
        'database': (parsed_url.path or '/mediflow').lstrip('/'),
        'port': parsed_url.port or 3306
    }


DB_CONFIG = build_db_config()

def get_db():
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except Error as e:
        print(f"❌ Database connection error: {e}")
        return None

def get_db_connection():
    """Alias for get_db() for compatibility"""
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except Error as e:
        print(f"❌ Database connection error: {e}")
        return None

# ==================== GENERATE TOKEN NUMBER ====================
def generate_token_number():
    """Generate unique token number: TOK-XXXXX"""
    random_part = ''.join(random.choices(string.digits, k=5))
    return f"TOK-{random_part}"

# ==================== AUTHENTICATION ====================
@app.route('/login', methods=['GET', 'POST'])
def login_page():
    # Login page removed: auto-login as admin and redirect to hospital dashboard
    session['user_id'] = 1
    session['username'] = 'admin'
    session['full_name'] = 'Administrator'
    session['role'] = 'Admin'
    return redirect(url_for('hospital_view_dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login_page'))

# ==================== HOME PAGE (redirect to Hospital Dashboard) ====================
@app.route('/')
def home():
    # Directly show hospital dashboard (login removed)
    return redirect(url_for('hospital_view_dashboard'))

# ==================== HOSPITAL DASHBOARD ====================
# ==================== DASHBOARD SUMMARY API (for live updates) ====================
@app.route('/api/dashboard-summary')
def api_dashboard_summary():
    patients_today = 0
    in_queue = 0
    occupied_beds = 0
    total_beds = 50
    occupancy_percent = 0
    recent_patients = []
    wards = {
        'ICU': {'occupied': 0, 'total': 10},
        'General': {'occupied': 0, 'total': 30},
        'Semi-Private': {'occupied': 0, 'total': 10},
    }

    try:
        db = get_db()
        if db:
            cursor = db.cursor(dictionary=True)
            try:
                cursor.execute("SELECT COUNT(*) as count FROM patients WHERE DATE(created_at) = CURDATE()")
                result = cursor.fetchone()
                patients_today = result['count'] if result else 0
            except:
                patients_today = 0

            try:
                cursor.execute("SELECT COUNT(*) as count FROM patients WHERE status = 'Waiting'")
                result = cursor.fetchone()
                in_queue = result['count'] if result else 0
            except:
                in_queue = 0

            # TODO: Replace with real bed occupancy source when available
            try:
                cursor.execute("SELECT COUNT(*) as count FROM patients WHERE status = 'Admitted'")
                result = cursor.fetchone()
                occupied_beds = result['count'] if result else 0
            except:
                occupied_beds = 0

            try:
                cursor.execute("""
                    SELECT id, name, age, department, status, created_at
                    FROM patients
                    ORDER BY created_at DESC
                    LIMIT 5
                """)
                recent_patients = cursor.fetchall()
            except:
                recent_patients = []

            cursor.close()
            db.close()
    except Error as e:
        print(f"❌ Error building dashboard summary: {e}")

    occupancy_percent = int((occupied_beds / total_beds) * 100) if total_beds else 0

    ward_utilization = []
    for ward_name, data in wards.items():
        total = data['total']
        occ = data['occupied']
        percent = int((occ / total) * 100) if total else 0
        ward_utilization.append({
            'name': ward_name,
            'occupied': occ,
            'total': total,
            'percent': percent
        })

    def serialize_patient(p):
        created_val = p.get('created_at')
        created_str = created_val.isoformat() if hasattr(created_val, 'isoformat') else str(created_val)
        return {
            'id': p.get('id'),
            'name': p.get('name'),
            'age': p.get('age'),
            'department': p.get('department'),
            'status': p.get('status'),
            'created_at': created_str,
        }

    return jsonify({
        'patients_today': patients_today,
        'in_queue': in_queue,
        'occupied_beds': occupied_beds,
        'total_beds': total_beds,
        'occupancy_percent': occupancy_percent,
        'recent_patients': [serialize_patient(p) for p in recent_patients],
        'ward_utilization': ward_utilization,
    })

# ==================== OPD QUEUE API ====================
@app.route('/api/opd-queue')
def api_opd_queue():
    department = request.args.get('department')
    patients = []
    try:
        db = get_db()
        if db:
            cursor = db.cursor(dictionary=True)
            query = (
                "SELECT q.queue_id AS token_id, q.status AS queue_status, "
                "p.patient_id AS id, p.name, p.age, p.department, p.registration_date AS created_at, p.status as patient_status "
                "FROM opd_queue q JOIN patients p ON p.patient_id = q.patient_id "
                + ("WHERE q.department = %s " if department and department != 'All Departments' else "") +
                "ORDER BY q.queue_id ASC"
            )
            params = (department,) if department and department != 'All Departments' else None
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            rows = cursor.fetchall()
            status_map = {
                'waiting': 'Waiting',
                'in_consultation': 'In Consultation',
                'completed': 'Completed',
                'cancelled': 'Cancelled'
            }
            for r in rows:
                created_val = r.get('created_at')
                created_str = created_val.isoformat() if hasattr(created_val, 'isoformat') else str(created_val)
                raw_status = (r.get('queue_status') or 'waiting')
                human_status = status_map.get(raw_status, 'Waiting')
                patients.append({
                    'id': r['id'],
                    'token_id': r['token_id'],
                    'name': r['name'],
                    'age': r['age'],
                    'department': r['department'],
                    'status': human_status,
                    'created_at': created_str,
                    'assigned_doctor': None,
                    'symptoms': None
                })
            cursor.close()
            db.close()
    except Error as e:
        print(f"❌ Error building OPD queue: {e}")

    # Counters
    waiting = sum(1 for p in patients if p['status'] == 'Waiting')
    in_consult = sum(1 for p in patients if p['status'] == 'In Consultation')
    completed = sum(1 for p in patients if p['status'] == 'Completed')

    return jsonify({
        'department': department or 'All Departments',
        'counts': {
            'waiting': waiting,
            'in_consultation': in_consult,
            'completed': completed
        },
        'patients': patients
    })

# ==================== OPD ACTIONS ====================
@app.route('/start-consultation/<int:patient_id>', methods=['POST'])
def start_consultation(patient_id):
    try:
        db = get_db()
        if not db:
            return jsonify({'success': False, 'message': 'DB connection failed'}), 500
        cursor = db.cursor()
        cursor.execute("UPDATE patients SET status = 'In Consultation' WHERE patient_id = %s", (patient_id,))
        cursor.execute("UPDATE opd_queue SET status = 'in_consultation' WHERE patient_id = %s", (patient_id,))
        db.commit()
        cursor.close()
        db.close()
        return jsonify({'success': True})
    except Error as e:
        print(f"❌ start_consultation error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/complete-consultation/<int:patient_id>', methods=['POST'])
def complete_consultation(patient_id):
    try:
        db = get_db()
        if not db:
            return jsonify({'success': False, 'message': 'DB connection failed'}), 500
        cursor = db.cursor()
        cursor.execute("UPDATE patients SET status = 'Completed' WHERE patient_id = %s", (patient_id,))
        cursor.execute("UPDATE opd_queue SET status = 'completed' WHERE patient_id = %s", (patient_id,))
        db.commit()
        cursor.close()
        db.close()
        return jsonify({'success': True})
    except Error as e:
        print(f"❌ complete_consultation error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/cancel-consultation/<int:patient_id>', methods=['POST'])
def cancel_consultation(patient_id):
    try:
        db = get_db()
        if not db:
            return jsonify({'success': False, 'message': 'DB connection failed'}), 500
        cursor = db.cursor()
        cursor.execute("UPDATE patients SET status = 'Cancelled' WHERE patient_id = %s", (patient_id,))
        cursor.execute("UPDATE opd_queue SET status = 'cancelled' WHERE patient_id = %s", (patient_id,))
        db.commit()
        cursor.close()
        db.close()
        return jsonify({'success': True})
    except Error as e:
        print(f"❌ cancel_consultation error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/admit-patient/<int:patient_id>', methods=['POST'])
def admit_patient(patient_id):
    try:
        # Simple bed assignment - default to GEN-NA
        bed_label = 'GEN-NA'
        ward_name = 'General Ward'
        
        db = get_db()
        if not db:
            return jsonify({'success': False, 'message': 'DB connection failed'}), 500
        cursor = db.cursor(dictionary=True)
        
        # Update patient status and bed_id
        cursor.execute("UPDATE patients SET status = 'Admitted', bed_id = %s WHERE patient_id = %s", (bed_label, patient_id))
        
        if cursor.rowcount == 0:
            # Fallback: treat provided value as token
            cursor.execute("SELECT patient_id FROM patients WHERE token = %s", (patient_id,))
            row = cursor.fetchone()
            if not row:
                cursor.close(); db.close()
                return jsonify({'success': False, 'message': 'Patient not found by ID or token'}), 404
            true_id = row['patient_id'] if isinstance(row, dict) else (row[0] if isinstance(row, (list, tuple)) else row)
            cursor.execute("UPDATE patients SET status = 'Admitted', bed_id = %s WHERE patient_id = %s", (bed_label, true_id))
            patient_id = true_id
        
        # Update OPD queue status
        try:
            cursor.execute("UPDATE opd_queue SET status = 'completed' WHERE patient_id = %s", (patient_id,))
        except Exception as e:
            print(f"⚠️  Warning updating OPD queue: {e}")
        
        # Fetch patient name for UI
        cursor.execute("SELECT name FROM patients WHERE patient_id = %s", (patient_id,))
        row = cursor.fetchone()
        patient_name = row['name'] if row and isinstance(row, dict) else (row[0] if row else None)
        
        db.commit()
        cursor.close()
        db.close()
        
        return jsonify({'success': True, 'bed_number': bed_label, 'ward_name': ward_name, 'patient_name': patient_name})
    except Exception as e:
        print(f"❌ admit_patient error: {e}")
        import traceback
        print(traceback.format_exc())
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/discharge-patient/<int:patient_id>', methods=['POST'])
def discharge_patient(patient_id):
    try:
        db = get_db()
        if not db:
            return jsonify({'success': False, 'message': 'DB connection failed'}), 500
        cursor = db.cursor()
        cursor.execute("UPDATE patients SET status = 'Discharged', bed_id = NULL WHERE patient_id = %s", (patient_id,))
        try:
            cursor.execute("UPDATE opd_queue SET status = 'completed' WHERE patient_id = %s", (patient_id,))
        except:
            pass
        db.commit()
        cursor.close()
        db.close()
        return jsonify({'success': True})
    except Error as e:
        print(f"❌ discharge_patient error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/discharge-by-bed', methods=['POST'])
def discharge_by_bed():
    bed_label = None
    if request.is_json:
        bed_label = request.json.get('bed_label')
    if not bed_label:
        bed_label = request.form.get('bed_label')
    if not bed_label:
        return jsonify({'success': False, 'message': 'bed_label required'}), 400
    try:
        db = get_db()
        if not db:
            return jsonify({'success': False, 'message': 'DB connection failed'}), 500
        cursor = db.cursor()
        # If bed_id column exists, clear by bed label; otherwise, just mark any admitted patient as discharged for demo.
        try:
            cursor.execute("UPDATE patients SET status = 'Discharged' WHERE bed_id = %s", (bed_label,))
            if cursor.rowcount == 0:
                # No mapping; do nothing else.
                pass
        except Exception:
            # Fallback behavior without bed_id column
            cursor.execute("UPDATE patients SET status = 'Discharged' WHERE status = 'Admitted' LIMIT 1")
        db.commit()
        cursor.close()
        db.close()
        return jsonify({'success': True})
    except Error as e:
        print(f"❌ discharge_by_bed error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

# ==================== SWITCH ROLE ====================
@app.route('/switch-role')
def switch_role():
    role = request.args.get('role', 'Public View')
    session['role'] = role
    return redirect(url_for('home'))

# ==================== PATIENT REGISTRATION ====================
@app.route('/patient-registration', methods=['GET', 'POST'])
def patient_registration():
    if request.method == 'POST':
        try:
            # Get form data - REQUIRED FIELDS
            name = request.form.get('name', '').strip()
            age = request.form.get('age', '').strip()
            department = request.form.get('department', '').strip()
            phone = request.form.get('phone', '').strip()
            
            # Optional fields
            email = request.form.get('email', '').strip()
            gender = request.form.get('gender', '').strip()
            blood_group = request.form.get('blood_group', '').strip()
            date_of_birth = request.form.get('date_of_birth', '').strip()
            address = request.form.get('address', '').strip()
            medical_history = request.form.get('medical_history', '').strip()
            emergency_contact = request.form.get('emergency_contact', '').strip()
            
            # Validation
            if not all([name, age, department, phone]):
                flash('Name, Age, Department, and Phone are required!', 'error')
                return render_template('patient_registration.html')
            
            try:
                age = int(age)
                if age < 1 or age > 150:
                    flash('Please enter a valid age (1-150)', 'error')
                    return render_template('patient_registration.html')
            except ValueError:
                flash('Age must be a number', 'error')
                return render_template('patient_registration.html')
            
            # Generate unique token number
            token_number = random.randint(10000, 99999)
            
            # Insert into database
            db = get_db()
            if db:
                cursor = db.cursor()
                query = """
                    INSERT INTO patients 
                    (name, age, phone, department, status)
                    VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(query, (
                    name, age, phone, department, 'Waiting'
                ))
                db.commit()
                patient_id = cursor.lastrowid

                # Auto-add to OPD queue with token = patient_id
                try:
                    cursor.execute("""
                        INSERT INTO opd_queue (patient_id, department, status, token)
                        VALUES (%s, %s, 'waiting', %s)
                    """, (patient_id, department, patient_id))
                    db.commit()
                except Error as e:
                    print(f"⚠️  Warning: Could not add to OPD queue: {e}")

                cursor.close()
                db.close()
                
                # Store in session
                session['patient_id'] = patient_id
                session['patient_name'] = name
                session['patient_age'] = age
                session['patient_department'] = department
                session['token_number'] = token_number
                
                print(f"✅ Patient registered: {name} - Token: {token_number}")
                flash(f'Registration successful! Token: {token_number}', 'success')
                return redirect(url_for('registration_success', token=token_number))
            else:
                flash('Database connection error', 'error')
                return render_template('patient_registration.html')
                
        except Error as e:
            print(f"❌ Database error: {e}")
            flash(f'Database Error: {str(e)}', 'error')
            return render_template('patient_registration.html')
        except Exception as e:
            print(f"❌ Error: {e}")
            flash(f'Error: {str(e)}', 'error')
            return render_template('patient_registration.html')
    
    return render_template('patient_registration.html')

# ==================== REGISTRATION SUCCESS ====================
@app.route('/registration-success')
def registration_success():
    token = request.args.get('token')
    patient_name = session.get('patient_name')
    patient_age = session.get('patient_age')
    patient_department = session.get('patient_department')
    patient_id = session.get('patient_id')
    
    print(f"📋 Registration Success - Token: {token}, Name: {patient_name}")
    
    if not token or not patient_name:
        flash('Please complete registration first', 'error')
        return redirect(url_for('patient_registration'))
    
    return render_template('registration_success.html', 
                         token=token, 
                         patient_name=patient_name,
                         patient_age=patient_age,
                         patient_department=patient_department,
                         patient_id=patient_id)

# ==================== BED MANAGEMENT ====================
@app.route('/bed-management')
def bed_management():
    return render_template('bed_test.html')

@app.route('/bed-management-advanced')
def bed_management_advanced():
    return render_template('bed_management_advanced.html')

# ==================== OPD QUEUE ====================
@app.route('/opd-queue')
def opd_queue():
    return redirect(url_for('opd_queue_advanced'))

@app.route('/opd-queue-advanced')
def opd_queue_advanced():
    return render_template('opd_queue_advanced.html')

@app.route('/opd-queue-old')
def opd_queue_old():
    role = session.get('role', 'Admin/Receptionist')
    dept = request.args.get('dept', 'All Departments')
    doctor = request.args.get('doctor', 'Dr. On Duty')
    return render_template('opd_queue.html', role=role, selected_department=dept, doctor_name=doctor)

# ==================== PATIENT DASHBOARD ====================
@app.route('/patient-dashboard')
def patient_dashboard():
    role = session.get('role', 'Public View')
    
    # Default stats
    patients_today = 0
    in_queue = 0
    occupied_beds = 0
    total_beds = 50
    recent_patients = []
    
    try:
        db = get_db()
        if db:
            cursor = db.cursor(dictionary=True)
            
            # Get total registered patients today
            try:
                cursor.execute("SELECT COUNT(*) as count FROM patients WHERE DATE(created_at) = CURDATE()")
                result = cursor.fetchone()
                patients_today = result['count'] if result else 0
            except:
                patients_today = 0
            
            # Get patients in queue
            try:
                cursor.execute("SELECT COUNT(*) as count FROM patients WHERE status = 'Waiting'")
                result = cursor.fetchone()
                in_queue = result['count'] if result else 0
            except:
                in_queue = 0
            
            # Get occupied beds
            try:
                cursor.execute("SELECT COUNT(*) as count FROM patients WHERE status = 'Admitted'")
                result = cursor.fetchone()
                occupied_beds = result['count'] if result else 0
            except:
                occupied_beds = 0
            
            # Get recent patients
            try:
                cursor.execute("""
                    SELECT id, name, age, department, status, created_at 
                    FROM patients 
                    ORDER BY created_at DESC 
                    LIMIT 10
                """)
                recent_patients = cursor.fetchall()
            except:
                recent_patients = []
            
            cursor.close()
            db.close()
    except Error as e:
        print(f"❌ Error fetching patient dashboard data: {e}")
    
    return render_template('patient_dashboard.html', 
                         role=role,
                         patients_today=patients_today,
                         in_queue=in_queue,
                         occupied_beds=occupied_beds,
                         total_beds=total_beds,
                         recent_patients=recent_patients)

# ==================== ROLE-BASED DASHBOARD ROUTES ====================
@app.route('/dashboard/patient')
def patient_view_dashboard():
    """Patient Dashboard View - No sidebar, simple UI"""
    # Set session role to patient
    session['view_role'] = 'patient'
    
    patients_today = 0
    in_queue = 0
    occupied_beds = 0
    total_beds = 50
    
    try:
        db = get_db()
        if db:
            cursor = db.cursor(dictionary=True)
            
            # Get patients registered today
            try:
                cursor.execute("SELECT COUNT(*) as count FROM patients WHERE DATE(created_at) = CURDATE()")
                result = cursor.fetchone()
                patients_today = result['count'] if result else 0
            except:
                patients_today = 0
            
            # Get patients in queue
            try:
                cursor.execute("SELECT COUNT(*) as count FROM patients WHERE status IN ('Waiting', 'In Queue')")
                result = cursor.fetchone()
                in_queue = result['count'] if result else 0
            except:
                in_queue = 0
            
            # Get occupied beds
            try:
                cursor.execute("SELECT COUNT(*) as count FROM patients WHERE status = 'Admitted'")
                result = cursor.fetchone()
                occupied_beds = result['count'] if result else 0
            except:
                occupied_beds = 0
            
            cursor.close()
            db.close()
    except Error as e:
        print(f"❌ Error fetching patient dashboard data: {e}")
    
    return render_template('dashboards/patient.html',
                         patients_today=patients_today,
                         in_queue=in_queue,
                         occupied_beds=occupied_beds,
                         total_beds=total_beds)

@app.route('/dashboard/hospital')
def hospital_view_dashboard():
    """Hospital/Doctor Dashboard View - With sidebar and full admin interface"""
    # Set session role to hospital
    session['view_role'] = 'hospital'
    
    patients_today = 0
    in_queue = 0
    occupied_beds = 0
    total_beds = 50
    consultations_today = 0
    avg_wait_time = 12
    bed_occupancy_rate = 0
    
    # Recent activity data
    recent_activities = []
    
    # Department status data
    departments = [
        {'name': 'Emergency', 'patients': 0, 'available': 0},
        {'name': 'OPD', 'patients': 0, 'available': 0},
        {'name': 'ICU', 'patients': 0, 'available': 0},
        {'name': 'General Ward', 'patients': 0, 'available': 0}
    ]
    
    try:
        db = get_db()
        if db:
            cursor = db.cursor(dictionary=True)
            
            # Get patients registered today
            try:
                cursor.execute("SELECT COUNT(*) as count FROM patients WHERE DATE(created_at) = CURDATE()")
                result = cursor.fetchone()
                patients_today = result['count'] if result else 0
            except:
                patients_today = 0
            
            # Get patients in queue
            try:
                cursor.execute("SELECT COUNT(*) as count FROM patients WHERE status IN ('Waiting', 'In Queue')")
                result = cursor.fetchone()
                in_queue = result['count'] if result else 0
            except:
                in_queue = 0
            
            # Get occupied beds
            try:
                cursor.execute("SELECT COUNT(*) as count FROM patients WHERE status = 'Admitted'")
                result = cursor.fetchone()
                occupied_beds = result['count'] if result else 0
                if total_beds > 0:
                    bed_occupancy_rate = round((occupied_beds / total_beds) * 100, 1)
            except:
                occupied_beds = 0
            
            # Get consultations today
            try:
                cursor.execute("SELECT COUNT(*) as count FROM patients WHERE status = 'Consulted' AND DATE(created_at) = CURDATE()")
                result = cursor.fetchone()
                consultations_today = result['count'] if result else 0
            except:
                consultations_today = 0
            
            # Get department-wise patient count
            try:
                for dept in departments:
                    cursor.execute("SELECT COUNT(*) as count FROM patients WHERE department = %s AND status IN ('Waiting', 'In Queue', 'Consulted')", (dept['name'],))
                    result = cursor.fetchone()
                    dept['patients'] = result['count'] if result else 0
                    dept['available'] = 5  # Static for now
            except:
                pass
            
            # Get recent activities (last 5 patient registrations)
            try:
                cursor.execute("""
                    SELECT name, department, status, created_at 
                    FROM patients 
                    ORDER BY created_at DESC 
                    LIMIT 5
                """)
                activities = cursor.fetchall()
                for activity in activities:
                    recent_activities.append({
                        'type': 'registration',
                        'title': f'New Patient: {activity["name"]}',
                        'description': f'{activity["department"]} - {activity["status"]}',
                        'time': activity['created_at'].strftime('%I:%M %p') if activity['created_at'] else 'Just now',
                        'badge': 'success' if activity['status'] == 'Consulted' else 'warning'
                    })
            except:
                pass
            
            cursor.close()
            db.close()
    except Error as e:
        print(f"❌ Error fetching hospital dashboard data: {e}")
    
    return render_template('dashboards/hospital.html',
                         patients_today=patients_today,
                         in_queue=in_queue,
                         occupied_beds=occupied_beds,
                         total_beds=total_beds,
                         consultations_today=consultations_today,
                         avg_wait_time=avg_wait_time,
                         bed_occupancy_rate=bed_occupancy_rate,
                         departments=departments,
                         recent_activities=recent_activities)

@app.route('/switch-view/<view>')
def switch_view(view):
    """Switch between patient and hospital views"""
    if view in ['patient', 'hospital']:
        session['view_role'] = view
        flash(f'Switched to {view.capitalize()} View', 'success')
        
        # Redirect to appropriate dashboard
        if view == 'patient':
            return redirect(url_for('patient_view_dashboard'))
        else:
            return redirect(url_for('hospital_view_dashboard'))
    else:
        flash('Invalid view type', 'error')
        return redirect(url_for('home'))

# ==================== DASHBOARD ROOT REDIRECT ====================
@app.route('/dashboard')
def dashboard_root():
    """Redirect to the appropriate dashboard based on session role."""
    role = session.get('view_role')
    if role in ['hospital', 'doctor']:
        return redirect(url_for('hospital_view_dashboard'))
    return redirect(url_for('patient_view_dashboard'))

# ==================== ROUTE ALIASES ====================
app.add_url_rule('/', 'index', home)
app.add_url_rule('/opd-queue', 'opd_queue_assignment', opd_queue)
app.add_url_rule('/bed-management', 'bed_management_view', bed_management)

# ==================== BED ASSIGNMENT API ====================
@app.route('/api/assign-bed', methods=['POST'])
def assign_bed():
    """Assign a patient to a bed"""
    try:
        data = request.get_json()
        patient_id = data.get('patient_id')
        bed_name = data.get('bed_name')
        doctor_name = data.get('doctor_name')
        
        if not patient_id or not bed_name:
            return jsonify({'success': False, 'message': 'Patient ID and Bed Name are required'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Check if bed is available
        cursor.execute("SELECT * FROM beds WHERE bed_name = %s AND status = 'Available'", (bed_name,))
        bed = cursor.fetchone()
        
        if not bed:
            return jsonify({'success': False, 'message': 'Bed is not available'}), 400
        
        # Update patient with bed assignment
        cursor.execute("""
            UPDATE patients 
            SET bed_id = %s, assigned_doctor = %s, status = 'Admitted'
            WHERE id = %s
        """, (bed_name, doctor_name, patient_id))
        
        # Update bed status
        cursor.execute("""
            UPDATE beds 
            SET status = 'Occupied'
            WHERE bed_name = %s
        """, (bed_name,))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Patient assigned to bed successfully'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/discharge-patient', methods=['POST'])
def api_discharge_patient():
    """Discharge a patient and free up the bed"""
    try:
        data = request.get_json()
        patient_id = data.get('patient_id')
        
        if not patient_id:
            return jsonify({'success': False, 'message': 'Patient ID is required'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get patient's bed
        cursor.execute("SELECT bed_id FROM patients WHERE id = %s", (patient_id,))
        patient = cursor.fetchone()
        
        if not patient or not patient['bed_id']:
            return jsonify({'success': False, 'message': 'Patient not found or not admitted'}), 400
        
        bed_name = patient['bed_id']
        
        # Update patient status
        cursor.execute("""
            UPDATE patients 
            SET status = 'Discharged', bed_id = NULL, assigned_doctor = NULL
            WHERE id = %s
        """, (patient_id,))
        
        # Free up the bed
        cursor.execute("""
            UPDATE beds 
            SET status = 'Available'
            WHERE bed_name = %s
        """, (bed_name,))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Patient discharged successfully'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# ==================== BED ASSIGNMENT & DISCHARGE APIs ====================
@app.route('/api/assign-bed-patient', methods=['POST'])
def assign_bed_patient():
    """Assign a new patient to an available bed"""
    try:
        data = request.get_json()
        bed_id = data.get('bed_id')
        patient_name = data.get('patient_name')
        doctor_name = data.get('doctor_name')
        patient_age = data.get('patient_age', 0)
        department = data.get('department', 'General')
        
        if not bed_id or not patient_name or not doctor_name:
            return jsonify({'success': False, 'message': 'Bed ID, Patient Name and Doctor Name are required'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Check if bed is available
        cursor.execute("SELECT * FROM beds WHERE bed_id = %s AND status = 'Available'", (bed_id,))
        bed = cursor.fetchone()
        
        if not bed:
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'message': 'Bed is not available'}), 400
        
        # Insert new patient
        cursor.execute("""
            INSERT INTO patients (name, age, phone, department, status, bed_id, assigned_doctor)
            VALUES (%s, %s, %s, %s, 'Admitted', %s, %s)
        """, (patient_name, patient_age, '', department, bed_id, doctor_name))
        
        # Update bed status
        cursor.execute("""
            UPDATE beds 
            SET status = 'Occupied', patient_id = LAST_INSERT_ID()
            WHERE bed_id = %s
        """, (bed_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Patient assigned to bed successfully'})
    
    except Exception as e:
        print(f"Error in assign_bed_patient: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/discharge-bed-patient', methods=['POST'])
def discharge_bed_patient():
    """Discharge a patient and free up the bed"""
    try:
        data = request.get_json()
        bed_id = data.get('bed_id')
        
        if not bed_id:
            return jsonify({'success': False, 'message': 'Bed ID is required'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get bed info
        cursor.execute("SELECT patient_id FROM beds WHERE bed_id = %s", (bed_id,))
        bed = cursor.fetchone()
        
        if not bed or not bed['patient_id']:
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'message': 'No patient found in this bed'}), 400
        
        patient_id = bed['patient_id']
        
        # Update patient status
        cursor.execute("""
            UPDATE patients 
            SET status = 'Discharged', bed_id = NULL, assigned_doctor = NULL
            WHERE id = %s
        """, (patient_id,))
        
        # Free up the bed
        cursor.execute("""
            UPDATE beds 
            SET status = 'Available', patient_id = NULL
            WHERE bed_id = %s
        """, (bed_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Patient discharged successfully'})
    
    except Exception as e:
        print(f"Error in discharge_bed_patient: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

# ==================== BED ASSIGNMENT FEATURE ====================
@app.route('/api/available-beds', methods=['GET'])
def get_available_beds():
    """Get all available beds"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT bed_id AS bed_id, bed_number AS bed_name, ward, status 
            FROM beds 
            WHERE status = 'available'
            ORDER BY ward, bed_number
        """)
        
        available_beds = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'beds': available_beds})
    
    except Exception as e:
        print(f"Error fetching available beds: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/all-beds', methods=['GET'])
def get_all_beds():
    """Get all beds with patient information"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT 
                b.bed_id AS id,
                b.bed_number AS bed_name,
                b.ward,
                b.status,
                b.patient_id,
                p.name as patient_name,
                p.age as patient_age,
                p.phone as patient_phone,
                p.registration_date as admission_date
            FROM beds b
            LEFT JOIN patients p ON b.patient_id = p.patient_id
            ORDER BY 
                CASE b.ward 
                    WHEN 'ICU' THEN 1 
                    WHEN 'General' THEN 2 
                    WHEN 'Semi-Private' THEN 3 
                    ELSE 4 
                END,
                b.bed_number
        """)
        
        all_beds = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'beds': all_beds})
    
    except Exception as e:
        print(f"Error fetching all beds: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/waiting-patients', methods=['GET'])
def get_waiting_patients():
    """Get all patients waiting for admission"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT patient_id AS id, name, age, phone, department, status,
                   registration_date AS created_at
            FROM patients
            WHERE status = 'Waiting'
            ORDER BY registration_date ASC
        """)
        
        waiting_patients = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'patients': waiting_patients})
    
    except Exception as e:
        print(f"Error fetching waiting patients: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/assign-bed-to-patient', methods=['POST'])
def assign_bed_to_patient():
    """Assign an available bed to a waiting patient"""
    try:
        data = request.get_json()
        patient_id = data.get('patient_id')
        bed_id = data.get('bed_id')
        doctor_name = data.get('doctor_name', 'On Duty')
        
        if not patient_id or not bed_id:
            return jsonify({'success': False, 'message': 'Patient ID and Bed ID are required'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Verify bed is available
        cursor.execute("SELECT bed_name FROM beds WHERE bed_id = %s AND status = 'Available'", (bed_id,))
        bed = cursor.fetchone()
        
        if not bed:
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'message': 'Bed is not available'}), 400
        
        bed_name = bed['bed_name']
        
        # Verify patient exists and is waiting
        cursor.execute("SELECT name FROM patients WHERE patient_id = %s AND status = 'Waiting'", (patient_id,))
        patient = cursor.fetchone()
        
        if not patient:
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'message': 'Patient not found or not in waiting status'}), 400
        
        patient_name = patient['name']
        
        # Update patient with bed assignment
        cursor.execute("""
            UPDATE patients 
            SET bed_id = %s, assigned_doctor = %s, status = 'Admitted'
            WHERE patient_id = %s
        """, (bed_id, doctor_name, patient_id))
        
        # Update bed status
        cursor.execute("""
            UPDATE beds 
            SET status = 'Occupied', patient_id = %s
            WHERE bed_id = %s
        """, (patient_id, bed_id))

        # Reflect in OPD queue: move to In Consultation
        cursor.execute(
            "UPDATE opd_queue SET status = 'in_consultation' WHERE patient_id = %s",
            (patient_id,)
        )
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"✅ Bed assigned: {patient_name} -> {bed_name} (Doctor: {doctor_name})")
        
        return jsonify({
            'success': True, 
            'message': f'{patient_name} assigned to {bed_name} successfully',
            'patient_id': patient_id,
            'bed_id': bed_id,
            'bed_name': bed_name
        })
    
    except Exception as e:
        print(f"Error in assign_bed_to_patient: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

# ==================== ADMISSION PAGE ====================
@app.route('/admission')
def admission_page():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    return render_template('admission.html')

# ==================== PATIENT SEARCH API ====================
@app.route('/api/patient-by-id/<search_term>')
def get_patient_by_id(search_term):
    """Search patient by ID or Token Number"""
    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        
        # Search by patient ID or token number
        query = """
            SELECT * FROM patients 
            WHERE id = %s OR id LIKE %s
            LIMIT 1
        """
        
        cursor.execute(query, (search_term, f"{search_term}%"))
        patient = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if patient:
            return jsonify({
                'success': True,
                'patient': patient
            })
        else:
            return jsonify({
                'success': False,
                'message': f'Patient with ID "{search_term}" not found'
            })
    
    except Exception as e:
        print(f"Error in get_patient_by_id: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)

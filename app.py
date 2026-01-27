from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import mysql.connector
from mysql.connector import Error
from datetime import datetime
import random
import string
import os
from functools import wraps
from urllib.parse import urlparse

# Use mediflow's own templates directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')
app = Flask(__name__, template_folder=TEMPLATES_DIR)
app.secret_key = 'mediflow-secret-key-2024'

# Allow loading templates from the parent workspace /templates directory as a fallback.
PARENT_TEMPLATES = os.path.abspath(os.path.join(BASE_DIR, '..', 'templates'))
if os.path.isdir(PARENT_TEMPLATES) and PARENT_TEMPLATES not in app.jinja_loader.searchpath:
    app.jinja_loader.searchpath.append(PARENT_TEMPLATES)

# Database Configuration - Railway.app MySQL
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


# Role and access helpers
ADMIN_ROLES = {'Admin', 'Doctor', 'Receptionist'}
DEMO_CREDENTIALS = {
    'admin': {'password': 'admin123', 'role': 'Admin', 'full_name': 'Administrator'},
    'doctor': {'password': 'doctor123', 'role': 'Doctor', 'full_name': 'Doctor'},
    'repception': {'password': 'repception123', 'role': 'Receptionist', 'full_name': 'Reception Desk'}
}


def is_admin():
    return (session.get('role') or '').title() in ADMIN_ROLES


def require_admin(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if is_admin():
            return view_func(*args, **kwargs)
        if str(request.path).startswith('/api/'):
            return jsonify({'success': False, 'message': 'Unauthorized'}), 403
        flash('You are not authorized to access that page.', 'error')
        return redirect(url_for('login_page'))

    return wrapper


def ensure_appointments_table():
    """Create lightweight appointment tracking table if it does not exist."""
    try:
        db = get_db()
        if db:
            cursor = db.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS patient_appointments (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    patient_id INT NOT NULL,
                    token_number VARCHAR(50),
                    department VARCHAR(100),
                    appointment_date DATE,
                    appointment_time TIME,
                    status VARCHAR(50) DEFAULT 'Waiting',
                    queue_position INT DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    INDEX idx_patient (patient_id)
                )
                """
            )
            db.commit()
            cursor.close()
            db.close()
    except Error as e:
        print(f"❌ Unable to ensure appointment table: {e}")


def record_patient_appointment(patient_id, token_number, department, appointment_date, appointment_time):
    """Persist a patient appointment entry and return queue position."""
    ensure_appointments_table()
    try:
        db = get_db()
        if not db:
            return None

        cursor = db.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT COUNT(*) AS position
            FROM patient_appointments
            WHERE status IN ('Waiting', 'In Queue')
        """
        )
        position_result = cursor.fetchone() or {}
        queue_position = int(position_result.get('position', 0)) + 1

        cursor.execute(
            """
            INSERT INTO patient_appointments
            (patient_id, token_number, department, appointment_date, appointment_time, status, queue_position)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
            (patient_id, str(token_number), department, appointment_date, appointment_time, 'Waiting', queue_position)
        )
        db.commit()
        cursor.close()
        db.close()
        return queue_position
    except Error as e:
        print(f"❌ Error recording appointment: {e}")
        return None


def fetch_dashboard_counts():
    """Fetch key dashboard counts for reuse in page and API."""
    counts = {
        'patients_today': 0,
        'in_queue': 0,
        'occupied_beds': 0,
        'total_beds': 0,
        'consultations_today': 0,
        'avg_wait_time': 12,
        'bed_occupancy_rate': 0
    }

    try:
        db = get_db()
        if db:
            cursor = db.cursor(dictionary=True)

            try:
                cursor.execute("SELECT COUNT(*) as count FROM patients WHERE DATE(registration_date) = CURDATE()")
                result = cursor.fetchone()
                counts['patients_today'] = result['count'] if result else 0
            except:
                counts['patients_today'] = 0

            try:
                cursor.execute("SELECT COUNT(*) as count FROM patients WHERE status IN ('Waiting', 'In Queue')")
                result = cursor.fetchone()
                counts['in_queue'] = result['count'] if result else 0
            except:
                counts['in_queue'] = 0

            try:
                cursor.execute("SELECT COUNT(*) as count FROM patients WHERE status = 'Admitted'")
                result = cursor.fetchone()
                counts['occupied_beds'] = result['count'] if result else 0
            except:
                counts['occupied_beds'] = 0

            try:
                cursor.execute("SELECT COUNT(*) as count FROM beds")
                result = cursor.fetchone()
                counts['total_beds'] = result['count'] if result else 0
            except:
                counts['total_beds'] = 0

            try:
                cursor.execute("SELECT COUNT(*) as count FROM patients WHERE status = 'Consulted' AND DATE(registration_date) = CURDATE()")
                result = cursor.fetchone()
                counts['consultations_today'] = result['count'] if result else 0
            except:
                counts['consultations_today'] = 0

            try:
                cursor.execute("SELECT AVG(TIMESTAMPDIFF(MINUTE, registration_date, NOW())) as avg_wait FROM patients WHERE status IN ('Waiting', 'In Queue')")
                result = cursor.fetchone()
                counts['avg_wait_time'] = round(result['avg_wait'], 1) if result and result['avg_wait'] else 12
            except:
                counts['avg_wait_time'] = 12

            if counts['total_beds'] > 0:
                counts['bed_occupancy_rate'] = round((counts['occupied_beds'] / counts['total_beds']) * 100, 1)

            cursor.close()
            db.close()
    except Error as e:
        print(f"❌ Error fetching dashboard counts: {e}")

    return counts

# ==================== GENERATE TOKEN NUMBER ====================
def generate_token_number():
    """Generate unique token number: TOK-XXXXX"""
    random_part = ''.join(random.choices(string.digits, k=5))
    return f"TOK-{random_part}"

# ==================== AUTHENTICATION ====================
@app.route('/login', methods=['GET', 'POST'])
def login_page():
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        requested_role = request.form.get('role', 'Admin').strip() or 'Admin'

        if not username or not password:
            error = 'Username and password are required.'
        else:
            user_record = None
            try:
                db = get_db()
                if db:
                    cursor = db.cursor(dictionary=True)
                    cursor.execute(
                        "SELECT id, username, password, full_name, role FROM admin_users WHERE username = %s LIMIT 1",
                        (username,)
                    )
                    user_record = cursor.fetchone()
                    cursor.close()
                    db.close()
            except Error as e:
                print(f"❌ Login lookup failed: {e}")

            # Demo fallback credentials if DB lookup fails or no user found
            if not user_record and username in DEMO_CREDENTIALS:
                demo = DEMO_CREDENTIALS[username]
                if password == demo['password']:
                    user_record = {
                        'id': -1,
                        'username': username,
                        'password': demo['password'],
                        'full_name': demo.get('full_name') or username.title(),
                        'role': demo.get('role', 'Admin')
                    }

            if user_record and (password == user_record['password']) and (requested_role == user_record['role'] or requested_role in ADMIN_ROLES):
                session['user_id'] = user_record.get('id')
                session['username'] = user_record.get('username')
                session['full_name'] = user_record.get('full_name') or user_record.get('username')
                session['role'] = user_record.get('role') or 'Admin'
                session['view_role'] = 'hospital'
                flash('Logged in successfully.', 'success')
                return redirect(url_for('hospital_view_dashboard'))
            else:
                error = 'Invalid credentials or role.'

    if is_admin():
        return redirect(url_for('hospital_view_dashboard'))

    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login_page'))

# ==================== HOME PAGE (redirect to Hospital Dashboard) ====================
@app.route('/')
def home():
    # Default to patient-friendly view; admin users will be routed after login
    return redirect(url_for('patient_view_dashboard'))

# ==================== HOSPITAL DASHBOARD ====================
# ==================== DASHBOARD SUMMARY API (for live updates) ====================
@app.route('/api/dashboard/summary')
@app.route('/api/dashboard-summary')
@require_admin
def api_dashboard_summary():
    counts = fetch_dashboard_counts()
    return jsonify({'success': True, **counts})

@app.route('/api/dashboard/summary-public')
def api_dashboard_summary_public():
    """Public endpoint for patient dashboard - no authentication required"""
    counts = fetch_dashboard_counts()
    return jsonify({'success': True, **counts})

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
                "p.patient_id AS id, p.name, p.age, p.department, p.registration_date AS created_at, p.status as patient_status, p.assigned_doctor "
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
                    'assigned_doctor': r.get('assigned_doctor'),
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


@app.route('/my-appointments')
def my_appointments():
    """Dedicated page for patient to view all their appointments."""
    # Allow access without session - users can search by token/name
    return render_template('my_appointments.html')

@app.route('/api/appointment-history')
def api_appointment_history():
    """Return all appointments for the logged-in patient."""
    patient_id = session.get('patient_id')
    if not patient_id:
        return jsonify({'success': False, 'message': 'No patient session found.'}), 404

    ensure_appointments_table()
    appointments = []

    try:
        db = get_db()
        if db:
            cursor = db.cursor(dictionary=True)
            cursor.execute(
                """
                SELECT 
                    pa.*,
                    p.assigned_doctor as doctor_name
                FROM patient_appointments pa
                LEFT JOIN patients p ON p.patient_id = pa.patient_id
                WHERE pa.patient_id = %s
                ORDER BY pa.created_at DESC
                LIMIT 10
                """,
                (patient_id,)
            )
            appointments = cursor.fetchall()
            
            # Normalize dates/times
            for appt in appointments:
                if appt.get('appointment_date'):
                    appt['appointment_date'] = appt['appointment_date'].isoformat() if hasattr(appt['appointment_date'], 'isoformat') else str(appt['appointment_date'])
                if appt.get('appointment_time'):
                    appt['appointment_time'] = appt['appointment_time'].strftime('%H:%M') if hasattr(appt['appointment_time'], 'strftime') else str(appt['appointment_time'])
            
            cursor.close()
            db.close()
    except Error as e:
        print(f"❌ Error fetching appointment history: {e}")

    return jsonify({'success': True, 'appointments': appointments})

@app.route('/api/appointment-status-updates')
def api_appointment_status_updates():
    """Get recent status updates for patient's appointments."""
    patient_id = session.get('patient_id')
    if not patient_id:
        return jsonify({'success': False, 'message': 'No patient session found.'}), 404

    updates = []
    try:
        db = get_db()
        if db:
            cursor = db.cursor(dictionary=True)
            
            # Get latest appointment with status
            cursor.execute(
                """
                SELECT 
                    pa.status,
                    pa.queue_position,
                    pa.updated_at,
                    pa.department,
                    p.assigned_doctor as doctor_name
                FROM patient_appointments pa
                LEFT JOIN patients p ON p.patient_id = pa.patient_id
                WHERE pa.patient_id = %s
                ORDER BY pa.updated_at DESC
                LIMIT 5
                """,
                (patient_id,)
            )
            
            rows = cursor.fetchall()
            for row in rows:
                updates.append({
                    'status': row.get('status'),
                    'queue_position': row.get('queue_position'),
                    'timestamp': row.get('updated_at').isoformat() if row.get('updated_at') else None,
                    'department': row.get('department'),
                    'doctor': row.get('doctor_name')
                })
            
            cursor.close()
            db.close()
    except Error as e:
        print(f"❌ Error fetching status updates: {e}")

    return jsonify({'success': True, 'updates': updates})

# ==================== TOKEN SEARCH (PUBLIC) ====================
@app.route('/api/queue-status-by-token')
def api_queue_status_by_token():
    """Lookup queue/appointment status by token number (public). Accepts
    appointment token_number (e.g., 'TOK-12345' or '12345'), OPD queue id,
    or patient name (partial match) to pull the most recent appointment.
    """
    token = (request.args.get('token') or '').strip()
    name_query = (request.args.get('name') or '').strip()
    if not token and not name_query:
        return jsonify({'success': False, 'message': 'token or name is required'}), 400

    def human_status(raw):
        m = {
            'waiting': 'Waiting',
            'in_consultation': 'In Consultation',
            'completed': 'Completed',
            'cancelled': 'Cancelled',
            'discharged': 'Discharged',
            'admitted': 'Admitted',
        }
        return m.get((raw or '').lower(), (raw or 'Waiting').title())

    appt = None
    queue_row = None
    patient = None

    try:
        db = get_db()
        if db:
            cursor = db.cursor(dictionary=True, buffered=True)

            # If searching by name, resolve latest patient, appointment, and queue
            if name_query:
                cursor.execute(
                    """
                    SELECT p.patient_id, p.name, p.department, p.assigned_doctor
                    FROM patients p
                    WHERE p.name LIKE %s
                    ORDER BY p.patient_id DESC
                    LIMIT 1
                    """,
                    (f"%{name_query}%",)
                )
                patient = cursor.fetchone()
                if not patient:
                    cursor.close(); db.close()
                    return jsonify({'success': False, 'message': 'No patient found with that name'}), 404

                cursor.execute(
                    """
                    SELECT *
                    FROM patient_appointments
                    WHERE patient_id = %s
                    ORDER BY created_at DESC
                    LIMIT 1
                    """,
                    (patient['patient_id'],)
                )
                appt = cursor.fetchone()

                cursor.execute(
                    """
                    SELECT *
                    FROM opd_queue
                    WHERE patient_id = %s
                    ORDER BY queue_id DESC
                    LIMIT 1
                    """,
                    (patient['patient_id'],)
                )
                queue_row = cursor.fetchone()

                if appt and appt.get('token_number'):
                    token = appt.get('token_number')
                elif queue_row and queue_row.get('queue_id'):
                    token = str(queue_row.get('queue_id'))

            if token:
                plain = token.replace('TOK-', '').strip()

                # Try patient_appointments by token_number first
                cursor.execute(
                    """
                    SELECT pa.*, p.name, p.department, p.assigned_doctor
                    FROM patient_appointments pa
                    LEFT JOIN patients p ON pa.patient_id = p.patient_id
                    WHERE token_number = %s OR token_number = %s
                    ORDER BY pa.created_at DESC
                    LIMIT 1
                    """,
                    (token, plain)
                )
                appt = appt or cursor.fetchone()

                if appt:
                    cursor.execute(
                        """
                        SELECT *
                        FROM opd_queue
                        WHERE patient_id = %s
                        ORDER BY queue_id DESC
                        LIMIT 1
                        """,
                        (appt['patient_id'],)
                    )
                    queue_row = queue_row or cursor.fetchone()
                    patient = patient or appt
                else:
                    # Try opd_queue by queue_id / token
                    try:
                        cursor.execute(
                            "SELECT * FROM opd_queue WHERE queue_id = %s OR token = %s LIMIT 1",
                            (plain, token)
                        )
                        queue_row = queue_row or cursor.fetchone()
                    except Exception as e:
                        print(f"⚠️  Queue lookup failed: {e}")
                    if queue_row:
                        try:
                            cursor.execute(
                                "SELECT * FROM patients WHERE patient_id = %s LIMIT 1",
                                (queue_row['patient_id'],)
                            )
                            patient = patient or cursor.fetchone()
                        except Exception as e:
                            print(f"⚠️  Patient lookup failed: {e}")

            cursor.close()
            db.close()
    except Error as e:
        print(f"❌ token lookup error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': 'Lookup failed'}), 500
    except Exception as e:
        print(f"❌ Unexpected error in token lookup: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': 'Lookup failed'}), 500

    if not (appt or queue_row or patient):
        return jsonify({'success': False, 'message': 'Token not found'}), 404

    raw_status = None
    queue_position = None
    if queue_row:
        raw_status = queue_row.get('status') or queue_row.get('queue_status')
        queue_position = queue_row.get('queue_position') or queue_row.get('queue_id') or queue_row.get('token_id')
    elif appt:
        raw_status = appt.get('status')
        queue_position = appt.get('queue_position')

    status = human_status(raw_status)

    # Estimate wait: 15 minutes per person ahead
    est = None
    try:
        qp = int(queue_position) if queue_position is not None else None
        if qp and qp > 0:
            est = (qp - 1) * 15
    except Exception:
        est = None

    return jsonify({
        'success': True,
        'token': token,
        'data': {
            'patient_name': (patient or {}).get('name'),
            'department': (patient or {}).get('department') or (appt or {}).get('department'),
            'doctor_name': (patient or {}).get('assigned_doctor'),
            'status': status,
            'queue_position': queue_position,
            'estimated_wait_minutes': est,
            'appointment_date': (appt or {}).get('appointment_date'),
            'appointment_time': (appt or {}).get('appointment_time'),
        }
    })

@app.route('/api/my-appointment')
def api_my_appointment():
    """Return the latest appointment/queue info for the logged-in patient session."""
    patient_id = session.get('patient_id')
    if not patient_id:
        return jsonify({'success': False, 'message': 'No appointment on file for this session.'}), 404

    ensure_appointments_table()
    appointment = None
    patient_name = session.get('patient_name')
    queue_position = None
    queue_status = None
    queue_token = session.get('token_number')

    assigned_doctor = None
    try:
        db = get_db()
        if db:
            cursor = db.cursor(dictionary=True)
            cursor.execute(
                """
                SELECT * FROM patient_appointments
                WHERE patient_id = %s
                ORDER BY created_at DESC
                LIMIT 1
                """,
                (patient_id,)
            )
            appointment = cursor.fetchone()

            # Try to sync with OPD queue if available
            try:
                cursor.execute(
                    """
                    SELECT * FROM opd_queue
                    WHERE patient_id = %s
                    ORDER BY created_at DESC
                    LIMIT 1
                    """,
                    (patient_id,)
                )
                queue_row = cursor.fetchone()
                if queue_row:
                    queue_status = queue_row.get('status') or queue_row.get('queue_status')
                    queue_token = queue_row.get('queue_id') or queue_row.get('token_id') or queue_row.get('token') or queue_token

                    if queue_row.get('queue_id'):
                        cursor.execute(
                            """
                            SELECT COUNT(*) AS position
                            FROM opd_queue
                            WHERE status IN ('waiting', 'Waiting', 'in_consultation', 'In Consultation')
                                AND queue_id <= %s
                            """,
                            (queue_row['queue_id'],)
                        )
                        pos_row = cursor.fetchone() or {}
                        queue_position = pos_row.get('position', queue_position)
            except Exception as e:
                print(f"⚠️  Could not sync queue status: {e}")

            # Fetch assigned doctor if any
            try:
                cursor.execute(
                    "SELECT assigned_doctor FROM patients WHERE patient_id = %s",
                    (patient_id,)
                )
                doc_row = cursor.fetchone()
                if doc_row:
                    assigned_doctor = doc_row.get('assigned_doctor') or assigned_doctor
            except Exception as e:
                print(f"⚠️  Could not fetch doctor: {e}")

            cursor.close()
            db.close()
    except Error as e:
        print(f"❌ Error fetching appointment: {e}")

    if not appointment:
        return jsonify({'success': False, 'message': 'Appointment not found.'}), 404

    appt_date = appointment.get('appointment_date')
    appt_time = appointment.get('appointment_time')
    status = (queue_status or appointment.get('status') or 'Waiting').title()
    queue_position = queue_position or appointment.get('queue_position')

    def normalize_date(val):
        return val.isoformat() if hasattr(val, 'isoformat') else (val.strftime('%Y-%m-%d') if hasattr(val, 'strftime') else val)

    def normalize_time(val):
        if hasattr(val, 'total_seconds'):
            # Handle timedelta objects
            total_seconds = int(val.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            return f"{hours:02d}:{minutes:02d}"
        if hasattr(val, 'strftime'):
            return val.strftime('%H:%M')
        if isinstance(val, str):
            return val[:5] if len(val) >= 5 else val
        return str(val) if val is not None else None

    try:
        queue_position_val = int(queue_position) if queue_position is not None else None
    except (TypeError, ValueError):
        queue_position_val = None

    # Calculate estimated wait time (assuming 15 minutes per patient)
    estimated_wait_minutes = None
    if queue_position_val and queue_position_val > 0:
        estimated_wait_minutes = (queue_position_val - 1) * 15

    return jsonify({
        'success': True,
        'appointment': {
            'token_number': appointment.get('token_number') or queue_token,
            'patient_id': patient_id,
            'patient_name': patient_name,
            'department': appointment.get('department'),
            'appointment_date': normalize_date(appt_date),
            'appointment_time': normalize_time(appt_time),
            'status': status,
            'queue_position': queue_position_val,
            'doctor_name': assigned_doctor,
            'estimated_wait_minutes': estimated_wait_minutes
        }
    })

# ==================== PATIENT MANAGEMENT (Staff) ====================
@app.route('/api/patients-registered')
@require_admin
def api_patients_registered():
    """Fetch all registered patients with filters (department, status, search)"""
    try:
        department_filter = request.args.get('department', '').strip()
        status_filter = request.args.get('status', '').strip()
        search_query = request.args.get('search', '').strip()
        
        db = get_db()
        if not db:
            return jsonify({'success': False, 'message': 'DB connection failed'}), 500
        
        cursor = db.cursor(dictionary=True)
        
        # Use id or patient_id, whichever exists
        query = "SELECT * FROM patients WHERE 1=1"
        params = []
        
        if department_filter:
            query += " AND department = %s"
            params.append(department_filter)
        
        if status_filter:
            query += " AND status = %s"
            params.append(status_filter)
        
        if search_query:
            query += " AND (name LIKE %s OR phone LIKE %s)"
            params.extend([f"%{search_query}%", f"%{search_query}%"])
        
        # Try to order by id if available, otherwise no order
        try:
            cursor.execute(query + " ORDER BY id DESC LIMIT 100", params)
        except:
            try:
                cursor.execute(query + " ORDER BY patient_id DESC LIMIT 100", params)
            except:
                cursor.execute(query + " LIMIT 100", params)
        
        patients = cursor.fetchall()
        
        # Normalize patient_id field
        for patient in patients:
            if 'patient_id' not in patient and 'id' in patient:
                patient['patient_id'] = patient['id']
        
        cursor.close()
        db.close()
        
        return jsonify({'success': True, 'patients': patients})
    except Error as e:
        print(f"❌ Error fetching patients: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/patient-details/<int:patient_id>')
@require_admin
def api_patient_details(patient_id):
    """Fetch full details for a patient"""
    try:
        db = get_db()
        if not db:
            return jsonify({'success': False, 'message': 'DB connection failed'}), 500
        
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM patients WHERE patient_id = %s", (patient_id,))
        patient = cursor.fetchone()
        
        if not patient:
            cursor.close()
            db.close()
            return jsonify({'success': False, 'message': 'Patient not found'}), 404
        
        # Get appointment info
        ensure_appointments_table()
        cursor.execute(
            """
            SELECT * FROM patient_appointments
            WHERE patient_id = %s
            ORDER BY created_at DESC
            LIMIT 1
            """,
            (patient_id,)
        )
        appointment = cursor.fetchone()
        
        cursor.close()
        db.close()
        
        return jsonify({
            'success': True,
            'patient': patient,
            'appointment': appointment
        })
    except Error as e:
        print(f"❌ Error fetching patient details: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/assign-slot', methods=['POST'])
@require_admin
def api_assign_slot():
    """Assign availability/slot to a patient (mark ready for consultation)"""
    try:
        data = request.get_json(silent=True) or {}
        patient_id = data.get('patient_id')
        slot_time = data.get('slot_time', '').strip()
        doctor_name = data.get('doctor_name', '').strip()
        notes = data.get('notes', '').strip()
        
        if not patient_id:
            return jsonify({'success': False, 'message': 'patient_id required'}), 400
        
        db = get_db()
        if not db:
            return jsonify({'success': False, 'message': 'DB connection failed'}), 500
        
        cursor = db.cursor()
        
        # Update patient status
        update_fields = []
        update_params = []
        
        if doctor_name:
            update_fields.append("assigned_doctor = %s")
            update_params.append(doctor_name)
        
        update_fields.append("status = %s")
        update_params.append('Ready for Consultation')
        
        update_params.append(patient_id)
        
        cursor.execute(
            f"UPDATE patients SET {', '.join(update_fields)} WHERE patient_id = %s",
            update_params
        )
        
        # Update appointment if it exists
        if slot_time:
            try:
                cursor.execute(
                    """
                    UPDATE patient_appointments
                    SET status = 'Ready', appointment_time = %s
                    WHERE patient_id = %s
                    """,
                    (slot_time, patient_id)
                )
            except Exception as e:
                print(f"⚠️  Could not update appointment: {e}")
        
        db.commit()
        cursor.close()
        db.close()
        
        return jsonify({'success': True, 'message': 'Slot assigned successfully'})
    except Error as e:
        print(f"❌ Error assigning slot: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/patient-management')
@require_admin
def patient_management():
    """Staff view to manage registered patients"""
    session['view_role'] = 'hospital'
    return render_template('patient_management.html')

@app.route('/total-patients')
@require_admin
def total_patients():
    """View all registered patients with complete details"""
    session['view_role'] = 'hospital'
    return render_template('total_patients.html')

@app.route('/api/all-patients')
@require_admin
def api_all_patients():
    """Fetch all registered patients with full details"""
    try:
        search_query = request.args.get('search', '').strip()
        department_filter = request.args.get('department', '').strip()
        
        db = get_db()
        if not db:
            return jsonify({'success': False, 'message': 'DB connection failed'}), 500
        
        cursor = db.cursor(dictionary=True)

        # Pull latest token per patient from appointments table
        query = """
            SELECT p.*, pa.token_number
            FROM patients p
            LEFT JOIN (
                SELECT patient_id, token_number
                FROM patient_appointments
                WHERE id IN (
                    SELECT MAX(id) FROM patient_appointments GROUP BY patient_id
                )
            ) pa ON pa.patient_id = p.patient_id
            WHERE 1=1
        """
        params = []
        
        # Unified search - searches in name, phone, gender, and token (patient_id/token_number)
        if search_query:
            token_num = ''.join(filter(str.isdigit, search_query))
            search_like = f"%{search_query}%"
            query += " AND (p.name LIKE %s OR p.phone LIKE %s OR p.gender LIKE %s OR pa.token_number LIKE %s"
            params.extend([search_like, search_like, search_like, search_like])
            if token_num:
                query += " OR p.patient_id = %s OR pa.token_number LIKE %s"
                params.extend([int(token_num), f"%{token_num}%"])
            query += ")"
        
        # Department filter
        if department_filter:
            query += " AND p.department LIKE %s"
            params.append(f"%{department_filter}%")
        
        # Order by patient_id
        cursor.execute(query + " ORDER BY p.patient_id DESC", params)
        
        patients = cursor.fetchall()
        
        # Ensure all required fields are present
        for patient in patients:
            # Ensure patient_id is set
            if 'patient_id' not in patient:
                patient['patient_id'] = patient.get('id', 0)
            
            # Fallback token if missing (older records)
            if not patient.get('token_number'):
                patient['token_number'] = f"P{str(patient['patient_id']).zfill(3)}"
            
            # Add blood_group if missing
            if 'blood_group' not in patient:
                patient['blood_group'] = 'N/A'
            
            # Ensure created_at exists for date display
            if 'created_at' not in patient and 'registration_date' in patient:
                patient['created_at'] = patient['registration_date']
        
        cursor.close()
        db.close()
        
        return jsonify({'success': True, 'patients': patients})
    except Error as e:
        print(f"❌ Error fetching all patients: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

# ==================== OPD ACTIONS ====================
@app.route('/start-consultation/<int:patient_id>', methods=['POST'])
@require_admin
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
@require_admin
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
@require_admin
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

@app.route('/assign-doctor/<int:patient_id>', methods=['POST'])
@require_admin
def assign_doctor(patient_id):
    try:
        payload = request.get_json(silent=True) or {}
        doctor_name = (payload.get('doctor_name') or '').strip()
        if not doctor_name:
            return jsonify({'success': False, 'message': 'Doctor name is required'}), 400

        db = get_db()
        if not db:
            return jsonify({'success': False, 'message': 'DB connection failed'}), 500
        cursor = db.cursor()
        cursor.execute("UPDATE patients SET assigned_doctor = %s WHERE patient_id = %s", (doctor_name, patient_id))
        db.commit()
        cursor.close()
        db.close()
        return jsonify({'success': True, 'doctor_name': doctor_name})
    except Error as e:
        print(f"❌ assign_doctor error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/admit-patient/<int:patient_id>', methods=['POST'])
@require_admin
def admit_patient(patient_id):
    try:
        db = get_db()
        if not db:
            return jsonify({'success': False, 'message': 'DB connection failed'}), 500
        cursor = db.cursor(dictionary=True)
        
        # Get patient details first
        cursor.execute("SELECT patient_id, name, department FROM patients WHERE patient_id = %s", (patient_id,))
        patient = cursor.fetchone()
        
        if not patient:
            # Fallback: treat provided value as token
            cursor.execute("SELECT patient_id, name, department FROM patients WHERE token = %s", (patient_id,))
            patient = cursor.fetchone()
            if not patient:
                cursor.close()
                db.close()
                return jsonify({'success': False, 'message': 'Patient not found'}), 404
            patient_id = patient['patient_id']
        
        # Get patient's department to find appropriate bed
        patient_department = patient.get('department', 'General Ward')
        
        # Map departments to wards
        ward_mapping = {
            'ICU': 'ICU',
            'Cardiology': 'Cardiology Ward',
            'Orthopedics': 'Orthopedic Ward',
            'Neurology': 'Neurology Ward',
            'Pediatrics': 'Pediatric Ward',
            'Emergency': 'Emergency Ward'
        }
        ward_name = ward_mapping.get(patient_department, 'General Ward')
        
        # Find available bed in matching ward or general ward
        cursor.execute(
            """
            SELECT bed_id, bed_name, ward, status FROM beds 
            WHERE status = 'available' AND (ward = %s OR ward = %s)
            ORDER BY FIELD(ward, %s, %s) DESC, bed_id ASC
            LIMIT 1
            """,
            (ward_name, 'General Ward', ward_name, 'General Ward')
        )
        available_bed = cursor.fetchone()
        
        if not available_bed:
            cursor.close()
            db.close()
            return jsonify({
                'success': False, 
                'message': f'No available beds in {ward_name} or General Ward'
            }), 400
        
        bed_id = available_bed['bed_id']
        bed_name = available_bed['bed_name']
        actual_ward = available_bed['ward']
        
        # Update bed status to occupied
        cursor.execute(
            """
            UPDATE beds 
            SET status = 'occupied', patient_id = %s, allocation_date = CURRENT_TIMESTAMP 
            WHERE bed_id = %s
            """,
            (patient_id, bed_id)
        )
        
        # Update patient status and bed_id
        cursor.execute(
            "UPDATE patients SET status = 'Admitted', bed_id = %s WHERE patient_id = %s",
            (bed_name, patient_id)
        )
        
        # Update OPD queue status
        try:
            cursor.execute("UPDATE opd_queue SET status = 'completed' WHERE patient_id = %s", (patient_id,))
        except Exception as e:
            print(f"⚠️  Warning updating OPD queue: {e}")
        
        db.commit()
        cursor.close()
        db.close()
        
        return jsonify({
            'success': True,
            'bed_number': bed_name,
            'bed_id': bed_id,
            'ward_name': actual_ward,
            'patient_name': patient['name'],
            'message': f'✅ Patient admitted to Bed {bed_name} in {actual_ward}'
        })
    except Exception as e:
        print(f"❌ admit_patient error: {e}")
        import traceback
        print(traceback.format_exc())
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/delete-patient/<int:patient_id>', methods=['POST'])
@require_admin
def delete_patient(patient_id):
    """Delete a patient record"""
    try:
        db = get_db()
        if not db:
            return jsonify({'success': False, 'message': 'DB connection failed'}), 500
        
        cursor = db.cursor()
        
        # Delete from related tables first
        cursor.execute("DELETE FROM opd_queue WHERE patient_id = %s", (patient_id,))
        cursor.execute("DELETE FROM patient_appointments WHERE patient_id = %s", (patient_id,))
        cursor.execute("DELETE FROM patients WHERE patient_id = %s", (patient_id,))
        
        db.commit()
        cursor.close()
        db.close()
        
        return jsonify({'success': True, 'message': 'Patient deleted successfully'})
    except Error as e:
        print(f"❌ Error deleting patient: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/discharge-patient/<int:patient_id>', methods=['POST'])
@require_admin
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
@require_admin
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
@require_admin
def switch_role():
    role = request.args.get('role', 'Admin')
    if role not in ADMIN_ROLES:
        flash('Invalid role change request.', 'error')
        return redirect(url_for('hospital_view_dashboard'))
    session['role'] = role
    session['view_role'] = 'hospital'
    return redirect(url_for('hospital_view_dashboard'))

# ==================== PATIENT REGISTRATION ====================
@app.route('/patient-registration', methods=['GET', 'POST'])
def patient_registration():
    was_staff = session.get('role') in ADMIN_ROLES
    prev_role = session.get('role')
    prev_view_role = session.get('view_role')

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
            appointment_date_raw = request.form.get('appointment_date', '').strip()
            appointment_time_raw = request.form.get('appointment_time', '').strip()

            appointment_date_val = None
            appointment_time_val = None

            if appointment_date_raw:
                try:
                    appointment_date_val = datetime.strptime(appointment_date_raw, '%Y-%m-%d').date()
                except ValueError:
                    flash('Please choose a valid appointment date.', 'error')
                    return render_template('patient_registration.html', force_form=True)
            else:
                appointment_date_val = datetime.today().date()

            if appointment_time_raw:
                try:
                    appointment_time_val = datetime.strptime(appointment_time_raw, '%H:%M').time()
                except ValueError:
                    flash('Please choose a valid appointment time.', 'error')
                    return render_template('patient_registration.html', force_form=True)
            
            # Validation
            if not all([name, age, department, phone]):
                flash('Name, Age, Department, and Phone are required!', 'error')
                return render_template('patient_registration.html', force_form=True)
            
            try:
                age = int(age)
                if age < 1 or age > 150:
                    flash('Please enter a valid age (1-150)', 'error')
                    return render_template('patient_registration.html', force_form=True)
            except ValueError:
                flash('Age must be a number', 'error')
                return render_template('patient_registration.html', force_form=True)
            
            # Generate unique token number
            token_number = random.randint(10000, 99999)
            queue_position = None
            
            # Insert into database
            db = get_db()
            if db:
                cursor = db.cursor()
                
                # Check which columns exist in the patients table
                try:
                    cursor.execute("SHOW COLUMNS FROM patients")
                    columns = [col[0] for col in cursor.fetchall()]
                    
                    # Build dynamic INSERT query based on available columns
                    insert_cols = ['name', 'age', 'phone', 'department', 'status']
                    insert_vals = [name, age, phone, department, 'Waiting']
                    
                    if 'gender' in columns and gender:
                        insert_cols.append('gender')
                        insert_vals.append(gender)
                    
                    if 'blood_group' in columns and blood_group:
                        insert_cols.append('blood_group')
                        insert_vals.append(blood_group)
                    
                    if 'date_of_birth' in columns and date_of_birth:
                        insert_cols.append('date_of_birth')
                        insert_vals.append(date_of_birth)
                    
                    if 'email' in columns and email:
                        insert_cols.append('email')
                        insert_vals.append(email)
                    
                    if 'address' in columns and address:
                        insert_cols.append('address')
                        insert_vals.append(address)
                    
                    if 'medical_history' in columns and medical_history:
                        insert_cols.append('medical_history')
                        insert_vals.append(medical_history)
                    
                    if 'emergency_contact' in columns and emergency_contact:
                        insert_cols.append('emergency_contact')
                        insert_vals.append(emergency_contact)
                    
                    placeholders = ', '.join(['%s'] * len(insert_vals))
                    query = f"""
                        INSERT INTO patients 
                        ({', '.join(insert_cols)})
                        VALUES ({placeholders})
                    """
                    
                    cursor.execute(query, insert_vals)
                except Exception as e:
                    # Fallback to basic insert
                    print(f"⚠️ Column check failed, using basic insert: {e}")
                    query = """
                        INSERT INTO patients 
                        (name, age, phone, department, status)
                        VALUES (%s, %s, %s, %s, %s)
                    """
                    cursor.execute(query, (name, age, phone, department, 'Waiting'))
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

                try:
                    queue_position = record_patient_appointment(
                        patient_id,
                        token_number,
                        department,
                        appointment_date_val.isoformat() if appointment_date_val else None,
                        appointment_time_val.strftime('%H:%M:%S') if appointment_time_val else None
                    )
                except Error as e:
                    queue_position = None
                    print(f"⚠️  Warning: Could not record appointment: {e}")

                cursor.close()
                db.close()
                
                # Store in session
                session['patient_id'] = patient_id
                session['patient_name'] = name
                session['patient_age'] = age
                session['patient_department'] = department
                session['token_number'] = token_number
                session['appointment_date'] = appointment_date_val.isoformat() if appointment_date_val else None
                session['appointment_time'] = appointment_time_val.strftime('%H:%M') if appointment_time_val else None
                session['queue_position'] = queue_position
                
                # Preserve staff session so admin/doctor/receptionist keeps assign controls after registration
                if was_staff:
                    session['role'] = prev_role
                    session['view_role'] = prev_view_role or 'hospital'
                    session['last_registered_patient_id'] = patient_id
                    session['last_registered_token'] = token_number
                else:
                    session['role'] = 'Patient'
                    session['view_role'] = 'patient'
                
                print(f"✅ Patient registered: {name} - Token: {token_number}")
                flash(f'Registration successful! Token: {token_number}', 'success')
                return redirect(url_for('registration_success', token=token_number))
            else:
                flash('Database connection error', 'error')
                return render_template('patient_registration.html', force_form=True)
                
        except Error as e:
            print(f"❌ Database error: {e}")
            flash(f'Database Error: {str(e)}', 'error')
            return render_template('patient_registration.html', force_form=True)
        except Exception as e:
            print(f"❌ Error: {e}")
            flash(f'Error: {str(e)}', 'error')
            return render_template('patient_registration.html', force_form=True)
    
    # GET: always show form by default unless explicitly viewing existing registration
    force_form = True  # Always show form by default
    return render_template('patient_registration.html', force_form=force_form)

# ==================== REGISTRATION SUCCESS ====================
@app.route('/registration-success')
def registration_success():
    token = request.args.get('token')
    patient_name = session.get('patient_name')
    patient_age = session.get('patient_age')
    patient_department = session.get('patient_department')
    patient_id = session.get('patient_id')
    appointment_date = session.get('appointment_date')
    appointment_time = session.get('appointment_time')
    queue_position = session.get('queue_position')
    
    print(f"📋 Registration Success - Token: {token}, Name: {patient_name}")
    
    if not token or not patient_name:
        flash('Please complete registration first', 'error')
        return redirect(url_for('patient_registration'))
    
    return render_template('registration_success.html', 
                         token=token, 
                         patient_name=patient_name,
                         patient_age=patient_age,
                         patient_department=patient_department,
                         patient_id=patient_id,
                         appointment_date=appointment_date,
                         appointment_time=appointment_time,
                         queue_position=queue_position)

# ==================== BED MANAGEMENT ====================
@app.route('/bed-management')
@require_admin
def bed_management():
    return render_template('bed_test.html')

@app.route('/bed-management-advanced')
@require_admin
def bed_management_advanced():
    return render_template('bed_management_advanced.html')

@app.route('/view-beds-public')
def view_beds_public():
    """Public view of bed availability - anyone can see available beds"""
    return render_template('bed_availability_public.html')

# ==================== OPD QUEUE ====================
@app.route('/opd-queue')
def opd_queue():
    # Smart redirect:
    # - If user is admin (Admin/Doctor/Receptionist) AND not in patient view → admin view (buttons visible)
    # - Otherwise → public read-only view
    view_role = session.get('view_role') or ''
    if is_admin() and view_role != 'patient':
        return redirect(url_for('opd_queue_advanced'))
    return redirect(url_for('opd_queue_advanced', public='1'))

@app.route('/opd-queue-advanced')
def opd_queue_advanced():
    # Public read-only mode is active when:
    # - query param ?public=1, or
    # - current session view is 'patient'
    public_qs = (request.args.get('public', '').lower() in ['1', 'true', 'yes'])
    is_patient_view = (session.get('view_role') == 'patient')
    public_flag = public_qs or is_patient_view
    effective_is_admin = (is_admin() and not public_flag)
    return render_template('opd_queue_advanced.html', is_admin=effective_is_admin)

@app.route('/opd-queue-old')
def opd_queue_old():
    role = session.get('role', 'Public View')
    dept = request.args.get('dept', 'All Departments')
    doctor = request.args.get('doctor', 'Dr. On Duty')
    return render_template('opd_queue.html', role=role, selected_department=dept, doctor_name=doctor)

# ==================== PATIENT DASHBOARD ====================
@app.route('/patient-dashboard')
def patient_dashboard():
    role = session.get('role', 'Public View')
    if not is_admin():
        role = 'Patient'
        session['role'] = role
    
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
    # Set session role to patient for guests
    session['view_role'] = 'patient'
    if not is_admin():
        session['role'] = 'Patient'
    
    # Use fetch_dashboard_counts() to get consistent data
    counts = fetch_dashboard_counts()
    
    return render_template('dashboards/patient.html',
                         patients_today=counts['patients_today'],
                         in_queue=counts['in_queue'],
                         occupied_beds=counts['occupied_beds'],
                         total_beds=counts['total_beds'],
                         bed_occupancy_rate=counts['bed_occupancy_rate'])

@app.route('/dashboard/hospital')
@require_admin
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

@app.route('/reports')
@require_admin
def reports():
    """Hospital Reports and Analytics Dashboard"""
    session['view_role'] = 'hospital'
    
    # Initialize variables
    total_patients = 0
    patients_today = 0
    patients_this_week = 0
    patients_this_month = 0
    total_consultations = 0
    consultations_today = 0
    total_admissions = 0
    admissions_today = 0
    avg_wait_time = 0
    bed_occupancy_rate = 0
    
    # Department-wise statistics
    department_stats = []
    
    # Monthly trend data (last 6 months)
    monthly_data = []
    
    # Status distribution
    status_distribution = {
        'waiting': 0,
        'in_queue': 0,
        'in_consultation': 0,
        'completed': 0,
        'admitted': 0,
        'discharged': 0
    }
    
    try:
        db = get_db()
        if db:
            cursor = db.cursor(dictionary=True)
            
            # Total patients
            try:
                cursor.execute("SELECT COUNT(*) as count FROM patients")
                result = cursor.fetchone()
                total_patients = result['count'] if result else 0
            except:
                pass
            
            # Patients today
            try:
                cursor.execute("SELECT COUNT(*) as count FROM patients WHERE DATE(created_at) = CURDATE()")
                result = cursor.fetchone()
                patients_today = result['count'] if result else 0
            except:
                pass
            
            # Patients this week
            try:
                cursor.execute("SELECT COUNT(*) as count FROM patients WHERE YEARWEEK(created_at) = YEARWEEK(CURDATE())")
                result = cursor.fetchone()
                patients_this_week = result['count'] if result else 0
            except:
                pass
            
            # Patients this month
            try:
                cursor.execute("SELECT COUNT(*) as count FROM patients WHERE YEAR(created_at) = YEAR(CURDATE()) AND MONTH(created_at) = MONTH(CURDATE())")
                result = cursor.fetchone()
                patients_this_month = result['count'] if result else 0
            except:
                pass
            
            # Total consultations
            try:
                cursor.execute("SELECT COUNT(*) as count FROM patients WHERE status IN ('Consulted', 'Completed')")
                result = cursor.fetchone()
                total_consultations = result['count'] if result else 0
            except:
                pass
            
            # Consultations today
            try:
                cursor.execute("SELECT COUNT(*) as count FROM patients WHERE status IN ('Consulted', 'Completed') AND DATE(created_at) = CURDATE()")
                result = cursor.fetchone()
                consultations_today = result['count'] if result else 0
            except:
                pass
            
            # Total admissions
            try:
                cursor.execute("SELECT COUNT(*) as count FROM patients WHERE status = 'Admitted'")
                result = cursor.fetchone()
                total_admissions = result['count'] if result else 0
            except:
                pass
            
            # Admissions today
            try:
                cursor.execute("SELECT COUNT(*) as count FROM patients WHERE status = 'Admitted' AND DATE(created_at) = CURDATE()")
                result = cursor.fetchone()
                admissions_today = result['count'] if result else 0
            except:
                pass
            
            # Bed occupancy
            try:
                cursor.execute("SELECT COUNT(*) as occupied FROM beds WHERE status = 'Occupied'")
                result = cursor.fetchone()
                occupied = result['occupied'] if result else 0
                
                cursor.execute("SELECT COUNT(*) as total FROM beds")
                result = cursor.fetchone()
                total = result['total'] if result else 50
                
                if total > 0:
                    bed_occupancy_rate = round((occupied / total) * 100, 1)
            except:
                pass
            
            # Status distribution
            try:
                cursor.execute("""
                    SELECT status, COUNT(*) as count 
                    FROM patients 
                    GROUP BY status
                """)
                statuses = cursor.fetchall()
                for s in statuses:
                    status_key = s['status'].lower().replace(' ', '_')
                    if status_key in status_distribution:
                        status_distribution[status_key] = s['count']
            except:
                pass
            
            # Department-wise statistics
            try:
                cursor.execute("""
                    SELECT 
                        department,
                        COUNT(*) as total_patients,
                        SUM(CASE WHEN status IN ('Consulted', 'Completed') THEN 1 ELSE 0 END) as completed,
                        SUM(CASE WHEN status IN ('Waiting', 'In Queue') THEN 1 ELSE 0 END) as waiting
                    FROM patients
                    WHERE department IS NOT NULL
                    GROUP BY department
                    ORDER BY total_patients DESC
                """)
                department_stats = cursor.fetchall()
            except:
                pass
            
            # Monthly trend (last 6 months)
            try:
                cursor.execute("""
                    SELECT 
                        DATE_FORMAT(created_at, '%Y-%m') as month,
                        COUNT(*) as patient_count
                    FROM patients
                    WHERE created_at >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH)
                    GROUP BY DATE_FORMAT(created_at, '%Y-%m')
                    ORDER BY month ASC
                """)
                monthly_data = cursor.fetchall()
            except:
                pass
            
            cursor.close()
            db.close()
    except Error as e:
        print(f"❌ Error fetching reports data: {e}")
    
    return render_template('reports.html',
                         total_patients=total_patients,
                         patients_today=patients_today,
                         patients_this_week=patients_this_week,
                         patients_this_month=patients_this_month,
                         total_consultations=total_consultations,
                         consultations_today=consultations_today,
                         total_admissions=total_admissions,
                         admissions_today=admissions_today,
                         avg_wait_time=avg_wait_time,
                         bed_occupancy_rate=bed_occupancy_rate,
                         status_distribution=status_distribution,
                         department_stats=department_stats,
                         monthly_data=monthly_data)

@app.route('/switch-view/<view>')
def switch_view(view):
    """Switch between patient and hospital views"""
    if view not in ['patient', 'hospital']:
        flash('Invalid view type', 'error')
        return redirect(url_for('home'))

    if view == 'hospital' and not is_admin():
        flash('You need admin access to open the hospital dashboard.', 'error')
        session['view_role'] = 'patient'
        return redirect(url_for('patient_view_dashboard'))

    session['view_role'] = view
    if view == 'patient' and not is_admin():
        session['role'] = 'Patient'
    flash(f'Switched to {view.capitalize()} View', 'success')

    if view == 'patient':
        return redirect(url_for('patient_view_dashboard'))
    return redirect(url_for('hospital_view_dashboard'))

# ==================== DASHBOARD ROOT REDIRECT ====================
@app.route('/dashboard')
def dashboard_root():
    """Redirect to the appropriate dashboard based on session role."""
    if session.get('view_role') in ['hospital', 'doctor'] and is_admin():
        return redirect(url_for('hospital_view_dashboard'))
    return redirect(url_for('patient_view_dashboard'))

# ==================== ROUTE ALIASES ====================
app.add_url_rule('/', 'index', home)
app.add_url_rule('/opd-queue', 'opd_queue_assignment', opd_queue)
app.add_url_rule('/bed-management', 'bed_management_view', bed_management)

# ==================== BED ASSIGNMENT API ====================
@app.route('/api/assign-bed', methods=['POST'])
@require_admin
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
            WHERE patient_id = %s
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
@require_admin
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
        cursor.execute("SELECT bed_id FROM patients WHERE patient_id = %s", (patient_id,))
        patient = cursor.fetchone()
        
        if not patient or not patient['bed_id']:
            return jsonify({'success': False, 'message': 'Patient not found or not admitted'}), 400
        
        bed_name = patient['bed_id']
        
        # Update patient status
        cursor.execute("""
            UPDATE patients 
            SET status = 'Discharged', bed_id = NULL, assigned_doctor = NULL
            WHERE patient_id = %s
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
@require_admin
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
@require_admin
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
            WHERE patient_id = %s
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
@require_admin
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
                p.registration_date as admission_date,
                p.department as patient_department,
                p.assigned_doctor as assigned_doctor
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

        # Public read-only: hide patient PII for non-admin viewers
        if not is_admin():
            sanitized = []
            for b in all_beds:
                sanitized.append({
                    'id': b.get('id'),
                    'bed_name': b.get('bed_name'),
                    'ward': b.get('ward'),
                    'status': b.get('status')
                })
            return jsonify({'success': True, 'beds': sanitized})

        return jsonify({'success': True, 'beds': all_beds})
    
    except Exception as e:
        print(f"Error fetching all beds: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/waiting-patients', methods=['GET'])
@require_admin
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
@require_admin
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
@require_admin
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
            WHERE patient_id = %s OR patient_id LIKE %s OR token = %s OR token LIKE %s
            LIMIT 1
        """
        
        cursor.execute(query, (search_term, f"{search_term}%", search_term, f"{search_term}%"))
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
    app.run(debug=False, host='0.0.0.0', port=5000)

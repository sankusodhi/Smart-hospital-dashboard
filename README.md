# MediFlow Hospital Management System

A modern hospital management system built with Flask and MySQL.

## Features
- Patient registration and management
- OPD queue management
- Bed availability tracking
- Doctor management
- Responsive dashboard

## Requirements
- Python 3.7+
- MySQL 5.7+
- pip

## Installation

1. Create virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
from mysql.connector import Error
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key_here_change_in_production'

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'your_password',  # Change this
    'database': 'mediflow'
}

def get_db():
    """
    Create and return a database connection
    """
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"Database connection error: {e}")
        return None

@app.route('/')
def index():
    """
    Dashboard route - displays patient statistics and recent patients
    """
    db = get_db()
    if not db:
        flash('Database connection failed', 'error')
        return render_template('index.html', 
                             patients_today=0, 
                             in_queue=0,
                             occupied_beds=0,
                             total_beds=100,
                             icu_occupied=0,
                             icu_total=20,
                             icu_percent=0,
                             general_occupied=0,
                             general_total=80,
                             general_percent=0,
                             recent_patients=[])
    
    try:
        cursor = db.cursor(dictionary=True)
        
        # Get total patients count
        cursor.execute("SELECT COUNT(*) as total FROM patients")
        total_patients = cursor.fetchone()['total']
        
        # Get patients registered today
        cursor.execute("""
            SELECT COUNT(*) as today 
            FROM patients 
            WHERE DATE(created_at) = CURDATE()
        """)
        patients_today = cursor.fetchone()['today']
        
        # Get recent patients (last 5)
        cursor.execute("""
            SELECT id, name, department, 
                   CASE 
                       WHEN status IS NULL THEN 'Waiting'
                       ELSE status 
                   END as status
            FROM patients 
            ORDER BY created_at DESC 
            LIMIT 5
        """)
        recent_patients = cursor.fetchall()
        
        # Mock data for bed utilization (you can replace with real data)
        icu_occupied = 12
        icu_total = 20
        general_occupied = 45
        general_total = 80
        
        cursor.close()
        db.close()
        
        return render_template('index.html',
                             patients_today=patients_today,
                             in_queue=total_patients,
                             occupied_beds=icu_occupied + general_occupied,
                             total_beds=icu_total + general_total,
                             icu_occupied=icu_occupied,
                             icu_total=icu_total,
                             icu_percent=int((icu_occupied/icu_total)*100),
                             general_occupied=general_occupied,
                             general_total=general_total,
                             general_percent=int((general_occupied/general_total)*100),
                             recent_patients=recent_patients)
    
    except Error as e:
        print(f"Database query error: {e}")
        flash('Error fetching data', 'error')
        return render_template('index.html',
                             patients_today=0,
                             in_queue=0,
                             occupied_beds=0,
                             total_beds=100,
                             icu_occupied=0,
                             icu_total=20,
                             icu_percent=0,
                             general_occupied=0,
                             general_total=80,
                             general_percent=0,
                             recent_patients=[])

@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    Patient registration route
    GET: Display registration form
    POST: Process form and insert patient into database
    """
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name', '').strip()
        age = request.form.get('age', '').strip()
        department = request.form.get('department', '').strip()
        
        # Validate form data
        if not name or not age or not department:
            flash('All fields are required!', 'error')
            return render_template('register.html')
        
        try:
            age = int(age)
            if age <= 0 or age > 150:
                flash('Please enter a valid age', 'error')
                return render_template('register.html')
        except ValueError:
            flash('Age must be a number', 'error')
            return render_template('register.html')
        
        # Insert into database
        db = get_db()
        if not db:
            flash('Database connection failed', 'error')
            return render_template('register.html')
        
        try:
            cursor = db.cursor()
            
            # Use parameterized query to prevent SQL injection
            query = """
                INSERT INTO patients (name, age, department, status, created_at) 
                VALUES (%s, %s, %s, %s, %s)
            """
            values = (name, age, department, 'Waiting', datetime.now())
            
            cursor.execute(query, values)
            db.commit()
            
            cursor.close()
            db.close()
            
            flash(f'Patient {name} registered successfully!', 'success')
            return redirect(url_for('index'))
        
        except Error as e:
            print(f"Database insert error: {e}")
            flash('Error registering patient. Please try again.', 'error')
            if db:
                db.close()
            return render_template('register.html')
    
    # GET request - show form
    return render_template('register.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
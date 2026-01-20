from flask import Flask, render_template

app = Flask(__name__, template_folder='templates')

@app.route('/bed-management')
def bed_management():
    wards = {
        'General': {
            'beds': [
                {'bed_id': 1, 'bed_name': 'GEN-01', 'status': 'Available', 'patient_name': None, 'assigned_doctor': None},
                {'bed_id': 2, 'bed_name': 'GEN-02', 'status': 'Occupied', 'patient_name': 'Rajesh Kumar', 'assigned_doctor': 'Dr. Sharma'},
                {'bed_id': 3, 'bed_name': 'GEN-03', 'status': 'Available', 'patient_name': None, 'assigned_doctor': None},
            ],
            'total': 3,
            'available': 2,
            'occupied': 1
        }
    }
    return render_template('bed_management_simple.html', wards=wards)

if __name__ == '__main__':
    app.run(debug=True, port=5000)

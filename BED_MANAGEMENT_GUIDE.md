# Bed Management System - Setup Guide

## Overview
The improved bed management system now displays:
✅ Patient names on assigned beds
✅ Assigned doctor names
✅ Red color for occupied/booked beds (Green for available)
✅ Bed assignments based on actual bed names from database

## Database Setup

### Step 1: Update Database Schema
Run the following SQL commands to update your database:

```sql
-- Add assigned_doctor column to patients table
ALTER TABLE patients ADD COLUMN IF NOT EXISTS assigned_doctor VARCHAR(100);

-- Add bed_name column to beds table
ALTER TABLE beds ADD COLUMN IF NOT EXISTS bed_name VARCHAR(20) UNIQUE;
```

### Step 2: Populate Sample Bed Data
Run the `sample_bed_data.sql` file to create sample beds and patient assignments:

```bash
mysql -u root -p mediflow < sample_bed_data.sql
```

Or manually execute the SQL from `sample_bed_data.sql` in your MySQL client.

## Features

### 1. Visual Status Indicators
- **Green beds**: Available beds with pulsing green indicator
- **Red beds**: Occupied beds with pulsing red indicator
- Hover effects for better interactivity

### 2. Bed Information Display
Each bed card shows:
- Bed Name (e.g., ICU-01, GEN-02, SEMI-03, PVT-01)
- Status indicator (animated pulse)
- For occupied beds:
  - Patient name with 👤 icon
  - Assigned doctor name with 👨‍⚕️ icon
- For available beds:
  - "Available" badge

### 3. Ward Organization
Beds are organized by wards:
- **ICU** (Intensive Care Unit) - Red theme
- **General** (Standard patient care) - Blue theme
- **Semi-Private** (Shared accommodation) - Purple theme
- **Private** (Private rooms) - Orange theme

Each ward section shows:
- Total beds
- Available beds count
- Occupied beds count

### 4. Responsive Design
- Desktop: Multi-column grid layout
- Tablet: Adjusted column layout
- Mobile: Single column layout

## Bed Naming Convention

The system uses the following bed naming convention:

| Ward Type | Prefix | Example |
|-----------|--------|---------|
| ICU | ICU- | ICU-01, ICU-02, ICU-03 |
| General Ward | GEN- | GEN-01, GEN-02, GEN-03 |
| Semi-Private | SEMI- | SEMI-01, SEMI-02, SEMI-03 |
| Private | PVT- | PVT-01, PVT-02, PVT-03 |

## API Endpoints

### 1. Assign Patient to Bed
**Endpoint**: `POST /api/assign-bed`

**Request Body**:
```json
{
  "patient_id": 1,
  "bed_name": "ICU-01",
  "doctor_name": "Dr. Sharma"
}
```

**Response**:
```json
{
  "success": true,
  "message": "Patient assigned to bed successfully"
}
```

### 2. Discharge Patient
**Endpoint**: `POST /api/discharge-patient`

**Request Body**:
```json
{
  "patient_id": 1
}
```

**Response**:
```json
{
  "success": true,
  "message": "Patient discharged successfully"
}
```

## Usage Examples

### Assigning a Patient to a Bed (JavaScript)
```javascript
async function assignBed(patientId, bedName, doctorName) {
    const response = await fetch('/api/assign-bed', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            patient_id: patientId,
            bed_name: bedName,
            doctor_name: doctorName
        })
    });
    
    const result = await response.json();
    if (result.success) {
        alert('Patient assigned successfully!');
        location.reload(); // Refresh to see updated bed status
    } else {
        alert('Error: ' + result.message);
    }
}

// Example usage
assignBed(1, 'ICU-01', 'Dr. Sharma');
```

### Discharging a Patient (JavaScript)
```javascript
async function dischargePatient(patientId) {
    const response = await fetch('/api/discharge-patient', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            patient_id: patientId
        })
    });
    
    const result = await response.json();
    if (result.success) {
        alert('Patient discharged successfully!');
        location.reload();
    } else {
        alert('Error: ' + result.message);
    }
}
```

## Adding New Beds

To add new beds to the system, use this SQL:

```sql
-- Add a new ICU bed
INSERT INTO beds (bed_name, ward, status) VALUES ('ICU-07', 'ICU', 'Available');

-- Add multiple beds at once
INSERT INTO beds (bed_name, ward, status) VALUES
('GEN-11', 'General', 'Available'),
('GEN-12', 'General', 'Available'),
('SEMI-07', 'Semi-Private', 'Available'),
('PVT-05', 'Private', 'Available');
```

## Admitting a Patient with Bed Assignment

When admitting a patient:

```sql
-- Method 1: Direct SQL
UPDATE patients 
SET 
    bed_id = 'ICU-01',
    assigned_doctor = 'Dr. Sharma',
    status = 'Admitted'
WHERE id = 1;

UPDATE beds 
SET status = 'Occupied'
WHERE bed_name = 'ICU-01';

-- Method 2: Use the API endpoint (recommended)
-- See API Endpoints section above
```

## Troubleshooting

### Issue: Beds not showing
**Solution**: Run the sample_bed_data.sql to populate beds

### Issue: Patient names not appearing on occupied beds
**Solution**: Ensure the patient's `bed_id` matches the bed's `bed_name` exactly

### Issue: Colors not showing correctly
**Solution**: Clear browser cache and refresh the page

### Issue: Database column errors
**Solution**: Run the ALTER TABLE commands from Step 1 of Database Setup

## File Structure

```
mediflow/
├── app.py                              # Updated with bed management logic
├── schema.sql                          # Updated database schema
├── sample_bed_data.sql                 # Sample bed and patient data
└── templates/
    └── bed_management_dynamic.html     # New bed management template
```

## Testing the System

1. Start the Flask application:
```bash
cd mediflow
python app.py
```

2. Navigate to: `http://127.0.0.1:5000/bed-management`

3. You should see:
   - Green available beds
   - Red occupied beds with patient names and doctor names
   - Ward-wise organization
   - Real-time bed availability counts

## Sample Data Included

The system comes with 8 sample admitted patients:

| Patient | Bed | Doctor | Ward |
|---------|-----|--------|------|
| Rajesh Kumar | ICU-02 | Dr. Sharma | ICU |
| Amit Verma | ICU-05 | Dr. Gupta | ICU |
| Priya Singh | GEN-02 | Dr. Patel | General |
| Sunita Devi | GEN-05 | Dr. Reddy | General |
| Vikas Yadav | GEN-07 | Dr. Patel | General |
| Neha Agarwal | SEMI-01 | Dr. Kapoor | Semi-Private |
| Ramesh Patel | SEMI-03 | Dr. Sharma | Semi-Private |
| Kavita Mehta | PVT-01 | Dr. Reddy | Private |

## Next Steps

To integrate bed assignment into your patient admission workflow:

1. Add a bed selection dropdown in your patient registration/admission form
2. Include doctor assignment field
3. Call the `/api/assign-bed` endpoint when admitting
4. Use `/api/discharge-patient` endpoint when discharging

## Support

For issues or questions, check:
1. Database connection in config.py
2. Table structure matches schema.sql
3. Sample data loaded correctly
4. Browser console for JavaScript errors

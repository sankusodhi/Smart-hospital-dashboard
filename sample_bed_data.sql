-- Sample Bed Management Data for MediFlow

-- First, add the assigned_doctor column if it doesn't exist
ALTER TABLE patients ADD COLUMN IF NOT EXISTS assigned_doctor VARCHAR(100);

-- Add bed_name column if it doesn't exist
ALTER TABLE beds ADD COLUMN IF NOT EXISTS bed_name VARCHAR(20) UNIQUE;

-- Clear existing beds (optional - remove if you want to keep existing data)
-- DELETE FROM beds;

-- Insert sample beds with proper names
-- ICU Beds
INSERT INTO beds (bed_name, ward, status) VALUES
('ICU-01', 'ICU', 'Available'),
('ICU-02', 'ICU', 'Available'),
('ICU-03', 'ICU', 'Available'),
('ICU-04', 'ICU', 'Available'),
('ICU-05', 'ICU', 'Available'),
('ICU-06', 'ICU', 'Available')
ON DUPLICATE KEY UPDATE ward=VALUES(ward), status=VALUES(status);

-- General Ward Beds
INSERT INTO beds (bed_name, ward, status) VALUES
('GEN-01', 'General', 'Available'),
('GEN-02', 'General', 'Available'),
('GEN-03', 'General', 'Available'),
('GEN-04', 'General', 'Available'),
('GEN-05', 'General', 'Available'),
('GEN-06', 'General', 'Available'),
('GEN-07', 'General', 'Available'),
('GEN-08', 'General', 'Available'),
('GEN-09', 'General', 'Available'),
('GEN-10', 'General', 'Available')
ON DUPLICATE KEY UPDATE ward=VALUES(ward), status=VALUES(status);

-- Semi-Private Ward Beds
INSERT INTO beds (bed_name, ward, status) VALUES
('SEMI-01', 'Semi-Private', 'Available'),
('SEMI-02', 'Semi-Private', 'Available'),
('SEMI-03', 'Semi-Private', 'Available'),
('SEMI-04', 'Semi-Private', 'Available'),
('SEMI-05', 'Semi-Private', 'Available'),
('SEMI-06', 'Semi-Private', 'Available')
ON DUPLICATE KEY UPDATE ward=VALUES(ward), status=VALUES(status);

-- Private Ward Beds
INSERT INTO beds (bed_name, ward, status) VALUES
('PVT-01', 'Private', 'Available'),
('PVT-02', 'Private', 'Available'),
('PVT-03', 'Private', 'Available'),
('PVT-04', 'Private', 'Available')
ON DUPLICATE KEY UPDATE ward=VALUES(ward), status=VALUES(status);

-- Insert sample admitted patients with bed assignments
INSERT INTO patients (name, age, phone, department, status, bed_id, assigned_doctor) VALUES
('Rajesh Kumar', 45, '9876543210', 'Cardiology', 'Admitted', 'ICU-02', 'Dr. Sharma'),
('Priya Singh', 32, '9876543211', 'Orthopedics', 'Admitted', 'GEN-02', 'Dr. Patel'),
('Amit Verma', 58, '9876543212', 'Neurology', 'Admitted', 'ICU-05', 'Dr. Gupta'),
('Sunita Devi', 41, '9876543213', 'General Medicine', 'Admitted', 'GEN-05', 'Dr. Reddy'),
('Vikas Yadav', 29, '9876543214', 'Orthopedics', 'Admitted', 'GEN-07', 'Dr. Patel'),
('Neha Agarwal', 36, '9876543215', 'Gynecology', 'Admitted', 'SEMI-01', 'Dr. Kapoor'),
('Ramesh Patel', 52, '9876543216', 'Cardiology', 'Admitted', 'SEMI-03', 'Dr. Sharma'),
('Kavita Mehta', 48, '9876543217', 'General Medicine', 'Admitted', 'PVT-01', 'Dr. Reddy')
ON DUPLICATE KEY UPDATE 
    bed_id = VALUES(bed_id),
    assigned_doctor = VALUES(assigned_doctor),
    status = VALUES(status);

-- Update bed status based on patient assignments
UPDATE beds b
LEFT JOIN patients p ON b.bed_name = p.bed_id AND p.status = 'Admitted'
SET b.status = CASE 
    WHEN p.id IS NOT NULL THEN 'Occupied'
    ELSE 'Available'
END;

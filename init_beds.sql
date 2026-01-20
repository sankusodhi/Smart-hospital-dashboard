-- Initialize Beds Table with sample data
USE mediflow;

-- Create/recreate beds table
DROP TABLE IF EXISTS beds;
CREATE TABLE beds (
    id INT AUTO_INCREMENT PRIMARY KEY,
    bed_name VARCHAR(20) UNIQUE NOT NULL,
    ward VARCHAR(50) NOT NULL DEFAULT 'General',
    status VARCHAR(20) NOT NULL DEFAULT 'Available',
    patient_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Insert sample beds
INSERT INTO beds (bed_name, ward, status) VALUES
-- ICU Beds
('ICU-01', 'ICU', 'Available'),
('ICU-02', 'ICU', 'Available'),
('ICU-03', 'ICU', 'Occupied'),
('ICU-04', 'ICU', 'Available'),
('ICU-05', 'ICU', 'Available'),
('ICU-06', 'ICU', 'Available'),
('ICU-07', 'ICU', 'Available'),
('ICU-08', 'ICU', 'Available'),
('ICU-09', 'ICU', 'Available'),
('ICU-10', 'ICU', 'Available'),

-- General Ward
('GEN-01', 'General', 'Available'),
('GEN-02', 'General', 'Occupied'),
('GEN-03', 'General', 'Available'),
('GEN-04', 'General', 'Available'),
('GEN-05', 'General', 'Available'),
('GEN-06', 'General', 'Available'),
('GEN-07', 'General', 'Available'),
('GEN-08', 'General', 'Available'),
('GEN-09', 'General', 'Available'),
('GEN-10', 'General', 'Occupied'),
('GEN-11', 'General', 'Available'),
('GEN-12', 'General', 'Available'),
('GEN-13', 'General', 'Available'),
('GEN-14', 'General', 'Available'),
('GEN-15', 'General', 'Available'),
('GEN-16', 'General', 'Available'),
('GEN-17', 'General', 'Available'),
('GEN-18', 'General', 'Available'),
('GEN-19', 'General', 'Available'),
('GEN-20', 'General', 'Available'),
('GEN-21', 'General', 'Available'),
('GEN-22', 'General', 'Available'),
('GEN-23', 'General', 'Available'),
('GEN-24', 'General', 'Available'),
('GEN-25', 'General', 'Available'),
('GEN-26', 'General', 'Available'),
('GEN-27', 'General', 'Available'),
('GEN-28', 'General', 'Available'),
('GEN-29', 'General', 'Available'),
('GEN-30', 'General', 'Available'),

-- Semi-Private Ward
('SP-01', 'Semi-Private', 'Available'),
('SP-02', 'Semi-Private', 'Available'),
('SP-03', 'Semi-Private', 'Occupied'),
('SP-04', 'Semi-Private', 'Available'),
('SP-05', 'Semi-Private', 'Available'),
('SP-06', 'Semi-Private', 'Available'),
('SP-07', 'Semi-Private', 'Available'),
('SP-08', 'Semi-Private', 'Available'),
('SP-09', 'Semi-Private', 'Available'),
('SP-10', 'Semi-Private', 'Available');

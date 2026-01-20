CREATE DATABASE mediflow;
USE mediflow;

CREATE TABLE IF NOT EXISTS patients (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    age INT NOT NULL,
    phone VARCHAR(15),
    department VARCHAR(50),
    status ENUM('Registered', 'Waiting', 'In Consultation', 'Admitted', 'Discharged') DEFAULT 'Registered',
    bed_id VARCHAR(20),
    assigned_doctor VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE opd_queue (
    token_id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT,
    department VARCHAR(50),
    status VARCHAR(20) DEFAULT 'Waiting'
);

CREATE TABLE beds (
    bed_id INT AUTO_INCREMENT PRIMARY KEY,
    bed_name VARCHAR(20) UNIQUE NOT NULL,
    ward VARCHAR(50),
    status VARCHAR(20) DEFAULT 'Available',
    patient_id INT NULL
);


-- Admin users table for authentication
CREATE TABLE IF NOT EXISTS admin_users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    full_name VARCHAR(200),
    role VARCHAR(100) DEFAULT 'Admin',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert a default admin (username: admin, password: admin) — change in production
INSERT IGNORE INTO admin_users (username, password, full_name, role)
VALUES ('admin', 'admin', 'Administrator', 'Admin');


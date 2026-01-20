@echo off
REM Bed Management System Setup Script for Windows
REM This script helps initialize the bed management system in MediFlow

echo ========================================
echo MediFlow Bed Management System Setup
echo ========================================
echo.

REM Check if MySQL is installed
where mysql >nul 2>nul
if %errorlevel% neq 0 (
    echo [X] MySQL is not installed or not in PATH
    echo Please install MySQL first
    pause
    exit /b 1
)

echo [+] MySQL found
echo.

REM Get database credentials
set /p DB_USER="Enter MySQL Username [root]: "
if "%DB_USER%"=="" set DB_USER=root

set /p DB_PASS="Enter MySQL Password: "
echo.

REM Database name
set DB_NAME=mediflow

echo [*] Updating database schema...

REM Update patients table
echo ALTER TABLE patients ADD COLUMN IF NOT EXISTS assigned_doctor VARCHAR(100); | mysql -u %DB_USER% -p%DB_PASS% %DB_NAME%
if %errorlevel% equ 0 (
    echo [+] Added assigned_doctor column to patients table
) else (
    echo [X] Failed to update patients table
)

REM Update beds table
echo ALTER TABLE beds ADD COLUMN IF NOT EXISTS bed_name VARCHAR(20) UNIQUE; | mysql -u %DB_USER% -p%DB_PASS% %DB_NAME%
if %errorlevel% equ 0 (
    echo [+] Added bed_name column to beds table
) else (
    echo [X] Failed to update beds table
)

echo.
echo [*] Populating sample bed data...

REM Load sample data
mysql -u %DB_USER% -p%DB_PASS% %DB_NAME% < sample_bed_data.sql
if %errorlevel% equ 0 (
    echo [+] Sample bed data loaded successfully
) else (
    echo [X] Failed to load sample data
    pause
    exit /b 1
)

echo.
echo ========================================
echo [+] Setup completed successfully!
echo ========================================
echo.
echo Your bed management system is ready!
echo.
echo Next steps:
echo 1. Start the Flask app: python app.py
echo 2. Navigate to: http://127.0.0.1:5000/bed-management
echo 3. Check the BED_MANAGEMENT_GUIDE.md for usage instructions
echo.
echo Sample data loaded:
echo   - 26 beds across 4 wards (ICU, General, Semi-Private, Private)
echo   - 8 admitted patients with bed assignments
echo.
pause

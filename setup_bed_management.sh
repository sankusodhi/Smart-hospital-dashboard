#!/bin/bash

# Bed Management System Setup Script
# This script helps initialize the bed management system in MediFlow

echo "========================================"
echo "MediFlow Bed Management System Setup"
echo "========================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if MySQL is installed
if ! command -v mysql &> /dev/null; then
    echo -e "${RED}❌ MySQL is not installed or not in PATH${NC}"
    echo "Please install MySQL first"
    exit 1
fi

echo -e "${GREEN}✓ MySQL found${NC}"
echo ""

# Get database credentials
echo "Enter your MySQL credentials:"
read -p "Username [root]: " DB_USER
DB_USER=${DB_USER:-root}

read -sp "Password: " DB_PASS
echo ""
echo ""

# Database name
DB_NAME="mediflow"

echo -e "${YELLOW}→ Updating database schema...${NC}"

# Update patients table
mysql -u "$DB_USER" -p"$DB_PASS" "$DB_NAME" << EOF
ALTER TABLE patients ADD COLUMN IF NOT EXISTS assigned_doctor VARCHAR(100);
EOF

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Added assigned_doctor column to patients table${NC}"
else
    echo -e "${RED}❌ Failed to update patients table${NC}"
fi

# Update beds table
mysql -u "$DB_USER" -p"$DB_PASS" "$DB_NAME" << EOF
ALTER TABLE beds ADD COLUMN IF NOT EXISTS bed_name VARCHAR(20) UNIQUE;
EOF

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Added bed_name column to beds table${NC}"
else
    echo -e "${RED}❌ Failed to update beds table${NC}"
fi

echo ""
echo -e "${YELLOW}→ Populating sample bed data...${NC}"

# Load sample data
mysql -u "$DB_USER" -p"$DB_PASS" "$DB_NAME" < sample_bed_data.sql

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Sample bed data loaded successfully${NC}"
else
    echo -e "${RED}❌ Failed to load sample data${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}========================================"
echo "✅ Setup completed successfully!"
echo "========================================${NC}"
echo ""
echo "Your bed management system is ready!"
echo ""
echo "Next steps:"
echo "1. Start the Flask app: python app.py"
echo "2. Navigate to: http://127.0.0.1:5000/bed-management"
echo "3. Check the BED_MANAGEMENT_GUIDE.md for usage instructions"
echo ""
echo "Sample data loaded:"
echo "  - 26 beds across 4 wards (ICU, General, Semi-Private, Private)"
echo "  - 8 admitted patients with bed assignments"
echo ""

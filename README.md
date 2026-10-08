# Hostel Room Allocation System

## Project Description
A DBMS laboratory project for managing hostel students, rooms and room allocations using HTML, CSS, Vanilla JavaScript, Python Flask and MySQL.

## Features
- Student CRUD and search
- Room CRUD and search
- Room allocation
- Change room
- Cancel allocation
- Room availability and status
- Dashboard statistics
- Frontend and backend validation
- Parameterized SQL
- Primary keys, foreign keys, unique and check constraints
- JOIN and COUNT aggregate queries

## Technology Stack
- Frontend: HTML, CSS, Vanilla JavaScript
- Backend: Python Flask
- Database: MySQL
- Connector: mysql-connector-python

## Database Design
students stores student details.
rooms stores hostel room details and occupancy.
allocations connects students and rooms through foreign keys.

Relationship:
students (1) ---- (many) allocations (many) ---- (1) rooms

An active allocation increases rooms.occupied. Cancelling an active allocation decreases it.

## Folder Structure
HostelRoomAllocation/
- app.py
- config.py
- requirements.txt
- README.md
- database/hostel.sql
- templates/
- static/css/style.css
- static/js/script.js

## Installation

### 1. Create the database
Open MySQL Workbench or MySQL command line and run database/hostel.sql.

### 2. Configure MySQL
Open config.py and change:
MYSQL_PASSWORD = "YOUR_MYSQL_PASSWORD"

Keep the other values if MySQL is running locally on port 3306.

### 3. Create a Python virtual environment
Windows PowerShell:
python -m venv venv
.env\Scripts\Activate.ps1

If PowerShell blocks activation, use:
venv\Scriptsctivate.bat

### 4. Install packages
pip install -r requirements.txt

### 5. Run the application
python app.py

Open:
http://127.0.0.1:5000

## CRUD Explanation
Create: Add Student and Add Room forms use INSERT.
Read: Student, Room, Allocation and Dashboard pages use SELECT.
Update: Edit pages use UPDATE; room change updates both allocation and room occupancy.
Delete: Student and Room pages use DELETE where referential rules permit.

## DBMS Concepts Demonstrated
- PRIMARY KEY uniquely identifies rows.
- FOREIGN KEY preserves relationships.
- UNIQUE prevents duplicate phone, email and room number.
- NOT NULL requires important values.
- DEFAULT gives allocations the Active status and rooms an initial occupied count of zero.
- CHECK validates year, capacity, occupancy and allocation status.
- JOIN combines student, room and allocation information.
- COUNT() produces dashboard totals.
- Transactions keep room allocation changes consistent.

## Testing
1. Add a valid student.
2. Try duplicate student ID, phone or email.
3. Add a room with capacity 2.
4. Allocate students until it becomes full.
5. Try another allocation and verify it is rejected.
6. Cancel an allocation and verify occupied decreases.
7. Change an active allocation to another available room.
8. Search students, rooms and allocations.
9. Edit and delete records.
10. Verify dashboard counts after each operation.

## Future Enhancements
- Admin login and role-based access
- Hostel/block master tables
- Student profile photos
- Reports and PDF export
- Room-wise occupancy charts
- Audit logs
- Email/SMS notifications

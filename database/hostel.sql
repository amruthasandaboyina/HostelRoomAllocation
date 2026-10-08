CREATE DATABASE IF NOT EXISTS hostel_db;
USE hostel_db;

DROP TABLE IF EXISTS allocations;
DROP TABLE IF EXISTS rooms;
DROP TABLE IF EXISTS students;

CREATE TABLE students (
    student_id INT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    gender VARCHAR(20) NOT NULL,
    course VARCHAR(100) NOT NULL,
    year INT NOT NULL,
    phone VARCHAR(15) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    CONSTRAINT chk_student_year CHECK (year BETWEEN 1 AND 6)
);

CREATE TABLE rooms (
    room_id INT PRIMARY KEY AUTO_INCREMENT,
    room_number VARCHAR(20) UNIQUE NOT NULL,
    block VARCHAR(20) NOT NULL,
    floor INT NOT NULL,
    capacity INT NOT NULL,
    occupied INT NOT NULL DEFAULT 0,
    CONSTRAINT chk_room_floor CHECK (floor >= 0),
    CONSTRAINT chk_room_capacity CHECK (capacity > 0),
    CONSTRAINT chk_room_occupied CHECK (occupied >= 0 AND occupied <= capacity)
);

CREATE TABLE allocations (
    allocation_id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT NOT NULL,
    room_id INT NOT NULL,
    allocation_date DATE NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'Active',
    CONSTRAINT chk_allocation_status CHECK (status IN ('Active','Cancelled')),
    CONSTRAINT fk_allocation_student
        FOREIGN KEY (student_id) REFERENCES students(student_id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_allocation_room
        FOREIGN KEY (room_id) REFERENCES rooms(room_id)
        ON UPDATE CASCADE ON DELETE RESTRICT
);

INSERT INTO students VALUES
(101,'Rahul Kumar','Male','B.Tech CSE',2,'9876500001','rahul@example.com'),
(102,'Priya Sharma','Female','B.Tech CSM',2,'9876500002','priya@example.com'),
(103,'Arjun Reddy','Male','B.Tech CSE',3,'9876500003','arjun@example.com'),
(104,'Sneha Rao','Female','B.Tech ECE',1,'9876500004','sneha@example.com'),
(105,'Kiran Patel','Male','B.Tech CSM',2,'9876500005','kiran@example.com');

INSERT INTO rooms (room_number,block,floor,capacity,occupied) VALUES
('A101','A',1,4,2),
('A102','A',1,2,1),
('A103','A',1,4,0),
('B201','B',2,3,1),
('B202','B',2,2,0),
('C301','C',3,4,0);

INSERT INTO allocations (student_id,room_id,allocation_date,status) VALUES
(101,1,CURDATE(),'Active'),
(102,1,CURDATE(),'Active'),
(103,2,CURDATE(),'Active'),
(104,4,CURDATE(),'Active');

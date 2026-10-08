from datetime import date
from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
from mysql.connector import Error, IntegrityError
import config

app = Flask(__name__)
app.secret_key = "hostel-room-allocation-lab-secret-key"


def get_db():
    return mysql.connector.connect(
        host=config.MYSQL_HOST,
        user=config.MYSQL_USER,
        password=config.MYSQL_PASSWORD,
        database=config.MYSQL_DATABASE,
        port=config.MYSQL_PORT
    )


def fetch_one(query, params=()):
    conn = get_db()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(query, params)
        return cur.fetchone()
    finally:
        cur.close()
        conn.close()


def fetch_all(query, params=()):
    conn = get_db()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(query, params)
        return cur.fetchall()
    finally:
        cur.close()
        conn.close()


def execute_query(query, params=()):
    conn = get_db()
    try:
        cur = conn.cursor()
        cur.execute(query, params)
        conn.commit()
        return cur.lastrowid
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()


def valid_email(email):
    return "@" in email and "." in email.split("@")[-1] and " " not in email


def valid_phone(phone):
    return phone.isdigit() and 10 <= len(phone) <= 15


@app.route("/")
def index():
    stats = fetch_one("""
        SELECT
            (SELECT COUNT(*) FROM students) AS total_students,
            (SELECT COUNT(*) FROM rooms) AS total_rooms,
            (SELECT COUNT(*) FROM rooms WHERE occupied < capacity) AS available_rooms,
            (SELECT COUNT(*) FROM rooms WHERE occupied >= capacity) AS full_rooms,
            (SELECT COUNT(*) FROM allocations WHERE status='Active') AS active_allocations
    """)
    recent = fetch_all("""
        SELECT a.allocation_id, s.name, r.room_number, r.block,
               a.allocation_date, a.status
        FROM allocations a
        JOIN students s ON s.student_id = a.student_id
        JOIN rooms r ON r.room_id = a.room_id
        ORDER BY a.allocation_id DESC
        LIMIT 5
    """)
    return render_template("index.html", stats=stats, recent=recent)


@app.route("/students")
def students():
    q = request.args.get("q", "").strip()
    like = f"%{q}%"
    rows = fetch_all("""
        SELECT * FROM students
        WHERE CAST(student_id AS CHAR) LIKE %s
           OR name LIKE %s OR course LIKE %s OR email LIKE %s
        ORDER BY student_id
    """, (like, like, like, like))
    return render_template("students.html", students=rows, q=q)


@app.route("/students/add", methods=["GET", "POST"])
def add_student():
    if request.method == "POST":
        try:
            sid = int(request.form.get("student_id", "").strip())
            name = request.form.get("name", "").strip()
            gender = request.form.get("gender", "").strip()
            course = request.form.get("course", "").strip()
            year = int(request.form.get("year", "0"))
            phone = request.form.get("phone", "").strip()
            email = request.form.get("email", "").strip()

            if not all([name, gender, course, phone, email]):
                raise ValueError("All required fields must be filled.")
            if year < 1 or year > 6:
                raise ValueError("Year must be between 1 and 6.")
            if not valid_phone(phone):
                raise ValueError("Phone must contain 10 to 15 digits.")
            if not valid_email(email):
                raise ValueError("Enter a valid email address.")

            execute_query("""
                INSERT INTO students
                (student_id,name,gender,course,year,phone,email)
                VALUES (%s,%s,%s,%s,%s,%s,%s)
            """, (sid, name, gender, course, year, phone, email))
            flash("Student added successfully.", "success")
            return redirect(url_for("students"))
        except ValueError as e:
            flash(str(e), "error")
        except IntegrityError:
            flash("Student ID, phone, or email already exists.", "error")
        except Error:
            flash("Database error while adding student.", "error")
    return render_template("add_student.html")


@app.route("/students/edit/<int:id>", methods=["GET", "POST"])
def edit_student(id):
    student = fetch_one("SELECT * FROM students WHERE student_id=%s", (id,))
    if not student:
        flash("Student not found.", "error")
        return redirect(url_for("students"))

    if request.method == "POST":
        try:
            name = request.form.get("name", "").strip()
            gender = request.form.get("gender", "").strip()
            course = request.form.get("course", "").strip()
            year = int(request.form.get("year", "0"))
            phone = request.form.get("phone", "").strip()
            email = request.form.get("email", "").strip()

            if not all([name, gender, course, phone, email]):
                raise ValueError("All required fields must be filled.")
            if year < 1 or year > 6:
                raise ValueError("Year must be between 1 and 6.")
            if not valid_phone(phone):
                raise ValueError("Phone must contain 10 to 15 digits.")
            if not valid_email(email):
                raise ValueError("Enter a valid email address.")

            execute_query("""
                UPDATE students
                SET name=%s, gender=%s, course=%s, year=%s,
                    phone=%s, email=%s
                WHERE student_id=%s
            """, (name, gender, course, year, phone, email, id))
            flash("Student updated successfully.", "success")
            return redirect(url_for("students"))
        except ValueError as e:
            flash(str(e), "error")
        except IntegrityError:
            flash("Phone or email already belongs to another student.", "error")
        except Error:
            flash("Database error while updating student.", "error")
    return render_template("edit_student.html", student=student)


@app.route("/students/delete/<int:id>", methods=["POST"])
def delete_student(id):
    try:
        active = fetch_one(
            "SELECT COUNT(*) AS c FROM allocations WHERE student_id=%s AND status='Active'",
            (id,)
        )
        if active["c"] > 0:
            flash("Cannot delete a student with an active room allocation.", "warning")
        else:
            execute_query("DELETE FROM students WHERE student_id=%s", (id,))
            flash("Student deleted successfully.", "success")
    except IntegrityError:
        flash("Student cannot be deleted because allocation history exists.", "error")
    except Error:
        flash("Database error while deleting student.", "error")
    return redirect(url_for("students"))


@app.route("/rooms")
def rooms():
    q = request.args.get("q", "").strip()
    like = f"%{q}%"
    rows = fetch_all("""
        SELECT *, capacity - occupied AS available,
        CASE
            WHEN occupied = 0 THEN 'Available'
            WHEN occupied < capacity THEN 'Partially Occupied'
            ELSE 'Full'
        END AS room_status
        FROM rooms
        WHERE room_number LIKE %s OR block LIKE %s
        ORDER BY room_id
    """, (like, like))
    return render_template("rooms.html", rooms=rows, q=q)


@app.route("/rooms/add", methods=["GET", "POST"])
def add_room():
    if request.method == "POST":
        try:
            room_number = request.form.get("room_number", "").strip()
            block = request.form.get("block", "").strip()
            floor = int(request.form.get("floor", "-1"))
            capacity = int(request.form.get("capacity", "0"))

            if not room_number or not block:
                raise ValueError("Room number and block are required.")
            if floor < 0:
                raise ValueError("Floor must be zero or greater.")
            if capacity <= 0:
                raise ValueError("Capacity must be greater than zero.")

            execute_query("""
                INSERT INTO rooms (room_number,block,floor,capacity)
                VALUES (%s,%s,%s,%s)
            """, (room_number, block, floor, capacity))
            flash("Room added successfully.", "success")
            return redirect(url_for("rooms"))
        except ValueError as e:
            flash(str(e), "error")
        except IntegrityError:
            flash("Room number already exists.", "error")
        except Error:
            flash("Database error while adding room.", "error")
    return render_template("add_room.html")


@app.route("/rooms/edit/<int:id>", methods=["GET", "POST"])
def edit_room(id):
    room = fetch_one("SELECT * FROM rooms WHERE room_id=%s", (id,))
    if not room:
        flash("Room not found.", "error")
        return redirect(url_for("rooms"))

    if request.method == "POST":
        try:
            room_number = request.form.get("room_number", "").strip()
            block = request.form.get("block", "").strip()
            floor = int(request.form.get("floor", "-1"))
            capacity = int(request.form.get("capacity", "0"))

            if not room_number or not block:
                raise ValueError("Room number and block are required.")
            if floor < 0:
                raise ValueError("Floor must be zero or greater.")
            if capacity <= 0 or capacity < room["occupied"]:
                raise ValueError("Capacity must be greater than or equal to occupied count.")

            execute_query("""
                UPDATE rooms
                SET room_number=%s, block=%s, floor=%s, capacity=%s
                WHERE room_id=%s
            """, (room_number, block, floor, capacity, id))
            flash("Room updated successfully.", "success")
            return redirect(url_for("rooms"))
        except ValueError as e:
            flash(str(e), "error")
        except IntegrityError:
            flash("Room number already exists.", "error")
        except Error:
            flash("Database error while updating room.", "error")
    return render_template("edit_room.html", room=room)


@app.route("/rooms/delete/<int:id>", methods=["POST"])
def delete_room(id):
    try:
        count = fetch_one(
            "SELECT COUNT(*) AS c FROM allocations WHERE room_id=%s",
            (id,)
        )
        if count["c"] > 0:
            flash("Cannot delete a room with allocation history.", "warning")
        else:
            execute_query("DELETE FROM rooms WHERE room_id=%s", (id,))
            flash("Room deleted successfully.", "success")
    except Error:
        flash("Database error while deleting room.", "error")
    return redirect(url_for("rooms"))


@app.route("/allocate", methods=["GET", "POST"])
def allocate_room():
    students_list = fetch_all("""
        SELECT s.* FROM students s
        LEFT JOIN allocations a
          ON a.student_id=s.student_id AND a.status='Active'
        WHERE a.allocation_id IS NULL
        ORDER BY s.student_id
    """)
    rooms_list = fetch_all("""
        SELECT *, capacity-occupied AS available
        FROM rooms
        WHERE occupied < capacity
        ORDER BY room_number
    """)

    if request.method == "POST":
        try:
            student_id = int(request.form.get("student_id", "0"))
            room_id = int(request.form.get("room_id", "0"))
            allocation_date = request.form.get("allocation_date", "")

            if not allocation_date:
                raise ValueError("Allocation date is required.")

            conn = get_db()
            cur = conn.cursor(dictionary=True)
            conn.start_transaction()

            cur.execute("SELECT student_id FROM students WHERE student_id=%s FOR UPDATE", (student_id,))
            if not cur.fetchone():
                raise ValueError("Student does not exist.")

            cur.execute("""
                SELECT allocation_id FROM allocations
                WHERE student_id=%s AND status='Active'
                FOR UPDATE
            """, (student_id,))
            if cur.fetchone():
                raise ValueError("Student already has an active room allocation.")

            cur.execute("SELECT * FROM rooms WHERE room_id=%s FOR UPDATE", (room_id,))
            room = cur.fetchone()
            if not room:
                raise ValueError("Room does not exist.")
            if room["occupied"] >= room["capacity"]:
                raise ValueError("Room is full. Please select another room.")

            cur.execute("""
                INSERT INTO allocations (student_id,room_id,allocation_date,status)
                VALUES (%s,%s,%s,'Active')
            """, (student_id, room_id, allocation_date))
            cur.execute(
                "UPDATE rooms SET occupied=occupied+1 WHERE room_id=%s",
                (room_id,)
            )
            conn.commit()
            flash("Room allocated successfully.", "success")
            return redirect(url_for("allocations"))
        except ValueError as e:
            if 'conn' in locals():
                conn.rollback()
            flash(str(e), "error")
        except Error:
            if 'conn' in locals():
                conn.rollback()
            flash("Database error during allocation.", "error")
        finally:
            if 'cur' in locals():
                cur.close()
            if 'conn' in locals():
                conn.close()

    return render_template("allocate_room.html",
                           students=students_list,
                           rooms=rooms_list,
                           today=date.today().isoformat())


@app.route("/allocations")
def allocations():
    q = request.args.get("q", "").strip()
    like = f"%{q}%"
    rows = fetch_all("""
        SELECT a.allocation_id, a.student_id, s.name,
               r.room_number, r.block, a.allocation_date, a.status
        FROM allocations a
        JOIN students s ON s.student_id=a.student_id
        JOIN rooms r ON r.room_id=a.room_id
        WHERE s.name LIKE %s OR r.room_number LIKE %s OR a.status LIKE %s
        ORDER BY a.allocation_id DESC
    """, (like, like, like))
    return render_template("allocations.html", allocations=rows, q=q)


@app.route("/allocations/change/<int:id>", methods=["GET", "POST"])
def change_allocation(id):
    allocation = fetch_one("""
        SELECT a.*, s.name, r.room_number, r.block
        FROM allocations a
        JOIN students s ON s.student_id=a.student_id
        JOIN rooms r ON r.room_id=a.room_id
        WHERE a.allocation_id=%s
    """, (id,))
    if not allocation:
        flash("Allocation not found.", "error")
        return redirect(url_for("allocations"))
    if allocation["status"] != "Active":
        flash("Only active allocations can be changed.", "warning")
        return redirect(url_for("allocations"))

    rooms_list = fetch_all("""
        SELECT *, capacity-occupied AS available
        FROM rooms
        WHERE occupied < capacity OR room_id=%s
        ORDER BY room_number
    """, (allocation["room_id"],))

    if request.method == "POST":
        try:
            new_room_id = int(request.form.get("room_id", "0"))
            if new_room_id == allocation["room_id"]:
                flash("Please select a different room.", "warning")
                return redirect(url_for("change_allocation", id=id))

            conn = get_db()
            cur = conn.cursor(dictionary=True)
            conn.start_transaction()

            cur.execute("SELECT * FROM allocations WHERE allocation_id=%s FOR UPDATE", (id,))
            current = cur.fetchone()

            cur.execute("SELECT * FROM rooms WHERE room_id=%s FOR UPDATE", (new_room_id,))
            new_room = cur.fetchone()
            if not new_room:
                raise ValueError("New room does not exist.")
            if new_room["occupied"] >= new_room["capacity"]:
                raise ValueError("New room is full. Please select another room.")

            cur.execute(
                "UPDATE rooms SET occupied=occupied-1 WHERE room_id=%s AND occupied>0",
                (current["room_id"],)
            )
            cur.execute(
                "UPDATE rooms SET occupied=occupied+1 WHERE room_id=%s",
                (new_room_id,)
            )
            cur.execute(
                "UPDATE allocations SET room_id=%s WHERE allocation_id=%s",
                (new_room_id, id)
            )
            conn.commit()
            flash("Room allocation changed successfully.", "success")
            return redirect(url_for("allocations"))
        except ValueError as e:
            if 'conn' in locals(): conn.rollback()
            flash(str(e), "error")
        except Error:
            if 'conn' in locals(): conn.rollback()
            flash("Database error while changing allocation.", "error")
        finally:
            if 'cur' in locals(): cur.close()
            if 'conn' in locals(): conn.close()

    return render_template("change_allocation.html",
                           allocation=allocation, rooms=rooms_list)


@app.route("/allocations/cancel/<int:id>", methods=["POST"])
def cancel_allocation(id):
    try:
        conn = get_db()
        cur = conn.cursor(dictionary=True)
        conn.start_transaction()

        cur.execute("SELECT * FROM allocations WHERE allocation_id=%s FOR UPDATE", (id,))
        allocation = cur.fetchone()
        if not allocation:
            raise ValueError("Allocation not found.")
        if allocation["status"] != "Active":
            raise ValueError("Allocation is already cancelled.")

        cur.execute("UPDATE allocations SET status='Cancelled' WHERE allocation_id=%s", (id,))
        cur.execute(
            "UPDATE rooms SET occupied=occupied-1 WHERE room_id=%s AND occupied>0",
            (allocation["room_id"],)
        )
        conn.commit()
        flash("Allocation cancelled and room space released.", "success")
    except ValueError as e:
        if 'conn' in locals(): conn.rollback()
        flash(str(e), "warning")
    except Error:
        if 'conn' in locals(): conn.rollback()
        flash("Database error while cancelling allocation.", "error")
    finally:
        if 'cur' in locals(): cur.close()
        if 'conn' in locals(): conn.close()
    return redirect(url_for("allocations"))


if __name__ == "__main__":
    app.run(debug=True)

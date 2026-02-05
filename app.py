from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
import os
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime

app = Flask(__name__)
app.secret_key = "your_password"

# --- Database ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_cursor():
    conn = get_db_connection()
    return conn, conn.cursor()

# --- Create Admin ---
def create_admin():
    conn = get_db_connection()
    hashed = generate_password_hash("password123")
    try:
        conn.execute("INSERT OR IGNORE INTO admins (username, password) VALUES (?, ?)", ("admin", hashed))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error creating admin: {e}")
    finally:
        conn.close()

create_admin()

# --- Login Required Decorator ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("admin_logged_in"):
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

# --- Context Processor for Date ---
@app.context_processor
def inject_date():
    return {"current_date": datetime.now().strftime("%d %b %Y")}

# --- Helper Functions ---
def get_fee_status(total, paid):
    if paid >= total:
        return "Paid"
    elif paid == 0:
        return "Unpaid"
    else:
        return "Partial"

# ===== AUTH ROUTES =====
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # Récupérer les données du formulaire
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        
        # Validation basique
        if not username or not password:
            flash("Please fill in all fields", "error")
            return render_template("login.html")
        
        # Vérifier les identifiants
        conn = get_db_connection()
        admin = conn.execute(
            "SELECT * FROM admins WHERE username = ?", 
            (username,)
        ).fetchone()
        conn.close()
        
        if admin and check_password_hash(admin["password"], password):
            # Connexion réussie
            session["admin_logged_in"] = True
            session["user_name"] = "Administrator"
            session["user_role"] = "Admin"
            flash("Login successful!", "success")
            return redirect(url_for("dashboard"))
        else:
            # Identifiants incorrects
            flash("Invalid username or password", "error")
            return render_template("login.html")
    
    # GET request - afficher le formulaire
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()  # Efface toutes les données de session
    flash("You have been logged out successfully", "success")
    return redirect(url_for("login"))

# ===== DASHBOARD =====
@app.route("/")
@app.route("/dashboard")
@login_required
def dashboard():
    conn = get_db_connection()
    
    # Get statistics
    students_count = conn.execute("SELECT COUNT(*) as count FROM students").fetchone()["count"]
    teachers_count = conn.execute("SELECT COUNT(*) as count FROM teachers").fetchone()["count"]
    classes_count = conn.execute("SELECT COUNT(*) as count FROM classes").fetchone()["count"]
    
    # Get pending fees
    fees = conn.execute("""
        SELECT COUNT(*) as count FROM fees 
        WHERE (total_fee - amount_paid) > 0
    """).fetchone()["count"]
    
    # Recent enrollments
    recent_enrollments = conn.execute("""
        SELECT e.id, s.name as student_name, c.name as class_name, e.academic_year
        FROM enrollments e
        JOIN students s ON e.student_id = s.id
        JOIN classes c ON e.class_id = c.id
        ORDER BY e.id DESC LIMIT 5
    """).fetchall()
    
    conn.close()
    
    return render_template("dashboard.html",
                         students_count=students_count,
                         teachers_count=teachers_count,
                         classes_count=classes_count,
                         pending_fees=fees,
                         recent_enrollments=recent_enrollments,
                         page_title="Dashboard",
                         page_heading="Dashboard")

# ===== STUDENTS ROUTES =====
@app.route("/students")
@login_required
def students():
    conn = get_db_connection()
    students = conn.execute("SELECT * FROM students").fetchall()
    conn.close()
    return render_template("students.html", 
                         students=students,
                         page_title="Students",
                         page_heading="Students")

@app.route("/students/add", methods=["GET", "POST"])
@login_required
def add_student():
    if request.method == "POST":
        name = request.form["name"]
        matricule = request.form["matricule"]
        dob = request.form["date_of_birth"]
        gender = request.form["gender"]

        conn = get_db_connection()
        conn.execute(
            "INSERT INTO students (name, matricule, date_of_birth, gender) VALUES (?, ?, ?, ?)",
            (name, matricule, dob, gender),
        )
        conn.commit()
        conn.close()
        flash("Student added successfully!", "success")
        return redirect(url_for("students"))
    return render_template("add_student.html", page_title="Add Student")

@app.route("/students/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_student(id):
    conn = get_db_connection()
    
    if request.method == "POST":
        name = request.form["name"]
        matricule = request.form["matricule"]
        dob = request.form["date_of_birth"]
        gender = request.form["gender"]
        
        conn.execute("""
            UPDATE students 
            SET name = ?, matricule = ?, date_of_birth = ?, gender = ?
            WHERE id = ?
        """, (name, matricule, dob, gender, id))
        conn.commit()
        conn.close()
        flash("Student updated successfully!", "success")
        return redirect(url_for("students"))
    
    student = conn.execute("SELECT * FROM students WHERE id = ?", (id,)).fetchone()
    conn.close()
    
    if not student:
        flash("Student not found", "error")
        return redirect(url_for("students"))
    
    return render_template("edit_student.html", 
                         student=student,
                         page_title="Edit Student")

@app.route("/students/delete/<int:id>")
@login_required
def delete_student(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM students WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    flash("Student deleted successfully!", "success")
    return redirect(url_for("students"))

# ===== TEACHERS ROUTES =====
@app.route("/teachers")
@login_required
def teachers():
    conn = get_db_connection()
    teachers = conn.execute("SELECT * FROM teachers").fetchall()
    conn.close()
    return render_template("teachers.html",
                         teachers=teachers,
                         page_title="Teachers",
                         page_heading="Teachers")

@app.route("/teachers/add", methods=["GET", "POST"])
@login_required
def add_teacher():
    if request.method == "POST":
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        phone = request.form["phone"]
        profession = request.form["profession"]
        diploma = request.form["diploma"]
        country = request.form["country"]

        conn = get_db_connection()
        conn.execute("""
            INSERT INTO teachers (first_name, last_name, phone, profession, diploma, country)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (first_name, last_name, phone, profession, diploma, country))
        conn.commit()
        conn.close()
        flash("Teacher added successfully!", "success")
        return redirect(url_for("teachers"))
    return render_template("add_teacher.html", page_title="Add Teacher")

@app.route("/teachers/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_teacher(id):
    conn = get_db_connection()

    if request.method == "POST":
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        phone = request.form["phone"]
        profession = request.form["profession"]
        diploma = request.form["diploma"]
        country = request.form["country"]

        conn.execute("""
            UPDATE teachers
            SET first_name = ?, last_name = ?, phone = ?, 
                profession = ?, diploma = ?, country = ?
            WHERE id = ?
        """, (first_name, last_name, phone, profession, diploma, country, id))
        conn.commit()
        conn.close()
        flash("Teacher updated successfully!", "success")
        return redirect(url_for("teachers"))

    teacher = conn.execute("SELECT * FROM teachers WHERE id = ?", (id,)).fetchone()
    conn.close()
    
    if not teacher:
        flash("Teacher not found", "error")
        return redirect(url_for("teachers"))
    
    return render_template("edit_teacher.html", 
                         teacher=teacher,
                         page_title="Edit Teacher")

@app.route("/teachers/delete/<int:id>")
@login_required
def delete_teacher(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM teachers WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    flash("Teacher deleted successfully!", "success")
    return redirect(url_for("teachers"))

@app.route("/debug/tables")
@login_required
def debug_tables():
    conn = get_db_connection()
    
    # Voir la structure de la table teachers
    teachers_info = conn.execute("PRAGMA table_info(teachers)").fetchall()
    
    # Voir la structure de la table timetable
    timetable_info = conn.execute("PRAGMA table_info(timetable)").fetchall()
    
    conn.close()
    
    output = "<h2>Teachers Table Structure:</h2><pre>"
    for col in teachers_info:
        output += f"{col['name']} - {col['type']}\n"
    
    output += "</pre><h2>Timetable Table Structure:</h2><pre>"
    for col in timetable_info:
        output += f"{col['name']} - {col['type']}\n"
    
    output += "</pre>"
    return output

# ===== CLASSES ROUTES =====
@app.route("/classes")
@login_required
def classes():
    conn = get_db_connection()
    classes = conn.execute("SELECT * FROM classes").fetchall()
    conn.close()
    return render_template("classes.html",
                         classes=classes,
                         page_title="Classes",
                         page_heading="Classes")

@app.route("/classes/add", methods=["GET", "POST"])
@login_required
def add_class():
    if request.method == "POST":
        name = request.form["name"]
        level = request.form["level"]

        conn = get_db_connection()
        conn.execute(
            "INSERT INTO classes (name, level) VALUES (?, ?)",
            (name, level)
        )
        conn.commit()
        conn.close()
        flash("Class added successfully!", "success")
        return redirect(url_for("classes"))
    return render_template("add_class.html", page_title="Add Class")

@app.route("/classes/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_class(id):
    conn = get_db_connection()
    
    if request.method == "POST":
        name = request.form["name"]
        level = request.form["level"]
        
        conn.execute("""
            UPDATE classes 
            SET name = ?, level = ?
            WHERE id = ?
        """, (name, level, id))
        conn.commit()
        conn.close()
        flash("Class updated successfully!", "success")
        return redirect(url_for("classes"))
    
    class_data = conn.execute("SELECT * FROM classes WHERE id = ?", (id,)).fetchone()
    conn.close()
    
    if not class_data:
        flash("Class not found", "error")
        return redirect(url_for("classes"))
    
    return render_template("edit_class.html", 
                         class_data=class_data,
                         page_title="Edit Class")

@app.route("/classes/delete/<int:id>")
@login_required
def delete_class(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM classes WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    flash("Class deleted successfully!", "success")
    return redirect(url_for("classes"))

# ===== SUBJECTS ROUTES =====
@app.route("/subjects")
@login_required
def subjects():
    conn = get_db_connection()
    subjects = conn.execute("""
        SELECT sub.id, sub.name, sub.coefficient, c.name AS class_name
        FROM subjects sub
        LEFT JOIN classes c ON sub.class_id = c.id
    """).fetchall()
    
    classes_list = conn.execute("SELECT id, name FROM classes").fetchall()
    conn.close()
    
    return render_template("subjects.html",
                         subjects=subjects,
                         classes_list=classes_list,
                         page_title="Subjects",
                         page_heading="Subjects")

@app.route("/subjects/add", methods=["GET", "POST"])
@login_required
def add_subject():
    conn = get_db_connection()
    classes = conn.execute("SELECT id, name FROM classes").fetchall()

    if request.method == "POST":
        name = request.form["name"]
        coefficient = request.form["coefficient"]
        class_id = request.form["class_id"] if request.form["class_id"] else None

        conn.execute(
            "INSERT INTO subjects (name, coefficient, class_id) VALUES (?, ?, ?)",
            (name, coefficient, class_id)
        )
        conn.commit()
        conn.close()
        flash("Subject added successfully!", "success")
        return redirect(url_for("subjects"))

    conn.close()
    return render_template("add_subject.html", 
                         classes=classes,
                         page_title="Add Subject")

# ===== ENROLLMENTS ROUTES =====
@app.route("/enrollments")
@login_required
def enrollments():
    conn = get_db_connection()
    enrollments = conn.execute("""
        SELECT e.id, s.name AS student_name, c.name AS class_name, e.academic_year
        FROM enrollments e
        JOIN students s ON e.student_id = s.id
        JOIN classes c ON e.class_id = c.id
    """).fetchall()
    
    classes_list = conn.execute("SELECT id, name FROM classes").fetchall()
    conn.close()
    
    return render_template("enrollments.html",
                         enrollments=enrollments,
                         classes=classes_list,
                         page_title="Enrollments",
                         page_heading="Enrollments")

@app.route("/enrollments/add", methods=["GET", "POST"])
@login_required
def add_enrollment():
    conn = get_db_connection()
    students = conn.execute("SELECT id, name FROM students").fetchall()
    classes = conn.execute("SELECT id, name FROM classes").fetchall()

    if request.method == "POST":
        student_id = request.form["student_id"]
        class_id = request.form["class_id"]
        academic_year = request.form["academic_year"]

        conn.execute(
            "INSERT INTO enrollments (student_id, class_id, academic_year) VALUES (?, ?, ?)",
            (student_id, class_id, academic_year)
        )
        conn.commit()
        conn.close()
        flash("Enrollment added successfully!", "success")
        return redirect(url_for("enrollments"))

    conn.close()
    return render_template("add_enrollment.html", 
                         students=students, 
                         classes=classes,
                         page_title="Add Enrollment")

# ===== RESULTS ROUTES =====
@app.route("/results")
@login_required
def results():
    conn = get_db_connection()
    results = conn.execute("""
        SELECT r.id, s.name AS student_name, sub.name AS subject_name,
               r.score, r.semester, sub.coefficient
        FROM results r
        JOIN enrollments e ON r.enrollment_id = e.id
        JOIN students s ON e.student_id = s.id
        JOIN subjects sub ON r.subject_id = sub.id
    """).fetchall()
    
    subjects_list = conn.execute("SELECT id, name FROM subjects").fetchall()
    conn.close()
    
    return render_template("results.html",
                         results=results,
                         subjects=subjects_list,
                         page_title="Results",
                         page_heading="Results")

@app.route("/results/add", methods=["GET", "POST"])
@login_required
def add_result():
    conn = get_db_connection()
    enrollments = conn.execute("""
        SELECT e.id, s.name || ' - ' || c.name || ' (' || e.academic_year || ')' AS label
        FROM enrollments e
        JOIN students s ON e.student_id = s.id
        JOIN classes c ON e.class_id = c.id
    """).fetchall()
    subjects = conn.execute("SELECT id, name FROM subjects").fetchall()

    if request.method == "POST":
        enrollment_id = request.form["enrollment_id"]
        subject_id = request.form["subject_id"]
        score = request.form["score"]
        semester = request.form["semester"]

        conn.execute(
            "INSERT INTO results (enrollment_id, subject_id, score, semester) VALUES (?, ?, ?, ?)",
            (enrollment_id, subject_id, score, semester)
        )
        conn.commit()
        conn.close()
        flash("Result added successfully!", "success")
        return redirect(url_for("results"))

    conn.close()
    return render_template("add_result.html", 
                         enrollments=enrollments, 
                         subjects=subjects,
                         page_title="Add Result")

# ===== FEES ROUTES =====
@app.route("/fees")
@login_required
def fees():
    conn = get_db_connection()
    fees_data = conn.execute("""
        SELECT f.id,
               s.name AS student_name,
               s.id as student_id,
               c.name AS class_name,
               f.total_fee,
               f.amount_paid,
               (f.total_fee - f.amount_paid) AS remaining,
               f.payment_mode,
               f.status
        FROM fees f
        JOIN students s ON f.student_id = s.id
        JOIN classes c ON f.class_id = c.id
    """).fetchall()
    
    classes_list = conn.execute("SELECT id, name FROM classes").fetchall()
    conn.close()
    
    return render_template("fees.html",
                         fees=fees_data,
                         classes=classes_list,
                         page_title="Fees",
                         page_heading="Fees")

@app.route("/fees/add", methods=["GET", "POST"])
@login_required
def add_fee():
    conn = get_db_connection()
    students = conn.execute("SELECT id, name FROM students").fetchall()
    classes = conn.execute("SELECT id, name FROM classes").fetchall()

    if request.method == "POST":
        student_id = request.form["student_id"]
        class_id = request.form["class_id"]
        total_fee = float(request.form["total_fee"])
        amount_paid = float(request.form["amount_paid"])
        payment_mode = request.form["payment_mode"]
        
        # Calculate status
        remaining = total_fee - amount_paid
        status = "Paid" if remaining == 0 else "Partial" if amount_paid > 0 else "Unpaid"

        conn.execute("""
            INSERT INTO fees
            (student_id, class_id, total_fee, amount_paid, payment_mode, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (student_id, class_id, total_fee, amount_paid, payment_mode, status))
        
        conn.commit()
        conn.close()
        flash("Fee record added successfully!", "success")
        return redirect(url_for("fees"))

    conn.close()
    return render_template("add_fee.html", 
                         students=students, 
                         classes=classes,
                         page_title="Add Fee")

# ===== ROOMS ROUTES =====
@app.route("/rooms")
@login_required
def rooms():
    conn = get_db_connection()
    rooms = conn.execute("SELECT * FROM rooms ORDER BY name").fetchall()
    conn.close()
    return render_template("rooms.html",
                         rooms=rooms,
                         page_title="Rooms",
                         page_heading="Rooms")

@app.route("/rooms/add", methods=["GET", "POST"])
@login_required
def add_room():
    if request.method == "POST":
        name = request.form["name"]
        capacity = request.form["capacity"]
        location = request.form["location"]

        conn = get_db_connection()
        conn.execute("""
            INSERT INTO rooms (name, capacity, location)
            VALUES (?, ?, ?)
        """, (name, capacity, location))
        conn.commit()
        conn.close()
        flash("Room added successfully!", "success")
        return redirect(url_for("rooms"))

    return render_template("add_room.html", page_title="Add Room")

# ===== TIMETABLE ROUTES =====
@app.route("/timetable")
@login_required
def timetable():
    conn = get_db_connection()
    timetable_data = conn.execute("""
        SELECT t.id,
               c.name AS class_name,
               sub.name AS subject_name,
               te.first_name || ' ' || te.last_name AS teacher_name,  -- CHANGÉ ICI
               r.name AS room_name,
               t.day,
               t.start_time,
               t.end_time
        FROM timetable t
        JOIN classes c ON t.class_id = c.id
        JOIN subjects sub ON t.subject_id = sub.id
        JOIN teachers te ON t.teacher_id = te.id  -- CHANGÉ ICI
        JOIN rooms r ON t.room_id = r.id
        ORDER BY 
            CASE t.day 
                WHEN 'Monday' THEN 1
                WHEN 'Tuesday' THEN 2
                WHEN 'Wednesday' THEN 3
                WHEN 'Thursday' THEN 4
                WHEN 'Friday' THEN 5
                WHEN 'Saturday' THEN 6
                WHEN 'Sunday' THEN 7
            END,
            t.start_time
    """).fetchall()
    
    classes_list = conn.execute("SELECT id, name FROM classes").fetchall()
    teachers_list = conn.execute("SELECT id, first_name, last_name FROM teachers").fetchall()
    
    conn.close()
    
    return render_template("timetable.html",
                         timetable=timetable_data,
                         classes=classes_list,
                         teachers=teachers_list,
                         page_title="Timetable",
                         page_heading="Timetable")

@app.route("/timetable/add", methods=["GET", "POST"])
@login_required
def add_timetable():
    conn = get_db_connection()

    classes = conn.execute("SELECT id, name FROM classes").fetchall()
    subjects = conn.execute("SELECT id, name FROM subjects").fetchall()
    teachers = conn.execute("SELECT id, first_name, last_name FROM teachers").fetchall()
    rooms = conn.execute("SELECT id, name FROM rooms").fetchall()

    if request.method == "POST":
        conn.execute("""
            INSERT INTO timetable
            (class_id, subject_id, teacher_id, room_id, day, start_time, end_time)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            request.form["class_id"],
            request.form["subject_id"],
            request.form["teacher_id"],
            request.form["room_id"],
            request.form["day"],
            request.form["start_time"],
            request.form["end_time"],
        ))
        conn.commit()
        conn.close()
        flash("Timetable entry added successfully!", "success")
        return redirect(url_for("timetable"))

    conn.close()
    return render_template(
        "add_timetable.html",
        classes=classes,
        subjects=subjects,
        teachers=teachers,
        rooms=rooms,
        page_title="Add Timetable"
    )

# ===== BULLETIN =====
@app.route("/bulletin/<int:enrollment_id>")
@login_required
def bulletin(enrollment_id):
    conn = get_db_connection()

    enrollment = conn.execute("""
        SELECT e.id, s.name AS student_name, c.name AS class_name, e.academic_year
        FROM enrollments e
        JOIN students s ON e.student_id = s.id
        JOIN classes c ON e.class_id = c.id
        WHERE e.id = ?
    """, (enrollment_id,)).fetchone()

    if not enrollment:
        conn.close()
        flash("Enrollment not found", "error")
        return redirect(url_for("enrollments"))

    sem1_results = conn.execute("""
        SELECT sub.name AS subject_name, r.score, sub.coefficient
        FROM results r
        JOIN subjects sub ON r.subject_id = sub.id
        WHERE r.enrollment_id = ? AND r.semester = 1
    """, (enrollment_id,)).fetchall()

    sem2_results = conn.execute("""
        SELECT sub.name AS subject_name, r.score, sub.coefficient
        FROM results r
        JOIN subjects sub ON r.subject_id = sub.id
        WHERE r.enrollment_id = ? AND r.semester = 2
    """, (enrollment_id,)).fetchall()

    conn.close()

    def calculate_total_and_average(results):
        total_score = sum(r["score"] * r["coefficient"] for r in results)
        total_coeff = sum(r["coefficient"] for r in results)
        average = total_score / total_coeff if total_coeff else 0
        return total_score, total_coeff, average

    total1, coeff1, avg1 = calculate_total_and_average(sem1_results)
    total2, coeff2, avg2 = calculate_total_and_average(sem2_results)
    final_average = (total1 + total2) / (coeff1 + coeff2) if (coeff1 + coeff2) else 0

    return render_template(
        "bulletin.html",
        enrollment=enrollment,
        sem1_results=sem1_results,
        sem2_results=sem2_results,
        total1=total1, total2=total2,
        avg1=avg1, avg2=avg2,
        final_average=final_average,
        page_title="Bulletin"
    )

# ===== SIMPLE ACCOUNT ROUTES (optional) =====
@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', 
                         page_title="My Profile",
                         page_heading="My Profile")

@app.route('/settings')
@login_required
def settings():
    return render_template('settings.html',
                         page_title="Settings",
                         page_heading="Settings")

@app.route('/help')
@login_required
def help_page():
    return render_template('help.html',
                         page_title="Help & Support",
                         page_heading="Help & Support")

# ===== RUN APP =====
if __name__ == "__main__":
    app.run(debug=True)
from flask import Flask, render_template, request, redirect, url_for
import os
import sqlite3

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/")
def home():
    return redirect(url_for("students"))


# fetch all students
@app.route("/students")
def students():
    conn = get_db_connection()
    students = conn.execute("SELECT * FROM students").fetchall()
    conn.close()
    return render_template("students.html", students=students)


# add one student
@app.route("/students/add", methods=["GET", "POST"])
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
        return redirect(url_for("students"))

    return render_template("add_student.html")


# fetch all classes
@app.route("/classes")
def classes():
    conn = get_db_connection()
    classes = conn.execute("SELECT * FROM classes").fetchall()
    conn.close()
    return render_template("classes.html", classes=classes)


# add one class
@app.route("/classes/add", methods=["GET", "POST"])
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
        return redirect(url_for("classes"))

    return render_template("add_class.html")

# fetch all enrollments
@app.route("/enrollments")
def enrollments():
    conn = get_db_connection()
    enrollments = conn.execute("""
        SELECT e.id, s.name AS student_name, c.name AS class_name, e.academic_year
        FROM enrollments e
        JOIN students s ON e.student_id = s.id
        JOIN classes c ON e.class_id = c.id
    """).fetchall()
    conn.close()
    return render_template("enrollments.html", enrollments=enrollments)


# add one enrollment
@app.route("/enrollments/add", methods=["GET", "POST"])
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
        return redirect(url_for("enrollments"))

    conn.close()
    return render_template(
        "add_enrollment.html",
        students=students,
        classes=classes
    )

# fetch all subjects
@app.route("/subjects")
def subjects():
    conn = get_db_connection()
    subjects = conn.execute("""
        SELECT sub.id, sub.name, sub.coefficient, c.name AS class_name
        FROM subjects sub
        JOIN classes c ON sub.class_id = c.id
    """).fetchall()
    conn.close()
    return render_template("subjects.html", subjects=subjects)


# add one subject
@app.route("/subjects/add", methods=["GET", "POST"])
def add_subject():
    conn = get_db_connection()
    classes = conn.execute("SELECT id, name FROM classes").fetchall()

    if request.method == "POST":
        name = request.form["name"]
        coefficient = request.form["coefficient"]
        class_id = request.form["class_id"]

        conn.execute(
            "INSERT INTO subjects (name, coefficient, class_id) VALUES (?, ?, ?)",
            (name, coefficient, class_id)
        )
        conn.commit()
        conn.close()
        return redirect(url_for("subjects"))

    conn.close()
    return render_template("add_subject.html", classes=classes)

# fetch all results
@app.route("/results")
def results():
    conn = get_db_connection()
    results = conn.execute("""
        SELECT r.id, s.name AS student_name, sub.name AS subject_name,
               r.score, sub.coefficient
        FROM results r
        JOIN enrollments e ON r.enrollment_id = e.id
        JOIN students s ON e.student_id = s.id
        JOIN subjects sub ON r.subject_id = sub.id
    """).fetchall()
    conn.close()
    return render_template("results.html", results=results)


# add one results
@app.route("/results/add", methods=["GET", "POST"])
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

        conn.execute(
            "INSERT INTO results (enrollment_id, subject_id, score) VALUES (?, ?, ?)",
            (enrollment_id, subject_id, score)
        )
        conn.commit()
        conn.close()
        return redirect(url_for("results"))

    conn.close()
    return render_template(
        "add_result.html",
        enrollments=enrollments,
        subjects=subjects
    )


if __name__ == "__main__":
    app.run(debug=True)


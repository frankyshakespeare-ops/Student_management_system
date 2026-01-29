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


if __name__ == "__main__":
    app.run(debug=True)


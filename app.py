from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect("database.db")
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


if __name__ == "__main__":
    app.run(debug=True)

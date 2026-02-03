import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# --- STUDENTS ---
cursor.execute("""
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    matricule TEXT UNIQUE NOT NULL,
    date_of_birth TEXT,
    gender TEXT
)
""")

# --- CLASSES ---
cursor.execute("""
CREATE TABLE IF NOT EXISTS classes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    level TEXT NOT NULL
)
""")

# --- TEACHERS (detailed) ---
cursor.execute("""
CREATE TABLE IF NOT EXISTS teachers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    phone TEXT,
    profession TEXT,
    diploma TEXT,
    country TEXT,
    photo TEXT
)
""")

# --- SUBJECTS ---
cursor.execute("""
CREATE TABLE IF NOT EXISTS subjects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    coefficient INTEGER NOT NULL,
    class_id INTEGER,
    teacher_id INTEGER,
    FOREIGN KEY(class_id) REFERENCES classes(id),
    FOREIGN KEY(teacher_id) REFERENCES teachers(id)
)
""")

# --- ENROLLMENTS ---
cursor.execute("""
CREATE TABLE IF NOT EXISTS enrollments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER,
    class_id INTEGER,
    academic_year TEXT,
    FOREIGN KEY(student_id) REFERENCES students(id),
    FOREIGN KEY(class_id) REFERENCES classes(id)
)
""")

#  --- RESULTS ---
cursor.execute("""
CREATE TABLE IF NOT EXISTS results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    enrollment_id INTEGER,
    subject_id INTEGER,
    score REAL,
    semester INTEGER DEFAULT 1,
    FOREIGN KEY(enrollment_id) REFERENCES enrollments(id),
    FOREIGN KEY(subject_id) REFERENCES subjects(id)
)
""")

#  --- SCHOOL FEES / SCOLARITÉ ---
cursor.execute("""
CREATE TABLE IF NOT EXISTS school_fees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER,
    class_id INTEGER,
    total_fee REAL NOT NULL,
    payment_method TEXT,
    amount_paid REAL DEFAULT 0,
    remaining_amount REAL,
    status TEXT,
    FOREIGN KEY(student_id) REFERENCES students(id),
    FOREIGN KEY(class_id) REFERENCES classes(id)
)
""")

#  --- ROOMS ---
cursor.execute("""
CREATE TABLE IF NOT EXISTS rooms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    capacity INTEGER,
    location TEXT
)
""")

#  ---TIMETABLE ---
cursor.execute("""
CREATE TABLE IF NOT EXISTS timetable (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    day TEXT NOT NULL,
    start_time TEXT NOT NULL,
    end_time TEXT NOT NULL,
    subject_id INTEGER,
    room_id INTEGER,
    teacher_id INTEGER,
    class_id INTEGER,
    FOREIGN KEY(subject_id) REFERENCES subjects(id),
    FOREIGN KEY(room_id) REFERENCES rooms(id),
    FOREIGN KEY(teacher_id) REFERENCES teachers(id),
    FOREIGN KEY(class_id) REFERENCES classes(id)
)
""")

#  --- ADMINS ---
cursor.execute("""
CREATE TABLE IF NOT EXISTS admins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
""")

conn.commit()
conn.close()

print("Base Student Management System étendue avec succès.")

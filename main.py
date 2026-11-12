"""Student Record Management System using SQLite."""

import sqlite3
from contextlib import closing
from pathlib import Path

DB_PATH = Path(__file__).with_name("university.db")


# 1 & 2 & 3. Create the database, the students table and its columns
def create_table(conn):
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS students (
            student_id   INTEGER PRIMARY KEY AUTOINCREMENT,
            matric_no    TEXT    NOT NULL UNIQUE,
            first_name   TEXT    NOT NULL,
            last_name    TEXT    NOT NULL,
            gender       TEXT    CHECK (gender IN ('M', 'F')),
            department   TEXT    NOT NULL,
            level        INTEGER NOT NULL CHECK (level IN (100, 200, 300, 400, 500)),
            email        TEXT    UNIQUE,
            cgpa         REAL    CHECK (cgpa BETWEEN 0.0 AND 5.0)
        )
        """
    )
    conn.commit()


# 4. Insert five student records
def insert_students(conn):
    students = [
        ("CSC/2023/001", "Chidi", "Okafor", "M", "Computer Science", 200, "chidi.okafor@uni.edu", 4.25),
        ("CSC/2022/014", "Amaka", "Eze", "F", "Computer Science", 300, "amaka.eze@uni.edu", 3.90),
        ("MTH/2024/007", "Tunde", "Bello", "M", "Mathematics", 100, "tunde.bello@uni.edu", 3.45),
        ("PHY/2021/022", "Ngozi", "Adeyemi", "F", "Physics", 400, "ngozi.adeyemi@uni.edu", 4.60),
        ("ECO/2023/011", "Ibrahim", "Musa", "M", "Economics", 200, "ibrahim.musa@uni.edu", 2.95),
    ]
    # Skip only students whose matric_no already exists; any other
    # constraint violation (bad level, bad CGPA, ...) still raises.
    cur = conn.executemany(
        """
        INSERT INTO students
            (matric_no, first_name, last_name, gender, department, level, email, cgpa)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(matric_no) DO NOTHING
        """,
        students,
    )
    conn.commit()
    return cur.rowcount


def print_rows(rows):
    if not rows:
        print("  (no records found)")
        return
    header = f"  {'ID':<4}{'Matric No':<15}{'Name':<20}{'G':<3}{'Department':<18}{'Level':<7}{'CGPA':<5}"
    print(header)
    print("  " + "-" * (len(header) - 2))
    for r in rows:
        name = f"{r['first_name']} {r['last_name']}"
        gender = r['gender'] or "-"
        cgpa = "-" if r['cgpa'] is None else f"{r['cgpa']:.2f}"
        print(f"  {r['student_id']:<4}{r['matric_no']:<15}{name:<20}{gender:<3}"
              f"{r['department']:<18}{r['level']:<7}{cgpa:<5}")


# 5. Retrieve all student records
def get_all_students(conn):
    return conn.execute("SELECT * FROM students ORDER BY student_id").fetchall()


# 6. Retrieve students from a particular department
def get_students_by_department(conn, department):
    return conn.execute(
        "SELECT * FROM students WHERE department = ? COLLATE NOCASE ORDER BY student_id",
        (department,),
    ).fetchall()


# 7. Update a student's level
def update_student_level(conn, matric_no, new_level):
    cur = conn.execute(
        "UPDATE students SET level = ? WHERE matric_no = ?",
        (new_level, matric_no),
    )
    conn.commit()
    return cur.rowcount


# 8. Delete a student record
def delete_student(conn, matric_no):
    cur = conn.execute("DELETE FROM students WHERE matric_no = ?", (matric_no,))
    conn.commit()
    return cur.rowcount


def main():
    # closing() guarantees the connection is closed even if something raises
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.row_factory = sqlite3.Row

        create_table(conn)
        print(f"Database '{DB_PATH.name}' and table 'students' are ready.\n")

        inserted = insert_students(conn)
        print(f"Inserted {inserted} student record(s).\n")

        print("All students:")
        print_rows(get_all_students(conn))

        dept = "Computer Science"
        print(f"\nStudents in {dept}:")
        print_rows(get_students_by_department(conn, dept))

        updated = update_student_level(conn, "MTH/2024/007", 200)
        print(f"\nUpdated level of MTH/2024/007 to 200 ({updated} row(s) affected).")

        deleted = delete_student(conn, "ECO/2023/011")
        print(f"Deleted student ECO/2023/011 ({deleted} row(s) affected).")

        print("\nAll students after update and delete:")
        print_rows(get_all_students(conn))


if __name__ == "__main__":
    main()

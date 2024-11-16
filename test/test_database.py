import sqlite3

def insert_student(name, student_class, section, marks):
    """Insert a student record if it doesn't already exist."""
    connection = sqlite3.connect("student.db")
    cursor = connection.cursor()

    cursor.execute('''SELECT COUNT(*) FROM STUDENT WHERE NAME=? AND CLASS=? AND SECTION=? AND MARKS=?''', 
                   (name, student_class, section, marks))

    if cursor.fetchone()[0] == 0:
        cursor.execute('''INSERT INTO STUDENT VALUES(?,?,?,?)''', 
                       (name, student_class, section, marks))
        connection.commit()
        connection.close()
        return True
    else:
        connection.close()
        return False

def display_all_students():
    """Display all student records."""
    connection = sqlite3.connect("student.db")
    cursor = connection.cursor()
    data = cursor.execute('''SELECT * FROM STUDENT''')
    students = data.fetchall()
    connection.close()
    return students

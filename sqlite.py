import sqlite3

# Connect to SQLite
connection = sqlite3.connect("data/local/student.db")
cursor = connection.cursor()

# Create the table if it doesn't exist
table_info = """
CREATE TABLE IF NOT EXISTS STUDENT(
    NAME VARCHAR(25),
    CLASS VARCHAR(25),
    SECTION VARCHAR(25),
    MARKS INT
)
"""
cursor.execute(table_info)

def insert_student(name, student_class, section, marks):
    """
    Insert a student record if it doesn't already exist
    Returns True if inserted, False if record already exists
    """
    # Check if record already exists
    cursor.execute('''SELECT COUNT(*) FROM STUDENT WHERE NAME=? AND CLASS=? AND SECTION=? AND MARKS=?''', 
                   (name, student_class, section, marks))
    
    if cursor.fetchone()[0] == 0:  # If record doesn't exist
        cursor.execute('''INSERT INTO STUDENT VALUES(?,?,?,?)''', 
                       (name, student_class, section, marks))
        print(f"Successfully inserted record for {name}")
        return True
    else:
        print(f"Record for {name} already exists.")
        return False

# Example usage: Insert records
students = [
    ('John', 'Data Science', 'B', 80),
    ('Mukesh', 'Data Science', 'A', 86),
    ('Jacob', 'DEVOPS', 'A', 50),
    ('Dipesh', 'DEVOPS', 'A', 35)
]

# Insert each student
for student in students:
    insert_student(*student)



# Display all records
print("\nAll student records:")
data = cursor.execute('''SELECT * FROM STUDENT''')
for row in data:
    print(row)

# Commit changes and close the connection
connection.commit()
connection.close()
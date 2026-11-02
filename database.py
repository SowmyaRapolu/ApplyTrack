
import sqlite3

DATABASE_NAME = "applications.db"


def create_table():
    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT NOT NULL,
            role TEXT NOT NULL,
            status TEXT NOT NULL,
            job_link TEXT,
            applied_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    connection.commit()
    connection.close()


def add_application(company, role, status, job_link):
    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO applications (company, role, status, job_link)
        VALUES (?, ?, ?, ?)
    """, (company, role, status, job_link))

    connection.commit()
    connection.close()


def get_applications():
    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, company, role, status, job_link, applied_date
        FROM applications
        ORDER BY id DESC
    """)

    applications = cursor.fetchall()
    connection.close()

    return applications

    
def update_application(application_id, company, role, status, job_link):
    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE applications
        SET company = ?, role = ?, status = ?, job_link = ?
        WHERE id = ?
    """, (company, role, status, job_link, application_id))

    connection.commit()
    connection.close()


def delete_application(application_id):
    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM applications WHERE id = ?",
        (application_id,)
    )

    connection.commit()
    connection.close()

    


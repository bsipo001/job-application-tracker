import os
import json
import mysql.connector
from dotenv import load_dotenv

load_dotenv()


def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "jobuser"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "job_tracker")
    )


# =========================
# COMPANIES CRUD FUNCTIONS
# =========================

def get_companies():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM companies ORDER BY company_name")
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def get_company(company_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM companies WHERE company_id = %s", (company_id,))
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()


def create_company(data):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        query = """
            INSERT INTO companies (company_name, industry, website, city, state, notes)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        values = (
            data["company_name"],
            data.get("industry"),
            data.get("website"),
            data.get("city"),
            data.get("state"),
            data.get("notes")
        )
        cursor.execute(query, values)
        conn.commit()
        return cursor.lastrowid
    finally:
        cursor.close()
        conn.close()


def update_company(company_id, data):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        query = """
            UPDATE companies
            SET company_name = %s,
                industry = %s,
                website = %s,
                city = %s,
                state = %s,
                notes = %s
            WHERE company_id = %s
        """
        values = (
            data["company_name"],
            data.get("industry"),
            data.get("website"),
            data.get("city"),
            data.get("state"),
            data.get("notes"),
            company_id
        )
        cursor.execute(query, values)
        conn.commit()
    finally:
        cursor.close()
        conn.close()


def delete_company(company_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM companies WHERE company_id = %s", (company_id,))
        conn.commit()
    finally:
        cursor.close()
        conn.close()


# =====================
# JOBS CRUD FUNCTIONS
# =====================

def get_jobs():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        query = """
            SELECT j.*, c.company_name
            FROM jobs j
            LEFT JOIN companies c ON j.company_id = c.company_id
            ORDER BY j.date_posted DESC, j.job_title
        """
        cursor.execute(query)
        jobs = cursor.fetchall()

        for job in jobs:
            if job.get("requirements"):
                try:
                    job["requirements"] = json.loads(job["requirements"])
                except (TypeError, json.JSONDecodeError):
                    job["requirements"] = []
            else:
                job["requirements"] = []

        return jobs
    finally:
        cursor.close()
        conn.close()


def get_job(job_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        query = """
            SELECT j.*, c.company_name
            FROM jobs j
            LEFT JOIN companies c ON j.company_id = c.company_id
            WHERE j.job_id = %s
        """
        cursor.execute(query, (job_id,))
        job = cursor.fetchone()

        if job and job.get("requirements"):
            try:
                job["requirements"] = json.loads(job["requirements"])
            except (TypeError, json.JSONDecodeError):
                job["requirements"] = []
        elif job:
            job["requirements"] = []

        return job
    finally:
        cursor.close()
        conn.close()


def create_job(data):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        query = """
            INSERT INTO jobs (
                company_id, job_title, job_type, salary_min, salary_max,
                job_url, date_posted, requirements
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        requirements_json = json.dumps(data.get("requirements", []))

        values = (
            data.get("company_id"),
            data["job_title"],
            data.get("job_type"),
            data.get("salary_min"),
            data.get("salary_max"),
            data.get("job_url"),
            data.get("date_posted"),
            requirements_json
        )
        cursor.execute(query, values)
        conn.commit()
        return cursor.lastrowid
    finally:
        cursor.close()
        conn.close()


def update_job(job_id, data):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        query = """
            UPDATE jobs
            SET company_id = %s,
                job_title = %s,
                job_type = %s,
                salary_min = %s,
                salary_max = %s,
                job_url = %s,
                date_posted = %s,
                requirements = %s
            WHERE job_id = %s
        """
        requirements_json = json.dumps(data.get("requirements", []))

        values = (
            data.get("company_id"),
            data["job_title"],
            data.get("job_type"),
            data.get("salary_min"),
            data.get("salary_max"),
            data.get("job_url"),
            data.get("date_posted"),
            requirements_json,
            job_id
        )
        cursor.execute(query, values)
        conn.commit()
    finally:
        cursor.close()
        conn.close()


def delete_job(job_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM jobs WHERE job_id = %s", (job_id,))
        conn.commit()
    finally:
        cursor.close()
        conn.close()


# =============================
# APPLICATIONS CRUD FUNCTIONS
# =============================

def get_applications():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        query = """
            SELECT a.*, j.job_title, c.company_name
            FROM applications a
            LEFT JOIN jobs j ON a.job_id = j.job_id
            LEFT JOIN companies c ON j.company_id = c.company_id
            ORDER BY a.application_date DESC
        """
        cursor.execute(query)
        applications = cursor.fetchall()

        for app in applications:
            if app.get("interview_data"):
                try:
                    app["interview_data"] = json.loads(app["interview_data"])
                except (TypeError, json.JSONDecodeError):
                    app["interview_data"] = {}
            else:
                app["interview_data"] = {}

        return applications
    finally:
        cursor.close()
        conn.close()


def get_application(application_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        query = """
            SELECT a.*, j.job_title, c.company_name
            FROM applications a
            LEFT JOIN jobs j ON a.job_id = j.job_id
            LEFT JOIN companies c ON j.company_id = c.company_id
            WHERE a.application_id = %s
        """
        cursor.execute(query, (application_id,))
        application = cursor.fetchone()

        if application and application.get("interview_data"):
            try:
                application["interview_data"] = json.loads(application["interview_data"])
            except (TypeError, json.JSONDecodeError):
                application["interview_data"] = {}
        elif application:
            application["interview_data"] = {}

        return application
    finally:
        cursor.close()
        conn.close()


def create_application(data):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        query = """
            INSERT INTO applications (
                job_id, application_date, status, resume_version,
                cover_letter_sent, interview_data
            )
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        interview_json = json.dumps(data.get("interview_data", {}))

        values = (
            data.get("job_id"),
            data["application_date"],
            data.get("status"),
            data.get("resume_version"),
            data.get("cover_letter_sent", False),
            interview_json
        )
        cursor.execute(query, values)
        conn.commit()
        return cursor.lastrowid
    finally:
        cursor.close()
        conn.close()


def update_application(application_id, data):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        query = """
            UPDATE applications
            SET job_id = %s,
                application_date = %s,
                status = %s,
                resume_version = %s,
                cover_letter_sent = %s,
                interview_data = %s
            WHERE application_id = %s
        """
        interview_json = json.dumps(data.get("interview_data", {}))

        values = (
            data.get("job_id"),
            data["application_date"],
            data.get("status"),
            data.get("resume_version"),
            data.get("cover_letter_sent", False),
            interview_json,
            application_id
        )
        cursor.execute(query, values)
        conn.commit()
    finally:
        cursor.close()
        conn.close()


def delete_application(application_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM applications WHERE application_id = %s", (application_id,))
        conn.commit()
    finally:
        cursor.close()
        conn.close()


# ==========================
# CONTACTS CRUD FUNCTIONS
# ==========================

def get_contacts():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        query = """
            SELECT ct.*, c.company_name
            FROM contacts ct
            LEFT JOIN companies c ON ct.company_id = c.company_id
            ORDER BY ct.contact_name
        """
        cursor.execute(query)
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def get_contact(contact_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        query = """
            SELECT ct.*, c.company_name
            FROM contacts ct
            LEFT JOIN companies c ON ct.company_id = c.company_id
            WHERE ct.contact_id = %s
        """
        cursor.execute(query, (contact_id,))
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()


def create_contact(data):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        query = """
            INSERT INTO contacts (
                company_id, contact_name, title, email, phone, linkedin_url, notes
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        values = (
            data.get("company_id"),
            data["contact_name"],
            data.get("title"),
            data.get("email"),
            data.get("phone"),
            data.get("linkedin_url"),
            data.get("notes")
        )
        cursor.execute(query, values)
        conn.commit()
        return cursor.lastrowid
    finally:
        cursor.close()
        conn.close()


def update_contact(contact_id, data):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        query = """
            UPDATE contacts
            SET company_id = %s,
                contact_name = %s,
                title = %s,
                email = %s,
                phone = %s,
                linkedin_url = %s,
                notes = %s
            WHERE contact_id = %s
        """
        values = (
            data.get("company_id"),
            data["contact_name"],
            data.get("title"),
            data.get("email"),
            data.get("phone"),
            data.get("linkedin_url"),
            data.get("notes"),
            contact_id
        )
        cursor.execute(query, values)
        conn.commit()
    finally:
        cursor.close()
        conn.close()


def delete_contact(contact_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM contacts WHERE contact_id = %s", (contact_id,))
        conn.commit()
    finally:
        cursor.close()
        conn.close()

from flask import Flask, render_template, request, redirect, url_for, flash
from database import (
    get_db_connection,
    get_companies, get_company, create_company, update_company, delete_company,
    get_jobs, get_job, create_job, update_job, delete_job,
    get_applications, get_application, create_application, update_application, delete_application,
    get_contacts, get_contact, create_contact, update_contact, delete_contact
)
import json

app = Flask(__name__)
app.secret_key = "job_tracker_secret_key"


def parse_requirements_input(raw_text):
    """Convert comma-separated skills into a Python list."""
    if not raw_text or not raw_text.strip():
        return []
    return [item.strip() for item in raw_text.split(",") if item.strip()]


def parse_interview_input(raw_text):
    """
    Store interview notes inside a simple JSON object.
    Example saved format: {"notes": "Phone screen next week"}
    """
    if not raw_text or not raw_text.strip():
        return {}
    return {"notes": raw_text.strip()}


def get_dashboard_stats():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT COUNT(*) AS total_companies FROM companies")
        total_companies = cursor.fetchone()["total_companies"]

        cursor.execute("SELECT COUNT(*) AS total_jobs FROM jobs")
        total_jobs = cursor.fetchone()["total_jobs"]

        cursor.execute("SELECT COUNT(*) AS total_applications FROM applications")
        total_applications = cursor.fetchone()["total_applications"]

        cursor.execute("SELECT COUNT(*) AS total_contacts FROM contacts")
        total_contacts = cursor.fetchone()["total_contacts"]

        cursor.execute("""
            SELECT status, COUNT(*) AS count
            FROM applications
            GROUP BY status
            ORDER BY status
        """)
        status_counts = cursor.fetchall()

        return {
            "total_companies": total_companies,
            "total_jobs": total_jobs,
            "total_applications": total_applications,
            "total_contacts": total_contacts,
            "status_counts": status_counts
        }
    finally:
        cursor.close()
        conn.close()


def get_company_options():
    """Used for dropdowns in jobs and contacts forms."""
    return get_companies()


def get_job_options():
    """Used for dropdowns in applications forms."""
    return get_jobs()


@app.route("/")
def dashboard():
    stats = get_dashboard_stats()
    return render_template("dashboard.html", stats=stats)


# =========================
# COMPANIES ROUTES
# =========================

@app.route("/companies")
def companies():
    company_list = get_companies()
    return render_template("companies.html", companies=company_list)


@app.route("/companies/new", methods=["GET", "POST"])
def new_company():
    if request.method == "POST":
        company_name = request.form.get("company_name", "").strip()

        if not company_name:
            flash("Company name is required.", "error")
            return render_template("company_form.html", company=None)

        data = {
            "company_name": company_name,
            "industry": request.form.get("industry", "").strip() or None,
            "website": request.form.get("website", "").strip() or None,
            "city": request.form.get("city", "").strip() or None,
            "state": request.form.get("state", "").strip() or None,
            "notes": request.form.get("notes", "").strip() or None
        }

        create_company(data)
        flash("Company created successfully.", "success")
        return redirect(url_for("companies"))

    return render_template("company_form.html", company=None)


@app.route("/companies/<int:company_id>/edit", methods=["GET", "POST"])
def edit_company(company_id):
    company = get_company(company_id)

    if not company:
        flash("Company not found.", "error")
        return redirect(url_for("companies"))

    if request.method == "POST":
        company_name = request.form.get("company_name", "").strip()

        if not company_name:
            flash("Company name is required.", "error")
            return render_template("company_form.html", company=company)

        data = {
            "company_name": company_name,
            "industry": request.form.get("industry", "").strip() or None,
            "website": request.form.get("website", "").strip() or None,
            "city": request.form.get("city", "").strip() or None,
            "state": request.form.get("state", "").strip() or None,
            "notes": request.form.get("notes", "").strip() or None
        }

        update_company(company_id, data)
        flash("Company updated successfully.", "success")
        return redirect(url_for("companies"))

    return render_template("company_form.html", company=company)


@app.route("/companies/<int:company_id>/delete", methods=["POST"])
def remove_company(company_id):
    delete_company(company_id)
    flash("Company deleted successfully.", "success")
    return redirect(url_for("companies"))


# =====================
# JOBS ROUTES
# =====================

@app.route("/jobs")
def jobs():
    job_list = get_jobs()
    return render_template("jobs.html", jobs=job_list)


@app.route("/jobs/new", methods=["GET", "POST"])
def new_job():
    company_options = get_company_options()

    if request.method == "POST":
        job_title = request.form.get("job_title", "").strip()

        if not job_title:
            flash("Job title is required.", "error")
            return render_template("job_form.html", job=None, companies=company_options)

        company_id = request.form.get("company_id") or None
        salary_min = request.form.get("salary_min") or None
        salary_max = request.form.get("salary_max") or None

        if salary_min and salary_max:
            try:
                if int(salary_min) > int(salary_max):
                    flash("Salary minimum cannot be greater than salary maximum.", "error")
                    return render_template("job_form.html", job=None, companies=company_options)
            except ValueError:
                flash("Salary values must be numbers.", "error")
                return render_template("job_form.html", job=None, companies=company_options)

        data = {
            "company_id": int(company_id) if company_id else None,
            "job_title": job_title,
            "job_type": request.form.get("job_type") or None,
            "salary_min": int(salary_min) if salary_min else None,
            "salary_max": int(salary_max) if salary_max else None,
            "job_url": request.form.get("job_url", "").strip() or None,
            "date_posted": request.form.get("date_posted") or None,
            "requirements": parse_requirements_input(request.form.get("requirements", ""))
        }

        create_job(data)
        flash("Job created successfully.", "success")
        return redirect(url_for("jobs"))

    return render_template("job_form.html", job=None, companies=company_options)


@app.route("/jobs/<int:job_id>/edit", methods=["GET", "POST"])
def edit_job(job_id):
    job = get_job(job_id)
    company_options = get_company_options()

    if not job:
        flash("Job not found.", "error")
        return redirect(url_for("jobs"))

    if request.method == "POST":
        job_title = request.form.get("job_title", "").strip()

        if not job_title:
            flash("Job title is required.", "error")
            return render_template("job_form.html", job=job, companies=company_options)

        company_id = request.form.get("company_id") or None
        salary_min = request.form.get("salary_min") or None
        salary_max = request.form.get("salary_max") or None

        if salary_min and salary_max:
            try:
                if int(salary_min) > int(salary_max):
                    flash("Salary minimum cannot be greater than salary maximum.", "error")
                    return render_template("job_form.html", job=job, companies=company_options)
            except ValueError:
                flash("Salary values must be numbers.", "error")
                return render_template("job_form.html", job=job, companies=company_options)

        data = {
            "company_id": int(company_id) if company_id else None,
            "job_title": job_title,
            "job_type": request.form.get("job_type") or None,
            "salary_min": int(salary_min) if salary_min else None,
            "salary_max": int(salary_max) if salary_max else None,
            "job_url": request.form.get("job_url", "").strip() or None,
            "date_posted": request.form.get("date_posted") or None,
            "requirements": parse_requirements_input(request.form.get("requirements", ""))
        }

        update_job(job_id, data)
        flash("Job updated successfully.", "success")
        return redirect(url_for("jobs"))

    return render_template("job_form.html", job=job, companies=company_options)


@app.route("/jobs/<int:job_id>/delete", methods=["POST"])
def remove_job(job_id):
    delete_job(job_id)
    flash("Job deleted successfully.", "success")
    return redirect(url_for("jobs"))


# =============================
# APPLICATIONS ROUTES
# =============================

@app.route("/applications")
def applications():
    application_list = get_applications()
    return render_template("applications.html", applications=application_list)


@app.route("/applications/new", methods=["GET", "POST"])
def new_application():
    job_options = get_job_options()

    if request.method == "POST":
        application_date = request.form.get("application_date", "").strip()

        if not application_date:
            flash("Application date is required.", "error")
            return render_template("application_form.html", application=None, jobs=job_options)

        job_id = request.form.get("job_id") or None
        cover_letter_sent = "cover_letter_sent" in request.form

        data = {
            "job_id": int(job_id) if job_id else None,
            "application_date": application_date,
            "status": request.form.get("status") or None,
            "resume_version": request.form.get("resume_version", "").strip() or None,
            "cover_letter_sent": cover_letter_sent,
            "interview_data": parse_interview_input(request.form.get("interview_notes", ""))
        }

        create_application(data)
        flash("Application created successfully.", "success")
        return redirect(url_for("applications"))

    return render_template("application_form.html", application=None, jobs=job_options)


@app.route("/applications/<int:application_id>/edit", methods=["GET", "POST"])
def edit_application(application_id):
    application = get_application(application_id)
    job_options = get_job_options()

    if not application:
        flash("Application not found.", "error")
        return redirect(url_for("applications"))

    if request.method == "POST":
        application_date = request.form.get("application_date", "").strip()

        if not application_date:
            flash("Application date is required.", "error")
            return render_template("application_form.html", application=application, jobs=job_options)

        job_id = request.form.get("job_id") or None
        cover_letter_sent = "cover_letter_sent" in request.form

        data = {
            "job_id": int(job_id) if job_id else None,
            "application_date": application_date,
            "status": request.form.get("status") or None,
            "resume_version": request.form.get("resume_version", "").strip() or None,
            "cover_letter_sent": cover_letter_sent,
            "interview_data": parse_interview_input(request.form.get("interview_notes", ""))
        }

        update_application(application_id, data)
        flash("Application updated successfully.", "success")
        return redirect(url_for("applications"))

    return render_template("application_form.html", application=application, jobs=job_options)


@app.route("/applications/<int:application_id>/delete", methods=["POST"])
def remove_application(application_id):
    delete_application(application_id)
    flash("Application deleted successfully.", "success")
    return redirect(url_for("applications"))


# ==========================
# CONTACTS ROUTES
# ==========================

@app.route("/contacts")
def contacts():
    contact_list = get_contacts()
    return render_template("contacts.html", contacts=contact_list)


@app.route("/contacts/new", methods=["GET", "POST"])
def new_contact():
    company_options = get_company_options()

    if request.method == "POST":
        contact_name = request.form.get("contact_name", "").strip()

        if not contact_name:
            flash("Contact name is required.", "error")
            return render_template("contact_form.html", contact=None, companies=company_options)

        company_id = request.form.get("company_id") or None

        data = {
            "company_id": int(company_id) if company_id else None,
            "contact_name": contact_name,
            "title": request.form.get("title", "").strip() or None,
            "email": request.form.get("email", "").strip() or None,
            "phone": request.form.get("phone", "").strip() or None,
            "linkedin_url": request.form.get("linkedin_url", "").strip() or None,
            "notes": request.form.get("notes", "").strip() or None
        }

        create_contact(data)
        flash("Contact created successfully.", "success")
        return redirect(url_for("contacts"))

    return render_template("contact_form.html", contact=None, companies=company_options)


@app.route("/contacts/<int:contact_id>/edit", methods=["GET", "POST"])
def edit_contact(contact_id):
    contact = get_contact(contact_id)
    company_options = get_company_options()

    if not contact:
        flash("Contact not found.", "error")
        return redirect(url_for("contacts"))

    if request.method == "POST":
        contact_name = request.form.get("contact_name", "").strip()

        if not contact_name:
            flash("Contact name is required.", "error")
            return render_template("contact_form.html", contact=contact, companies=company_options)

        company_id = request.form.get("company_id") or None

        data = {
            "company_id": int(company_id) if company_id else None,
            "contact_name": contact_name,
            "title": request.form.get("title", "").strip() or None,
            "email": request.form.get("email", "").strip() or None,
            "phone": request.form.get("phone", "").strip() or None,
            "linkedin_url": request.form.get("linkedin_url", "").strip() or None,
            "notes": request.form.get("notes", "").strip() or None
        }

        update_contact(contact_id, data)
        flash("Contact updated successfully.", "success")
        return redirect(url_for("contacts"))

    return render_template("contact_form.html", contact=contact, companies=company_options)


@app.route("/contacts/<int:contact_id>/delete", methods=["POST"])
def remove_contact(contact_id):
    delete_contact(contact_id)
    flash("Contact deleted successfully.", "success")
    return redirect(url_for("contacts"))


# ==========================
# JOB MATCH ROUTE
# ==========================

def extract_job_skills(raw_requirements):
    job_skills = []

    if not raw_requirements:
        return []

    if isinstance(raw_requirements, list):
        job_skills.extend(raw_requirements)
    elif isinstance(raw_requirements, dict):
        required_skills = raw_requirements.get("required_skills", [])
        preferred_skills = raw_requirements.get("preferred_skills", [])

        if isinstance(required_skills, list):
            job_skills.extend(required_skills)
        if isinstance(preferred_skills, list):
            job_skills.extend(preferred_skills)
    elif isinstance(raw_requirements, str):
        raw_requirements = raw_requirements.strip()

        try:
            parsed = json.loads(raw_requirements)

            if isinstance(parsed, dict):
                required_skills = parsed.get("required_skills", [])
                preferred_skills = parsed.get("preferred_skills", [])

                if isinstance(required_skills, list):
                    job_skills.extend(required_skills)
                if isinstance(preferred_skills, list):
                    job_skills.extend(preferred_skills)
            elif isinstance(parsed, list):
                job_skills.extend(parsed)
            elif isinstance(parsed, str):
                job_skills.extend([item.strip() for item in parsed.split(",") if item.strip()])
        except Exception:
            job_skills.extend([
                item.strip()
                for item in raw_requirements.replace("\n", " ").split(",")
                if item.strip()
            ])

    normalized_skills = []
    for skill in job_skills:
        skill_text = str(skill).strip().lower()
        if skill_text and skill_text not in normalized_skills:
            normalized_skills.append(skill_text)

    return normalized_skills


@app.route("/job-match", methods=["GET", "POST"])
def job_match():
    results = []
    entered_skills = ""

    if request.method == "POST":
        entered_skills = request.form.get("skills", "")
        user_skills = [skill.strip().lower() for skill in entered_skills.split(",") if skill.strip()]
        user_skill_set = set(user_skills)

        jobs_list = get_jobs()

        for job in jobs_list:
            raw_requirements = job.get("requirements", [])
            normalized_requirements = extract_job_skills(raw_requirements)
            requirement_set = set(normalized_requirements)

            matched_skills = sorted(user_skill_set.intersection(requirement_set))
            missing_skills = sorted(requirement_set - user_skill_set)

            if len(requirement_set) > 0:
                match_percentage = round((len(matched_skills) / len(requirement_set)) * 100)
            else:
                match_percentage = 0

            results.append({
                "job_id": job["job_id"],
                "job_title": job["job_title"],
                "company_name": job.get("company_name"),
                "match_percentage": match_percentage,
                "matched_count": len(matched_skills),
                "user_skill_count": len(requirement_set),
                "matched_skills": matched_skills,
                "missing_skills": missing_skills
            })

        results.sort(key=lambda item: item["match_percentage"], reverse=True)

    return render_template("job_match.html", results=results, entered_skills=entered_skills)


if __name__ == "__main__":
    app.run(debug=True)

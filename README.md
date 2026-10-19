JobTracker — Job & Applicant Manager
JobTracker is a menu-driven job and applicant management application built with Python and MySQL. It provides separate workflows for applicants and recruiters, including job discovery, applications, applicant profiles, skill matching, and recruitment tracking.

Project status: Learning project. Review and test the source code, database setup, and security before using real accounts or presenting it as a finished application.

Features:-

Applicant:
- Register and log in.
- Create, view, and edit an applicant profile.
- Browse and search job listings; view job details.
- Compare skills with a job's required skills.
- View job recommendations and a basic skill-based eligibility indicator.
- Apply for jobs, view application history, and withdraw applications.
- View interview dates and notes.
- Receive deadline alerts for applied jobs.
- View a basic career-readiness score.
- Export application history to CSV.

Recruiter:
- Register and log in.
- Post jobs with company, position, description, required skills, salary, and optional deadline.
- View jobs posted by the recruiter.
- View applicants and rank them by basic skill-match percentage.
- Search applicant profiles by skill.
- Update application statuses and add interview details.
- View counts for jobs, applications, shortlisted applicants, and selected applicants.
- Browse all listed jobs.

Tech stack:
- Language: Python 3
- Database: MySQL
- Python dependency: mysql-connector-python
- Standard library: csv, datetime

Repository structure
jobtrack/
├── main.py
├── requirements.txt
├── README.md


Installation

1. Create and activate a virtual environment.
   macOS/Linux
   python3 -m venv .venv
   source .venv/bin/activate
   Windows PowerShell
   py -m venv .venv
   .venv\Scripts\Activate.ps1
2. Install the dependency:
   python -m pip install -r requirements.txt
3. Configure MySQL. The current source contains hard-coded MySQL connection credentials in connect_database(). 
4. After checking that the connection and database initialization are configured correctly, run:
   python main.py
The source attempts to create the jobtrack_db database and its tables at startup. The MySQL account needs permission to create the database.
Database tables
- users — account name, email, password, and role.
- applicant_profiles — applicant education, skills, experience, and projects.
- jobs — recruiter, company, position, description, required skills, salary, and deadline.
- applications — applicant/job relationship, application date, status, and interview information.
Skill matching
The application compares comma-separated applicant skills with comma-separated required skills and calculates the percentage of listed required skills that match. It can also show skills that are missing.

This is basic string-based matching, not an AI or machine-learning model. It does not automatically recognize synonyms.
Application statuses
Recruiters can set an application to Applied, Shortlisted, Interview, Selected, or Rejected. Applicants can withdraw an application, which sets its status to Withdrawn.


Future improvements
- Secure password hashing.
- Environment-based database configuration.
- Better input validation and error handling.
- Automated tests.
- More robust skill normalization and matching.
- Job and applicant filters.
- A graphical or web interface.

import mysql.connector
import csv
from datetime import datetime

#DATABASE CONNECTION

def connect_database(database=None):
    try:
        if database:
            con = mysql.connector.connect(host="localhost",user="root",password="24766",database=database)
        else:
            con = mysql.connector.connect(host="localhost",user="root",password="24766")
        return con
    except mysql.connector.Error as error:
        print("\nDatabase connection failed.")
        print("Error:",error)
        return None


#CREATE DATABASE

def create_database():
    con = connect_database()
    if con is None:
        return False

    cursor = con.cursor()

    try:
        cursor.execute("CREATE DATABASE IF NOT EXISTS jobtrack_db")
        con.commit()
        cursor.close()
        con.close()
        return True

    except mysql.connector.Error as error:
        print("Database creation failed!")
        print("Error:",error)
        cursor.close()
        con.close()
        return False


create_database()

con = connect_database("jobtrack_db")

if con is None:
    exit()

cursor = con.cursor()


#CREATE TABLES

def create_tables():

    cursor.execute("""CREATE TABLE IF NOT EXISTS users
                   (user_id INT AUTO_INCREMENT PRIMARY KEY,
                   name VARCHAR(100) NOT NULL,
                   email VARCHAR(100) UNIQUE NOT NULL,
                   password VARCHAR(100) NOT NULL,
                   role VARCHAR(30) NOT NULL)""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS applicant_profiles
                   (profile_id INT AUTO_INCREMENT PRIMARY KEY,
                   user_id INT NOT NULL,
                   education VARCHAR(200),
                   skills VARCHAR(500),
                   experience VARCHAR(500),
                   projects VARCHAR(500),
                   FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE)""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS jobs
                   (job_id INT AUTO_INCREMENT PRIMARY KEY,
                   recruiter_id INT NOT NULL,
                   company VARCHAR(100) NOT NULL,
                   position VARCHAR(100) NOT NULL,
                   description VARCHAR(1000),
                   required_skills VARCHAR(500),
                   salary VARCHAR(100),
                   deadline DATE,
                   FOREIGN KEY(recruiter_id) REFERENCES users(user_id) ON DELETE CASCADE)""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS applications
                   (application_id INT AUTO_INCREMENT PRIMARY KEY,
                   job_id INT NOT NULL,
                   applicant_id INT NOT NULL,
                   application_date DATE NOT NULL,
                   status VARCHAR(30) DEFAULT 'Applied',
                   interview_date DATE,
                   interview_notes VARCHAR(500),
                   FOREIGN KEY(job_id) REFERENCES jobs(job_id) ON DELETE CASCADE,
                   FOREIGN KEY(applicant_id) REFERENCES users(user_id) ON DELETE CASCADE)""")

    con.commit()


create_tables()


#INPUT FUNCTIONS

def get_non_empty(message):
    while True:
        value = input(message).strip()

        if value != "":
            return value

        print("Input cannot be empty.")


def get_date(message):
    while True:
        value = input(message).strip()

        try:
            date_obj = datetime.strptime(value,"%d-%m-%Y")
            return date_obj.strftime("%Y-%m-%d")

        except ValueError:
            print("Please enter date as DD-MM-YYYY.")


def get_optional_date(message):
    while True:
        value = input(message).strip()

        if value == "":
            return None

        try:
            date_obj = datetime.strptime(value,"%d-%m-%Y")
            return date_obj.strftime("%Y-%m-%d")

        except ValueError:
            print("Please enter date as DD-MM-YYYY or press Enter.")


#REGISTER

def register():

    print("\n" + "=" * 65)
    print("                    REGISTER")
    print("=" * 65)

    name = get_non_empty("Name: ")
    email = get_non_empty("Email: ")
    password = get_non_empty("Password: ")

    print("\n1. Applicant")
    print("2. Recruiter")

    choice = input("Choose account type: ")

    if choice == "1":
        role = "Applicant"

    elif choice == "2":
        role = "Recruiter"

    else:
        print("Invalid choice.")
        return

    try:
        cursor.execute("""INSERT INTO users(name,email,password,role)
                       VALUES(%s,%s,%s,%s)""",
                       (name,email,password,role))

        con.commit()

        user_id = cursor.lastrowid

        if role == "Applicant":

            education = input("Education: ").strip()
            skills = input("Skills: ").strip()
            experience = input("Experience: ").strip()
            projects = input("Projects: ").strip()

            cursor.execute("""INSERT INTO applicant_profiles
                           (user_id,education,skills,experience,projects)
                           VALUES(%s,%s,%s,%s,%s)""",
                           (user_id,education,skills,experience,projects))

            con.commit()

        print("\n✓ Registration successful!")
        print("You can now login.")

    except mysql.connector.Error as error:
        print("\nRegistration failed.")
        print("Error:",error)


#LOGIN

def login():

    print("\n" + "=" * 65)
    print("                      LOGIN")
    print("=" * 65)

    email = get_non_empty("Email: ")
    password = get_non_empty("Password: ")

    cursor.execute("""SELECT user_id,name,role FROM users
                   WHERE email = %s AND password = %s""",
                   (email,password))

    result = cursor.fetchone()

    if not result:
        print("\nInvalid email or password.")
        return

    user_id = result[0]
    name = result[1]
    role = result[2]

    print("\n✓ Login successful!")
    print("Welcome",name)

    if role == "Applicant":
        applicant_menu(user_id,name)

    else:
        recruiter_menu(user_id,name)


#VIEW JOBS

def browse_jobs():

    cursor.execute("""SELECT job_id,company,position,required_skills,
                   salary,deadline FROM jobs ORDER BY job_id DESC""")

    jobs = cursor.fetchall()

    print("\n" + "=" * 100)
    print("                         AVAILABLE JOBS")
    print("=" * 100)

    if not jobs:
        print("No jobs available.")
        return

    for job in jobs:

        print("\nJob ID:",job[0])
        print("Company:",job[1])
        print("Position:",job[2])
        print("Required Skills:",job[3] or "Not specified")
        print("Salary:",job[4] or "Not specified")
        print("Deadline:",job[5] or "No deadline")
        print("-" * 70)


#SEARCH JOBS

def search_jobs():

    keyword = get_non_empty("\nSearch job/company/skill: ")
    search = "%" + keyword + "%"

    cursor.execute("""SELECT job_id,company,position,required_skills,
                   salary,deadline FROM jobs
                   WHERE company LIKE %s
                   OR position LIKE %s
                   OR required_skills LIKE %s
                   ORDER BY job_id DESC""",
                   (search,search,search))

    results = cursor.fetchall()

    print("\n" + "=" * 80)
    print("                         SEARCH RESULTS")
    print("=" * 80)

    if not results:
        print("No jobs found.")
        return

    for row in results:

        print("\nJob ID:",row[0])
        print("Company:",row[1])
        print("Position:",row[2])
        print("Required Skills:",row[3])
        print("Salary:",row[4] or "Not specified")
        print("Deadline:",row[5] or "No deadline")


#JOB DETAILS

def job_details():

    try:
        job_id = int(input("\nEnter Job ID: "))

    except ValueError:
        print("Invalid ID.")
        return

    cursor.execute("""SELECT company,position,description,
                   required_skills,salary,deadline FROM jobs
                   WHERE job_id = %s""",(job_id,))

    job = cursor.fetchone()

    if not job:
        print("\nJob not found.")
        return

    print("\n" + "=" * 65)
    print("                       JOB DETAILS")
    print("=" * 65)

    print("Company:",job[0])
    print("Position:",job[1])
    print("Description:",job[2] or "Not provided")
    print("Required Skills:",job[3] or "Not provided")
    print("Salary:",job[4] or "Not provided")
    print("Deadline:",job[5] or "Not provided")


#SKILL MATCH

def calculate_skill_match(applicant_skills,required_skills):

    if not required_skills:
        return 100,[]

    applicant = []

    for skill in applicant_skills.split(","):
        applicant.append(skill.strip().lower())

    required = []

    for skill in required_skills.split(","):
        required.append(skill.strip().lower())

    matched = []
    missing = []

    for skill in required:

        if skill in applicant:
            matched.append(skill)

        else:
            missing.append(skill)

    if len(required) == 0:
        percentage = 100

    else:
        percentage = (len(matched) / len(required)) * 100

    return round(percentage,2),missing


#CHECK SKILL MATCH

def check_skill_match(user_id):

    try:
        job_id = int(input("\nEnter Job ID: "))

    except ValueError:
        print("Invalid ID.")
        return

    cursor.execute("""SELECT skills FROM applicant_profiles
                   WHERE user_id = %s""",(user_id,))

    applicant = cursor.fetchone()

    cursor.execute("""SELECT company,position,required_skills
                   FROM jobs WHERE job_id = %s""",(job_id,))

    job = cursor.fetchone()

    if not applicant or not job:
        print("\nInformation not found.")
        return

    percentage,missing = calculate_skill_match(applicant[0] or "",job[2] or "")

    print("\n" + "=" * 65)
    print("                     SKILL MATCH")
    print("=" * 65)

    print("Company:",job[0])
    print("Position:",job[1])
    print("Your Skill Match:",percentage,"%")

    if missing:
        print("\nMissing Skills:")

        for skill in missing:
            print("-",skill)

    else:
        print("\n✓ You have all the listed required skills!")


#ELIGIBILITY CHECKER

def eligibility_checker(user_id):

    try:
        job_id = int(input("\nEnter Job ID: "))

    except ValueError:
        print("Invalid ID.")
        return

    cursor.execute("""SELECT education,skills,experience
                   FROM applicant_profiles WHERE user_id = %s""",
                   (user_id,))

    applicant = cursor.fetchone()

    cursor.execute("""SELECT company,position,required_skills,
                   description FROM jobs WHERE job_id = %s""",
                   (job_id,))

    job = cursor.fetchone()

    if not applicant or not job:
        print("\nInformation not found.")
        return

    percentage,missing = calculate_skill_match(applicant[1] or "",job[2] or "")

    print("\n" + "=" * 65)
    print("                   ELIGIBILITY CHECKER")
    print("=" * 65)

    print("Company:",job[0])
    print("Position:",job[1])
    print("Skill Match:",percentage,"%")

    if percentage >= 70:
        print("\n✓ You appear to be a good match for this job.")

    elif percentage >= 40:
        print("\n⚠️ You partially match this job.")
        print("Consider improving your missing skills.")

    else:
        print("\n✗ Your current skill match is low.")

    if missing:
        print("\nSkills you may need:")

        for skill in missing:
            print("-",skill)


#JOB RECOMMENDATIONS

def job_recommendations(user_id):

    cursor.execute("""SELECT skills FROM applicant_profiles
                   WHERE user_id = %s""",(user_id,))

    applicant = cursor.fetchone()

    if not applicant:
        print("Applicant profile not found.")
        return

    applicant_skills = applicant[0] or ""

    cursor.execute("""SELECT job_id,company,position,
                   required_skills,salary,deadline FROM jobs""")

    jobs = cursor.fetchall()

    recommendations = []

    for job in jobs:

        percentage,missing = calculate_skill_match(applicant_skills,job[3] or "")

        recommendations.append((percentage,job,missing))

    recommendations.sort(reverse=True,key=lambda x:x[0])

    print("\n" + "=" * 90)
    print("                     JOB RECOMMENDATIONS")
    print("=" * 90)

    if not recommendations:
        print("No jobs available.")
        return

    for percentage,job,missing in recommendations[:10]:

        print("\nJob ID:",job[0])
        print("Company:",job[1])
        print("Position:",job[2])
        print("Skill Match:",percentage,"%")
        print("Salary:",job[4] or "Not specified")
        print("Deadline:",job[5] or "No deadline")


#APPLY FOR JOB

def apply_for_job(user_id):

    try:
        job_id = int(input("\nEnter Job ID to apply: "))

    except ValueError:
        print("Invalid ID.")
        return

    cursor.execute("""SELECT job_id,company,position,deadline
                   FROM jobs WHERE job_id = %s""",(job_id,))

    job = cursor.fetchone()

    if not job:
        print("\nJob not found.")
        return

    cursor.execute("""SELECT application_id FROM applications
                   WHERE job_id = %s AND applicant_id = %s""",
                   (job_id,user_id))

    already_applied = cursor.fetchone()

    if already_applied:
        print("\nYou have already applied for this job.")
        return

    today = datetime.now().strftime("%Y-%m-%d")

    cursor.execute("""INSERT INTO applications
                   (job_id,applicant_id,application_date,status)
                   VALUES(%s,%s,%s,'Applied')""",
                   (job_id,user_id,today))

    con.commit()

    print("\n✓ Application submitted successfully!")
    print("Company:",job[1])
    print("Position:",job[2])


#MY APPLICATIONS

def my_applications(user_id):

    cursor.execute("""SELECT applications.application_id,
                   jobs.company,jobs.position,applications.status,
                   applications.application_date,
                   applications.interview_date
                   FROM applications
                   JOIN jobs ON applications.job_id = jobs.job_id
                   WHERE applications.applicant_id = %s
                   ORDER BY applications.application_id DESC""",
                   (user_id,))

    records = cursor.fetchall()

    print("\n" + "=" * 95)
    print("                       MY APPLICATIONS")
    print("=" * 95)

    if not records:
        print("You have not applied for any jobs.")
        return

    print(f"{'ID':<6}{'COMPANY':<20}{'POSITION':<25}{'STATUS':<15}{'DATE':<15}")

    print("-" * 95)

    for row in records:

        print(f"{row[0]:<6}{row[1][:18]:<20}{row[2][:23]:<25}{row[3]:<15}{str(row[4]):<15}")


#WITHDRAW APPLICATION

def withdraw_application(user_id):

    try:
        application_id = int(input("\nEnter Application ID: "))

    except ValueError:
        print("Invalid ID.")
        return

    cursor.execute("""SELECT application_id FROM applications
                   WHERE application_id = %s AND applicant_id = %s""",
                   (application_id,user_id))

    result = cursor.fetchone()

    if not result:
        print("\nApplication not found.")
        return

    cursor.execute("""UPDATE applications SET status = 'Withdrawn'
                   WHERE application_id = %s""",(application_id,))

    con.commit()

    print("\n✓ Application withdrawn.")


#VIEW PROFILE

def view_profile(user_id):

    cursor.execute("""SELECT users.name,users.email,
                   applicant_profiles.education,
                   applicant_profiles.skills,
                   applicant_profiles.experience,
                   applicant_profiles.projects
                   FROM users
                   JOIN applicant_profiles
                   ON users.user_id = applicant_profiles.user_id
                   WHERE users.user_id = %s""",(user_id,))

    profile = cursor.fetchone()

    if not profile:
        print("\nProfile not found.")
        return

    print("\n" + "=" * 65)
    print("                     MY PROFILE")
    print("=" * 65)

    print("Name:",profile[0])
    print("Email:",profile[1])
    print("Education:",profile[2] or "Not provided")
    print("Skills:",profile[3] or "Not provided")
    print("Experience:",profile[4] or "Not provided")
    print("Projects:",profile[5] or "Not provided")


#EDIT PROFILE

def edit_profile(user_id):

    cursor.execute("""SELECT education,skills,experience,projects
                   FROM applicant_profiles WHERE user_id = %s""",
                   (user_id,))

    profile = cursor.fetchone()

    if not profile:
        print("\nProfile not found.")
        return

    print("\nPress Enter to keep the existing value.")

    education = input("Education [" + str(profile[0] or "") + "]: ").strip()
    skills = input("Skills [" + str(profile[1] or "") + "]: ").strip()
    experience = input("Experience [" + str(profile[2] or "") + "]: ").strip()
    projects = input("Projects [" + str(profile[3] or "") + "]: ").strip()

    if education == "":
        education = profile[0]

    if skills == "":
        skills = profile[1]

    if experience == "":
        experience = profile[2]

    if projects == "":
        projects = profile[3]

    cursor.execute("""UPDATE applicant_profiles
                   SET education=%s,skills=%s,experience=%s,projects=%s
                   WHERE user_id=%s""",
                   (education,skills,experience,projects,user_id))

    con.commit()

    print("\n✓ Profile updated successfully.")


#CAREER READINESS SCORE

def career_readiness(user_id):

    cursor.execute("""SELECT education,skills,experience,projects
                   FROM applicant_profiles WHERE user_id = %s""",
                   (user_id,))

    profile = cursor.fetchone()

    if not profile:
        return

    score = 0

    if profile[0]:
        score += 20

    if profile[1]:
        score += 20

    if profile[2]:
        score += 20

    if profile[3]:
        score += 20

    cursor.execute("""SELECT COUNT(*) FROM applications
                   WHERE applicant_id = %s""",(user_id,))

    applications = cursor.fetchone()[0]

    if applications > 0:
        score += 20

    print("\n" + "=" * 65)
    print("                  CAREER READINESS")
    print("=" * 65)

    print("Career Readiness Score:",score,"/ 100")

    if score >= 80:
        print("✓ Strong profile")

    elif score >= 60:
        print("✓ Good profile, but there is room to improve")

    elif score >= 40:
        print("⚠️ Your profile needs improvement")

    else:
        print("⚠️ Complete your profile to improve your score")


#INTERVIEW TRACKER

def interview_tracker(user_id):

    cursor.execute("""SELECT applications.application_id,
                   jobs.company,jobs.position,
                   applications.interview_date,
                   applications.interview_notes
                   FROM applications
                   JOIN jobs ON applications.job_id = jobs.job_id
                   WHERE applications.applicant_id = %s
                   AND applications.interview_date IS NOT NULL""",
                   (user_id,))

    records = cursor.fetchall()

    print("\n" + "=" * 80)
    print("                    INTERVIEW TRACKER")
    print("=" * 80)

    if not records:
        print("No interviews scheduled.")
        return

    for row in records:

        print("\nApplication ID:",row[0])
        print("Company:",row[1])
        print("Position:",row[2])
        print("Interview Date:",row[3])
        print("Notes:",row[4] or "None")


#APPLICANT DEADLINE ALERTS

def applicant_deadline_alerts(user_id):

    today = datetime.now().date()

    cursor.execute("""SELECT jobs.company,jobs.position,
                   jobs.deadline FROM applications
                   JOIN jobs ON applications.job_id = jobs.job_id
                   WHERE applications.applicant_id = %s
                   AND jobs.deadline IS NOT NULL""",
                   (user_id,))

    records = cursor.fetchall()

    print("\n" + "=" * 65)
    print("                  DEADLINE ALERTS")
    print("=" * 65)

    found = False

    for row in records:

        deadline = row[2]
        days_left = (deadline - today).days

        if days_left < 0:

            print("\n⚠️ EXPIRED:",row[0],"-",row[1])
            found = True

        elif days_left <= 7:

            print("\n⚠️ DEADLINE IN",days_left,"DAYS:",row[0],"-",row[1])
            found = True

    if not found:
        print("\n✓ No urgent deadlines.")


#RECRUITER POST JOB

def post_job(recruiter_id):

    print("\n" + "=" * 65)
    print("                     POST JOB")
    print("=" * 65)

    company = get_non_empty("Company: ")
    position = get_non_empty("Position: ")
    description = input("Job description: ").strip()
    required_skills = input("Required skills: ").strip()
    salary = input("Salary: ").strip()
    deadline = get_optional_date("Deadline (DD-MM-YYYY or Enter): ")

    cursor.execute("""INSERT INTO jobs
                   (recruiter_id,company,position,description,
                   required_skills,salary,deadline)
                   VALUES(%s,%s,%s,%s,%s,%s,%s)""",
                   (recruiter_id,company,position,description,
                    required_skills,salary,deadline))

    con.commit()

    print("\n✓ Job posted successfully!")
    print("Job ID:",cursor.lastrowid)


#RECRUITER JOBS

def recruiter_jobs(recruiter_id):

    cursor.execute("""SELECT job_id,company,position,
                   required_skills,salary,deadline
                   FROM jobs WHERE recruiter_id = %s
                   ORDER BY job_id DESC""",
                   (recruiter_id,))

    jobs = cursor.fetchall()

    print("\n" + "=" * 90)
    print("                       MY JOBS")
    print("=" * 90)

    if not jobs:
        print("You have not posted any jobs.")
        return

    for job in jobs:

        print("\nJob ID:",job[0])
        print("Company:",job[1])
        print("Position:",job[2])
        print("Required Skills:",job[3])
        print("Salary:",job[4])
        print("Deadline:",job[5])


#RECRUITER VIEW APPLICANTS

def view_applicants(recruiter_id):

    try:
        job_id = int(input("\nEnter Job ID: "))

    except ValueError:
        print("Invalid ID.")
        return

    cursor.execute("""SELECT company,position FROM jobs
                   WHERE job_id = %s AND recruiter_id = %s""",
                   (job_id,recruiter_id))

    job = cursor.fetchone()

    if not job:
        print("\nJob not found.")
        return

    cursor.execute("""SELECT applications.application_id,
                   users.name,users.email,
                   applicant_profiles.education,
                   applicant_profiles.skills,
                   applicant_profiles.experience,
                   applicant_profiles.projects,
                   applications.status
                   FROM applications
                   JOIN users ON applications.applicant_id = users.user_id
                   JOIN applicant_profiles
                   ON users.user_id = applicant_profiles.user_id
                   WHERE applications.job_id = %s""",
                   (job_id,))

    applicants = cursor.fetchall()

    print("\n" + "=" * 100)
    print("                     APPLICANTS")
    print("=" * 100)

    if not applicants:
        print("No applicants yet.")
        return

    for row in applicants:

        print("\nApplication ID:",row[0])
        print("Name:",row[1])
        print("Email:",row[2])
        print("Education:",row[3] or "Not provided")
        print("Skills:",row[4] or "Not provided")
        print("Experience:",row[5] or "Not provided")
        print("Projects:",row[6] or "Not provided")
        print("Status:",row[7])
        print("-" * 80)


#APPLICANT RANKING

def applicant_ranking(recruiter_id):

    try:
        job_id = int(input("\nEnter Job ID: "))

    except ValueError:
        print("Invalid ID.")
        return

    cursor.execute("""SELECT required_skills FROM jobs
                   WHERE job_id = %s AND recruiter_id = %s""",
                   (job_id,recruiter_id))

    job = cursor.fetchone()

    if not job:
        print("\nJob not found.")
        return

    cursor.execute("""SELECT applications.application_id,
                   users.name,applicant_profiles.skills,
                   applications.status
                   FROM applications
                   JOIN users ON applications.applicant_id = users.user_id
                   JOIN applicant_profiles
                   ON users.user_id = applicant_profiles.user_id
                   WHERE applications.job_id = %s""",
                   (job_id,))

    applicants = cursor.fetchall()

    ranked = []

    for applicant in applicants:

        percentage,missing = calculate_skill_match(
            applicant[2] or "",job[0] or "")

        ranked.append((percentage,applicant,missing))

    ranked.sort(reverse=True,key=lambda x:x[0])

    print("\n" + "=" * 80)
    print("                  APPLICANT RANKING")
    print("=" * 80)

    if not ranked:
        print("No applicants.")
        return

    rank = 1

    for percentage,applicant,missing in ranked:

        print("\nRank:",rank)
        print("Application ID:",applicant[0])
        print("Name:",applicant[1])
        print("Skill Match:",percentage,"%")
        print("Status:",applicant[3])

        rank += 1


#SEARCH APPLICANTS BY SKILL

def search_applicants(recruiter_id):

    skill = get_non_empty("\nEnter skill to search: ").lower()

    cursor.execute("""SELECT users.name,users.email,
                   applicant_profiles.education,
                   applicant_profiles.skills,
                   applicant_profiles.experience
                   FROM users
                   JOIN applicant_profiles
                   ON users.user_id = applicant_profiles.user_id
                   WHERE users.role = 'Applicant'
                   AND LOWER(applicant_profiles.skills) LIKE %s""",
                   ("%" + skill + "%",))

    applicants = cursor.fetchall()

    print("\n" + "=" * 80)
    print("                 APPLICANT SEARCH")
    print("=" * 80)

    if not applicants:
        print("No applicants found with this skill.")
        return

    for row in applicants:

        print("\nName:",row[0])
        print("Email:",row[1])
        print("Education:",row[2] or "Not provided")
        print("Skills:",row[3] or "Not provided")
        print("Experience:",row[4] or "Not provided")


#UPDATE APPLICATION STATUS

def recruiter_update_status(recruiter_id):

    try:
        application_id = int(input("\nEnter Application ID: "))

    except ValueError:
        print("Invalid ID.")
        return

    cursor.execute("""SELECT applications.application_id
                   FROM applications
                   JOIN jobs ON applications.job_id = jobs.job_id
                   WHERE applications.application_id = %s
                   AND jobs.recruiter_id = %s""",
                   (application_id,recruiter_id))

    result = cursor.fetchone()

    if not result:
        print("\nApplication not found.")
        return

    print("\nStatus options:")
    print("1. Applied")
    print("2. Shortlisted")
    print("3. Interview")
    print("4. Selected")
    print("5. Rejected")

    choice = input("Choose status: ")

    statuses = {
        "1":"Applied",
        "2":"Shortlisted",
        "3":"Interview",
        "4":"Selected",
        "5":"Rejected"
    }

    if choice not in statuses:
        print("Invalid choice.")
        return

    new_status = statuses[choice]

    cursor.execute("""UPDATE applications SET status = %s
                   WHERE application_id = %s""",
                   (new_status,application_id))

    if new_status == "Interview":

        interview_date = get_optional_date(
            "Interview date (DD-MM-YYYY or Enter): ")

        interview_notes = input("Interview notes: ").strip()

        cursor.execute("""UPDATE applications
                       SET interview_date=%s,interview_notes=%s
                       WHERE application_id=%s""",
                       (interview_date,interview_notes,application_id))

    con.commit()

    print("\n✓ Application status updated.")


#RECRUITER DASHBOARD

def recruiter_dashboard(recruiter_id):

    print("\n" + "=" * 70)
    print("                 RECRUITER DASHBOARD")
    print("=" * 70)

    cursor.execute("""SELECT COUNT(*) FROM jobs
                   WHERE recruiter_id = %s""",(recruiter_id,))

    jobs = cursor.fetchone()[0]

    cursor.execute("""SELECT COUNT(*) FROM applications
                   JOIN jobs ON applications.job_id = jobs.job_id
                   WHERE jobs.recruiter_id = %s""",(recruiter_id,))

    applications = cursor.fetchone()[0]

    cursor.execute("""SELECT COUNT(*) FROM applications
                   JOIN jobs ON applications.job_id = jobs.job_id
                   WHERE jobs.recruiter_id = %s
                   AND applications.status = 'Shortlisted'""",
                   (recruiter_id,))

    shortlisted = cursor.fetchone()[0]

    cursor.execute("""SELECT COUNT(*) FROM applications
                   JOIN jobs ON applications.job_id = jobs.job_id
                   WHERE jobs.recruiter_id = %s
                   AND applications.status = 'Selected'""",
                   (recruiter_id,))

    selected = cursor.fetchone()[0]

    print("\nTotal Jobs Posted:",jobs)
    print("Total Applications:",applications)
    print("Shortlisted:",shortlisted)
    print("Selected:",selected)


#EXPORT APPLICANT REPORT

def export_applicant_report(user_id):

    filename = "jobtrack_applicant_report.csv"

    cursor.execute("""SELECT jobs.company,jobs.position,
                   applications.application_date,
                   applications.status,
                   jobs.salary
                   FROM applications
                   JOIN jobs ON applications.job_id = jobs.job_id
                   WHERE applications.applicant_id = %s
                   ORDER BY applications.application_id DESC""",
                   (user_id,))

    records = cursor.fetchall()

    file = open(filename,"w",newline="",encoding="utf-8")

    writer = csv.writer(file)

    writer.writerow(["Company","Position","Application Date",
                     "Status","Salary"])

    writer.writerows(records)

    file.close()

    print("\n✓ Report exported as:",filename)


#APPLICANT MENU

def applicant_menu(user_id,name):

    while True:

        print("\n")
        print("=" * 70)
        print("                 💼 JOBTRACK APPLICANT")
        print("                    Welcome",name)
        print("=" * 70)

        print("\n1. Browse Jobs")
        print("2. Search Jobs")
        print("3. Job Details")
        print("4. Check Skill Match")
        print("5. Eligibility Checker")
        print("6. Job Recommendations")
        print("7. Apply for Job")
        print("8. My Applications")
        print("9. Withdraw Application")
        print("10. My Profile")
        print("11. Edit Profile")
        print("12. Career Readiness Score")
        print("13. Interview Tracker")
        print("14. Deadline Alerts")
        print("15. Export Report")
        print("16. Logout")

        choice = input("\nChoose an option: ")

        if choice == "1":
            browse_jobs()

        elif choice == "2":
            search_jobs()

        elif choice == "3":
            job_details()

        elif choice == "4":
            check_skill_match(user_id)

        elif choice == "5":
            eligibility_checker(user_id)

        elif choice == "6":
            job_recommendations(user_id)

        elif choice == "7":
            apply_for_job(user_id)

        elif choice == "8":
            my_applications(user_id)

        elif choice == "9":
            withdraw_application(user_id)

        elif choice == "10":
            view_profile(user_id)

        elif choice == "11":
            edit_profile(user_id)

        elif choice == "12":
            career_readiness(user_id)

        elif choice == "13":
            interview_tracker(user_id)

        elif choice == "14":
            applicant_deadline_alerts(user_id)

        elif choice == "15":
            export_applicant_report(user_id)

        elif choice == "16":
            print("\nLogged out.")
            break

        else:
            print("\nInvalid option.")


#RECRUITER MENU

def recruiter_menu(user_id,name):

    while True:

        print("\n")
        print("=" * 70)
        print("                 💼 JOBTRACK RECRUITER")
        print("                    Welcome",name)
        print("=" * 70)

        print("\n1. Post New Job")
        print("2. View My Jobs")
        print("3. View Applicants")
        print("4. Applicant Ranking")
        print("5. Search Applicants by Skill")
        print("6. Update Application Status")
        print("7. Recruiter Dashboard")
        print("8. Browse All Jobs")
        print("9. Logout")

        choice = input("\nChoose an option: ")

        if choice == "1":
            post_job(user_id)

        elif choice == "2":
            recruiter_jobs(user_id)

        elif choice == "3":
            view_applicants(user_id)

        elif choice == "4":
            applicant_ranking(user_id)

        elif choice == "5":
            search_applicants(user_id)

        elif choice == "6":
            recruiter_update_status(user_id)

        elif choice == "7":
            recruiter_dashboard(user_id)

        elif choice == "8":
            browse_jobs()

        elif choice == "9":
            print("\nLogged out.")
            break

        else:
            print("\nInvalid option.")


#MAIN MENU

def main():

    while True:

        print("\n")
        print("=" * 70)
        print("                         💼 JOBTRACK")
        print("                 Job & Applicant Manager")
        print("=" * 70)

        print("\n1. Register")
        print("2. Login")
        print("3. Browse Jobs")
        print("4. Search Jobs")
        print("5. Exit")

        choice = input("\nChoose an option: ")

        if choice == "1":
            register()

        elif choice == "2":
            login()

        elif choice == "3":
            browse_jobs()

        elif choice == "4":
            search_jobs()

        elif choice == "5":
            print("\nThank you for using JOBTRACK!")
            break

        else:
            print("\nInvalid option.")


#START PROGRAM

try:
    main()

finally:
    cursor.close()
    con.close()
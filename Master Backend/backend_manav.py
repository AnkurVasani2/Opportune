from flask import Flask, request, jsonify
import sqlite3
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
DATABASE = r'D:\\opportune\\sqlite_server\\ProfileDB.db'


# Initialize the SQLite database
def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS resume_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fullName TEXT,
            email TEXT,
            contactNumber TEXT,
            location TEXT,
            institution TEXT,
            fieldOfStudy TEXT,
            currentYear TEXT,
            gpa TEXT,
            shortTermGoals TEXT,
            longTermGoals TEXT,
            desiredRoles TEXT,
            technicalSkills TEXT,
            softSkills TEXT,
            certifications TEXT,
            areasOfInterest TEXT,
            workExperience TEXT,
            projects TEXT,
            extracurriculars TEXT,
            startDate TEXT,
            workSchedule TEXT,
            feedbackPreference TEXT,
            learningStyle TEXT,
            preferredResources TEXT,
            linkedinUrl TEXT,
            githubUrl TEXT,
            portfolioUrl TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Save profile data
@app.route('/save_profile', methods=['POST'])
def save_profile():
    data = request.json
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    try:
        # Convert list fields to comma-separated strings
        fieldOfStudy = ', '.join(data.get('fieldOfStudy', [])) if isinstance(data.get('fieldOfStudy'), list) else data.get('fieldOfStudy')
        technicalSkills = ', '.join(data.get('technicalSkills', [])) if isinstance(data.get('technicalSkills'), list) else data.get('technicalSkills')
        softSkills = ', '.join(data.get('softSkills', [])) if isinstance(data.get('softSkills'), list) else data.get('softSkills')
        certifications = ', '.join(data.get('certifications', [])) if isinstance(data.get('certifications'), list) else data.get('certifications')
        areasOfInterest = ', '.join(data.get('areasOfInterest', [])) if isinstance(data.get('areasOfInterest'), list) else data.get('areasOfInterest')
        
        # Ensure 'gpa' is treated as a string even if it's a list
        gpa = ', '.join(data.get('gpa', [])) if isinstance(data.get('gpa'), list) else data.get('gpa')

        # Ensure 'shortTermGoals', 'longTermGoals', and 'desiredRoles' are strings if they're lists
        shortTermGoals = ', '.join(data.get('shortTermGoals', [])) if isinstance(data.get('shortTermGoals'), list) else data.get('shortTermGoals')
        longTermGoals = ', '.join(data.get('longTermGoals', [])) if isinstance(data.get('longTermGoals'), list) else data.get('longTermGoals')
        desiredRoles = ', '.join(data.get('desiredRoles', [])) if isinstance(data.get('desiredRoles'), list) else data.get('desiredRoles')

        # Now execute the query
        cursor.execute('''
            INSERT INTO resume_data (
                fullName, email, contactNumber, location, institution, fieldOfStudy,
                currentYear, gpa, shortTermGoals, longTermGoals, desiredRoles,
                technicalSkills, softSkills, certifications, areasOfInterest,
                workExperience, projects, extracurriculars, startDate, workSchedule,
                feedbackPreference, learningStyle, preferredResources,
                linkedinUrl, githubUrl, portfolioUrl
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.get('fullName'), data.get('email'), data.get('contactNumber'), data.get('location'),
            data.get('institution'), fieldOfStudy, data.get('currentYear'), gpa, 
            shortTermGoals, longTermGoals, desiredRoles,
            technicalSkills, softSkills, certifications, areasOfInterest,
            data.get('workExperience'), data.get('projects'), data.get('extracurriculars'),
            data.get('startDate'), data.get('workSchedule'), data.get('feedbackPreference'),
            data.get('learningStyle'), data.get('preferredResources'),
            data.get('linkedinUrl'), data.get('githubUrl'), data.get('portfolioUrl')
        ))
        conn.commit()
        return jsonify({"success": True, "message": "Profile data saved successfully!"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
    finally:
        conn.close()

if __name__ == '__main__':
    app.run(debug=True)

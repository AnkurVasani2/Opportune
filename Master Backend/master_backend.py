from flask import Flask, request, jsonify
from flask_cors import CORS
import PyPDF2
import spacy
import re
import google.generativeai as ai
import json
import os
from flask import Flask, request, jsonify
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import requests
import pickle
import numpy as np
import firebase_admin
from firebase_admin import credentials, firestore
from send_email import *
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import json
import io
from PyPDF2 import PdfReader
import sqlite3
from speech_handler import process_speech_and_chat
import tempfile

app = Flask(__name__)
CORS(app)
cred = credentials.Certificate("service.json")
firebase_admin.initialize_app(cred)

ai.configure(api_key="AIzaSyBFwzpXDAy2ZRBgKIXDCGOyIDMsT2ljeZA")
model = ai.GenerativeModel("gemini-1.5-flash")
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/speech', methods=['POST'])
def speech_route():
    user_id = request.form.get('user_id', 'default_user')
    if 'audio' not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    audio_file = request.files['audio']
    interview_type=request.form.get('interview_type')
    result = process_speech_and_chat(user_id,audio_file,interview_type)
    print(result)
    if result:
        # # Connect to SQLite database (or create it if it doesn't exist)
        # conn = sqlite3.connect('audio_db.sqlite3')
        # cursor = conn.cursor()

        # # Create a table to store the audio file as a BLOB
        # cursor.execute('''
        #     CREATE TABLE IF NOT EXISTS audio_files (
        #         id INTEGER PRIMARY KEY,
        #         filename TEXT,
        #         audio_data BLOB
        #     )
        # ''')
        # conn.commit()

        # Function to insert audio file into the database
        # def insert_audio(file_path):
        #     with open(file_path, 'rb') as f:
        #         audio_data = f.read()
        #     filename = os.path.basename(file_path)
            
        #     # Insert the audio file data into the database
        #     cursor.execute('''
        #         INSERT INTO audio_files (filename, audio_data)
        #         VALUES (?, ?)
        #     ''', (filename, audio_data))
        #     conn.commit()
        #     print(f"Audio file '{filename}' inserted successfully.")


        # Insert an audio file into the database
        # insert_audio(audio_file)  # Replace with the path to your audio file
        
        print(result)
        return jsonify(result), 200
    else:
        return jsonify({"error": "Processing failed"}), 500

@app.route('/job', methods=['POST'])
def search_jobs():
    headers = {
        'ngrok-skip-browser-warning': 'skip-browser-warning'
    }
    data=request.json

    try:
        # Get query parameters from the data
        query = data.get('query', '').strip('"')
        location = data.get('location', '').strip('"')
        distance = data.get('distance', '1.0').strip('"')
        language = data.get('language', 'en_GB').strip('"')
        remote_only = data.get('remoteOnly', 'false').strip('"').lower() == 'true'
        date_posted = data.get('datePosted', 'month').strip('"')
        employment_types = data.get('employmentTypes', 'fulltime').strip('"')

        # Debug logging
        print(f"Received parameters: query={query}, location={location}, distance={distance}, "
              f"language={language}, remote_only={remote_only}, date_posted={date_posted}, "
              f"employment_types={employment_types}")

        if not query:
            return jsonify({"error": "Query parameter is required."}), 400

        # Split the query into skills
        skills = [skill.strip() for skill in query.split(',') if skill.strip()]

        if not skills:
            return jsonify({"error": "No valid skills provided in query."}), 400

        # Collect results for the skills
        job_results = []
        for skill in skills[:2]:  # Limit to 2 skills
            api_response = search_jobs_for_skill(
                skill=skill,
                location=location,
                distance=distance,
                language=language,
                remote_only=remote_only,
                date_posted=date_posted,
                employment_types=employment_types
            )
            
            if isinstance(api_response, dict):
                if 'error' not in api_response:
                    simplified_results = simplify_job_results(api_response, skill)
                    job_results.extend(simplified_results)
                else:
                    print(f"Error in API response for skill '{skill}': {api_response['error']}")

        if not job_results:
            return jsonify({"message": "No job results found", "results": []}), 200

        return jsonify({"message": "Success", "results": job_results}), 200, headers  # Include the header here

    except Exception as e:
        print(f"Error in search_jobs: {str(e)}")
        return jsonify({"error": "An unexpected error occurred while processing your request."}), 500, headers


def search_jobs_for_skill(skill, location, distance, language, remote_only=False, date_posted=None, employment_types=None):
    url = "https://jobs-api14.p.rapidapi.com/v2/list"
    headers = {
        "X-RapidAPI-Key": "c71ed1738dmshca243290e45afb0p17edf7jsn823377b25e41",
        "X-RapidAPI-Host": "jobs-api14.p.rapidapi.com"
    }

    querystring = {
        "query": skill,
        "location": location,
        "distance": distance,
        "language": language,
        "remote_only": str(remote_only).lower(),
        "date_posted": date_posted,
        "employment_types": employment_types,
    }   

    try:
        response = requests.get(url, params=querystring, headers=headers)
        print(f"API request URL: {response.url}")  # Debug logging
        print(f"API response status code: {response.status_code}")  # Debug logging
        
        if response.status_code == 200:
            print(response.json())
            return response.json()
        else:
            error_message = f"Failed to fetch job listings for {skill}. Status code: {response.status_code}"
            print(error_message)  # Debug logging
            return {"error": error_message}
    except Exception as e:
        error_message = f"Exception occurred for {skill}: {str(e)}"
        print(error_message)  # Debug logging
        return {"error": error_message}

# Function to simplify the job results
def simplify_job_results(api_response, keyword):
    simplified_jobs = []
    jobs = api_response.get('jobs', [])

    for job in jobs:
        if isinstance(job, dict):
            company_info = job.get('company', {})
            company = company_info.get('name', 'N/A') if isinstance(company_info, dict) else 'N/A'
            date_posted = job.get('datePosted', 'N/A')
            employment_type = job.get('employmentType', 'N/A')
            job_providers = job.get('jobProviders', [])
            job_url = job_providers[0].get('url') if job_providers and isinstance(job_providers[0], dict) else 'N/A'
            job_id = job.get('id', 'N/A')
            title = job.get('title', 'N/A')

            simplified_job = {
                "id": job_id,
                'role': title,
                "Keyword Matched": keyword,
                "Company": company_info,
                "Date Posted": date_posted,
                "Employment Type": employment_type,
                "First Job Provider URL": job_url
            }

            simplified_jobs.append(simplified_job)
        else:
            print(f"Unexpected job format: {job}")

    return simplified_jobs

# Function to search jobs for two domains and simplify the results
@app.route('/get_info', methods=['POST'])
def get_info():
    file = request.files.get('pdfFile')
    
    if not file:
        return jsonify({"error": "No PDF file uploaded"}), 400
    
    try:
        pdf_reader = PyPDF2.PdfReader(file)
    except Exception as e:
        return jsonify({"error": "Failed to read PDF file", "message": str(e)}), 500

    def store_pdf_in_sqlite(db_file, pdf_file):
        """
        Stores the content of a PDF file as a blob in an SQLite database.

        Args:
            db_file (str): Path to the SQLite database file.
            pdf_file (FileStorage): The uploaded PDF file.
        """
        try:
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()

            # Create the table if it doesn't exist
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS pdf_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT,
                    pdf_blob BLOB
                )
            ''')

            # Read the file content from the FileStorage object
            pdf_data = pdf_file.read()
            print(f"PDF size: {len(pdf_data)} bytes")

            # Insert the PDF data into the database
            cursor.execute("INSERT INTO pdf_data (filename, pdf_blob) VALUES (?, ?)",
                        (pdf_file.filename, pdf_data))

            conn.commit()
            print(f"Data committed successfully: {pdf_file.filename}")
        except sqlite3.Error as e:
            print(f"SQLite error: {e}")
        finally:
            conn.close()


    # Example usage:
    db_file = 'my_database.db'

    store_pdf_in_sqlite(db_file, file)
    print("Data Inserted to databse")

    file_content = ""
    for page_num in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[page_num]
        file_content += page.extract_text()

    if not file_content.strip():
        return jsonify({"error": "PDF content is empty"}), 400

    # print(file_content)  # Debugging log

    nlp = spacy.load("en_core_web_sm")
    nlp_text = nlp(file_content)

    resume_data = { 
        'fullName': '',
        'email': '',
        'contactNumber': '',
        'location': '',
        'institution': '',
        'fieldOfStudy': '',
        'currentYear': '',
        'gpa': '',
        'shortTermGoals': '',
        'longTermGoals': '',
        'desiredRoles': '',
        'technicalSkills': '',
        'softSkills': '',
        'certifications': '',
        'areasOfInterest': '',
        'workExperience': '',
        'projects': '',
        'extracurriculars': '',
        'startDate': '',
        'workSchedule': '',
        'feedbackPreference': '',
        'learningStyle': '',
        'preferredResources': '',
        'linkedinUrl': '',
        'githubUrl': '',
        'portfolioUrl': '',
    }

    # Extract Name
    for ent in nlp_text.ents:
        if ent.label_ == 'PERSON':
            resume_data['fullName'] = ent.text
            break

    # Extract Email
    email = re.search(r'[\w\.-]+@[\w\.-]+', file_content)
    resume_data['email'] = email.group(0) if email else ""
    
    # Extract Contact Number
    contact = re.search(r'\+?\d{10,}', file_content)
    resume_data['contactNumber'] = contact.group(0) if contact else ""

    # List of Indian cities
    indian_cities = [
        'Mumbai', 'Delhi', 'Bengaluru', 'Kolkata', 'Chennai', 'Hyderabad', 'Pune', 'Ahmedabad',
        'Jaipur', 'Surat', 'Lucknow', 'Kanpur', 'Nagpur', 'Indore', 'Thane', 'Bhopal', 'Visakhapatnam',
        'Patna', 'Vadodara', 'Ghaziabad', 'Ludhiana', 'Agra', 'Nashik', 'Faridabad', 'Meerut', 'Rajkot',
        'Varanasi', 'Srinagar', 'Aurangabad', 'Dhanbad', 'Amritsar', 'Ranchi', 'Jodhpur', 'Raipur', 
        'Kota', 'Guwahati', 'Chandigarh', 'Mysore', 'Gwalior', 'Coimbatore'
    ]

    # Extract Location
    for city in indian_cities:
        if city.lower() in file_content.lower():
            resume_data['location'] = city
            break

    # Function to match entire string if any word from it is found
    def match_and_append(content, list_of_phrases):
        detected = []
        for phrase in list_of_phrases:
            phrase_words = phrase.lower().split()
            if any(word in content.lower() for word in phrase_words):
                detected.append(phrase)
        return detected

    # List of technical skills and short forms
    common_skills = [
        'Python', 'Java', 'C', 'C++', 'C#', 'JavaScript', 'React', 'Node', 'Express', 
        'PHP', 'SQL', 'MySQL', 'MongoDB', 'Flask', 'Django', 'Tensorflow', 'Keras', 
        'Pytorch', 'OpenCV', 'Docker', 'Kubernetes', 'Git', 'GitHub', 'AWS', 'Azure', 
        'Google Cloud', 'Firebase', 'HTML', 'CSS', 'Bootstrap', 'Vue.js', 'Angular', 
        'TypeScript', 'Machine Learning', 'ML', 'Deep Learning', 'AI', 'NLP', 
        'Computer Vision', 'CV', 'Artificial Intelligence', 'Data Science', 'DS', 
        'Data Analysis', 'Streamlit', 'Jupyter', 'Postman', 'Figma', 'Roboflow', 'Tableau'
    ]

    # Extract Technical Skills
    resume_data['technicalSkills'] = match_and_append(file_content, common_skills)

    # List of common areas of interest and short forms
    common_areas_of_interest = [
        'Machine Learning', 'ML', 'Artificial Intelligence', 'AI', 'Data Science', 'DS', 
        'Web Development', 'Mobile Development', 'Cloud Computing', 'Cybersecurity', 
        'Blockchain', 'Internet of Things', 'IoT', 'Big Data', 'DevOps', 'Game Development', 
        'Augmented Reality', 'AR', 'Virtual Reality', 'VR', 'Digital Marketing', 
        'UI/UX Design', 'Research and Development', 'R&D'
    ]

    # Extract Areas of Interest
    resume_data['areasOfInterest'] = match_and_append(file_content, common_areas_of_interest)

    common_fields_of_study = [
        'Computer Engineering', 'Information Technology', 'Data Science', 'Artificial Intelligence', 
        'Machine Learning', 'Software Engineering', 'Cybersecurity', 'Electrical Engineering', 
        'Mechanical Engineering', 'Civil Engineering', 'Biotechnology', 'Chemical Engineering', 
        'Physics', 'Mathematics', 'Statistics', 'Bioinformatics', 'Business Administration', 
        'Economics', 'Marketing', 'Finance', 'Accounting', 'Human Resources'
    ]

    # Extract Field of Study
    resume_data['fieldOfStudy'] = match_and_append(file_content, common_fields_of_study)

    common_desired_roles = [
        'Software Engineer', 'Full Stack Developer', 'Data Scientist', 'Data Analyst', 'Machine Learning Engineer',
        'Web Developer', 'Backend Developer', 'Frontend Developer', 'Mobile App Developer', 'DevOps Engineer',
        'UI/UX Designer', 'Cloud Engineer', 'Cybersecurity Analyst', 'AI Engineer', 'Research Scientist',
        'Database Administrator', 'Network Engineer', 'Product Manager', 'Project Manager', 'IT Consultant'
    ]

    # Extract Desired Roles
    resume_data['desiredRoles'] = match_and_append(file_content, common_desired_roles)


    short_term_goals = [
        'Gain hands-on experience', 'Improve technical skills', 'Contribute to team success', 
        'Secure a job as', 'Build a solid foundation', 'Achieve certification', 'Enhance problem-solving skills', 
        'Expand knowledge', 'Complete internships', 'Develop leadership skills'
    ]

    # Extract Short-term Goals
    resume_data['shortTermGoals'] = match_and_append(file_content, short_term_goals)

    # List of long-term goals
    long_term_goals = [
        'Become a technical leader', 'Lead a team', 'Establish expertise', 'Achieve mastery', 
        'Innovate in', 'Start a technology company', 'Transition into a managerial role', 
        'Drive large-scale projects', 'Impact industry-wide practices', 'Pursue research and development'
    ]

    # Extract Long-term Goals
    resume_data['longTermGoals'] = match_and_append(file_content, long_term_goals)

    # Extract LinkedIn URL
    linkedin = re.search(r'https?://(www\.)?linkedin\.com/in/\S+', file_content)
    resume_data['linkedinUrl'] = linkedin.group(0) if linkedin else ""

    # Extract GitHub URL
    github = re.search(r'https?://github\.com/\S+', file_content)
    resume_data['githubUrl'] = github.group(0) if github else ""
    
    # Extract Portfolio URL
    portfolio = re.search(r'https?://\S+netlify\.app', file_content)
    resume_data['portfolioUrl'] = portfolio.group(0) if portfolio else ""

    return jsonify(resume_data)

@app.route('/generate-roadmap', methods=['POST'])
def generate_roadmap():
    data = request.get_json()
    technology = data['technology']
    print(technology)

    prompt = f"""Generate a detailed, structured, and complete roadmap for learning {technology}. The roadmap should be broken down into key learning phases or milestones (nodes), with each phase containing one or more subtopics (subnodes). For each phase, provide:

    A title representing the main learning stage or milestone.
    A description explaining the content or goal of that phase.
    A list of subnodes, if applicable, where each subnode should have:
    A title for the subtopic.
    A brief description and if possible reference links.
    Further subnodes if necessary.
    The response should be in a JSON format, with a structure that clearly outlines each node and subnode. Use the following structure as a guide:

    {{
        'node_1': {{
            'title': 'Introduction to {technology}',
            'description': 'Learn the basics and setup for {technology}.',
            'subnodes': [
                {{
                    'title': 'Topic 1',
                    'description': 'Explanation of topic 1.',
                    'subnodes': ['Something here', ''something]
                }},
                ...
            ]
        }},
        'node_2': {{
            'title': 'Next Phase',
            'description': 'Intermediate-level learning.',
            'subnodes': ['something', something]
        }},
        ...
    }}

Ensure the roadmap covers foundational to advanced topics, and each phase transitions logically to the next. Aim for clarity and brevity.

also give subnodes in subnodes where ever possible. pls don't keep it empty where ever possible
    """

    response = model.generate_content(prompt)
    cleaned_response=response.text.replace("```json","").replace("```","").strip()
    print(cleaned_response)
    try:
        json_response = json.loads(cleaned_response)
        print(json_response)  # This will print the parsed JSON in the console
        return jsonify(json_response)  # Send the valid JSON response
    except json.JSONDecodeError as e:
        return jsonify({"error": "Invalid JSON response", "details": str(e)}), 400

@app.route('/upload', methods=["POST"])
def evaluate_pdf():
    file = request.files.get('pdfFile')
    if file and file.filename.endswith('.pdf'):
        try:
            # Create a temporary file
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)
            pdf_file_path=file_path
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
                with open(pdf_file_path, 'rb') as original_file:
                    temp_file.write(original_file.read())

                context_template = """
                Please evaluate this PDF resume file. Analyze it comprehensively from multiple perspectives, including structure, clarity, content quality, relevance, technical skills, and conciseness.
                Provide an overall score out of 100 and suggest areas for improvement (bullet points) 
                also complusorily give the response in json format only.
                score: string, suggestion: string also dont include any \n   symbols in the response.
                """

                pdf = ai.upload_file(temp_file.name)
                response = model.generate_content([context_template, pdf])

                # Step 1: Remove the newline characters (\n) and extra backslashes
                cleaned_text = re.sub(r'\\n', '', response.text)  # Removes \n
                cleaned_text = re.sub(r'\\"', '"', cleaned_text)  # Fix escaped quotes (\")
                cleaned_text = cleaned_text.strip('"')  # Remove surrounding quotes
                print(cleaned_text)

            # Clean up the temporary file
            os.remove(temp_file.name)
            json_data=cleaned_text.replace("```json","").replace("```","").strip()
            return json_data

        except Exception as e:
            return f"An error occurred: {str(e)}"

    return "No file or invalid file format."

db = firestore.client()
def get_career_document(id):
    # Reference to the document
    doc_ref = db.collection('Career').document(str(id))
    
    # Fetch the document
    doc = doc_ref.get()

    if doc.exists:
        print("Document data:", doc.to_dict())
        return doc.to_dict()  # Print the document data
    else:
        print("No such document!")
# Load datasets
students_df = pd.read_csv("datasets/student_data.csv")
courses_df = pd.read_csv("datasets/courses.csv")

# Create 'Profile' column for students
students_df['Profile'] = (
    students_df['Interested Domain'] + " " +
    students_df['Projects'] + " " +
    students_df['Future Career'] + " " +
    students_df['experience'].astype(str) + " " +
    students_df['certifications'].astype(str) + " " +
    students_df['technicalSkills'].astype(str)
)

students_df.drop(columns=["Python", "SQL", "Java"], axis=1, inplace=True)

# Create 'course_info' column for courses
courses_df["course_info"] = (
    courses_df['Name'] + " " +
    courses_df['about'] + " " +
    courses_df['course_description'].fillna('')
)

# Vectorize both student profiles and courses
tfidf_vectorizer = TfidfVectorizer(stop_words='english')
combined_data = pd.concat([students_df['Profile'], courses_df['course_info']], ignore_index=True)
combined_data = combined_data.fillna("")
tfidf_vectorizer.fit(combined_data)

student_profiles_tfidf = tfidf_vectorizer.transform(students_df['Profile'])
courses_df = courses_df.fillna("")
courses_tfidf = tfidf_vectorizer.transform(courses_df['course_info'])

# Cosine similarity between student profiles and courses
similarity_matrix = cosine_similarity(student_profiles_tfidf, courses_tfidf)

# Recommend courses based on the profile text (not student ID)
def recommend_courses_by_profile(user_profile, top_n=10):
    # Transform the input profile into TF-IDF
    user_profile_tfidf = tfidf_vectorizer.transform([user_profile])
    
    # Compute similarity between the input profile and all courses
    similarity_scores = cosine_similarity(user_profile_tfidf, courses_tfidf).flatten()
    
    # Get top course recommendations based on similarity scores
    top_courses_idx = similarity_scores.argsort()[-top_n:][::-1]  # Sort in descending order
    recommended_courses = []
    
    for idx in top_courses_idx:
        if 0 <= idx < len(courses_df):  # Ensure the index is valid
            row = courses_df.iloc[idx]
            course_info = {
                "course_id": int(row['course_id']) if 'course_id' in row else 'Unknown',
                "course_name": row['Name'] if 'Name' in row else 'Unknown',
                "level": row['level'] if 'level' in row else 'Unknown',
                "link": row['link'] if 'link' in row else 'Unknown',
                "about": row['about'] if 'about' in row else 'Unknown',
                "provider": row['University'] if 'University' in row else 'Unknown'
            }
            recommended_courses.append(course_info)
        else:
            print(f"Index {idx} is out of bounds for courses_df")
    
    return recommended_courses



def send_email(recommendation,user_email):
    # Debugging: Check the input data
    

    # Email details
    sender_email = 'ey.hackathon24@gmail.com'
    sender_password = 'ehrb phzv dwrs mopq'  # Make sure to store this securely
    subject = 'Personalized Recommendations for Your Profile'

    # Email body with HTML content using a modern card design
    try:
        card_template = ""
        for course in recommendation[:3]:  # Limit to 3 courses for the email
            card_template += f'''
            <div style="border: 1px solid #ddd; border-radius: 8px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); margin: 16px 0; padding: 16px; background-color: #fff;">
                <h2 style="margin: 0; font-size: 1.5em; color: #333;">{course["course_name"]}</h2>
                <p style="margin: 8px 0; font-size: 1em; color: #666;"><strong>Level:</strong> {course["level"]}</p>
                <p style="margin: 8px 0; font-size: 1em; color: #666;"><strong>Provider:</strong> {course["provider"]}</p>
                <p style="margin: 8px 0; font-size: 0.95em; line-height: 1.5; color: #555;">{course["about"]}</p>
                <a href="{course["link"]}" style="display: inline-block; margin-top: 12px; padding: 10px 16px; color: #fff; background-color: #007bff; text-decoration: none; border-radius: 5px; font-size: 1em;">Start Learning Now</a>
            </div>
            '''

        message = f'''
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0;">
            <div style="max-width: 600px; margin: 0 auto; padding: 16px; background-color: #f9f9f9; border: 1px solid #ddd; border-radius: 8px;">
                <h1 style="text-align: center; color: #007bff;">Recommended Courses for You</h1>
                <p style="text-align: center; font-size: 1.1em;">We’ve handpicked courses tailored to your profile. Explore them below:</p>
                {card_template}
                <p style="text-align: center; margin-top: 24px; font-size: 1em; color: #666;">
                    Each course is designed to offer practical knowledge and real-world insights. Don’t miss out on these opportunities!
                </p>
                <p style="text-align: center; font-size: 1em; margin-top: 16px; color: #555;">Happy Learning,<br><strong>Team Opportune</strong></p>
            </div>
        </body>
        </html>
        '''
    except IndexError:
        print("The recommendation list has fewer than 3 courses.")
        return

    try:
        # Setting up SMTP server
        smtp_server = smtplib.SMTP('smtp.gmail.com', 587)
        smtp_server.starttls()
        smtp_server.login(sender_email, sender_password)

        # Create the email message
        email_message = MIMEMultipart()
        email_message['From'] = sender_email
        email_message['To'] = user_email
        email_message['Subject'] = subject

        # Attach the HTML message
        email_message.attach(MIMEText(message, 'html'))  # Use 'html' for HTML content

        # Send the email
        smtp_server.send_message(email_message)
        smtp_server.quit()

        print("Email sent successfully.")

    except Exception as e:
        print(f"Failed to send email. Error: {str(e)}")




# Flask endpoint for recommendations
@app.route('/recommend', methods=['POST', 'GET'])
def recommend():
    data = request.json
    user_profile = data.get('profile')
    user_email = data.get('email')

    # Check if profile data is provided
    if not user_profile:
        return jsonify({"error": "Profile data is required"}), 400

    # Ensure user_profile is a string
    if isinstance(user_profile, dict):
        # Convert the dictionary to a string (e.g., JSON string or concatenated values)
        user_profile = " ".join(f"{key}: {value}" for key, value in user_profile.items())
    elif not isinstance(user_profile, str):
        return jsonify({"error": "Profile data must be a string or dictionary"}), 400

    # Ensure user_email is a string
    if isinstance(user_email, dict):
        user_email = user_email.get('email')  # Extract email if it's nested in a dictionary

    try:
        # Get recommended courses
        recommended_courses = recommend_courses_by_profile(user_profile)

        # Send email if user_email is provided
        if user_email:
            if isinstance(user_email, str):
                print("User Email:", user_email)
                send_email(recommended_courses, user_email)
            else:
                print("Invalid email format. Skipping email notification.")
        else:
            print("User Email not provided. Skipping email notification.")

        # Return recommendations
        return jsonify({"recommended_courses": recommended_courses}), 200
    except Exception as e:
        # Handle unexpected errors
        return jsonify({"error": str(e)}), 500




# Load ratings matrix with course IDs as columns
ratings_df = pd.read_csv("datasets/ratings_matrix.csv")

# Load courses and create a mapping of course names to IDs
# Load courses and create a mapping of course names to IDs
courses_df = pd.read_csv("datasets/courses.csv")  # Ensure this path is correct
course_id_mapping = pd.Series(courses_df['course_id'].values, index=courses_df['Name']).to_dict()
def get_jaccard_similarity(ratings_df):
    num_students = len(ratings_df)
    similarity_matrix = pd.DataFrame(index=ratings_df['Student ID'], columns=ratings_df['Student ID'])

    for i in range(num_students):
        set_i = set(ratings_df.columns[1:][ratings_df.iloc[i, 1:] > 0])
        for j in range(num_students):
            set_j = set(ratings_df.columns[1:][ratings_df.iloc[j, 1:] > 0])
            similarity = jaccard_similarity(set_i, set_j)
            similarity_matrix.iloc[i, j] = similarity

    similarity_matrix = similarity_matrix.astype(float)
    return similarity_matrix

def jaccard_similarity(set1, set2):
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    return intersection / union if union != 0 else 0

# Recommend courses for a new user based on similar users
# Recommend courses for a new user based on similar users
def recommend_courses_for_new_user(new_user_profile, ratings_df, num_recommendations=3, top_similar=10):
    # Create a new similarity matrix including the new user profile
    similarity_matrix = get_jaccard_similarity(ratings_df)

    # Convert new user profile to a set (e.g., their rated courses)
    new_user_courses = set(new_user_profile)
    
    # Find similarity of new user with all other students
    similarities = []
    for i in range(len(ratings_df)):
        student_courses = set(ratings_df.columns[1:][ratings_df.iloc[i, 1:] > 0])
        similarity = jaccard_similarity(new_user_courses, student_courses)
        similarities.append((ratings_df.iloc[i]['Student ID'], similarity))
    
    # Sort students by similarity to the new user
    sorted_similarities = sorted(similarities, key=lambda x: x[1], reverse=True)
    similar_students = [student for student, _ in sorted_similarities[:top_similar]]
    
    # Find courses that similar students have rated highly but the new user hasn't rated yet
    new_user_course_set = set(new_user_profile)
    recommended_courses = []
    
    for student_id in similar_students:
        student_ratings = ratings_df.loc[ratings_df['Student ID'] == student_id].iloc[:, 1:]
        student_courses = set(student_ratings.columns[student_ratings.values[0] > 0].tolist())
        
        # Get courses rated by similar students but not yet by the new user
        recommendations = student_courses - new_user_course_set
        recommended_courses.extend(recommendations)
        
        if len(recommended_courses) >= num_recommendations:
            break

    # Return detailed course information instead of just IDs
    recommended_course_info = []
    for course in list(set(recommended_courses))[:num_recommendations]:  # Convert set to list here
        if course in course_id_mapping:
            course_details = courses_df[courses_df['Name'] == course].iloc[0]
            recommended_course_info.append({
                "course_name": course_details['Name'],
                "level": course_details['level'],
                "link": course_details['link'],
                "about": course_details['about']
            })
    email=send_email(recommended_course_info)
    if email:
        print("Email sent")
    return recommended_course_info


# Flask endpoint for recommendations
@app.route('/jaccard-recommend', methods=['POST'])
def jaccard_recommend():
    data = request.json
    new_user_profile = data.get('profile')

    if not new_user_profile:
        return jsonify({"error": "Profile data is required"}), 400

    recommended_courses = recommend_courses_for_new_user(new_user_profile, ratings_df)

    return jsonify({"recommended_courses": recommended_courses}), 200


@app.route('/search-events', methods=['GET'])
def search_events():
    # Extract query parameters from the request
    query = request.args.get('query', 'Hackathons in India')  # Default query: 'Hackathon'
    date = request.args.get('date', 'any')          # Default date: 'any'
    is_virtual = request.args.get('is_virtual', 'false')  # Default: 'false'
    start = request.args.get('start', '0')          # Default start index: 0

    # API URL and headers
    url = "https://real-time-events-search.p.rapidapi.com/search-events"
    headers = {
        "x-rapidapi-key": "31f9f38f67msh61dc71a007fa815p1d2c63jsnf6de091561b4",
        "x-rapidapi-host": "real-time-events-search.p.rapidapi.com"
    }
    
    # Request parameters
    querystring = {
        "query": query,
        "date": date,
        "is_virtual": is_virtual,
        "start": start
    }
    
    # Send the GET request to the external API
    response = requests.get(url, headers=headers, params=querystring)

    # Check if the request was successful
    if response.status_code == 200:
        events = response.json().get('data', [])
        event_list = []

        # Loop through each event and extract the required fields
        for event in events:
            event_info = {
                'event_name': event.get('name', 'N/A'),
                'link': event.get('link', 'N/A'),
                'venue': event.get('venue', {}).get('name', 'N/A'),
                'publisher': event.get('publisher', 'N/A'),
                'start_time': event.get('start_time', 'N/A'),
                'end_time': event.get('end_time', 'N/A'),
                'description': event.get('description', 'N/A')
            }
            event_list.append(event_info)

        # Return the event list as JSON response
        return jsonify({"event_list": event_list}), 200

    else:
        return jsonify({"error": f"Failed to fetch data. Status code: {response.status_code}"}), response.status_code

@app.route("/getCareerRecommendation", methods=['GET', 'POST'])
def get_career_recommendation():
    with open('model.pkl', 'rb') as file:
        mlp_classifier= pickle.load(file)
    json_data = request.get_json()
    feature = json_data['list']
    feature = feature.split(",")
    def preprocess_user_input(user_input):
        user_input_encoded = [1 if answer.lower() == 'yes' else 0 for answer in user_input]
        return np.array(user_input_encoded).reshape(1, -1)
    
    ans = mlp_classifier.predict(preprocess_user_input(feature))
    response = {'prediction': ans.tolist()}
    return get_career_document(response['prediction'][0])


@app.route("/test", methods=['POST'])
def generate_course_qna():
    request_data = request.json  # Renamed to avoid overwriting `response`
    course_title = request_data.get('title')
    course_link = request_data.get('link')

    # Ensure the course title and link are provided
    if not course_title or not course_link:
        return jsonify({"error": "Missing course title or link"}), 400

    prompt_template = (
        "You are an expert teacher designing a short knowledge test for students who have completed a course. "
        "Below is the course title available on edX and its link: "
        "The course title is '{title}', and it is available at {link}. "
        "Generate a set of ten concise questions and their answers to test the student's understanding. "
        "Each question should have four options (labeled A, B, C, D), and one correct answer. "
        "Provide the output in JSON format containing four fields: "
        "1. 'index' (question number), 2. 'question' (the text of the question), 3. 'options' (a list of four options), 4. 'answer' (the correct option)."
    )
    prompt = prompt_template.format(title=course_title, link=course_link)

    try:
        # Call the model to generate the content
        model_response = model.generate_content(prompt)
        response_text = model_response.text.strip()

        # Try to parse the response as JSON
        response_text = response_text.replace("```json", "").replace("```", "").strip()
        generated_content = json.loads(response_text)

        # Log the generated content for debugging
        print(generated_content)

        return jsonify(generated_content)  # Return the quiz questions as a JSON response

    except json.JSONDecodeError:
        # If JSON parsing fails, return a detailed error message
        return jsonify({"error": "Failed to parse JSON response from the model.", "raw_response": response_text}), 500

    except Exception as e:
        # Catch any other unexpected errors
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


DATABASE = 'my_database.db'


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
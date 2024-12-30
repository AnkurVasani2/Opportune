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



app = Flask(__name__)
CORS(app)
cred = credentials.Certificate("service.json")
firebase_admin.initialize_app(cred)

ai.configure(api_key="AIzaSyDxCKDfWCsFlVgswz7xd6PV-6_rTXbllmo")
model = ai.GenerativeModel("gemini-1.5-flash")
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
from speech_handler import process_speech_and_chat

@app.route('/speech', methods=['POST'])
def speech_route():
    user_id = request.form.get('user_id', 'default_user')
    if 'audio' not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    audio_file = request.files['audio']
    interview_type=request.form.get('interview_type')
    result = process_speech_and_chat(user_id,audio_file,interview_type)

    if result:
        print(result)
        return jsonify(result), 200
    else:
        return jsonify({"error": "Processing failed"}), 500


@app.route('/job', methods=['GET'])
def search_jobs():
    try:
        # Get query parameters from the request
        # Remove any extra quotation marks that might be in the request args
        query = request.args.get('query', '').strip('"')
        location = request.args.get('location', '').strip('"')
        distance = request.args.get('distance', '1.0').strip('"')
        language = request.args.get('language', 'en_GB').strip('"')
        remote_only = request.args.get('remoteOnly', 'false').strip('"').lower() == 'true'
        date_posted = request.args.get('datePosted', 'month').strip('"')
        employment_types = request.args.get('employmentTypes', 'fulltime').strip('"')

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

        return jsonify({"message": "Success", "results": job_results}), 200

    except Exception as e:
        print(f"Error in search_jobs: {str(e)}")
        return jsonify({"error": "An unexpected error occurred while processing your request."}), 500

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
        response = requests.get(url, params=querystring, headers=headers )
        print(f"API request URL: {response.url}")  # Debug logging
        print(f"API response status code: {response.status_code}")  # Debug logging
        
        if response.status_code == 200:
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
    """
    Simplifies the JSON output of the API response.

    Args:
    - api_response: The original JSON response from the API.
    - keyword: The search keyword to be associated with each result.

    Returns:
    - A simplified list of job details.
    """
    simplified_jobs = []
    jobs = api_response.get('jobs', [])

    for job in jobs:
        # Ensure job is a dictionary
        if isinstance(job, dict):
            # Check if 'company' is a dictionary before trying to access its properties
            if isinstance(job, dict):
            # Check if 'company' is a dictionary or string
                company_info = job.get('company', {})
            if isinstance(company_info, dict):
                company = company_info.get('name', 'N/A')
            elif isinstance(company_info, str):
                company = company_info
            else:
                company = 'N/A'
            date_posted = job.get('datePosted', 'N/A')
            employment_type = job.get('employmentType', 'N/A')

            job_providers = job.get('jobProviders', [])
            job_url = job_providers[0].get('url') if job_providers and isinstance(job_providers[0], dict) else 'N/A'

            simplified_job = {
                "Keyword Matched": keyword,
                "Company": company,
                "Date Posted": date_posted,
                "Employment Type": employment_type,
                "First Job Provider URL": job_url
            }

            simplified_jobs.append(simplified_job)
        else:
            # Handle cases where 'job' is not a dictionary (log or handle as needed)
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

    file_content = ""
    for page_num in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[page_num]
        file_content += page.extract_text()

    if not file_content.strip():
        return jsonify({"error": "PDF content is empty"}), 400

    print(file_content)  # Debugging log

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

import tempfile
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
                Provide an overall score out of 100 and suggest areas for improvement 
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
def recommend_courses_by_profile(user_profile, top_n=3):
    # Transform the input profile into TF-IDF
    user_profile_tfidf = tfidf_vectorizer.transform([user_profile])
    
    # Compute similarity between the input profile and all courses
    similarity_scores = cosine_similarity(user_profile_tfidf, courses_tfidf).flatten()
    
    # Get top course recommendations based on similarity scores
    top_courses_idx = similarity_scores.argsort()[-top_n:][::-1]  # Sort in descending order
    recommended_courses = []
    for idx in top_courses_idx:
        course_info = {
            "course_name": courses_df.iloc[idx]['Name'],
            "level": courses_df.iloc[idx]['level'],
            "link": courses_df.iloc[idx]['link'],
            "about": courses_df.iloc[idx]['about']
        }
        recommended_courses.append(course_info)
    
    return recommended_courses
def send_email(recommendation):
    # Define the JSON object you want to send
    json_data = recommendation

    # Check if recommended_courses exists and has at least 3 courses
    if "recommended_courses" not in json_data or len(json_data["recommended_courses"]) < 3:
        print("Error: Recommended courses data is missing or incomplete.")
        return

    # Email details
    sender_email = 'ankurvasani2585@gmail.com'
    sender_password = 'mmwk gxbf otkm hcjf'  # Make sure to store this securely
    subject = 'Personalized Recommendation for your Profile'

    # Email body with HTML content
    message = f'''
    <html>
    <body>
    <p>Hi there,</p>
    <p>We have handpicked a few exciting courses to help you level up your skills and explore new opportunities. Whether you’re looking to dive deeper into marketing analytics, electronics, or cybersecurity, these courses will guide you to success!</p>
    <hr>
    <p><b>1. {json_data["recommended_courses"][0]["course_name"]}</b> ({json_data["recommended_courses"][0]["level"]})<br>
    <i>{json_data["recommended_courses"][0]["about"]}</i><br>
    <a href="{json_data["recommended_courses"][0]["link"]}">Start Learning Now</a></p>
    <hr>
    <p><b>2. {json_data["recommended_courses"][1]["course_name"]}</b> ({json_data["recommended_courses"][1]["level"]})<br>
    <i>{json_data["recommended_courses"][1]["about"]}</i><br>
    <a href="{json_data["recommended_courses"][1]["link"]}">Start Learning Now</a></p>
    <hr>
    <p><b>3. {json_data["recommended_courses"][2]["course_name"]}</b> ({json_data["recommended_courses"][2]["level"]})<br>
    <i>{json_data["recommended_courses"][2]["about"]}</i><br>
    <a href="{json_data["recommended_courses"][2]["link"]}">Start Learning Now</a></p>
    <hr>
    <p>Each course has been designed to offer practical knowledge and real-world insights. Don’t miss out on the opportunity to advance your expertise and unlock new possibilities!</p>
    <p>Happy Learning,<br>Team Opportune</p>
    </body>
    </html>
    '''

    try:
        # Setting up SMTP server
        smtp_server = smtplib.SMTP('smtp.gmail.com', 587)
        smtp_server.starttls()
        smtp_server.login(sender_email, sender_password)

        # Create the email message
        email_message = MIMEMultipart()
        email_message['From'] = sender_email
        email_message['To'] = "chintan222005@gmail.com"
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
@app.route('/recommend', methods=['POST','GET'])
def recommend():
    data = request.json
    user_profile = data.get('profile')
    
    if not user_profile:
        return jsonify({"error": "Profile data is required"}), 400
    
    recommended_courses = recommend_courses_by_profile(user_profile)
    send_email(recommended_courses)
    return jsonify({"recommended_courses": recommended_courses}), 200

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
                'venue': event.get('venue', {}).get('google_location', 'N/A'),
                'publisher': event.get('publisher', 'N/A'),
                'info_links': event.get('info_links', [{'link': 'N/A'}])[0].get('link', 'N/A'),
                'start_time': event.get('start_time', 'N/A'),
                'end_time': event.get('end_time', 'N/A'),
                'description': event.get('description', 'N/A')
            }
            event_list.append(event_info)

        # Return the event list as JSON response
        return jsonify(event_list)

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


if __name__ == '__main__':
    app.run(debug=True)
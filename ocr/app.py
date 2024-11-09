from flask import Flask, request, jsonify
from flask_cors import CORS
import PyPDF2
import spacy
import re

app = Flask(__name__)
CORS(app)

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

if __name__ == '__main__':
    app.run(debug=False, port=5000)

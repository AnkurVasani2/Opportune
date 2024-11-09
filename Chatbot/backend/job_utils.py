import requests
from flask import request, jsonify

# Function to search jobs for a single skill
def search_jobs_for_skill(skill, location, distance, language, remote_only, date_posted, employment_types):
    url = "https://jobs-api14.p.rapidapi.com/list"
    headers = {
        "X-RapidAPI-Key": "38682d92cbmshec1211307e44631p118ba4jsna6ed84946bf9",  # Replace with your actual API key
        "X-RapidAPI-Host": "jobs-api14.p.rapidapi.com"
    }

    # Construct the query string
    querystring = {
        "query": skill,
        "location": location,
        "distance": distance,
        "language": language,
        "remoteOnly": remote_only,
        "datePosted": date_posted,
        "employmentTypes": employment_types,
        "index": "0"
    }

    try:
        response = requests.get(url, headers=headers, params=querystring)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Failed to fetch job listings for {skill}."}
    except Exception as e:
        return {"error": f"Exception occurred for {skill}: {str(e)}"}

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
def search_jobs():
    # Get query parameters from the request
    query = request.args.get('query', '')  # Expecting something like "software engineer, python"
    location = request.args.get('location', '')
    distance = request.args.get('distance', '1.0')
    language = request.args.get('language', 'en_GB')
    remote_only = request.args.get('remoteOnly', 'false')
    date_posted = request.args.get('datePosted', 'month')
    employment_types = request.args.get('employmentTypes', 'fulltime;parttime;intern;contractor')

    # Split the query into two skills
    skills = [skill.strip() for skill in query.split(',') if skill.strip()]

    if not skills:
        return jsonify({"error": "No skills provided."}), 400

    # Collect the results for the two domains (limited to 2 skills)
    job_results = []
    for skill in skills[:2]:  # Limit to 2 skills
        api_response = search_jobs_for_skill(skill, location, distance, language, remote_only, date_posted, employment_types)
        if isinstance(api_response, dict) and 'jobs' in api_response:  # Proceed if valid jobs were fetched
            simplified_results = simplify_job_results(api_response, skill)
            job_results.extend(simplified_results)

    # Combine the results and return
    return jsonify(job_results)

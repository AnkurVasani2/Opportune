from flask import Flask, request, jsonify
import google.generativeai as ai
from flask_cors import CORS
import json

app = Flask(__name__)
ai.configure(api_key="AIzaSyDgd78YM6QJxFCqtpvn7DoHcg0GJMsmDVA")
model = ai.GenerativeModel("gemini-1.5-flash")
CORS(app)
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
    A brief description.
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

if __name__ == '__main__':
    app.run(debug=False, port=5000)

import tempfile
import os
import google.generativeai as ai
import json
from flask import Flask, request


app = Flask(__name__)
ai.configure(api_key="AIzaSyBp67iPLnpqrIuDdTdhdozj4tmtSL9IEMs")
model = ai.GenerativeModel("gemini-1.5-flash")
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/upload', methods=["POST"])
def evaluate_pdf():
    file = request.files.get('pdfFile')
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    pdf_file_path=file_path
    if os.path.exists(pdf_file_path) and pdf_file_path.endswith('.pdf'):
        try:
            # Create a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
                with open(pdf_file_path, 'rb') as original_file:
                    temp_file.write(original_file.read())

                context_template = """
                Please evaluate this PDF resume file. Analyze it comprehensively from multiple perspectives, including structure, clarity, content quality, relevance, technical skills, and conciseness.
                Provide an overall score out of 100 and suggest areas for improvement.
                """

                pdf = ai.upload_file(temp_file.name)
                response = model.generate_content([context_template, pdf])

            # Clean up the temporary file
            os.remove(temp_file.name)

            return response.text

        except Exception as e:
            return f"An error occurred: {str(e)}"

    return "No file or invalid file format."

if __name__ == "__main__":
    app.run(debug=False, port=5000)

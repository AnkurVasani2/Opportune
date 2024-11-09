from flask import Flask, request, jsonify
from speech_handler import process_speech_and_chat
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/speech', methods=['POST'])
def speech_route():
    user_id = request.form.get('user_id', 'default_user')
    if 'audio' not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    audio_file = request.files['audio']
    interview_type=request.form.get('interview_type')
    result = process_speech_and_chat(user_id,audio_file,interview_type)

    if result:
        print(jsonify(result))
        return jsonify(result), 200
    else:
        return jsonify({"error": "Processing failed"}), 500


if __name__ == '__main__':
    app.run(debug=True)
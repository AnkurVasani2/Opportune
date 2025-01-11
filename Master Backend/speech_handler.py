from groq import Groq
from conversation_memory import load_conversation_history, save_conversation_history, get_user_history, update_user_history

# Initialize Groq client
client = Groq(api_key="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")

# Initialize conversation history
conversation_history = []

def transcribe_audio(audio_file):
    """
    Transcribe audio using Groq's Whisper implementation directly from a .wav file.
    """
    try:
        transcription = client.audio.transcriptions.create(
            file=("audio.wav", audio_file.read()),
            model="whisper-large-v3",
            prompt="You are an AI interviewer conducting mock interviews.",
            response_format="text",
            language="en",
        )
        return transcription
    except Exception as e:
        print(f"An error occurred during transcription: {str(e)}")
        return None

def query_groq_api(input_text, conversation_history,interview_type):
    skills = interview_type
    
    # Add user input to the conversation history
    conversation_history.append({"role": "user", "content": input_text})
    
    # System role with context
    messages = [
        {"role": "system", "content": f"""You are an AI interviewer. Ask questions and adapt based on the answers. 
        The interviewee is applying for a role requiring the following skills: {skills}.
        Avoid discussing other topics politely. But answer related queries. Also provide feedback on Provide constructive feedback after some questions.
        If the interviewee says i want to stop, generate and respond with a comprehensive report based upon the users previous responses that how prepred he is for that particular interview. give him the feeback and tell him where he can improve and the way for improvement"""}
    ] + conversation_history  # Append all conversations

    chat_completion = client.chat.completions.create(
        messages=messages,
        model="llama-3.1-8b-instant"
    )

    response = chat_completion.choices[0].message.content
    conversation_history.append({"role": "assistant", "content": response})
    
    return response

def process_transcript(user_id,transcript,interview_type):
    try:
        conversation_history = get_user_history(user_id)
        response = query_groq_api(transcript, conversation_history,interview_type)
        update_user_history(user_id, {"role": "user", "content": transcript})
        update_user_history(user_id, {"role": "assistant", "content": response})
        return response
    except Exception as e:
        print(f"Error processing transcript: {e}")
        return None

def process_speech_and_chat(user_id,audio_file,interview_type):
    transcription = transcribe_audio(audio_file)
    
    if transcription:
        chatbot_response = process_transcript(user_id,transcription,interview_type)
        

        if chatbot_response:
            print("hi ")
            return {
                "query": transcription,
                "response": chatbot_response,
                "history": get_user_history(user_id)
            }
    
    return None


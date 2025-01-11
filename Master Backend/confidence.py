import speech_recognition as sr
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline

def initialize_recognizer():
    """Initialize and return the speech recognizer."""
    return sr.Recognizer()

def adjust_microphone_noise(recognizer, source, duration=1):
    """Adjust the microphone for ambient noise."""
    print("Adjusting for ambient noise... Please wait.")
    recognizer.adjust_for_ambient_noise(source, duration=duration)
    print(f"Ambient noise adjusted. Energy threshold set to {recognizer.energy_threshold}.")

def capture_and_recognize(recognizer, source):
    # """Capture audio and recognize speech."""
    try:
        print("Listening... Speak now or say 'exit' to quit.")
        audio = recognizer.listen(source)
        text = recognizer.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        print("Sorry, I could not understand your speech. Please try again.")
    except sr.RequestError as e:
        print(f"Could not request results from the speech recognition service; {e}")
    return None

def analyze_sentiment(text, sentiment_analyzer):
    """Analyze sentiment of the given text using a pre-trained model."""
    results = sentiment_analyzer(text)
    # Extract label and score from the most likely result
    label = results[0]['label']
    score = results[0]['score']
    return label, score

def real_time_speech_to_text():
    """Main function to process real-time speech-to-text with sentiment analysis."""
    recognizer = initialize_recognizer()
    speech_list = []  # List to store recognized speech

    # Load a pre-trained sentiment analysis pipeline
    sentiment_analyzer = pipeline(
        "sentiment-analysis",
        model="cardiffnlp/twitter-roberta-base-sentiment",
        tokenizer="cardiffnlp/twitter-roberta-base-sentiment"
    )

    # Use the microphone as the audio source
    with sr.Microphone() as source:
        adjust_microphone_noise(recognizer, source)

        print("You can start speaking now. Say 'exit' to stop.")
        while True:
            text = capture_and_recognize(recognizer, source)
            if text:
                print(f"You said: {text}")
                # Exit the loop if the user says 'exit'
                if text.lower() == "exit":
                    print("Exiting speech-to-text. Goodbye!")
                    break
                
                # Add the recognized text to the list
                speech_list.append(text)

                # Analyze sentiment of the speech
                sentiment_label, sentiment_score = analyze_sentiment(text, sentiment_analyzer)

                if sentiment_label == "LABEL_2":
                    sentiment_label = "Positive"
                elif sentiment_label == "LABEL_0":
                    sentiment_label = "Negative"
                else:
                    sentiment_label = "Neutral"
                    
                print(f"Sentiment: {sentiment_label} (Score: {sentiment_score:.2f})")

    print("\nSummary of all recognized speech:")
    for idx, speech in enumerate(speech_list, 1):
        print(f"{idx}. {speech}")

if __name__ == "__main__":
    real_time_speech_to_text()

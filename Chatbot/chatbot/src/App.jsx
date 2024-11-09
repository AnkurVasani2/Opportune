import { useState, useRef, useEffect } from 'react';
import axios from 'axios'; // To send the recorded audio to the Flask server
import './App.css'; // Import CSS for styling
import ai from "../src/assets/ai.png";
import user from "../src/assets/user.png";

function App() {
  const [isRecording, setIsRecording] = useState(false);
  const [audioUrl, setAudioUrl] = useState(null);
  const [interviewType, setInterviewType] = useState('Python'); // Default interview type
  const [conversationHistory, setConversationHistory] = useState([]);
  const mediaRecorderRef = useRef(null);
  const audioChunks = useRef([]);
  const [userId, setUserId] = useState('');
  const apiEndpoint = 'https://meerkat-saving-seriously.ngrok-free.app/speech';
  const messageEndRef = useRef(null); // Ref for scrolling to the bottom

  // Text-to-speech function for assistant's responses
  const speakText = (text) => {
    if ('speechSynthesis' in window && text) {
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = 'en-US'; // Set language if needed
      window.speechSynthesis.speak(utterance);
    } else {
      console.error('SpeechSynthesis not supported or text is empty');
    }
  };

  // Start recording the audio
  const startRecording = async () => {
    if (!userId) {
      alert('Please enter a user ID before starting the interview.');
      return;
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorderRef.current = new MediaRecorder(stream);

      mediaRecorderRef.current.ondataavailable = (event) => {
        audioChunks.current.push(event.data);
      };

      mediaRecorderRef.current.onstop = () => {
        const audioBlob = new Blob(audioChunks.current, { type: 'audio/wav' });
        const url = URL.createObjectURL(audioBlob);
        setAudioUrl(url);
        audioChunks.current = [];
        // Send audio to Flask server
        sendAudioToServer(audioBlob);
      };

      mediaRecorderRef.current.start();
      setIsRecording(true);
    } catch (error) {
      console.error('Error accessing the microphone', error);
    }
  };

  // Stop recording the audio
  const stopRecording = () => {
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  // Send the recorded audio to the Flask server
  const sendAudioToServer = (audioBlob) => {
    const formData = new FormData();
    formData.append('audio', audioBlob, 'recording.wav');
    formData.append('user_id', userId); // Send the user ID along with the audio
    formData.append('interview_type', interviewType); // Send the interview type

    axios.post(apiEndpoint, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
      .then((response) => {
        // Print the received response to the console
        console.log('Received response from server:', response.data);

        // Update the conversation history
        updateConversation(response.data);
      })
      .catch((error) => {
        console.error('Error sending audio to server:', error);
      });
  };

  // Update conversation history with response from the server
  const updateConversation = (data) => {
    const updatedHistory = [...conversationHistory];

    // Only add new history items (avoid duplicates)
    const newHistory = data.history.filter(
      (newMessage) =>
        !updatedHistory.some(
          (oldMessage) => oldMessage.content === newMessage.content && oldMessage.role === newMessage.role
        )
    );

    // Update conversation history with only new messages
    setConversationHistory([...updatedHistory, ...newHistory]);

    // Speak the assistant's response (text-to-speech)
    newHistory.forEach((message) => {
      if (message.role === 'assistant') {
        speakText(message.content); // Convert assistant's response to speech
      }
    });
  };

  // Scroll to the bottom of the chat when new messages are added
  useEffect(() => {
    if (messageEndRef.current) {
      messageEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [conversationHistory]);

  return (
    <div className="chatbot-container">
      <div className="chatbot-header">
        <h1>{interviewType} Interview</h1>
      </div>

      <div className="interview-settings">
        <label htmlFor="userId">User ID:</label>
        <input
          type="text"
          id="userId"
          value={userId}
          onChange={(e) => setUserId(e.target.value)}
          placeholder="Enter User ID"
        />

        <label htmlFor="interviewType">Interview Type:</label>
        <select
          id="interviewType"
          value={interviewType}
          onChange={(e) => setInterviewType(e.target.value)}
        >
          <option value="Python">Python</option>
          <option value="JavaScript">JavaScript</option>
          <option value="React">React</option>
          <option value="Node">Node</option>
          <option value="Flask">Flask</option>
        </select>
      </div>

      <div className="chatbot-message-container">
        {conversationHistory.map((message, index) => (
          <div key={index} className={`chatbot-message ${message.role}`}>
            {message.role === 'assistant' ? (
              <>
                <img src={ai} alt="AI Icon" className="assistant-icon" />
                <span>{message.content}</span>
              </>
            ) : (
              <>
                <span>{message.content}</span>
                <img src={user} alt="User Icon" className="user-icon" />
              </>
            )}
          </div>
        ))}
        <div ref={messageEndRef} />
      </div>

      <button className="record-button" onClick={isRecording ? stopRecording : startRecording}>
        {isRecording ? 'Stop Talking' : 'Start Talking'}
      </button>

    </div>
  );
}

export default App;

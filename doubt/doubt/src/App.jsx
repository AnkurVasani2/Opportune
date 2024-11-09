import { useState, useRef, useEffect } from 'react';
import axios from 'axios'; // To send the recorded audio to the Flask server
import './App.css'; // Import CSS for styling
import ai from "../src/assets/ai.png";
import user from "../src/assets/user.png";

function App() {
  const [conversationHistory, setConversationHistory] = useState([]);
  const [userInput, setUserInput] = useState(''); // Add state for user input
  const [userId, setUserId] = useState('');
  const apiEndpoint = 'https://meerkat-saving-seriously.ngrok-free.app/doubt';
  const messageEndRef = useRef(null); // Ref for scrolling to the bottom

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!userInput.trim()) return; // Ignore empty input

    setConversationHistory((prevHistory) => [
      ...prevHistory,
      { role: 'user', content: userInput },
    ]);

    try {
      const response = await axios.post(apiEndpoint, {
        text: userInput,
        user_id: userId,
      });

      updateConversation(response.data);
    } catch (error) {
      console.error('Error sending text to server:', error);
    }

    setUserInput(''); // Clear input field after submission
  };

  const updateConversation = (data) => {
    const updatedHistory = [...conversationHistory];

    const newHistory = data.history.filter(
      (newMessage) =>
        !updatedHistory.some(
          (oldMessage) =>
            oldMessage.content === newMessage.content && oldMessage.role === newMessage.role
        )
    );

    // Update conversation history with only new messages
    setConversationHistory([...updatedHistory, ...newHistory]);
  };

  // Scroll to the bottom of the chat when new messages are added
  useEffect(() => {
    if (messageEndRef.current) {
      messageEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [conversationHistory]);

  return (
    <div className="text-chatbot-container">
      <label htmlFor="userId">User ID:</label>
      <input
        type="text"
        id="userId"
        value={userId}
        onChange={(e) => setUserId(e.target.value)}
        placeholder="Enter User ID"
      />
      <div className="chatbot-header">
        <h1>General Doubt Solver</h1>
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

      <form className="text-input-form" onSubmit={handleSubmit}>
        <input
          type="text"
          value={userInput}
          onChange={(e) => setUserInput(e.target.value)}
          placeholder="Ask your question..."
          className="text-input-field"
        />
        <button type="submit" className="send-button">
          Send
        </button>
      </form>
    </div>
  );
}

export default App;

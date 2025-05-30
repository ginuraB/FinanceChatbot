import React, { useState } from 'react';
import axios from 'axios';

const ChatInterface = ({ userId }) => {
    const [message, setMessage] = useState('');
    const [chatHistory, setChatHistory] = useState([]);
    const [loading, setLoading] = useState(false);
    const API_BASE_URL = 'http://localhost:5000'; // Ensure this matches your backend URL

    const handleSendMessage = async () => {
        if (message.trim() === '') return;

        const userMessage = { sender: 'user', text: message };
        setChatHistory((prev) => [...prev, userMessage]);
        setMessage(''); // Clear input field
        setLoading(true);

        try {
            const response = await axios.post(`${API_BASE_URL}/chat`, {
                user_id: userId, // Pass the user ID to the backend
                message: message
            });
            const botMessage = { sender: 'bot', text: response.data.response };
            setChatHistory((prev) => [...prev, botMessage]);
        } catch (error) {
            console.error('Error sending message to chatbot:', error);
            const errorMessage = { sender: 'bot', text: `Error: ${error.response?.data?.error || error.message}. Please try again.` };
            setChatHistory((prev) => [...prev, errorMessage]);
        } finally {
            setLoading(false);
        }
    };

    const handleKeyPress = (e) => {
        if (e.key === 'Enter') {
            handleSendMessage();
        }
    };

    return (
        <div style={{ border: '1px solid #ccc', padding: '10px', display: 'flex', flexDirection: 'column', height: '400px' }}>
            <h2>Chat Interface (User ID: {userId})</h2>
            <div style={{ flexGrow: 1, overflowY: 'auto', marginBottom: '10px', border: '1px solid #eee', padding: '5px' }}>
                {chatHistory.map((msg, index) => (
                    <div key={index} style={{ textAlign: msg.sender === 'user' ? 'right' : 'left', margin: '5px 0' }}>
                        <span style={{
                            backgroundColor: msg.sender === 'user' ? '#dcf8c6' : '#e0e0e0',
                            padding: '8px 12px',
                            borderRadius: '15px',
                            display: 'inline-block',
                            maxWidth: '70%'
                        }}>
                            {msg.text}
                        </span>
                    </div>
                ))}
                {loading && (
                    <div style={{ textAlign: 'left', margin: '5px 0' }}>
                        <span style={{ backgroundColor: '#e0e0e0', padding: '8px 12px', borderRadius: '15px', display: 'inline-block', maxWidth: '70%' }}>
                            Typing...
                        </span>
                    </div>
                )}
            </div>
            <div style={{ display: 'flex' }}>
                <input
                    type="text"
                    placeholder="Type your message..."
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    onKeyPress={handleKeyPress}
                    style={{ flexGrow: 1, marginRight: '10px' }}
                    disabled={loading}
                />
                <button onClick={handleSendMessage} disabled={loading}>Send</button>
            </div>
        </div>
    );
};

export default ChatInterface;

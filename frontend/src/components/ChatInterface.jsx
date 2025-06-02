// import React, { useState } from 'react';
// import axios from 'axios';

// const ChatInterface = ({ userId }) => {
//     const [message, setMessage] = useState('');
//     const [chatHistory, setChatHistory] = useState([]);
//     const [loading, setLoading] = useState(false);
//     const API_BASE_URL = 'http://localhost:5000'; // Ensure this matches your backend URL

//     const handleSendMessage = async () => {
//         if (message.trim() === '') return;

//         const userMessage = { sender: 'user', text: message };
//         setChatHistory((prev) => [...prev, userMessage]);
//         setMessage(''); // Clear input field
//         setLoading(true);

//         try {
//             const response = await axios.post(`${API_BASE_URL}/chat`, {
//                 user_id: userId, // Pass the user ID to the backend
//                 message: message
//             });
//             const botMessage = { sender: 'bot', text: response.data.response };
//             setChatHistory((prev) => [...prev, botMessage]);
//         } catch (error) {
//             console.error('Error sending message to chatbot:', error);
//             const errorMessage = { sender: 'bot', text: `Error: ${error.response?.data?.error || error.message}. Please try again.` };
//             setChatHistory((prev) => [...prev, errorMessage]);
//         } finally {
//             setLoading(false);
//         }
//     };

//     const handleKeyPress = (e) => {
//         if (e.key === 'Enter') {
//             handleSendMessage();
//         }
//     };

//     return (
//         <div style={{ border: '1px solid #ccc', padding: '10px', display: 'flex', flexDirection: 'column', height: '400px' }}>
//             <h2>Chat Interface (User ID: {userId})</h2>
//             <div style={{ flexGrow: 1, overflowY: 'auto', marginBottom: '10px', border: '1px solid #eee', padding: '5px' }}>
//                 {chatHistory.map((msg, index) => (
//                     <div key={index} style={{ textAlign: msg.sender === 'user' ? 'right' : 'left', margin: '5px 0' }}>
//                         <span style={{
//                             backgroundColor: msg.sender === 'user' ? '#dcf8c6' : '#e0e0e0',
//                             padding: '8px 12px',
//                             borderRadius: '15px',
//                             display: 'inline-block',
//                             maxWidth: '70%'
//                         }}>
//                             {msg.text}
//                         </span>
//                     </div>
//                 ))}
//                 {loading && (
//                     <div style={{ textAlign: 'left', margin: '5px 0' }}>
//                         <span style={{ backgroundColor: '#e0e0e0', padding: '8px 12px', borderRadius: '15px', display: 'inline-block', maxWidth: '70%' }}>
//                             Typing...
//                         </span>
//                     </div>
//                 )}
//             </div>
//             <div style={{ display: 'flex' }}>
//                 <input
//                     type="text"
//                     placeholder="Type your message..."
//                     value={message}
//                     onChange={(e) => setMessage(e.target.value)}
//                     onKeyPress={handleKeyPress}
//                     style={{ flexGrow: 1, marginRight: '10px' }}
//                     disabled={loading}
//                 />
//                 <button onClick={handleSendMessage} disabled={loading}>Send</button>
//             </div>
//         </div>
//     );
// };

// export default ChatInterface;


















import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';

const ChatInterface = ({ userId }) => {
    const [message, setMessage] = useState('');
    const [chatHistory, setChatHistory] = useState([]);
    const [loading, setLoading] = useState(false);
    const API_BASE_URL = 'http://localhost:5000';
    const chatContainerRef = useRef(null); // Ref for the chat messages container

    // Effect to scroll to the bottom of the chat history whenever it updates
    useEffect(() => {
        if (chatContainerRef.current) {
            chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
        }
    }, [chatHistory]);

    const handleSendMessage = async () => {
        if (message.trim() === '') return;

        const userMessage = { sender: 'user', text: message };
        setChatHistory((prev) => [...prev, userMessage]); // Add user's message to history
        setMessage(''); // Clear input field
        setLoading(true); // Show loading indicator

        try {
            // Make API call to the backend chat endpoint
            const response = await axios.post(`${API_BASE_URL}/chat`, {
                user_id: userId, // Pass the user ID to the backend
                message: message
            });
            const botMessage = { sender: 'bot', text: response.data.response };
            setChatHistory((prev) => [...prev, botMessage]); // Add bot's response to history
        } catch (error) {
            console.error('Error sending message to chatbot:', error);
            const errorMessage = { sender: 'bot', text: `Error: ${error.response?.data?.error || error.message}. Please try again.` };
            setChatHistory((prev) => [...prev, errorMessage]); // Display error message in chat
        } finally {
            setLoading(false); // Hide loading indicator
        }
    };

    const handleKeyPress = (e) => {
        // Send message on Enter key press
        if (e.key === 'Enter') {
            handleSendMessage();
        }
    };

    return (
        <div style={{
            border: '1px solid #e0e0e0', // Light grey border
            borderRadius: '12px', // More rounded corners
            overflow: 'hidden',
            height: '550px', // Slightly increased height for better chat experience
            display: 'flex',
            flexDirection: 'column',
            boxShadow: '0 4px 12px rgba(0, 0, 0, 0.08)' // Subtle shadow for depth
        }}>
            {/* Chat Header */}
            <div style={{
                backgroundColor: '#f8f8f8', // Very light grey header
                padding: '15px',
                textAlign: 'center',
                fontWeight: 'bold',
                color: '#333', // Darker text for contrast
                borderBottom: '1px solid #e0e0e0'
            }}>
                Personal Finance Chatbot (User ID: {userId})
            </div>

            {/* Chat Messages Area */}
            <div ref={chatContainerRef} style={{
                flexGrow: 1,
                overflowY: 'auto',
                padding: '15px',
                backgroundColor: '#fdfdfd' // Almost white background for chat area
            }}>
                {chatHistory.map((msg, index) => (
                    <div key={index} style={{
                        textAlign: msg.sender === 'user' ? 'right' : 'left',
                        marginBottom: '10px',
                        display: 'flex',
                        justifyContent: msg.sender === 'user' ? 'flex-end' : 'flex-start'
                    }}>
                        <span style={{
                            backgroundColor: msg.sender === 'user' ? '#DCF8C6' : '#E8E8E8', // Light green for user, light grey for bot
                            padding: '10px 15px',
                            borderRadius: '20px', // More rounded for chat bubbles
                            maxWidth: '75%', // Limit bubble width
                            wordWrap: 'break-word', // Ensure long words wrap
                            color: '#333',
                            boxShadow: '0 1px 2px rgba(0, 0, 0, 0.1)' // Subtle shadow on bubbles
                        }}>
                            {msg.text}
                        </span>
                    </div>
                ))}
                {loading && (
                    <div style={{ textAlign: 'left', marginBottom: '10px' }}>
                        <span style={{
                            backgroundColor: '#E8E8E8',
                            padding: '10px 15px',
                            borderRadius: '20px',
                            display: 'inline-block',
                            maxWidth: '75%',
                            fontStyle: 'italic',
                            color: '#666' // Greyer text for "Typing..."
                        }}>
                            Typing...
                        </span>
                    </div>
                )}
            </div>

            {/* Chat Input Area */}
            <div style={{
                display: 'flex',
                padding: '15px',
                borderTop: '1px solid #e0e0e0',
                backgroundColor: '#f8f8f8' // Match header background
            }}>
                <input
                    type="text"
                    placeholder="Type your message..."
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    onKeyPress={handleKeyPress}
                    style={{
                        flexGrow: 1,
                        marginRight: '10px',
                        padding: '10px 15px',
                        borderRadius: '25px', // Very rounded input field
                        border: '1px solid #d0d0d0', // Slightly darker border
                        outline: 'none', // Remove default outline on focus
                        fontSize: '16px'
                    }}
                    disabled={loading}
                />
                <button
                    onClick={handleSendMessage}
                    disabled={loading}
                    style={{
                        padding: '10px 20px',
                        backgroundColor: '#007BFF', // Blue button
                        color: 'white',
                        border: 'none',
                        borderRadius: '25px', // Very rounded button
                        cursor: 'pointer',
                        fontSize: '16px',
                        fontWeight: 'bold',
                        transition: 'background-color 0.2s ease, transform 0.1s ease' // Smooth transition
                    }}
                >
                    Send
                </button>
            </div>
        </div>
    );
};

export default ChatInterface;

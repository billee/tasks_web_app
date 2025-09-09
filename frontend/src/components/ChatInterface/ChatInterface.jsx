import React, { useState, useRef, useEffect } from 'react';
import './ChatInterface.css';

const ChatInterface = () => {
  const [messages, setMessages] = useState([
    { text: "Hello! I'm your AI assistant. How can I help with your business tasks today?", isUser: false, time: "Just now" },
    { text: "I can help you with email categorization, document analysis, data reporting, and task automation. What would you like to start with?", isUser: false, time: "Just now" }
  ]);
  const [inputText, setInputText] = useState('');
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = () => {
    if (inputText.trim()) {
      // Add user message
      const newMessage = { text: inputText, isUser: true, time: "Just now" };
      setMessages([...messages, newMessage]);
      setInputText('');
      
      // Simulate AI response after a short delay
      setTimeout(() => {
        const responses = [
          "I understand your request. I'm processing it now.",
          "That's an interesting question. Let me think about that.",
          "I can help with that. Here's what I found...",
          "I'm analyzing your request. One moment please.",
          "Thanks for the information. I'm working on it now."
        ];
        const aiResponse = { 
          text: responses[Math.floor(Math.random() * responses.length)], 
          isUser: false, 
          time: "Just now" 
        };
        setMessages(prevMessages => [...prevMessages, aiResponse]);
      }, 1000);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSendMessage();
    }
  };

    const handleLogout = () => {
    localStorage.removeItem('isAuthenticated');
    localStorage.removeItem('userEmail');
    window.location.href = '/login';
    };

  return (
    <div className="chat-container">
        <header>
        <div className="logo">
            <i className="fas fa-robot"></i>
            <span>AI Assistant</span>
        </div>
        <div className="tagline">Your intelligent business productivity partner</div>
        <button className="logout-button" onClick={handleLogout}>
            <i className="fas fa-sign-out-alt"></i>
            Logout
        </button>
        </header>
      
      <div className="chat-content">
        <div className="sidebar">
          <div className="sidebar-title">Recent Chats</div>
          <div className="chat-history">
            <div className="history-item active">Email Categorization</div>
            <div className="history-item">Document Analysis</div>
            <div className="history-item">Data Reporting</div>
            <div className="history-item">Task Automation</div>
          </div>
          
          <div className="sidebar-title">Quick Actions</div>
          <div className="features">
            <div className="feature-button">Categorize Emails</div>
            <div className="feature-button">Generate Report</div>
            <div className="feature-button">Analyze Data</div>
          </div>
        </div>
        
        <div className="main-chat">
          <div className="response-section">
            {messages.map((message, index) => (
              <div key={index} className={`message ${message.isUser ? 'user-message' : 'ai-message'}`}>
                <div className="message-bubble">
                  {message.text}
                </div>
                <span className="message-time">{message.time}</span>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>
          
          <div className="chat-input">
            <input 
              type="text" 
              className="message-input" 
              placeholder="Type your message here..." 
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyPress={handleKeyPress}
            />
            <button className="send-button" onClick={handleSendMessage}>
              <i className="fas fa-paper-plane"></i>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;
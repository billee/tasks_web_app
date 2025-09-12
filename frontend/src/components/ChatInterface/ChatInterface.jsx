// ChatInterface.jsx
import React, { useState, useRef, useEffect } from 'react';
import './ChatInterface.css';
import { getLLMResponse } from '../../services/llm'; // Import the service

const ChatInterface = () => {
  const [messages, setMessages] = useState([
    { text: "Hello! I'm your AI assistant. How can I help with your business tasks today?", isUser: false, time: "Just now" }
  ]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (inputText.trim()) {
      // Add user message
      const newMessage = { text: inputText, isUser: true, time: "Just now" };
      const updatedMessages = [...messages, newMessage];
      setMessages(updatedMessages);
      setInputText('');
      setIsLoading(true);
      
      try {
        // Call the actual LLM service
        const aiResponseText = await getLLMResponse(updatedMessages);
        const aiResponse = { 
          text: aiResponseText, 
          isUser: false, 
          time: "Just now" 
        };
        setMessages(prevMessages => [...prevMessages, aiResponse]);
      } catch (error) {
        // Handle API errors gracefully
        console.error('Error getting AI response:', error);
        const errorResponse = { 
          text: "Sorry, I'm having trouble responding right now. Please try again.", 
          isUser: false, 
          time: "Just now" 
        };
        setMessages(prevMessages => [...prevMessages, errorResponse]);
      } finally {
        setIsLoading(false);
      }
    }
  };

  // Add the missing handleKeyPress function
  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !isLoading) {
      handleSendMessage();
    }
  };

  const handleLogout = () => {
      localStorage.removeItem('isAuthenticated');
      localStorage.removeItem('userEmail');
      localStorage.removeItem('userName');
      window.location.href = '/login';
  };

  return (
    <div className="chat-interface">
      {/* Sticky Header */}
      <header className="chat-header">
        <div className="chat-logo">
            <i className="fas fa-robot"></i>
            <span>AI Assistant</span>
        </div>
        <div className="chat-tagline">Your intelligent business productivity partner</div>
        <button className="chat-logout-button" onClick={handleLogout}>
            <i className="fas fa-sign-out-alt"></i>
            Logout
        </button>
      </header>
      
      {/* Main Chat Content */}
      <div className="chat-main-container">
        <div className="chat-ui-container">
          <div className="chat-sidebar">
            <div className="chat-history">
              <div className="history-item active">Email Tasks</div>
              <div className="history-item">To Do List</div>
            </div>
          </div>
        
          <div className="chat-main">
            <div className="response-section">
              {messages.map((message, index) => (
                <div key={index} className={`chat-message ${message.isUser ? 'user-message' : 'ai-message'}`}>
                  <div className="message-bubble">
                  {message.text}
                </div>
                <span className="message-time">{message.time}</span>
                </div>
              ))}

              {/* Typing indicator */}
              {isLoading && (
                <div className="chat-message ai-message">
                <div className="message-bubble typing-indicator">
                      <span></span>
                      <span></span>
                      <span></span>
                    </div>
                </div>
              )}
            
              <div ref={messagesEndRef} />
            </div>
          
            <div className="chat-input-container">
              <input 
                type="text" 
                className="message-input" 
                placeholder="Type your message here..." 
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                onKeyPress={handleKeyPress}
              disabled={isLoading}
              />
            <button 
              className="send-button" 
              onClick={handleSendMessage}
              disabled={isLoading}
            >
                <i className="fas fa-paper-plane"></i>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;
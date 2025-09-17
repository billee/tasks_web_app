// ChatInterface.jsx
import React, { useState, useRef, useEffect } from 'react';
import './ChatInterface.css';
import { getLLMResponse } from '../../services/llm';
import { emailToolsChat, approveAndSendEmail } from '../../services/emailTools';
import EmailComposer from '../EmailComposer/EmailComposer';
import { getEmailContent } from '../../services/emailTools';

const ChatInterface = () => {
  const [messages, setMessages] = useState([
    { text: "Hello! I'm your AI assistant. How can I help with your business tasks today?", isUser: false, time: "Just now" }
  ]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [activeMenu, setActiveMenu] = useState('Email Tasks');
  const [pendingEmail, setPendingEmail] = useState(null);
  const [processedEmails, setProcessedEmails] = useState([]);
  const messagesEndRef = useRef(null);
  const [isEmailModalOpen, setIsEmailModalOpen] = useState(false);
  const [currentEmailContent, setCurrentEmailContent] = useState('');

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    const token = localStorage.getItem('authToken');
    if (!token) {
      window.location.href = '/login';
      return;
    }
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, pendingEmail, processedEmails]);

  const handleSendMessage = async () => {
    if (inputText.trim()) {
      // Add user message
      const newMessage = { text: inputText, isUser: true, time: "Just now" };
      const updatedMessages = [...messages, newMessage];
      setMessages(updatedMessages);
      setInputText('');
      setIsLoading(true);
      
      try {
        let response;
        const MAX_RETRIES = 2;
        let retryCount = 0;
        
        // Retry logic for timeout errors
        while (retryCount <= MAX_RETRIES) {
          try {
            // Use email tools if Email Tasks is selected
            if (activeMenu === 'Email Tasks') {
              response = await emailToolsChat(updatedMessages);
            } else {
              // Use regular LLM for other menus
              const aiResponseText = await getLLMResponse(updatedMessages);
              response = {
                success: true,
                message: aiResponseText,
                tool_results: [],
                has_tool_calls: false
              };
            }
            break; // Break out of retry loop on success
          } catch (error) {
            if (error.code === 'ECONNABORTED' && retryCount < MAX_RETRIES) {
              // It's a timeout error and we have retries left
              retryCount++;
              // Show user that we're retrying
              const retryMessage = { 
                text: `Request taking longer than expected. Retrying (${retryCount}/${MAX_RETRIES})...`, 
                isUser: false, 
                time: "Just now",
                isStatus: true
              };
              setMessages(prevMessages => [...prevMessages, retryMessage]);
              // Wait before retrying (exponential backoff)
              await new Promise(resolve => setTimeout(resolve, 1000 * retryCount));
              // Remove the status message
              setMessages(prevMessages => prevMessages.filter(msg => !msg.isStatus));
            } else {
              throw error; // Re-throw if not timeout or no retries left
            }
          }
        }
        
        console.log('Full email tools response:', JSON.stringify(response, null, 2));

        if (response && response.success) {
          // Check if response contains email composition data
          if (response.email_composition) {
            console.log('Setting pending email:', response.email_composition);
            setPendingEmail({
              ...response.email_composition,
              messageId: Date.now() // unique ID for this composition
            });
          } else {
            // Add AI response to chat only if there's a message
            if (response.message && response.message !== "I've composed an email for your review:") {
              const aiMessage = { 
                  text: response.message, 
                  isUser: false, 
                  time: "Just now" 
              };
              setMessages(prevMessages => [...prevMessages, aiMessage]);
            }

            // Add tool results if any
            if (response.tool_results && response.tool_results.length > 0) {
              response.tool_results.forEach(toolResult => {
                const toolMessage = {
                  text: `Tool Result: ${JSON.stringify(toolResult.result, null, 2)}`,
                  isUser: false,
                  time: "Just now",
                  isToolResult: true
                };
                setMessages(prevMessages => [...prevMessages, toolMessage]);
              });
            }
          }
        } else {
          // Handle API errors gracefully 
          const errorText = response && response.message 
            ? response.message 
            : "Sorry, I'm having trouble with email tools right now. Please try again.";
          
          const errorResponse = { 
            text: errorText, 
            isUser: false, 
            time: "Just now" 
          };
          setMessages(prevMessages => [...prevMessages, errorResponse]);
        }
      } catch (error) {
        // Handle API errors gracefully
        console.error('Error getting AI response:', error);
        
        let errorMessageText = "Sorry, I'm having trouble responding right now. Please try again.";
        
        if (error.code === 'ECONNABORTED') {
          errorMessageText = "The request is taking too long. Please check your connection and try again.";
        } else if (error.response && error.response.status >= 500) {
          errorMessageText = "The server is experiencing issues. Please try again later.";
        }
        
        const errorResponse = { 
          text: errorMessageText, 
          isUser: false, 
          time: "Just now" 
        };
        setMessages(prevMessages => [...prevMessages, errorResponse]);
      } finally {
        setIsLoading(false);
      }
    }
  };

  // Handler for email edit
  const handleEmailEdit = (newContent) => {
    setPendingEmail(prev => ({
      ...prev,
      body: newContent
    }));
  };

  // Handler for email approval
  const handleEmailApprove = async (emailData) => {
    try {
      // Send the approved email
      const response = await approveAndSendEmail(emailData);
      
      // Mark this email as processed
      const processedEmail = {
        ...emailData,
        status: response.success ? 'sent' : 'failed',
        message: response.success 
          ? `Email sent successfully to ${emailData.recipient}` 
          : `Failed to send email: ${response.message}`,
        messageId: Date.now(),
        emailId: response.email_id // Store the email ID from the database
      };
      
      setProcessedEmails(prev => [...prev, processedEmail]);
      
      if (response.success) {
        // Add success message to chat
        const successMessage = { 
          text: `Email sent successfully to ${emailData.recipient}`, 
          isUser: false, 
          time: "Just now" 
        };
        setMessages(prevMessages => [...prevMessages, successMessage]);
      } else {
        // Add error message to chat
        const errorMessage = { 
          text: `Failed to send email: ${response.message}`, 
          isUser: false, 
          time: "Just now" 
        };
        setMessages(prevMessages => [...prevMessages, errorMessage]);
      }
    } catch (error) {
      // Handle error
      const errorMessage = { 
        text: "Failed to send email. Please try again.", 
        isUser: false, 
        time: "Just now" 
      };
      setMessages(prevMessages => [...prevMessages, errorMessage]);
    } finally {
      setPendingEmail(null);
    }
  };

  // Handler for email cancellation
  const handleEmailCancel = () => {
    // Mark this email as cancelled
    const processedEmail = {
      ...pendingEmail,
      status: 'cancelled',
      message: 'Email composition cancelled',
      messageId: Date.now()
    };
    
    setProcessedEmails(prev => [...prev, processedEmail]);
    
    // Add cancellation message to chat
    const cancelMessage = { 
      text: 'Email composition cancelled', 
      isUser: false, 
      time: "Just now" 
    };
    setMessages(prevMessages => [...prevMessages, cancelMessage]);
    
    setPendingEmail(null);
  };

  // Add the missing handleKeyPress function
  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !isLoading) {
      handleSendMessage();
    }
  };

  const handleLogout = () => {
      localStorage.removeItem('authToken');
      localStorage.removeItem('userEmail');
      localStorage.removeItem('userName');
      window.location.href = '/login';
  };

  const fetchEmailContent = async (emailId) => {
    try {
      const response = await getEmailContent(emailId);
      if (response.success) {
        setCurrentEmailContent(response.email_content);
        setIsEmailModalOpen(true);
      }
    } catch (error) {
      console.error('Error fetching email content:', error);
    }
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
              <div 
                className={`history-item ${activeMenu === 'Email Tasks' ? 'active' : ''}`}
                onClick={() => setActiveMenu('Email Tasks')}
              >
                Email Tasks
              </div>
              <div 
                className={`history-item ${activeMenu === 'To Do List' ? 'active' : ''}`}
                onClick={() => setActiveMenu('To Do List')}
              >
                To Do List
              </div>
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

              {/* Processed email compositions */}
              {processedEmails.map((email) => (
                <div key={email.messageId} className="chat-message ai-message">
                  <div className="email-sent-message">
                    {email.message}
                    {email.status === 'sent' && (
                      <button 
                        className="email-view-icon" 
                        onClick={() => fetchEmailContent(email.emailId)}
                        title="View email content"
                      >
                        <i className="fas fa-envelope"></i>
                      </button>
                    )}
                  </div>
                </div>
              ))}

              {/* Current pending email composition */}
              {pendingEmail && (
                <div className="chat-message ai-message">
                  <EmailComposer
                    emailData={pendingEmail}
                    onEdit={handleEmailEdit}
                    onApprove={handleEmailApprove}
                    onCancel={handleEmailCancel}
                    isProcessed={false}
                  />
                </div>
              )}

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

              {/* Email Content Modal */}
              {isEmailModalOpen && (
                <div className="modal-overlay" onClick={() => setIsEmailModalOpen(false)}>
                  <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                    <div className="modal-header">
                      <h3>Email Content</h3>
                      <button 
                        className="modal-close" 
                        onClick={() => setIsEmailModalOpen(false)}
                      >
                        &times;
                      </button>
                    </div>
                    <div 
                      className="email-content-preview" 
                      dangerouslySetInnerHTML={{ __html: currentEmailContent }} 
                    />
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
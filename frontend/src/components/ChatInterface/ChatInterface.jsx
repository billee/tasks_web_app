// ChatInterface.jsx
import React, { useState, useRef, useEffect } from 'react';
import './ChatInterface.css';
import { getLLMResponse } from '../../services/llm';
import { emailToolsChat, approveAndSendEmail, sendGmailReply, createGmailReplyDraft } from '../../services/emailTools';
import EmailComposer from '../EmailComposer/EmailComposer';
import ReplyComposer from '../ReplyComposer/ReplyComposer';
import { getEmailContent } from '../../services/emailTools';
import { formatTime, getCurrentTimestamp } from '../../utils/timeUtils';
import GmailDisplay from '../GmailDisplay/GmailDisplay';

const ChatInterface = () => {
  const [messages, setMessages] = useState([
    {
      text: "Hello! I'm your AI assistant. How can I help with your business tasks today?",
      isUser: false,
      time: new Date().toISOString(),
      id: Date.now()
    }
  ]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [activeMenu, setActiveMenu] = useState('Email Tasks');
  const [pendingEmail, setPendingEmail] = useState(null);
  const messagesEndRef = useRef(null);
  const [isEmailModalOpen, setIsEmailModalOpen] = useState(false);
  const [currentEmail, setCurrentEmail] = useState({
    recipient: '',
    subject: '',
    content: ''
  });
  const [selectedGmailEmail, setSelectedGmailEmail] = useState(null);
  const [replyingToEmail, setReplyingToEmail] = useState(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, pendingEmail, isLoading, replyingToEmail]);

  useEffect(() => {
    const token = localStorage.getItem('authToken');
    if (!token) {
      window.location.href = '/login';
      return;
    }
  }, []);

  useEffect(() => {
    const interval = setInterval(() => {
      // This will force a re-render and update the time displays
      setMessages(prevMessages => [...prevMessages]);
    }, 60000); // Update every minute

    return () => clearInterval(interval);
  }, []);

  const handleSendMessage = async () => {
    if (inputText.trim() && !isLoading) {
      // Add user message
      const newMessage = {
        text: inputText,
        isUser: true,
        time: new Date().toISOString(),
        id: Date.now()
      };
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
                time: new Date().toISOString(),
                isStatus: true,
                id: Date.now() + retryCount
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

        // Check for OAuth requirement first (regardless of success status)
        if (response && response.tool_results && response.tool_results.length > 0) {
          const oauthResult = response.tool_results.find(result => result.type === 'oauth_required');
          if (oauthResult) {
            console.log('OAuth required detected:', oauthResult);
            const oauthMessage = {
              text: response.message,
              isUser: false,
              time: new Date().toISOString(),
              isOAuthRequired: true,
              oauthData: oauthResult,
              id: Date.now()
            };
            console.log('Creating OAuth message:', oauthMessage);
            setMessages(prevMessages => [...prevMessages, oauthMessage]);
            return; // Exit early for OAuth handling
          }
        }

        if (response && response.success) {
          // Check if response contains email composition data
          if (response.email_composition) {
            console.log('Setting pending email:', response.email_composition);
            setPendingEmail({
              ...response.email_composition,
              messageId: Date.now() // unique ID for this composition
            });
          }
          // Check if response contains Gmail emails
          else if (response.gmail_emails && response.gmail_emails.length > 0) {
            console.log('Setting Gmail emails:', response.gmail_emails);
            const gmailMessage = {
              text: response.message || `I found ${response.gmail_emails.length} emails in your inbox.`,
              isUser: false,
              time: new Date().toISOString(),
              gmailEmails: response.gmail_emails,
              id: Date.now()
            };
            setMessages(prevMessages => [...prevMessages, gmailMessage]);
          }
          else {
            // Add AI response to chat only if there's a message
            if (response.message && response.message !== "I've composed an email for your review:") {
              const aiMessage = {
                text: response.message,
                isUser: false,
                time: new Date().toISOString(),
                id: Date.now()
              };
              setMessages(prevMessages => [...prevMessages, aiMessage]);
            }

            // Add tool results if any (non-OAuth)
            if (response.tool_results && response.tool_results.length > 0) {
              response.tool_results.forEach(toolResult => {
                // Skip OAuth results (handled above)
                if (toolResult.type !== 'oauth_required') {
                  const toolMessage = {
                    text: `Tool Result: ${JSON.stringify(toolResult.result, null, 2)}`,
                    isUser: false,
                    time: new Date().toISOString(),
                    isToolResult: true,
                    id: Date.now()
                  };
                  setMessages(prevMessages => [...prevMessages, toolMessage]);
                }
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
            time: new Date().toISOString(),
            id: Date.now()
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
          time: new Date().toISOString(),
          id: Date.now()
        };
        setMessages(prevMessages => [...prevMessages, errorResponse]);
      } finally {
        setIsLoading(false);
      }
    }
  };

  // Handler for email edit
  const handleEmailEdit = (newEmailData) => {
    setPendingEmail(newEmailData);
  };

  // Handler for email approval
  const handleEmailApprove = async (emailData) => {
    try {
      // Send the approved email
      const response = await approveAndSendEmail(emailData);

      if (response.success) {
        // Add success message to chat with icon and time
        const successMessage = {
          text: `Email sent to ${emailData.recipient}`,
          isUser: false,
          time: new Date().toISOString(),
          isEmailStatus: true,
          emailId: response.email_id,
          statusIcon: true,
          recipient: emailData.recipient,
          subject: emailData.subject,
          id: Date.now()
        };
        setMessages(prevMessages => [...prevMessages, successMessage]);
      } else {
        // Add error message to chat with time
        const errorMessage = {
          text: `Failed to send email: ${response.message}`,
          isUser: false,
          time: new Date().toISOString(),
          id: Date.now()
        };
        setMessages(prevMessages => [...prevMessages, errorMessage]);
      }
    } catch (error) {
      // Handle error with time
      const errorMessage = {
        text: "Failed to send email. Please try again.",
        isUser: false,
        time: new Date().toISOString(),
        id: Date.now()
      };
      setMessages(prevMessages => [...prevMessages, errorMessage]);
    } finally {
      setPendingEmail(null);
    }
  };

  // Handler for email cancellation
  const handleEmailCancel = () => {
    // Add cancellation message to chat
    const cancelMessage = {
      text: 'Email composition cancelled',
      isUser: false,
      time: new Date().toISOString(),
      id: Date.now()
    };
    setMessages(prevMessages => [...prevMessages, cancelMessage]);

    setPendingEmail(null);
  };

  // Handler for Gmail email click
  const handleGmailEmailClick = (email) => {
    setSelectedGmailEmail(email);
  };

  // Handler for email reply
  const handleEmailReply = (email) => {
    setReplyingToEmail(email);
  };

  // Handler for reply send
  const handleReplySend = async (replyData) => {
    try {
      const response = await sendGmailReply(replyData);
      if (response.success) {
        // Add success message
        const successMessage = {
          text: `Reply sent to ${replyData.to_email}`,
          isUser: false,
          time: new Date().toISOString(),
          isEmailStatus: true,
          id: Date.now()
        };
        setMessages(prevMessages => [...prevMessages, successMessage]);
        setReplyingToEmail(null);
      } else {
        // Handle error
        const errorMessage = {
          text: `Failed to send reply: ${response.message}`,
          isUser: false,
          time: new Date().toISOString(),
          id: Date.now()
        };
        setMessages(prevMessages => [...prevMessages, errorMessage]);
      }
    } catch (error) {
      // Handle error
      const errorMessage = {
        text: "Failed to send reply. Please try again.",
        isUser: false,
        time: new Date().toISOString(),
        id: Date.now()
      };
      setMessages(prevMessages => [...prevMessages, errorMessage]);
    }
  };

  // Handler for reply draft save
  const handleReplySaveDraft = async (draftData) => {
    try {
      const response = await createGmailReplyDraft(draftData);
      if (response.success) {
        const successMessage = {
          text: `Draft saved for reply to ${draftData.to_email}`,
          isUser: false,
          time: new Date().toISOString(),
          id: Date.now()
        };
        setMessages(prevMessages => [...prevMessages, successMessage]);
        setReplyingToEmail(null);
      } else {
        const errorMessage = {
          text: `Failed to save draft: ${response.message}`,
          isUser: false,
          time: new Date().toISOString(),
          id: Date.now()
        };
        setMessages(prevMessages => [...prevMessages, errorMessage]);
      }
    } catch (error) {
      const errorMessage = {
        text: "Failed to save draft. Please try again.",
        isUser: false,
        time: new Date().toISOString(),
        id: Date.now()
      };
      setMessages(prevMessages => [...prevMessages, errorMessage]);
    }
  };

  // Handler for reply cancellation
  const handleReplyCancel = () => {
    setReplyingToEmail(null);
  };

  // Handler for OAuth authorization - FIXED VERSION
  const handleOAuthAuthorize = (authUrl) => {
    // Open OAuth URL in a new window with relaxed security
    const authWindow = window.open(
      authUrl,
      'oauth_authorization',
      'width=600,height=700,scrollbars=yes,resizable=yes,noopener=no'
    );

    if (!authWindow) {
      // If popup is blocked, show fallback message
      const errorMessage = {
        text: "Popup blocked! Please allow popups for this site and try again.",
        isUser: false,
        time: new Date().toISOString(),
        id: Date.now()
      };
      setMessages(prevMessages => [...prevMessages, errorMessage]);
      return;
    }

    // Listen for messages from the OAuth callback
    const handleMessage = (event) => {
      if (event.data.type === 'OAUTH_SUCCESS') {
        console.log('OAuth successful for:', event.data.service);
        // Add success message
        const successMessage = {
          text: "Gmail authentication successful! You can now use Gmail features.",
          isUser: false,
          time: new Date().toISOString(),
          id: Date.now()
        };
        setMessages(prevMessages => [...prevMessages, successMessage]);
        window.removeEventListener('message', handleMessage);
      } else if (event.data.type === 'OAUTH_ERROR') {
        console.error('OAuth error:', event.data.error);
        const errorMessage = {
          text: `Authentication failed: ${event.data.error}`,
          isUser: false,
          time: new Date().toISOString(),
          id: Date.now()
        };
        setMessages(prevMessages => [...prevMessages, errorMessage]);
        window.removeEventListener('message', handleMessage);
      }
    };

    window.addEventListener('message', handleMessage);

    // Use timeout instead of polling to avoid Cross-Origin-Opener-Policy issues
    const timeout = setTimeout(() => {
        window.removeEventListener('message', handleMessage);
      // Check if we should show a timeout message
      const timeoutMessage = {
        text: "Authorization process completed. You can now try your request again.",
          isUser: false,
          time: new Date().toISOString(),
          id: Date.now()
        };
      setMessages(prevMessages => [...prevMessages, timeoutMessage]);
    }, 30000); // 30 second timeout

    // Cleanup function
    return () => {
      clearTimeout(timeout);
      window.removeEventListener('message', handleMessage);
    };
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

  const fetchEmailContent = async (emailId, recipient, subject) => {
    try {
      const response = await getEmailContent(emailId);
      if (response.success) {
        setCurrentEmail({
          recipient: recipient,
          subject: subject,
          content: response.email_content
        });
        setIsEmailModalOpen(true);
      }
    } catch (error) {
      console.error('Error fetching email content:', error);
    }
  };

  const handleEmailArchived = (emailId) => {
    // Remove the archived email from the current message's email list
    setMessages(prevMessages =>
      prevMessages.map(msg => {
        if (msg.gmailEmails) {
          const updatedEmails = msg.gmailEmails.filter(email => email.id !== emailId);
          return {
            ...msg,
            gmailEmails: updatedEmails,
            text: updatedEmails.length === 0
              ? "All emails have been archived."
              : `I found ${updatedEmails.length} emails in your inbox.`
          };
        }
        return msg;
      })
    );
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
                <div key={message.id || index} className={`chat-message ${message.isUser ? 'user-message' : 'ai-message'}`}>
                  <div className={`message-bubble ${message.isOAuthRequired ? 'ai-oauth-message' : ''}`}>
                    {message.text}
                    {message.gmailEmails && (
                      <GmailDisplay
                        emails={message.gmailEmails}
                        onEmailClick={handleGmailEmailClick}
                        onEmailArchived={handleEmailArchived}
                        onEmailReply={handleEmailReply}
                      />
                    )}
                    {message.isOAuthRequired && message.oauthData && (
                      <div className="oauth-authorization">
                        <button
                          className="oauth-authorize-btn"
                          onClick={() => handleOAuthAuthorize(message.oauthData.auth_url)}
                        >
                          <i className="fas fa-shield-alt"></i>
                          {message.oauthData.button_text || 'Authorize Gmail Access'}
                        </button>
                        <p className="oauth-note">
                          This will open a secure Google authorization page in a new window.
                        </p>
                      </div>
                    )}
                    {message.statusIcon && (
                      <button
                        className="email-view-icon"
                        onClick={() => fetchEmailContent(message.emailId, message.recipient, message.subject)}
                        title="View email content"
                      >
                        <i className="fas fa-envelope"></i>
                      </button>
                    )}
                  </div>
                  <span className="message-time">{message.time ? formatTime(message.time) : "Just now"}</span>
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
                    <div className="email-content-preview">
                      <div className="email-meta">
                        <p><strong>To:</strong> {currentEmail.recipient}</p>
                        <p><strong>Subject:</strong> {currentEmail.subject}</p>
                      </div>
                      <div
                        dangerouslySetInnerHTML={{ __html: currentEmail.content }}
                      />
                    </div>
                  </div>
                </div>
              )}

              {/* Gmail Email Detail Modal */}
              {selectedGmailEmail && (
                <div className="modal-overlay" onClick={() => setSelectedGmailEmail(null)}>
                  <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                    <div className="modal-header">
                      <h3>Email Details</h3>
                      <button
                        className="modal-close"
                        onClick={() => setSelectedGmailEmail(null)}
                      >
                        &times;
                      </button>
                    </div>
                    <div className="email-content-preview">
                      <div className="email-meta">
                        <p><strong>From:</strong> {selectedGmailEmail.from_address}</p>
                        <p><strong>Subject:</strong> {selectedGmailEmail.subject || '(No subject)'}</p>
                        <p><strong>Date:</strong> {formatTime(selectedGmailEmail.date)}</p>
                      </div>
                      <div className="email-body">
                        <p>{selectedGmailEmail.snippet}</p>
                        <p className="email-note">
                          <i>Note: This is a preview from your Gmail inbox. To read the full email, please check your Gmail account.</i>
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Reply Composer Modal */}
              {replyingToEmail && (
                <div className="modal-overlay" onClick={handleReplyCancel}>
                  <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                    <ReplyComposer
                      email={replyingToEmail}
                      onCancel={handleReplyCancel}
                      onSend={handleReplySend}
                      onSaveDraft={handleReplySaveDraft}
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
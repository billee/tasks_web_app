import React from 'react';
import './GmailDisplay.css';
import { formatTime } from '../../utils/timeUtils';

const GmailDisplay = ({ emails, onEmailClick }) => {
  if (!emails || emails.length === 0) {
    return null;
  }

  const handleReplyClick = (email, e) => {
    e.stopPropagation(); // Prevent triggering the email click
    console.log('Reply to email:', email);
    // Reply functionality will be added later
  };

  const handleCategorizeClick = (email, e) => {
    e.stopPropagation(); // Prevent triggering the email click
    console.log('Categorize email:', email);
    // Categorize functionality will be added later
  };

  const handleRemoveClick = (email, e) => {
    e.stopPropagation(); // Prevent triggering the email click
    console.log('Remove email:', email);
    // Remove functionality will be added later
  };

  return (
    <div className="gmail-display">
      <div className="gmail-header">
        <i className="fas fa-envelope"></i>
        <span>Your Inbox ({emails.length} emails)</span>
      </div>
      <div className="email-list">
        {emails.map((email, index) => (
          <div 
            key={email.id || index} 
            className="email-item"
            onClick={() => onEmailClick && onEmailClick(email)}
          >
            <div className="email-content">
              <div className="email-info">
            <div className="email-sender">{email.from_address}</div>
            <div className="email-subject">{email.subject || '(No subject)'}</div>
            <div className="email-snippet">{email.snippet}</div>
            <div className="email-date">{formatTime(email.date)}</div>
          </div>
              <div className="email-actions">
                <button 
                  className="email-action-btn reply-btn"
                  onClick={(e) => handleReplyClick(email, e)}
                  title="Reply"
                >
                  <i className="fas fa-reply"></i>
                </button>
                <button 
                  className="email-action-btn categorize-btn"
                  onClick={(e) => handleCategorizeClick(email, e)}
                  title="Categorize"
                >
                  <i className="fas fa-tag"></i>
                </button>
                <button 
                  className="email-action-btn remove-btn"
                  onClick={(e) => handleRemoveClick(email, e)}
                  title="Remove"
                >
                  <i className="fas fa-trash"></i>
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default GmailDisplay;
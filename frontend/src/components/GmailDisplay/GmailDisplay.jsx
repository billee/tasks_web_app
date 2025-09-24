import React from 'react';
import './GmailDisplay.css';
import { formatTime } from '../../utils/timeUtils';
import { archiveGmailEmail } from '../../services/emailTools';

const GmailDisplay = ({ emails, onEmailClick, onEmailArchived, onEmailReply }) => {
  if (!emails || emails.length === 0) {
    return null;
  }

  const handleReplyClick = (email, e) => {
    e.stopPropagation();
    if (onEmailReply) {
      onEmailReply(email);
    }
  };

  const handleCategorizeClick = (email, e) => {
    e.stopPropagation();
    console.log('Categorize email:', email);
  };

  const handleArchiveClick = async (email, e) => {
    e.stopPropagation();
    try {
      console.log('Archiving email:', email);
      const result = await archiveGmailEmail(email.id);
      
      if (result.success) {
        console.log('Email archived successfully');
        // Notify parent component to update the email list
        if (onEmailArchived) {
          onEmailArchived(email.id);
        }
      } else {
        console.error('Failed to archive email:', result.message);
        // You might want to show an error message to the user
      }
    } catch (error) {
      console.error('Error archiving email:', error);
    }
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
                  className="email-action-btn archive-btn"
                  onClick={(e) => handleArchiveClick(email, e)}
                  title="Archive"
                >
                  <i className="fas fa-archive"></i>
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
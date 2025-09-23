import React from 'react';
import './GmailDisplay.css';
import { formatTime } from '../../utils/timeUtils';

const GmailDisplay = ({ emails, onEmailClick }) => {
  if (!emails || emails.length === 0) {
    return null;
  }

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
            <div className="email-sender">{email.from_address}</div>
            <div className="email-subject">{email.subject || '(No subject)'}</div>
            <div className="email-snippet">{email.snippet}</div>
            <div className="email-date">{formatTime(email.date)}</div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default GmailDisplay;
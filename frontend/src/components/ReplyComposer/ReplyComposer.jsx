import React, { useState, useEffect } from 'react';
import './ReplyComposer.css';

const ReplyComposer = ({ email, onCancel, onSend, onSaveDraft }) => {
  const [subject, setSubject] = useState('');
  const [body, setBody] = useState('');
  const [isSending, setIsSending] = useState(false);

  useEffect(() => {
    if (email) {
      // Prepare subject with "Re: " prefix
      const replySubject = email.subject.startsWith('Re: ') 
        ? email.subject 
        : `Re: ${email.subject || 'No subject'}`;
      
      setSubject(replySubject);
      
      // Use the full body content instead of just snippet
      const originalContent = email.body || email.snippet || 'No content available';
      
      // Prepare reply body with proper formatting
      const formattedReply = `Hi,\n\nThank you for your email.\n\n--- Original Message ---\nFrom: ${email.from_address}\nSubject: ${email.subject || 'No subject'}\nDate: ${email.date || 'Unknown date'}\n\n${originalContent}`;
      
      setBody(formattedReply);
    }
  }, [email]);

  const handleSend = async () => {
    if (!body.trim()) {
      alert('Please enter a message body.');
      return;
    }

    setIsSending(true);
    try {
      await onSend({
        thread_id: email.thread_id || email.id,
        to_email: email.from_address,
        subject: subject,
        body: body,
        references: email.id
      });
    } finally {
      setIsSending(false);
    }
  };

  const handleSaveDraft = async () => {
    if (!body.trim()) {
      alert('Please enter a message body.');
      return;
    }

    setIsSending(true);
    try {
      await onSaveDraft({
        thread_id: email.thread_id || email.id,
        to_email: email.from_address,
        subject: subject,
        body: body
      });
    } finally {
      setIsSending(false);
    }
  };

  if (!email) return null;

  return (
    <div className="reply-composer">
      <div className="composer-header">
        <h3>Reply to {email.from_address}</h3>
        <button className="close-button" onClick={onCancel}>×</button>
      </div>
      
      <div className="composer-fields">
        <div className="field-group">
          <label>To:</label>
          <input type="text" value={email.from_address} readOnly />
        </div>
        
        <div className="field-group">
          <label>Subject:</label>
          <input 
            type="text" 
            value={subject} 
            onChange={(e) => setSubject(e.target.value)}
          />
        </div>
        
        <div className="field-group">
          <label>Message:</label>
          <textarea 
            value={body} 
            onChange={(e) => setBody(e.target.value)}
            rows={15}
            placeholder="Type your reply here..."
          />
        </div>
      </div>
      
      <div className="composer-actions">
        <button 
          className="cancel-btn"
          onClick={onCancel}
          disabled={isSending}
        >
          Cancel
        </button>
        
        <button 
          className="draft-btn"
          onClick={handleSaveDraft}
          disabled={isSending}
        >
          {isSending ? 'Saving...' : 'Save Draft'}
        </button>
        
        <button 
          className="send-btn"
          onClick={handleSend}
          disabled={isSending}
        >
          {isSending ? 'Sending...' : 'Send Reply'}
        </button>
      </div>
    </div>
  );
};

export default ReplyComposer;
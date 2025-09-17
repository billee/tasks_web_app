import React, { useState, useEffect } from 'react';
import './EmailComposer.css';
import { formatTime } from '../../utils/timeUtils';

const EmailComposer = ({
  emailData,
  onEdit,
  onApprove,
  onCancel,
  isProcessed = false,
  status = '',
  statusMessage = ''
}) => {
  const [editedContent, setEditedContent] = useState(emailData.body);
  const [editedRecipient, setEditedRecipient] = useState(emailData.recipient);
  const [editedSubject, setEditedSubject] = useState(emailData.subject);
  
  // Update local states when emailData changes
  useEffect(() => {
    setEditedContent(emailData.body);
    setEditedRecipient(emailData.recipient);
    setEditedSubject(emailData.subject);
  }, [emailData]);

  const handleContentChange = (e) => {
    const newContent = e.target.value;
    setEditedContent(newContent);
    if (onEdit) onEdit({ ...emailData, body: newContent });
  };
  
  const handleRecipientChange = (e) => {
    const newRecipient = e.target.value;
    setEditedRecipient(newRecipient);
    if (onEdit) onEdit({ ...emailData, recipient: newRecipient });
  };
  
  const handleSubjectChange = (e) => {
    const newSubject = e.target.value;
    setEditedSubject(newSubject);
    if (onEdit) onEdit({ ...emailData, subject: newSubject });
  };
  
  const handleApprove = () => {
    onApprove({
      ...emailData,
      recipient: editedRecipient,
      subject: editedSubject,
      body: editedContent
    });
  };

  return (
    <div className="email-composer">
      <div className="email-header">
        <h3>Email Composition</h3>
        {isProcessed && (
          <div className={`email-status ${status}`}>
            {statusMessage}
          </div>
        )}
      </div>
      
        <div className="email-field">
          <label>To:</label>
        <input 
          type="text" 
          value={editedRecipient} 
          onChange={handleRecipientChange}
          disabled={isProcessed}
        />
        </div>
      
        <div className="email-field">
          <label>Subject:</label>
        <input 
          type="text" 
          value={editedSubject} 
          onChange={handleSubjectChange}
          disabled={isProcessed}
        />
        </div>
      
        <div className="email-field">
          <label>Body:</label>
            <textarea
              value={editedContent}
          onChange={handleContentChange}
          disabled={isProcessed}
          rows={10}
            />
      </div>
      
      {!isProcessed && (
      <div className="email-actions">
          <button className="btn-approve" onClick={handleApprove}>
            Approve & Send
          </button>
          <button className="btn-cancel" onClick={onCancel}>
            Cancel
          </button>
      </div>
      )}
    </div>
  );
};

export default EmailComposer;
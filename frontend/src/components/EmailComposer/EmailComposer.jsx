import React, { useState } from 'react';
import './EmailComposer.css';

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

  const handleContentChange = (e) => {
    const newContent = e.target.value;
    setEditedContent(newContent);
    if (onEdit) onEdit(newContent);
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
          value={emailData.recipient} 
          disabled={isProcessed}
          readOnly
        />
        </div>
      
        <div className="email-field">
          <label>Subject:</label>
        <input 
          type="text" 
          value={emailData.subject} 
          disabled={isProcessed}
          readOnly
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
          <button className="btn-approve" onClick={() => onApprove({...emailData, body: editedContent})}>
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
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
  const [resolvingName, setResolvingName] = useState(false);
  const [nameResolutionMessage, setNameResolutionMessage] = useState('');
  
  // Update local states when emailData changes
  useEffect(() => {
    setEditedContent(emailData.body);
    setEditedRecipient(emailData.recipient);
    setEditedSubject(emailData.subject);
  }, [emailData]);

  // Check if recipient is a name (not an email) and try to resolve it
  useEffect(() => {
    const resolveNameToEmail = async () => {
      // Check if the recipient looks like a name (not an email)
      if (editedRecipient && !editedRecipient.includes('@')) {
        setResolvingName(true);
        setNameResolutionMessage(`Looking up email for ${editedRecipient}...`);
        
        try {
          const response = await fetch(`/email-tools/name-mappings/${encodeURIComponent(editedRecipient)}`, {
            headers: {
              'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
          });
          
          const result = await response.json();
          if (result.success) {
            setEditedRecipient(result.email_address);
            setNameResolutionMessage(`Resolved to: ${result.email_address}`);
            
            // Auto-update the email data
            if (onEdit) onEdit({ 
              ...emailData, 
              recipient: result.email_address,
              originalName: editedRecipient
            });
          } else {
            setNameResolutionMessage('Name not found in your contacts. Please enter an email address.');
          }
        } catch (error) {
          setNameResolutionMessage('Error looking up name. Please enter an email address.');
        } finally {
          setResolvingName(false);
        }
      } else {
        setNameResolutionMessage('');
      }
    };
    
    // Only resolve if we're not in the middle of processing
    if (!isProcessed) {
      resolveNameToEmail();
    }
  }, [editedRecipient, isProcessed]);

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
          disabled={isProcessed || resolvingName}
          placeholder="Name or email address"
        />
        {nameResolutionMessage && (
          <div className="name-resolution-message">
            {nameResolutionMessage}
          </div>
        )}
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
          <button className="btn-approve" onClick={handleApprove} disabled={resolvingName}>
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
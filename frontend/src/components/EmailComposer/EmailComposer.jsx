import React, { useState } from 'react';
import './EmailComposer.css';

const EmailComposer = ({ emailData, onEdit, onApprove, onCancel }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editedContent, setEditedContent] = useState(emailData.body);

  const handleEdit = () => {
    setIsEditing(true);
  };

  const handleSave = () => {
    setIsEditing(false);
    onEdit(editedContent);
  };

  const handleApprove = () => {
    onApprove({
      ...emailData,
      body: editedContent
    });
  };

  return (
    <div className="email-composer">
      <div className="email-header">
        <h3>Email Preview</h3>
      </div>
      <div className="email-content">
        <div className="email-field">
          <label>To:</label>
          <span>{emailData.recipient}</span>
        </div>
        <div className="email-field">
          <label>Subject:</label>
          <span>{emailData.subject}</span>
        </div>
        <div className="email-field">
          <label>Body:</label>
          {isEditing ? (
            <textarea
              value={editedContent}
              onChange={(e) => setEditedContent(e.target.value)}
              className="email-body-editable"
            />
          ) : (
            <div className="email-body">{emailData.body}</div>
          )}
        </div>
      </div>
      <div className="email-actions">
        {isEditing ? (
          <button onClick={handleSave} className="btn-save">Save Changes</button>
        ) : (
          <button onClick={handleEdit} className="btn-edit">Edit</button>
        )}
        <button onClick={handleApprove} className="btn-approve">Approve & Send</button>
        <button onClick={onCancel} className="btn-cancel">Cancel</button>
      </div>
    </div>
  );
};

export default EmailComposer;
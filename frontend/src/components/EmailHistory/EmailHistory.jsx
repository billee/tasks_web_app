import React, { useState, useEffect } from 'react';
import { getEmailHistory } from '../../services/emailTools';
import './EmailHistory.css';

const EmailHistory = () => {
  const [emails, setEmails] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchEmailHistory();
  }, []);

  const fetchEmailHistory = async () => {
    try {
      const response = await getEmailHistory();
      setEmails(response.data);
    } catch (error) {
      console.error('Error fetching email history:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div>Loading email history...</div>;
  }

  return (
    <div className="email-history">
      <h2>Email History</h2>
      {emails.length === 0 ? (
        <p>No emails sent yet.</p>
      ) : (
        <div className="email-list">
          {emails.map((email) => (
            <div key={email.id} className="email-item">
              <div className="email-header">
                <span className="recipient">To: {email.recipient}</span>
                <span className="date">{new Date(email.created_at).toLocaleString()}</span>
              </div>
              <div className="subject">Subject: {email.subject}</div>
              <div className="preview">Preview: {email.content_preview}</div>
              <div className="status">Status: {email.status}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default EmailHistory;
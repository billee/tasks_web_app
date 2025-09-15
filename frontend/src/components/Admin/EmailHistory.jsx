import React, { useState, useEffect } from 'react';
import { getAdminEmailHistory } from '../../services/emailTools';
import './EmailHistory.css';

const AdminEmailHistory = () => {
  const [emails, setEmails] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchEmailHistory();
  }, []);

  const fetchEmailHistory = async () => {
    try {
      const response = await getAdminEmailHistory();
      setEmails(response.data);
    } catch (error) {
      console.error('Error fetching email history:', error);
      setError('Failed to fetch email history. You may not have admin privileges.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="loading">Loading email history...</div>;
  }

  if (error) {
    return <div className="error">{error}</div>;
  }

  return (
    <div className="admin-email-history">
      <h2>Email History (Admin)</h2>
      {emails.length === 0 ? (
        <p>No emails sent yet.</p>
      ) : (
        <div className="email-table">
          <table>
            <thead>
              <tr>
                <th>Date</th>
                <th>Recipient</th>
                <th>Subject</th>
                <th>Status</th>
                <th>Preview</th>
                <th>User</th>
              </tr>
            </thead>
            <tbody>
              {emails.map((email) => (
                <tr key={email.id}>
                  <td>{new Date(email.created_at).toLocaleString()}</td>
                  <td>{email.recipient}</td>
                  <td>{email.subject}</td>
                  <td>{email.status}</td>
                  <td>{email.content_preview}</td>
                  <td>{email.user_email}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default AdminEmailHistory;
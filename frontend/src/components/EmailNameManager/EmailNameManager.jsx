import React, { useState, useEffect } from 'react';
import './EmailNameManager.css';

const EmailNameManager = () => {
  const [mappings, setMappings] = useState([]);
  const [newName, setNewName] = useState('');
  const [newEmail, setNewEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    fetchMappings();
  }, []);

  const fetchMappings = async () => {
    try {
      const response = await fetch('/email-tools/name-mappings', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      const data = await response.json();
      setMappings(data);
    } catch (error) {
      console.error('Error fetching mappings:', error);
    }
  };

  const addMapping = async () => {
    if (!newName || !newEmail) {
      setMessage('Please enter both name and email');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch('/email-tools/name-mappings', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          name: newName,
          email_address: newEmail
        })
      });

      const result = await response.json();
      if (result.success) {
        setNewName('');
        setNewEmail('');
        setMessage('Mapping added successfully');
        fetchMappings();
      } else {
        setMessage(result.message || 'Error adding mapping');
      }
    } catch (error) {
      setMessage('Error adding mapping');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="email-name-manager">
      <h3>Name-Email Mappings</h3>
      
      <div className="add-mapping-form">
        <input
          type="text"
          placeholder="Name"
          value={newName}
          onChange={(e) => setNewName(e.target.value)}
        />
        <input
          type="email"
          placeholder="Email Address"
          value={newEmail}
          onChange={(e) => setNewEmail(e.target.value)}
        />
        <button onClick={addMapping} disabled={loading}>
          {loading ? 'Adding...' : 'Add Mapping'}
        </button>
      </div>

      {message && <div className="message">{message}</div>}

      <div className="mappings-list">
        <h4>Your Mappings</h4>
        {mappings.length === 0 ? (
          <p>No mappings yet. Add some above.</p>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Name</th>
                <th>Email Address</th>
              </tr>
            </thead>
            <tbody>
              {mappings.map((mapping, index) => (
                <tr key={index}>
                  <td>{mapping.name}</td>
                  <td>{mapping.email_address}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
};

export default EmailNameManager;
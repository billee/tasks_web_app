import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { authService } from '../../services/auth';
import './AdminLogin.css';

const AdminLogin = () => {
  const [credentials, setCredentials] = useState({
    email: '',
    password: ''
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    
    try {
      // Use the proper admin login method
      const result = await authService.adminLogin(credentials.email, credentials.password);
      
      if (result.success) {
        navigate('/admin/dashboard');
      } else {
        setError(result.error);
      }
    } catch (err) {
      setError('An unexpected error occurred. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="admin-login-container">
      <div className="admin-login-card">
        <div className="admin-login-header">
          <h2>Admin Portal Login</h2>
          <p>System administrators only</p>
        </div>
        
        <form onSubmit={handleSubmit}>
          {error && <div>{typeof error === 'string' ? error : JSON.stringify(error)}</div>}
          
          <div className="form-group">
            <label>Admin Email</label>
            <input
              type="email"
              value={credentials.email}
              onChange={(e) => setCredentials({...credentials, email: e.target.value})}
              required
              disabled={isLoading}
            />
          </div>
          
          <div className="form-group">
            <label>Password</label>
            <input
              type="password"
              value={credentials.password}
              onChange={(e) => setCredentials({...credentials, password: e.target.value})}
              required
              disabled={isLoading}
            />
          </div>
          
          <button type="submit" disabled={isLoading}>
            {isLoading ? 'Logging in...' : 'Login to Admin Portal'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default AdminLogin;
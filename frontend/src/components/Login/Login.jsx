import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Link } from 'react-router-dom';
import { authService } from '../../services/auth';
import './Login.css';

const Login = () => {
  const [credentials, setCredentials] = useState({
    email: '',
    password: ''
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleChange = (e) => {
    setCredentials({
      ...credentials,
      [e.target.name]: e.target.value
    });
    if (error) setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    
    try {
      // Changed from authService.adminLogin to authService.login for regular users
      const result = await authService.login(credentials.email, credentials.password);
      
      if (result.success) {
        navigate('/chat');
      } else {
        setError(result.error);
      }
    } catch (err) {
      setError('An unexpected error occurred. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const showContactInfo = (e) => {
    e.preventDefault();
    alert('Please contact your system administrator verbally to request an account. They will create your login credentials for you.');
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <div className="admin-portal-link">
          <Link to="/admin/login">Admin Portal</Link>
        </div>
        <div className="login-header">
          <div className="logo">
            <i className="fas fa-robot"></i>
            <span>Business AI Assistant</span>
          </div>
          <h2>Sign In to Your Account</h2>
          <p>Enter your credentials to access the AI assistant</p>
        </div>
        
        <form onSubmit={handleSubmit} className="login-form">
          {error && <div className="error-message">{error}</div>}
          
          <div className="form-group">
            <label htmlFor="email">Email Address</label>
            <input
              type="email"
              id="email"
              name="email"
              value={credentials.email}
              onChange={handleChange}
              placeholder="Enter your email"
              required
              disabled={isLoading}
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              type="password"
              id="password"
              name="password"
              value={credentials.password}
              onChange={handleChange}
              placeholder="Enter your password"
              required
              disabled={isLoading}
            />
          </div>
          
          <button 
            type="submit" 
            className="login-button"
            disabled={isLoading}
          >
            {isLoading ? (
              <>
                <i className="fas fa-spinner fa-spin"></i>
                Signing In...
              </>
            ) : (
              <>
                <i className="fas fa-sign-in-alt"></i>
                Sign In
              </>
            )}
          </button>
        </form>
        
        <div className="login-footer">
          <p>Don't have an account? <a href="#" onClick={showContactInfo}>Contact administrator</a></p>
          <p><a href="#forgot">Forgot your password?</a></p>
        </div>
      </div>
    </div>
  );
};

export default Login;
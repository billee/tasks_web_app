import React, { useState, useEffect } from 'react';
import './AdminDashboard.css';
import { authService } from '../../services/auth'; // Add this import

const AdminDashboard = () => {
  const [users, setUsers] = useState([]);
  const [currentUser, setCurrentUser] = useState(null);
  const [newUser, setNewUser] = useState({
    email: '',
    password: ''
  });
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Simulate fetching users from an API
    const fetchUsers = async () => {
      try {
        // This would be replaced with an actual API call
        await new Promise(resolve => setTimeout(resolve, 1000));
          
        // Mock data for demonstration
          const mockUsers = [
          { id: 1, email: 'user1@example.com', is_active: true, created_at: new Date().toISOString() },
          { id: 2, email: 'user2@example.com', is_active: true, created_at: new Date().toISOString() }
        ];
        
          setUsers(mockUsers);
        
        // Get current user email from localStorage and find user info
        const userEmail = localStorage.getItem('userEmail');
        if (userEmail) {
          // Try to find the user in the users list, or create a mock current user
          const currentUserData = mockUsers.find(user => user.email === userEmail) || 
                                  { email: userEmail, is_admin: true, id: 999, is_active: true, created_at: new Date().toISOString() };
          setCurrentUser(currentUserData);
        } else {
          // Fallback for demonstration
          setCurrentUser({ email: 'admin@example.com', is_admin: true, id: 999, is_active: true, created_at: new Date().toISOString() });
        }
      } catch (error) {
        console.error('Failed to fetch users:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchUsers();
  }, []);

  const handleCreateUser = async (e) => {
    e.preventDefault();
    try {
      // This would call your backend API to create a user
      console.log('Creating user:', newUser);
      
      // For now, just add to the local state
      const newUserObj = {
        id: users.length + 1,
        email: newUser.email,
        is_active: true,
        created_at: new Date().toISOString()
      };
      
      setUsers([...users, newUserObj]);
      setNewUser({ email: '', password: '' });
      
      alert('User created successfully!');
    } catch (error) {
      console.error('Failed to create user:', error);
      alert('Failed to create user');
    }
  };

  const handleDeactivate = async (userId) => {
    try {
      // This would call your backend API to deactivate a user
      console.log('Deactivating user:', userId);
      
      // For now, just update the local state
      setUsers(users.map(user => 
        user.id === userId ? { ...user, is_active: false } : user
      ));
      
      alert('User deactivated successfully!');
    } catch (error) {
      console.error('Failed to deactivate user:', error);
      alert('Failed to deactivate user');
    }
  };

  const handleLogout = async () => {
    try {
      console.log('Logging out...');
      
      // Use the authService logout method which calls the backend
      const result = await authService.logout();
      
      if (result.success) {
        console.log('Logout successful:', result.message);
      } else {
        console.log('Logout had issues but local session cleared:', result.error);
      }
      
      // Force a page reload to redirect to login page
      window.location.reload();
      
      // Alternative options if you prefer:
      // window.location.href = '/login';
      // Or if using React Router: navigate('/login');
      
    } catch (error) {
      console.error('Logout failed:', error);
      
      // Fallback: clear localStorage directly and reload
      localStorage.removeItem('authToken');
      localStorage.removeItem('userEmail');
      localStorage.removeItem('isAdmin');
      
      window.location.reload();
    }
  };

  // Helper function to get user initials
  const getUserInitials = (email) => {
    if (!email) return 'A';
    const parts = email.split('@')[0].split('.');
    if (parts.length >= 2) {
      return (parts[0][0] + parts[1][0]).toUpperCase();
    }
    return email.substring(0, 2).toUpperCase();
  };

  // Helper function to format display name
  const getDisplayName = (email) => {
    if (!email) return 'Administrator';
    const username = email.split('@')[0];
    // Convert email username to a more readable format
    return username.split('.').map(part => 
      part.charAt(0).toUpperCase() + part.slice(1)
    ).join(' ');
  };

  // Calculate stats
  const activeUsers = users.filter(user => user.is_active).length;
  const inactiveUsers = users.filter(user => !user.is_active).length;

  if (isLoading) return <div className="loading">Loading...</div>;

  return (
    <>
      {/* Sticky Header */}
      <header className="admin-header">
        <div className="logo-section">
          <div className="logo">A</div>
          <div className="logo-text">Admin Dashboard</div>
        </div>
        
        <div className="admin-profile">
          <div className="profile-info">
            <div className="admin-name">
              {currentUser ? getDisplayName(currentUser.email) : 'Administrator'}
            </div>
            <div className="admin-role">Administrator</div>
          </div>
          <div className="profile-avatar">
            {currentUser ? getUserInitials(currentUser.email) : 'A'}
          </div>
          <button className="logout-btn" onClick={handleLogout}>
            Log Out
          </button>
        </div>
      </header>

      <div className="users-list">
        <h2>Existing Users</h2>
        <table>
          <thead>
            <tr>
              <th>Email</th>
              <th>Status</th>
              <th>Created</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {users.map(user => (
              <tr key={user.id}>
                <td>{user.email}</td>
                  <td>
                    <span className={`status-badge ${user.is_active ? 'status-active' : 'status-inactive'}`}>
                      {user.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                <td>{new Date(user.created_at).toLocaleDateString()}</td>
                <td>
                  {user.is_active && (
                    <button 
                      onClick={() => handleDeactivate(user.id)}
                      className="deactivate-btn"
                    >
                    Deactivate
                  </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Main Dashboard Content */}
      <div className="admin-dashboard">      
        <div className="dashboard-grid"></div>
        <div className="dashboard-stats">
          <h2>Quick Stats</h2>
          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-number">{activeUsers}</div>
              <div className="stat-label">Active Users</div>
            </div>
            <div className="stat-card">
              <div className="stat-number">{inactiveUsers}</div>
              <div className="stat-label">Inactive Users</div>
            </div>
          </div>
        </div>
        <div className="dashboard-grid"></div>
        <div className="user-creation-form">
          <h2>Create New User</h2>
          <form onSubmit={handleCreateUser}>
                <div className="form-group">
                  <label htmlFor="email">Email Address</label>
            <input
              type="email"
                    id="email"
                    placeholder="Enter email address"
              value={newUser.email}
              onChange={(e) => setNewUser({...newUser, email: e.target.value})}
              required
            />
                </div>
                <div className="form-group">
                  <label htmlFor="password">Password</label>
            <input
              type="password"
                    id="password"
                    placeholder="Enter password"
              value={newUser.password}
              onChange={(e) => setNewUser({...newUser, password: e.target.value})}
              required
            />
                </div>
            <button type="submit">Create User</button>
          </form>
        </div>
      </div>
    </>
  );
};

export default AdminDashboard;
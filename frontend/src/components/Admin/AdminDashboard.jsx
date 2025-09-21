// AdminDashboard.jsx
import React, { useState, useEffect } from 'react';
import './AdminDashboard.css';
import { authService } from '../../services/auth';
import { adminService } from '../../services/admin';
import EmailHistory from './EmailHistory';

const AdminDashboard = () => {
  const [users, setUsers] = useState([]);
  const [currentUser, setCurrentUser] = useState(null);
  const [newUser, setNewUser] = useState({
    email: '',
    password: '',
    name: ''
  });
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchUsers = async () => {
      try {
        const usersData = await adminService.getUsers();
        setUsers(usersData);
          
        try {
          const currentUserData = await adminService.getCurrentUser();
          setCurrentUser(currentUserData);
        } catch (currentUserError) {
          console.error('Failed to fetch current user, using localStorage fallback:', currentUserError);
        
        const userEmail = localStorage.getItem('userEmail');
          const userName = localStorage.getItem('userName') || 'Administrator';
        
        if (userEmail) {
            const currentUserData = usersData.find(user => user.email === userEmail) || 
                                  { 
                                    email: userEmail, 
                                    name: userName,
                                    is_admin: true, 
                                    id: 999, 
                                    is_active: true, 
                                    created_at: new Date().toISOString() 
                                  };
          setCurrentUser(currentUserData);
        } else {
          setCurrentUser({ 
            email: 'admin@example.com', 
            name: userName,
            is_admin: true, 
            id: 999, 
            is_active: true, 
            created_at: new Date().toISOString() 
          });
        }
        }
      } catch (error) {
        console.error('Failed to fetch users:', error);
        alert('Failed to load users: ' + error.message);
      } finally {
        setIsLoading(false);
      }
    };

    fetchUsers();
  }, []);

  const handleCreateUser = async (e) => {
    e.preventDefault();
    try {
      const createdUser = await adminService.createUser(newUser);
      setUsers([...users, createdUser]);
      setNewUser({ email: '', password: '', name: '' });
      alert('User created successfully!');
    } catch (error) {
      console.error('Failed to create user:', error);
      alert('Failed to create user: ' + error.message);
    }
  };

  const handleDeactivate = async (userId) => {
    try {
      const updatedUser = await adminService.deactivateUser(userId);
      setUsers(users.map(user => 
        user.id === userId ? updatedUser : user
      ));
      alert('User deactivated successfully!');
    } catch (error) {
      console.error('Failed to deactivate user:', error);
      alert('Failed to deactivate user: ' + error.message);
    }
  };

  const handleLogout = async () => {
    try {
      console.log('Logging out...');
      const result = await authService.logout();
      
      if (result.success) {
        console.log('Logout successful:', result.message);
      } else {
        console.log('Logout had issues but local session cleared:', result.error);
      }
      
      window.location.reload();
    } catch (error) {
      console.error('Logout failed:', error);
      localStorage.removeItem('authToken');
      localStorage.removeItem('userEmail');
      localStorage.removeItem('userName');
      localStorage.removeItem('isAdmin');
      window.location.reload();
    }
  };

  const getUserInitials = (user) => {
    if (!user) return 'A';
    
    if (user.name) {
      const nameParts = user.name.split(' ');
      if (nameParts.length >= 2) {
        return (nameParts[0][0] + nameParts[nameParts.length - 1][0]).toUpperCase();
      }
      return user.name.substring(0, 2).toUpperCase();
    }
    
    const parts = user.email.split('@')[0].split('.');
    if (parts.length >= 2) {
      return (parts[0][0] + parts[1][0]).toUpperCase();
    }
    return user.email.substring(0, 2).toUpperCase();
  };

  const getDisplayName = (user) => {
    if (!user) return 'Administrator';
    
    if (user.name) {
      return user.name;
    }
    
    const username = user.email.split('@')[0];
    return username.split('.').map(part => 
      part.charAt(0).toUpperCase() + part.slice(1)
    ).join(' ');
  };

  const activeUsers = users.filter(user => user.is_active).length;
  const inactiveUsers = users.filter(user => !user.is_active).length;

  if (isLoading) return <div className="admin-dashboard-loading">Loading...</div>;

  return (
    <div className="admin-dashboard">
      <header className="admin-dashboard-header">
        <div className="admin-dashboard-logo-section">
          <div className="admin-dashboard-logo">A</div>
          <div className="admin-dashboard-logo-text">Admin Dashboard</div>
        </div>
        
        <div className="admin-dashboard-profile">
          <div className="admin-dashboard-profile-info">
            <div className="admin-dashboard-name">
              {currentUser ? getDisplayName(currentUser) : 'Administrator'}
            </div>
            <div className="admin-dashboard-role">Administrator</div>
          </div>
          <div className="admin-dashboard-profile-avatar">
            {currentUser ? getUserInitials(currentUser) : 'A'}
          </div>
          <button className="admin-dashboard-logout-btn" onClick={handleLogout}>
            Log Out
          </button>
        </div>
      </header>

      <div className="admin-dashboard-content">
        <div className="admin-dashboard-stats">
          <h2>Quick Stats</h2>
          <div className="admin-dashboard-stats-grid">
            <div className="admin-dashboard-stat-card">
              <div className="admin-dashboard-stat-number">{users.length}</div>
              <div className="admin-dashboard-stat-label">Total Users</div>
            </div>
            <div className="admin-dashboard-stat-card">
              <div className="admin-dashboard-stat-number">{activeUsers}</div>
              <div className="admin-dashboard-stat-label">Active Users</div>
            </div>
            <div className="admin-dashboard-stat-card">
              <div className="admin-dashboard-stat-number">{inactiveUsers}</div>
              <div className="admin-dashboard-stat-label">Inactive Users</div>
            </div>
          </div>
        </div>

      <div className="admin-dashboard-users-list">
        <h2>Existing Users</h2>
        <table>
          <thead>
            <tr>
              <th>Name</th>
              <th>Email</th>
              <th>Admin</th>
              <th>Status</th>
              <th>Created</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {users.map(user => (
              <tr key={user.id}>
                <td>{user.name || 'N/A'}</td>
                <td>{user.email}</td>
                <td>
                  <span className={`admin-dashboard-admin-badge ${user.is_admin ? 'admin-dashboard-admin-yes' : 'admin-dashboard-admin-no'}`}>
                    {user.is_admin ? 'Yes' : 'No'}
                  </span>
                </td>
                <td>
                  <span className={`admin-dashboard-status-badge ${user.is_active ? 'admin-dashboard-status-active' : 'admin-dashboard-status-inactive'}`}>
                    {user.is_active ? 'Active' : 'Inactive'}
                  </span>
                </td>
                <td>{new Date(user.created_at).toLocaleDateString()}</td>
                <td>
                  {user.is_active && (
                    <button 
                      onClick={() => handleDeactivate(user.id)}
                      className="admin-dashboard-deactivate-btn"
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

          <div className="admin-dashboard-user-creation-form">
          <h2>Create New User</h2>
          <form onSubmit={handleCreateUser}>
              <div className="admin-dashboard-form-group">
                  <label htmlFor="name">Full Name</label>
            <input
              type="text"
                    id="name"
                    placeholder="Enter full name"
              value={newUser.name}
              onChange={(e) => setNewUser({...newUser, name: e.target.value})}
              required
            />
                </div>
              <div className="admin-dashboard-form-group">
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
              <div className="admin-dashboard-form-group">
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
    </div>
  );
};

export default AdminDashboard;
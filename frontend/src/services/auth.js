import api from './api';

export const authService = {
  // Login user
  async login(email, password) {
    try {
      // Use FormData for x-www-form-urlencoded format
      console.log('===============pass the auth.js- login')
      const formData = new URLSearchParams();
      formData.append('username', email);
      formData.append('password', password);

      const response = await api.post('/auth/login', formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      });
      
      if (response.data.access_token) {
        // Store the token
        localStorage.setItem('authToken', response.data.access_token);
        localStorage.setItem('userEmail', email);
        localStorage.setItem('userName', response.data.user_name || response.data.name || '');
        
        return { success: true, data: response.data };
      }
      
      return { success: false, error: 'Invalid response from server' };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Login failed' 
      };
    }
  },

  // Admin login
  async adminLogin(email, password) {
    try {
      // Use FormData for x-www-form-urlencoded format
      console.log('===============pass the auth.js- adminLogin')
      const formData = new URLSearchParams();
      formData.append('username', email);
      formData.append('password', password);
      
      // Updated to use the correct endpoint path with /auth prefix
      const response = await api.post('/auth/admin/login', formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      });
      
      if (response.data.access_token) {
        // Store the token and admin status
        localStorage.setItem('authToken', response.data.access_token);
        localStorage.setItem('userEmail', email);
        localStorage.setItem('userName', response.data.user_name || response.data.name || '');
        localStorage.setItem('isAdmin', 'true');
        
        return { success: true, data: response.data };
      }
      
      return { success: false, error: 'Invalid response from server' };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Admin login failed' 
      };
    }
  },

  // Logout user with backend call
  async logout() {
    try {
      // Call backend logout endpoint
      await api.post('/auth/logout');
      
      // Clear local storage regardless of backend response
      localStorage.removeItem('authToken');
      localStorage.removeItem('userEmail');
      localStorage.removeItem('userName'); 
      localStorage.removeItem('isAdmin');
      
      return { success: true, message: 'Logged out successfully' };
    } catch (error) {
      // Even if backend call fails, clear local storage
      localStorage.removeItem('authToken');
      localStorage.removeItem('userEmail');
      localStorage.removeItem('userName'); 
      localStorage.removeItem('isAdmin');
      
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Logout failed, but local session cleared' 
      };
    }
  },

  // Quick logout (client-side only) - keeping for backwards compatibility
  logoutQuick() {
    localStorage.removeItem('authToken');
    localStorage.removeItem('userEmail');
    localStorage.removeItem('userName');
    localStorage.removeItem('isAdmin');
  },

  // Check if user is authenticated
  isAuthenticated() {
    return !!localStorage.getItem('authToken');
  },

  // Check if user is admin
  isAdmin() {
    return localStorage.getItem('isAdmin') === 'true';
  },

  // Get stored token
  getToken() {
    return localStorage.getItem('authToken');
  }
};
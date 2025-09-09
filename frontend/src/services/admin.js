import api from './api';

export const adminService = {
  // Get all users
  async getUsers() {
    try {
      const response = await api.get('/admin/users');
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to fetch users');
    }
  },

  // Create a new user
  async createUser(userData) {
    try {
      const response = await api.post('/admin/users', userData);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to create user');
    }
  },

  // Deactivate a user
  async deactivateUser(userId) {
    try {
      const response = await api.put(`/admin/users/${userId}/deactivate`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to deactivate user');
    }
  }
};
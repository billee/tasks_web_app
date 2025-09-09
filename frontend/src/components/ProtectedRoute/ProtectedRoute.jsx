import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { authService } from '../../services/auth';

const ProtectedRoute = ({ children, requireAdmin = false }) => {
  const isAuthenticated = authService.isAuthenticated();
  const location = useLocation();
  
  // If not authenticated, redirect to appropriate login page
  if (!isAuthenticated) {
    // If we're on an admin route, redirect to admin login
    if (location.pathname.startsWith('/admin')) {
      return <Navigate to="/admin/login" replace />;
    }
    // Otherwise redirect to regular login
    return <Navigate to="/login" replace />;
  }
  
  // If admin required but user is not admin, redirect to home
  if (requireAdmin && !authService.isAdmin()) {
    return <Navigate to="/" replace />;
  }
  
  return children;
};

export default ProtectedRoute;
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Login from './components/Login/Login';
import ChatInterface from './components/ChatInterface/ChatInterface';
import ProtectedRoute from './components/ProtectedRoute/ProtectedRoute';
import AdminLogin from './components/Admin/AdminLogin';
import AdminDashboard from './components/Admin/AdminDashboard';
import UserManagement from './components/Admin/UserManagement';
import RegistrationRequests from './components/Admin/RegistrationRequests';
import AdminEmailHistory from './components/Admin/EmailHistory';
import AdminLayout from './components/Admin/AdminLayout';
import './App.css';

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route 
            path="/chat" 
            element={
              <ProtectedRoute>
                <ChatInterface />
              </ProtectedRoute>
            } 
          />
          <Route path="/" element={<Navigate to="/login" replace />} />
          
          {/* Admin routes */}
          <Route path="/admin/login" element={<AdminLogin />} />
          <Route 
            path="/admin/dashboard" 
            element={
              <ProtectedRoute requireAdmin={true}>
                <AdminLayout>
                <AdminDashboard />
                </AdminLayout>
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/admin/users" 
            element={
              <ProtectedRoute requireAdmin={true}>
                <AdminLayout>
                <UserManagement />
                </AdminLayout>
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/admin/requests" 
            element={
              <ProtectedRoute requireAdmin={true}>
                <AdminLayout>
                <RegistrationRequests />
                </AdminLayout>
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/admin/email-history" 
            element={
              <ProtectedRoute requireAdmin={true}>
                <AdminLayout>
                  <AdminEmailHistory />
                </AdminLayout>
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/admin" 
            element={<Navigate to="/admin/dashboard" replace />} 
          />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
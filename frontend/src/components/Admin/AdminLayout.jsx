import React from 'react';
import AdminMenu from './AdminMenu';
import './AdminLayout.css';

const AdminLayout = ({ children }) => {
  return (
    <div className="admin-layout">
      <div className="admin-layout-sidebar">
        <AdminMenu />
      </div>
      <div className="admin-layout-content">
        {children}
      </div>
    </div>
  );
};

export default AdminLayout;
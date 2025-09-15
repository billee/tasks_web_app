import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import './AdminMenu.css';

const AdminMenu = () => {
  const location = useLocation();
  
  const menuItems = [
    { path: '/admin/users', label: 'User Management', icon: 'fas fa-users' },
    { path: '/admin/email-history', label: 'Email History', icon: 'fas fa-envelope' },
    // Add more admin menu items as needed
  ];

  return (
    <div className="admin-menu">
      <h3 className="admin-menu-title">Admin Panel</h3>
      <ul className="admin-menu-list">
        {menuItems.map((item) => (
          <li key={item.path} className="admin-menu-item">
            <Link 
              to={item.path} 
              className={`admin-menu-link ${location.pathname === item.path ? 'active' : ''}`}
            >
              <i className={item.icon}></i>
              <span>{item.label}</span>
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default AdminMenu;
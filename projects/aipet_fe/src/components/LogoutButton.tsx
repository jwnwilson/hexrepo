import React from 'react';

interface LogoutButtonProps {
  className?: string;
  style?: React.CSSProperties;
}

const LogoutButton: React.FC<LogoutButtonProps> = ({ 
  className = "", 
  style = {} 
}) => {
  const handleLogout = () => {
    const confirmed = window.confirm('Are you sure you want to logout? This will clear all your data and refresh the page.');
    if (confirmed) {
      // Clear localStorage
      localStorage.clear();
      // Force browser refresh
      window.location.reload();
    }
  };

  const defaultStyle: React.CSSProperties = {
    position: 'absolute',
    top: '40px',
    right: '20px',
    padding: '10px 20px',
    backgroundColor: '#ff4444',
    color: 'white',
    border: 'none',
    borderRadius: '5px',
    cursor: 'pointer',
    fontSize: '14px',
    fontWeight: 'bold',
    zIndex: 1000,
    boxShadow: '0 2px 4px rgba(0,0,0,0.2)',
    ...style
  };

  return (
    <button
      onClick={handleLogout}
      className={className}
      style={defaultStyle}
      onMouseOver={(e) => {
        e.currentTarget.style.backgroundColor = '#cc3333';
      }}
      onMouseOut={(e) => {
        e.currentTarget.style.backgroundColor = '#ff4444';
      }}
    >
      Logout
    </button>
  );
};

export default LogoutButton; 
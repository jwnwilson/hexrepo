import React, { useState, useEffect } from 'react';
import { AuthProvider } from './context';
import { useAuth } from './hooks';
import Login from './components/Login';
import Signup from './components/Signup';
import BabylonScene from './components/BabylonScene';
import './css/main.css';

type Page = 'login' | 'signup' | 'app';

const AppContent: React.FC = () => {
  const [currentPage, setCurrentPage] = useState<Page>('login');
  const { isAuthenticated } = useAuth();

  // Check for valid login on initial load
  useEffect(() => {
    if (isAuthenticated) {
      setCurrentPage('app');
    }
  }, [isAuthenticated]);

  const renderPage = () => {
    switch (currentPage) {
      case 'login':
        return <Login onNavigate={setCurrentPage} />;
      case 'signup':
        return <Signup onNavigate={setCurrentPage} />;
      case 'app':
        return <BabylonScene className="babylon-canvas" />;
      default:
        return <Login onNavigate={setCurrentPage} />;
    }
  };

  return (
    <div className="app">
      {renderPage()}
    </div>
  );
};

const App: React.FC = () => {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
};

export default App; 
import React, { useState } from 'react';
import { AuthProvider } from './context';
import Login from './components/Login';
import Signup from './components/Signup';
import BabylonScene from './components/BabylonScene';
import './css/main.css';

type Page = 'login' | 'signup' | 'app';

const App: React.FC = () => {
  const [currentPage, setCurrentPage] = useState<Page>('login');

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
    <AuthProvider>
      <div className="app">
        {renderPage()}
      </div>
    </AuthProvider>
  );
};

export default App; 
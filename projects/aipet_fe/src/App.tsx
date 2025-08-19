import React from 'react';
import BabylonScene from './components/BabylonScene';
import './css/main.css';

const App: React.FC = () => {
  return (
    <div className="app">
      <BabylonScene className="babylon-canvas" />
    </div>
  );
};

export default App; 
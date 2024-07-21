import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Home from './components/Home';
import Session from './components/Session';
import HealthCheck from './HealthCheck';

const App: React.FC = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/session" element={<Session />} />
        <Route path="/healthcheck" element={<HealthCheck />} />
      </Routes>
    </Router>
  );
}

export default App;

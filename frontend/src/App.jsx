
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";

import Home from "./pages/home/Home";
import Callback from "./pages/callback/Callback";
import { useEffect, useState } from 'react';
import Nebula from './pages/dashboard/nebula/Nebula.jsx'
import NebulaDashboard from './pages/dashboard/Dashboard.jsx';



function App() {
  

  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/callback" element={<Callback />} />
        <Route path="/dashboard" element={<NebulaDashboard/>} />
      </Routes>
    </Router>
  );
}


export default App

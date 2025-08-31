import { BrowserRouter as Router, Routes, Route } from "react-router-dom";

import Home from "./pages/home/Home";
import Callback from "./pages/callback/Callback";
import Dashboard from "./pages/dashboard/Dashboard";

function App() {

  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/callback" element={<Callback />} />
        <Route path="/dashboard" element={<Dashboard />} />
      </Routes>
    </Router>
  );
}


export default App

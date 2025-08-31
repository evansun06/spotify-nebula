
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";

import Home from "./pages/home/Home";
import Callback from "./pages/callback/Callback";
import Dashboard from './pages/dashboard/Dashboard.jsx';
import Test from "./pages/test/Test.jsx";



function App() {
  

  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/callback" element={<Callback />} />
        <Route path="/dashboard" element={<Dashboard/>} />
        <Route path="/test" element={<Test/>} />
      </Routes>
    </Router>
  );
}


export default App

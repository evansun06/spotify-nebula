import { useEffect, useState } from 'react';
import Nebula from './pages/nebula/Nebula.jsx'
import sample from '../sample.json'

function App() {
  const [data, setData] = useState([]);

  useEffect(() => {
    fetch('../sample.json')
      .then(response => response.json())
      .then(json => {
        setData(json); // Store the data in state
      })
      .catch(err => console.error('Failed to load JSON:', err));
  }, []);

  return (
    <Nebula data={data} /> 
  );
}

export default App;

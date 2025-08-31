
import Nebula from '../dashboard/nebula/Nebula'
import ControlPanel from '../dashboard/controlpanel/ControPanel';
import styles from './Test.module.css'
import { useEffect, useState } from 'react';

function Test() {
  const [data, setData] = useState([]);
  const [highlighted, setHighlighted] = useState(null); // lifted state
  const [track, selectedTrack] = useState(null)

  useEffect(() => {
    fetch('../sample.json')
      .then(response => response.json())
      .then(json => {
        setData(json);
      })
      .catch(err => console.error('Failed to load JSON:', err));
  }, []);

  return (
    <>
      <Nebula data={data} highlighted={highlighted} setHighlighted={setHighlighted} />
      <ControlPanel data={data} highlighted={highlighted} setHighlighted={setHighlighted} />
    </>
  );
}

export default Test;
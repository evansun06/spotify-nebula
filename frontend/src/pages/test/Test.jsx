
import Nebula from '../dashboard/nebula/Nebula'
import ControlPanel from '../dashboard/controlpanel/ControPanel';
import styles from '../dashboard/Dashboard.module.css'
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
    <div className={styles.dash}>
                {data.length > 0 && (
                    <>
                    <div className={styles.nebula}>
                        <Nebula data={data} highlighted={highlighted} setHighlighted={setHighlighted} />
                    </div>
                    <div className={styles.panelOverlay}>
                        <ControlPanel data={data} highlighted={highlighted} setHighlighted={setHighlighted} />
                    </div>
                    </>
                )}
    </div>

  );
}

export default Test;
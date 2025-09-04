import styles from './ControlPanel.module.css';
import { useState } from 'react';

export default function ControlPanel({ data = [], highlighted, setHighlighted }) {
  const uniqueClusters = [...new Set(data.map(p => p.cluster))];
  const [clustSongs, setClustSongs] = useState([]);

  const handleClusterChange = (clusterId) => {
    // Convert clusterId back to number if needed
    const parsedId = isNaN(clusterId) ? clusterId : Number(clusterId);

    setHighlighted(parsedId);
    const filteredSongs = data.filter((song) => song.cluster === parsedId);
    setClustSongs(filteredSongs);
  };

  return (
    <div className={styles.panel}>
      <h3>Your Constellations</h3>
      <div>
        <select
  className={styles.select}
  onChange={(e) => handleClusterChange(e.target.value)}
  value={highlighted ?? ""}
>
  <option value="" disabled>
    Select a cluster
  </option>
  {uniqueClusters.map((clusterId, index) => (
    <option key={index} value={clusterId}>
      Cluster {clusterId}
    </option>
  ))}
</select>

      </div>

      <div className={styles.songs}>
        {clustSongs.map((song, index) => (
          <h3 key={index} className={styles.song}>
            {song.name} by {song.artist}
          </h3>
        ))}
      </div>
    </div>
  );
}






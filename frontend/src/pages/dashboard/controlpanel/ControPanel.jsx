import styles from './ControlPanel.module.css';
import { useMemo } from 'react';

export default function ControlPanel({ data = [], highlighted, setHighlighted }) {
    const uniqueClusters = [...new Set(data.map(p => p.cluster))];

    // Derive songs for the selected cluster
    const clustSongs = useMemo(() => {
        if (highlighted == null) return [];
        return data.filter((song) => song.cluster === highlighted);
    }, [data, highlighted]);

    const handleClusterChange = (clusterId) => {
        const parsedId = isNaN(clusterId) ? clusterId : Number(clusterId);
        setHighlighted(parsedId);
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

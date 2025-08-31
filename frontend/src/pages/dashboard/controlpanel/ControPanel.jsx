import styles from './ControlPanel.module.css';


export default function ControlPanel({ data = [], highlighted, setHighlighted }) {
  const uniqueClusters = [...new Set(data.map(p => p.cluster))];

  return (
    <div className={styles.panel}>
      <h3>Your Constellations</h3>
      <div>
        {uniqueClusters.map((clusterId, index) => (
          <li
            key={index}
            onClick={() => {
                setHighlighted(clusterId)}}
          >
            Cluster {clusterId}
          </li>
        ))}
      </div>
    </div>
  );
}

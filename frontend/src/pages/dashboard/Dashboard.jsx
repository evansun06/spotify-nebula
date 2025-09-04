import Nebula from './nebula/Nebula';
import LoadingBar from 'react-top-loading-bar'
import { fetchNebula } from "../../api/nebula";
import ControlPanel from './controlpanel/ControPanel';
import { useState, useRef} from 'react';
import styles from './Dashboard.module.css'

function Dashboard() {

    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [term, setTerm] = useState("short_term");
    const loadingRef = useRef(null)

    const [data, setData] = useState([]);
    const [highlighted, setHighlighted] = useState(null); // lifted state

    const handleGetNebula = async () => {
        setLoading(true);
        loadingRef.current.continuousStart()

        try {
            const nebulaData = await fetchNebula(term);
            console.log("Nebula data:", nebulaData);
            setData(nebulaData);
        } catch (err) {
            console.error(err);
            setError("Failed to fetch nebula data");
        } finally {
            setLoading(false);
            loadingRef.current.complete();
        }
    };

    return (
        <>
            <div style={{ padding: "50px", textAlign: "center" }}>
                <h1>Your Dashboard</h1>

                <div>
                    <label htmlFor="term-select">Select term: </label>
                    <select value={term} onChange={(e) => setTerm(e.target.value)}>
                        <option value="short_term">4 Weeks</option>
                        <option value="medium_term">6 Months</option>
                        <option value="long_term">1 Year</option>
                    </select>
                </div>

                <button
                    onClick={handleGetNebula}
                    style={{ padding: "10px 20px", marginTop: "20px" }}
                    disabled={loading}
                >
                    {loading ? "Fetching..." : "Get Nebula"}
                </button>
                <LoadingBar ref={loadingRef} />

                {error && <p style={{ color: "red", marginTop: "20px" }}>{error}</p>}

            </div>
            <div className={styles.dash}>
  {data.length > 0 && (
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
        )}
    </div>
    

            
               
        </>
    );
}

export default Dashboard;

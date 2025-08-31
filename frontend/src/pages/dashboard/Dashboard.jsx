import { fetchNebula } from "../../api/nebula";
import Nebula from './nebula/Nebula';
import { useEffect, useState } from 'react';

function Dashboard() {
    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const handleGetNebula = async () => {
        setLoading(true);
        setError(null);

        try {
            const nebulaData = await fetchNebula("short_term");
            console.log("Nebula data:", nebulaData);
            setData(nebulaData);
        } catch (err) {
            console.error(err);
            setError("Failed to fetch nebula data");
        } finally {
            setLoading(false);
        }
    };

    return (
        <>
            <div style={{ padding: "50px", textAlign: "center" }}>
                <h1>Your Dashboard</h1>
                <button
                    onClick={handleGetNebula}
                    style={{ padding: "10px 20px", marginTop: "20px" }}
                    disabled={loading}
                >
                    {loading ? "Fetching..." : "Get Nebula"}
                </button>

                {error && <p style={{ color: "red", marginTop: "20px" }}>{error}</p>}

                {data.length > 0 && (
                    <div style={{ marginTop: "30px" }}>
                        <h2>Tracks:</h2>
                        <ul style={{ listStyle: "none", padding: 0 }}>
                            {data.map((track, idx) => (
                                <li key={idx}>
                                    {track.name} by {track.artist.join(", ")}
                                </li>
                            ))}
                        </ul>
                    </div>
                )}
            </div>
            {data.length > 0 && <Nebula data={data} />}

        </>
    );
}

export default Dashboard;

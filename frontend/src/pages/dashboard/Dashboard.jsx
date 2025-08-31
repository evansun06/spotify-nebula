import { useState } from "react";
import { fetchNebula } from "../../api/nebula";

function Dashboard() {
    const [loading, setLoading] = useState(false);
    const [tracks, setTracks] = useState([]);
    const [error, setError] = useState(null);

    const handleGetNebula = async () => {
        setLoading(true);
        setError(null);

        try {
            // Example: term could be 'short_term', 'medium_term', 'long_term'
            const data = await fetchNebula("short_term");
            console.log("Nebula data:", data);
            setTracks(data);
        } catch (err) {
            console.error(err);
            setError("Failed to fetch nebula data");
        } finally {
            setLoading(false);
        }
    };

    return (
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

            {tracks.length > 0 && (
                <div style={{ marginTop: "30px" }}>
                    <h2>Tracks:</h2>
                    <ul style={{ listStyle: "none", padding: 0 }}>
                        {tracks.map((track, idx) => (
                            <li key={idx}>
                                {track.name} by {track.artist.join(", ")}
                            </li>
                        ))}
                    </ul>
                </div>
            )}
        </div>
    );
}

export default Dashboard;
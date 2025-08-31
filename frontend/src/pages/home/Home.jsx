import { loginSpotify } from "../../api/nebula";

function Home() {
    return (
        <div style={{ padding: "50px", textAlign: "center" }}>
            <h1>Welcome to Nebula</h1>
            <p>Connect your Spotify account to generate your nebula.</p>
            <button onClick={loginSpotify} style={{ padding: "10px 20px", marginTop: "20px" }}>
                Login with Spotify
            </button>
        </div>
    );
}

export default Home;
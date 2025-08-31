import { loginSpotify } from "../../api/nebula";
import styles from './Home.module.css';
import spotifyLogo from "../../assets/spotify-logo.png";
import nebulaBackground from "../../assets/b5.jpg";

function Home() {
    return (
        <div className={styles.container} style={{ backgroundImage: `url(${nebulaBackground})` }}>

            <h1 className={styles.title}>Welcome to Nebula</h1>


            <button className={styles.button} onClick={loginSpotify}>
                <img src={spotifyLogo} className={styles.spotifyLogo}/>
                <span>Continue with Spotify</span>
            </button>

        </div>
    );
}

export default Home;
import Nebula from './nebula/Nebula';
import LoadingBar from 'react-top-loading-bar'
import { fetchNebula } from "../../api/nebula";
import ControlPanel from './controlpanel/ControPanel';
import { useState, useRef, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import styles from './dashboard.module.css'
import Lottie from "lottie-react";
import rocketAnim from "../../assets/rocket.json";

function Dashboard() {

    const { term } = useParams();

    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const [data, setData] = useState([]);
    const [highlighted, setHighlighted] = useState(null);
    const loadingRef = useRef(null);
    const fetchedRef = useRef(false);

    useEffect(() => {
        if (!term || fetchedRef.current) return;

        fetchedRef.current = true;
        const getData = async () => {
            setLoading(true);
            loadingRef.current.continuousStart();

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

        getData();
    }, [term])

    return (
        <>
            <LoadingBar color="#001076ff" ref={loadingRef} />

            {loading && (
                <div className={styles.rocket}>
                    <Lottie animationData={rocketAnim} loop={true} />
                </div>
            )}
            {error && <p>{error}</p>}
            {data.length > 0 && <Nebula data={data} highlighted={highlighted} setHighlighted={setHighlighted} />}
            {data.length > 0 && <ControlPanel data={data} highlighted={highlighted} setHighlighted={setHighlighted} />}
        </>
    );
}

export default Dashboard;

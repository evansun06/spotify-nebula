import Nebula from './nebula/Nebula';
import LoadingBar from 'react-top-loading-bar'
import { fetchNebula } from "../../api/nebula";
import ControlPanel from './controlpanel/ControPanel';
import styles from './Dashboard.module.css'
import { useState, useRef, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import Lottie from "lottie-react";
import rocketAnim from "../../assets/loading-animation.json";


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
            <LoadingBar color="#bc70ffff" ref={loadingRef} />

            {loading && (
                <div className={styles.rocket}>
                    <Lottie animationData={rocketAnim} loop={true} />
                </div>
            )}




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
        </>
    );
}

export default Dashboard;

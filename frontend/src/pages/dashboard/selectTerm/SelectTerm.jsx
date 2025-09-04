import { useNavigate } from "react-router-dom";
import { useState } from "react";
import styles from "./selectTerm.module.css"
import nebulaBackground from "../../../assets/b5.jpg";
import neb from "../../../assets/neb.jpg";

function SelectTerm() {
    const [selectedTerm, setSelectedTerm] = useState(null);

    const navigate = useNavigate();

    const handleGenerate = () => {
        if (!selectedTerm) {
            alert("Please select term first!!!");
        }
        navigate(`/dashboard/${selectedTerm}`);
    }

    return (
        <div className={styles.selectTermPage} >

            <p className={styles.selectTermText}>Please select what listening time frame your nebula is generated from.</p>
            <div className={styles.selectTermButtons}>
                <button className={`${styles.selectTermButton} ${selectedTerm === "short_term" ? styles.selected : ""}`}
                    onClick={() => setSelectedTerm("short_term")}>
                    4 Weeks
                </button>

                <button className={`${styles.selectTermButton} ${selectedTerm === "medium_term" ? styles.selected : ""}`}
                    onClick={() => setSelectedTerm("medium_term")}>
                    6 Months
                </button>

                <button className={`${styles.selectTermButton} ${selectedTerm === "long_term" ? styles.selected : ""}`}
                    onClick={() => setSelectedTerm("long_term")}>
                    1 Year
                </button>
            </div>

            <button className={styles.generateNebulaButton} style={{ backgroundImage: `url(${nebulaBackground})` }} onClick={handleGenerate}>Generate Nebula</button>
        </div>
    );
}

export default SelectTerm;
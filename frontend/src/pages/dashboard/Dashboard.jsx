import Nebula from './nebula/Nebula';

import { useEffect, useState } from 'react';
import styles from './NebulaDashboard.module.css'


export default function nebulaDashboard() {
    const [data, setData] = useState([]);

    useEffect(() => {
        fetch('../sample.json')
        .then(response => response.json())
        .then(json => {
            setData(json); // Store the data in state
        })
        .catch(err => console.error('Failed to load JSON:', err));
    }, []);

    return(
        <>
            <></>
            <Nebula data={data}/>
        </>
    );

}


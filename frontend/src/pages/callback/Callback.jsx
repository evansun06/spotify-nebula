import { useEffect } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";

function Callback() {
    const [searchParams] = useSearchParams();
    const navigate = useNavigate();

    useEffect(() => {

        const token = searchParams.get("token");

        if (token) {
            localStorage.setItem("jwt", token)
            navigate("/select-term")
        }
    }, [searchParams, navigate]);

    return (<p>Loading...</p>)
}

export default Callback
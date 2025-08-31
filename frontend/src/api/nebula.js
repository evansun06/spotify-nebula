const BASE_URL = "http://localhost:8000";

export function loginSpotify() {
    window.location.href = `${BASE_URL}/login`;
}

export async function fetchNebula(term) {
    const token = localStorage.getItem("jwt");

    if (!token) {
        throw new Error("No token found");
    }

    const response = await fetch(`${BASE_URL}/nebula/${term}`, { headers: { Authorization: `Bearer ${token}` } });

    if (!response.ok) {
        throw new Error("Failed to fetch nebula");
    }

    const nebula_data = await response.json();
    return nebula_data
}
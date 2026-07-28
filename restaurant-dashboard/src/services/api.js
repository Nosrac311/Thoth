const API = "http://127.0.0.1:8000";

async function request(endpoint) {
    const response = await fetch(`${API}${endpoint}`);

    if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
    }

    return response.json();
}

export function getStats() {
    return request("/stats");
}

export function getLatest(limit = 50) {
    return request(`/inspections/latest?limit=${limit}`);
}

export function searchRestaurant(name) {
    return request(
        `/restaurants/search?name=${encodeURIComponent(name)}`
    );
}
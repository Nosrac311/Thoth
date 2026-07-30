const API = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000";

async function request(endpoint) {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 10000);

    try {
        const response = await fetch(`${API}${endpoint}`, {
            signal: controller.signal
        });

        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }

        return await response.json();
    } finally {
        clearTimeout(timeout);
    }
}

export function getStats() {
    return request("/stats");
}

export function getLatest(limit = 50) {
    const value = Math.max(1, Math.min(limit, 500));
    return request(`/inspections/latest?limit=${value}`);
}

export function searchRestaurant(name) {
    const query = name.trim();

    if (!query) {
        return Promise.resolve({
            query: "",
            results: []
        });
    }

    const params = new URLSearchParams({ name: query });
    return request(`/restaurants/search?${params}`);
}
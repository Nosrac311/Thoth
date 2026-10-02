const API_URL = "http://127.0.0.1:8000";

export async function apiRequest(
    endpoint: string,
    options: RequestInit = {},
    token?: string
) {

    const headers: Record<string, string> = {
        "Content-Type": "application/json",
        ...(options.headers as Record<string, string> || {}),
    };

    if (token) {
        headers.Authorization = `Bearer ${token}`;
    }

    const response = await fetch(
        `${API_URL}${endpoint}`,
        {
            ...options,
            headers,
        }
    );

    const text = await response.text();

    let data: any = null;

    try {
        data = text ? JSON.parse(text) : null;
    } catch {
        data = text;
    }

    if (!response.ok) {

        const message =
            data?.detail ||
            data?.message ||
            "Request failed";

        throw new Error(message);
    }

    return data;
}


// --------------------------------------------------
// REGISTER
// --------------------------------------------------

export async function register(
    email: string,
    password: string
) {

    return apiRequest(
        "/auth/register",
        {
            method: "POST",
            body: JSON.stringify({
                email,
                password,
            }),
        }
    );
}


// --------------------------------------------------
// LOGIN
// --------------------------------------------------

export async function login(
    email: string,
    password: string
) {

    return apiRequest(
        "/auth/login",
        {
            method: "POST",
            body: JSON.stringify({
                email,
                password,
            }),
        }
    );
}


// --------------------------------------------------
// WATCHLIST
// --------------------------------------------------

export async function getWatchlist(
    token: string
) {

    return apiRequest(
        "/watchlist",
        {},
        token
    );
}


export async function addWatchlist(
    token: string,
    keyword: string
) {

    return apiRequest(
        "/watchlist",
        {
            method: "POST",
            body: JSON.stringify({
                keyword,
            }),
        },
        token
    );
}


export async function removeWatchlist(
    token: string,
    keyword: string
) {

    return apiRequest(
        `/watchlist/${encodeURIComponent(keyword)}`,
        {
            method: "DELETE",
        },
        token
    );
}

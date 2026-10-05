import {
    getToken,
    saveToken,
    removeToken,
} from "./auth";

export const API_URL = "https://thoth-u72b.onrender.com";

type RequestOptions = RequestInit & {
    headers?: Record<string, string>;
};


// --------------------------------------------------
// REQUEST
// --------------------------------------------------

async function request(
    path: string,
    options: RequestOptions = {}
) {
    const token = await getToken();

    console.log("REQUEST:", path);
    

    const headers: Record<string, string> = {
        Accept: "application/json",
        "Content-Type": "application/json",
        ...(options.headers ?? {}),
    };

    if (token) {
        headers.Authorization = `Bearer ${token}`;
    }

    let response: Response;

    try {
        response = await fetch(
            `${API_URL}${path}`,
            {
                ...options,
                headers,
            }
        );
    } catch {
        throw new Error(
            "Could not connect to the Thoth server. Check your internet connection and try again."
        );
    }

    const text = await response.text();

    let data: any = null;

    if (text) {
        try {
            data = JSON.parse(text);
        } catch {
            data = text;
        }
    }

    if (!response.ok) {

        let message =
            `Request failed (${response.status})`;

        if (
            typeof data === "object" &&
            data !== null
        ) {

            const detail = data.detail;

            if (
                typeof detail === "string"
            ) {

                message = detail;

            } else if (
                Array.isArray(detail)
            ) {

                message = detail
                    .map((item: any) => {

                        if (
                            typeof item === "string"
                        ) {
                            return item;
                        }

                        if (
                            item &&
                            typeof item.msg === "string"
                        ) {
                            return item.msg;
                        }

                        return "Invalid request";

                    })
                    .join("\n");
            }

        } else if (
            typeof data === "string" &&
            data.trim()
        ) {

            message = data;
        }

        throw new Error(message);
    }

    return data;
}


// --------------------------------------------------
// AUTH
// --------------------------------------------------

export async function register(
    email: string,
    password: string
) {

    const data = await request(
        "/auth/register",
        {
            method: "POST",

            body: JSON.stringify({
                email: email
                    .trim()
                    .toLowerCase(),

                password,
            }),
        }
    );

    console.log(
        "REGISTER RESPONSE:",
        data
    );

    // If registration returns a token,
    // save it immediately.

    if (data?.access_token) {

        await saveToken(
            data.access_token
        );

        console.log(
            "REGISTRATION TOKEN SAVED:",
            !!(await getToken())
        );
    }

    return data;
}


export async function login(
    email: string,
    password: string
) {

    const data = await request(
        "/auth/login",
        {
            method: "POST",

            body: JSON.stringify({
                email: email
                    .trim()
                    .toLowerCase(),

                password,
            }),
        }
    );

    console.log(
        "LOGIN RESPONSE:",
        data
    );

    if (!data?.access_token) {

        throw new Error(
            "Login succeeded but no access token was returned."
        );
    }

    await saveToken(
        data.access_token
    );

    const savedToken =
        await getToken();

    console.log(
        "TOKEN SAVED:",
        !!savedToken
    );

    if (!savedToken) {

        throw new Error(
            "The authentication token could not be saved."
        );
    }

    return data;
}


export async function logout() {

    await removeToken();

    const token =
        await getToken();

    console.log(
        "LOGOUT - TOKEN EXISTS:",
        !!token
    );

}


// --------------------------------------------------
// WATCHLIST
// --------------------------------------------------

export async function getWatchlist() {

    const token = await getToken();

   

    return request(
        "/watchlist",
        {
            method: "GET",
        }
    );
}



export async function addWatchlist(
    keyword: string
) {

    return request(
        "/watchlist",
        {
            method: "POST",

            body: JSON.stringify({
                keyword: keyword.trim(),
            }),
        }
    );
}


export async function deleteWatchlist(
    keyword: string
) {

    return request(
        `/watchlist/${encodeURIComponent(
            keyword.trim()
        )}`,
        {
            method: "DELETE",
        }
    );
}

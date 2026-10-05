import * as SecureStore from "expo-secure-store";

const TOKEN_KEY = "thoth_token";

export async function saveToken(
token: string
): Promise<void> {
if (!token) {
throw new Error(
"Cannot save an empty authentication token."
);
}

await SecureStore.setItemAsync(
    TOKEN_KEY,
    token
);


}

export async function getToken(): Promise<string | null> {
return await SecureStore.getItemAsync(
TOKEN_KEY
);
}

export async function removeToken(): Promise<void> {
await SecureStore.deleteItemAsync(
TOKEN_KEY
);
}

export async function isLoggedIn(): Promise<boolean> {
const token = await getToken();

return token !== null;


}
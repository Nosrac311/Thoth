import * as SecureStore from "expo-secure-store";


const TOKEN_KEY = "thoth_access_token";


// --------------------------------------------------
// SAVE TOKEN
// --------------------------------------------------

export async function saveToken(
    token: string
) {

    await SecureStore.setItemAsync(
        TOKEN_KEY,
        token
    );
}


// --------------------------------------------------
// GET TOKEN
// --------------------------------------------------

export async function getToken() {

    return SecureStore.getItemAsync(
        TOKEN_KEY
    );
}


// --------------------------------------------------
// REMOVE TOKEN
// --------------------------------------------------

export async function removeToken() {

    await SecureStore.deleteItemAsync(
        TOKEN_KEY
    );
}

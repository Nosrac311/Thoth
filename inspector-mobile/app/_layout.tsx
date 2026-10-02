import {
    Stack,
    useRouter,
    useSegments,
} from "expo-router";

import {
    StatusBar,
} from "expo-status-bar";

import {
    useEffect,
    useState,
} from "react";

import "react-native-reanimated";

import {
    useColorScheme,
} from "@/hooks/use-color-scheme";

import {
    getToken,
} from "../auth";


export const unstable_settings = {
    anchor: "(tabs)",
};


export default function RootLayout() {

    const colorScheme = useColorScheme();

    const router = useRouter();

    const segments = useSegments();

    const [checkingAuth, setCheckingAuth] =
        useState(true);


    useEffect(() => {

        async function checkAuth() {

            try {

                const token = await getToken();

                const inAuth =
                    segments[0] === "auth";


                // ------------------------------------------
                // User is not logged in
                // ------------------------------------------

                if (!token && !inAuth) {

                    router.replace("/auth");

                    return;
                }


                // ------------------------------------------
                // User is already logged in
                // ------------------------------------------

                if (token && inAuth) {

                    router.replace("/");

                    return;
                }


            } catch (error) {

                console.log(
                    "AUTH CHECK ERROR:",
                    error
                );

            } finally {

                setCheckingAuth(false);
            }
        }


        checkAuth();

    }, [
        segments,
    ]);


    if (checkingAuth) {

        return null;
    }


    return (

        <>

            <Stack>

                <Stack.Screen
                    name="(tabs)"
                    options={{
                        headerShown: false,
                    }}
                />

                <Stack.Screen
                    name="auth"
                    options={{
                        headerShown: false,
                    }}
                />

                <Stack.Screen
                    name="modal"
                    options={{
                        presentation: "modal",
                        title: "Modal",
                    }}
                />

            </Stack>


            <StatusBar
                style={
                    colorScheme === "dark"
                        ? "light"
                        : "dark"
                }
            />

        </>
    );
}

import { useEffect, useState } from "react";

import {
    View,
    Text,
    TextInput,
    TouchableOpacity,
    StyleSheet,
    Alert,
} from "react-native";

import { useRouter } from "expo-router";

import { login, register } from "../api";

import {
    getToken,
    saveToken,
} from "../auth";


export default function AuthScreen() {

    const router = useRouter();

    const [email, setEmail] = useState("");

    const [password, setPassword] = useState("");

    const [isRegistering, setIsRegistering] =
        useState(false);

    const [loading, setLoading] =
        useState(false);

    const [checking, setChecking] =
        useState(true);


    // --------------------------------------------------
    // If already logged in, skip auth screen.
    // --------------------------------------------------

    useEffect(() => {

        async function checkLogin() {

            const token = await getToken();

            if (token) {

                router.replace("/");

                return;
            }

            setChecking(false);
        }

        checkLogin();

    }, []);


    async function handleSubmit() {

        if (
            !email.trim() ||
            !password
        ) {

            Alert.alert(
                "Missing information",
                "Enter your email and password."
            );

            return;
        }


        try {

            setLoading(true);


            const result = isRegistering
                ? await register(
                    email.trim(),
                    password
                )
                : await login(
                    email.trim(),
                    password
                );


            await saveToken(
                result.access_token
            );


            router.replace("/");


        } catch (error: any) {

            Alert.alert(
                isRegistering
                    ? "Registration failed"
                    : "Login failed",

                error.message ||
                "Something went wrong."
            );

        } finally {

            setLoading(false);
        }
    }


    if (checking) {

        return (
            <View style={styles.center}>

                <Text>
                    Loading...
                </Text>

            </View>
        );
    }


    return (

        <View style={styles.container}>

            <Text style={styles.title}>
                Thoth
            </Text>


            <Text style={styles.subtitle}>

                {isRegistering
                    ? "Create your account"
                    : "Welcome back"}

            </Text>


            <TextInput
                style={styles.input}
                placeholder="Email"
                autoCapitalize="none"
                autoCorrect={false}
                keyboardType="email-address"
                value={email}
                onChangeText={setEmail}
            />


            <TextInput
                style={styles.input}
                placeholder="Password"
                secureTextEntry
                value={password}
                onChangeText={setPassword}
            />


            <TouchableOpacity
                style={styles.button}
                onPress={handleSubmit}
                disabled={loading}
            >

                <Text style={styles.buttonText}>

                    {loading
                        ? "Please wait..."
                        : isRegistering
                            ? "Register"
                            : "Login"}

                </Text>

            </TouchableOpacity>


            <TouchableOpacity
                onPress={() =>
                    setIsRegistering(
                        !isRegistering
                    )
                }
            >

                <Text style={styles.switchText}>

                    {isRegistering
                        ? "Already have an account? Login"
                        : "Don't have an account? Register"}

                </Text>

            </TouchableOpacity>

        </View>
    );
}


const styles = StyleSheet.create({

    container: {
        flex: 1,
        justifyContent: "center",
        padding: 25,
        backgroundColor: "#f5f5f5",
    },

    center: {
        flex: 1,
        justifyContent: "center",
        alignItems: "center",
    },

    title: {
        fontSize: 40,
        fontWeight: "bold",
        textAlign: "center",
        marginBottom: 5,
    },

    subtitle: {
        fontSize: 20,
        textAlign: "center",
        marginBottom: 30,
        color: "#666",
    },

    input: {
        backgroundColor: "#fff",
        borderWidth: 1,
        borderColor: "#ddd",
        borderRadius: 10,
        padding: 15,
        marginBottom: 15,
        fontSize: 16,
    },

    button: {
        backgroundColor: "#2563eb",
        padding: 16,
        borderRadius: 10,
        alignItems: "center",
        marginBottom: 20,
    },

    buttonText: {
        color: "#fff",
        fontSize: 17,
        fontWeight: "bold",
    },

    switchText: {
        textAlign: "center",
        color: "#2563eb",
        fontSize: 15,
    },

});

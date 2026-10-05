import { useEffect, useState } from "react";

import {
    View,
    Text,
    TextInput,
    TouchableOpacity,
    StyleSheet,
    Alert,
    ActivityIndicator,
} from "react-native";

import { useRouter } from "expo-router";

import { login, register } from "../api";
import {
    getToken,
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
    // Check existing login
    // --------------------------------------------------

    useEffect(() => {

        let mounted = true;

        async function checkLogin() {

            try {

                const token = await getToken();

                if (token) {

                    router.replace("/");

                    return;
                }

            } catch (error) {

                console.log(
                    "AUTH CHECK ERROR:",
                    error
                );

            } finally {

                if (mounted) {
                    setChecking(false);
                }

            }
        }

        checkLogin();

        return () => {
            mounted = false;
        };

    }, [router]);


    // --------------------------------------------------
    // Submit
    // --------------------------------------------------

    async function handleSubmit() {

        const cleanEmail =
            email.trim().toLowerCase();

        const cleanPassword =
            password;


        if (!cleanEmail || !cleanPassword) {

            Alert.alert(
                "Missing information",
                "Enter your email and password."
            );

            return;
        }


        if (!cleanEmail.includes("@")) {

            Alert.alert(
                "Invalid email",
                "Enter a valid email address."
            );

            return;
        }


        try {

            setLoading(true);


            console.log(
                isRegistering
                    ? "REGISTERING..."
                    : "LOGGING IN..."
            );


            let result;


            // --------------------------------------------------
            // REGISTER
            // --------------------------------------------------

            if (isRegistering) {

                result = await register(
                    cleanEmail,
                    cleanPassword
                );

                console.log(
                    "REGISTER RESPONSE:",
                    result
                );


                // Some APIs return a token immediately
                // after registration.
                //
                // If yours does not, automatically log in
                // after creating the account.

                if (
                    !result ||
                    !result.access_token
                ) {

                    console.log(
                        "Registration succeeded. Logging in..."
                    );

                    result = await login(
                        cleanEmail,
                        cleanPassword
                    );

                }

            }

            // --------------------------------------------------
            // LOGIN
            // --------------------------------------------------

            else {

                result = await login(
                    cleanEmail,
                    cleanPassword
                );

                console.log(
                    "LOGIN RESPONSE:",
                    result
                );

            }


            // --------------------------------------------------
            // Get JWT
            // --------------------------------------------------

            


            // --------------------------------------------------
            // Enter application
            // --------------------------------------------------

            router.replace("/");


        } catch (error: any) {

            console.error(
                "AUTH ERROR:",
                error
            );


            const message =
                error?.message ||
                "Something went wrong. Please try again.";


            Alert.alert(
                isRegistering
                    ? "Registration failed"
                    : "Login failed",
                message
            );

        } finally {

            setLoading(false);

        }

    }


    // --------------------------------------------------
    // Loading screen
    // --------------------------------------------------

    if (checking) {

        return (
            <View style={styles.center}>

                <ActivityIndicator
                    size="large"
                    color="#2563eb"
                />

                <Text style={styles.loadingText}>
                    Checking login...
                </Text>

            </View>
        );

    }


    // --------------------------------------------------
    // Auth UI
    // --------------------------------------------------

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
                textContentType="emailAddress"
                value={email}
                onChangeText={setEmail}
                editable={!loading}
            />


            <TextInput
                style={styles.input}
                placeholder="Password"
                secureTextEntry
                textContentType={
                    isRegistering
                        ? "newPassword"
                        : "password"
                }
                value={password}
                onChangeText={setPassword}
                editable={!loading}
            />


            <TouchableOpacity
                style={[
                    styles.button,
                    loading && styles.buttonDisabled,
                ]}
                onPress={handleSubmit}
                disabled={loading}
            >

                {loading ? (

                    <ActivityIndicator
                        color="#fff"
                    />

                ) : (

                    <Text style={styles.buttonText}>

                        {isRegistering
                            ? "Register"
                            : "Login"}

                    </Text>

                )}

            </TouchableOpacity>


            <TouchableOpacity
                onPress={() => {

                    if (!loading) {

                        setIsRegistering(
                            previous => !previous
                        );

                    }

                }}
                disabled={loading}
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


// --------------------------------------------------
// STYLES
// --------------------------------------------------

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
        backgroundColor: "#f5f5f5",
    },

    loadingText: {
        marginTop: 12,
        color: "#666",
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
        justifyContent: "center",
        marginBottom: 20,
        minHeight: 54,
    },

    buttonDisabled: {
        opacity: 0.7,
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

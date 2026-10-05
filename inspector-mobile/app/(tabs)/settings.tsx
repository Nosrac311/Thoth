import {
    View,
    Text,
    TouchableOpacity,
    StyleSheet,
    Alert,
} from "react-native";

import { useRouter } from "expo-router";

import { logout } from "../../api";
;


export default function Settings() {

    const router = useRouter();


    async function handleLogout() {

        try {

            await logout();

            router.replace("/auth");

        } catch (error) {

            console.error(
                "LOGOUT ERROR:",
                error
            );

            Alert.alert(
                "Logout failed",
                "Could not log you out. Please try again."
            );

        }

    }


    return (

        <View style={styles.container}>

            <Text style={styles.title}>
                Settings
            </Text>


            <TouchableOpacity
                style={styles.logoutButton}
                onPress={handleLogout}
            >

                <Text style={styles.logoutText}>
                    Log Out
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
        padding: 20,
        backgroundColor: "#f5f5f5",
    },

    title: {
        fontSize: 32,
        fontWeight: "bold",
        marginBottom: 30,
    },

    logoutButton: {
        backgroundColor: "#dc2626",
        padding: 16,
        borderRadius: 10,
        alignItems: "center",
    },

    logoutText: {
        color: "#fff",
        fontSize: 17,
        fontWeight: "bold",
    },

});

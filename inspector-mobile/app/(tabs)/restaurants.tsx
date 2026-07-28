import { View, Text, StyleSheet } from "react-native";

export default function Restaurants() {
    return (
        <View style={styles.container}>
            <Text style={styles.title}>
                Restaurants
            </Text>

            <Text>
                Search and view restaurants here.
            </Text>
        </View>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        padding: 20,
        paddingTop: 60,
    },

    title: {
        fontSize: 32,
        fontWeight: "bold",
    }
});
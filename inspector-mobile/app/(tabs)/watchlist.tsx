import { useEffect, useState } from "react";

import {
    View,
    Text,
    FlatList,
    TextInput,
    TouchableOpacity,
    StyleSheet,
    Alert,
    ActivityIndicator,
} from "react-native";


const API_URL = "https://thoth-u72b.onrender.com";


export default function Watchlist() {

    const [watchlist, setWatchlist] = useState<string[]>([]);
    const [keyword, setKeyword] = useState("");
    const [loading, setLoading] = useState(true);
    const [adding, setAdding] = useState(false);


    // --------------------------------------------------
    // Load watchlist when screen opens
    // --------------------------------------------------

    useEffect(() => {

        loadWatchlist();

    }, []);


    // --------------------------------------------------
    // GET /watchlist
    // --------------------------------------------------

    async function loadWatchlist() {

        try {

            setLoading(true);

            const response = await fetch(
                `${API_URL}/watchlist`
            );


            if (!response.ok) {

                throw new Error(
                    `HTTP ${response.status}`
                );
            }


            const json = await response.json();


            console.log(
                "WATCHLIST:",
                json
            );


            setWatchlist(
                json.watchlist || []
            );

        } catch (error) {

            console.log(
                "WATCHLIST ERROR:",
                error
            );

            Alert.alert(
                "Error",
                "Could not load your watchlist."
            );

        } finally {

            setLoading(false);
        }
    }


    // --------------------------------------------------
    // POST /watchlist
    // --------------------------------------------------

    async function addKeyword() {

        const value = keyword.trim();


        if (!value) {

            Alert.alert(
                "Enter a restaurant",
                "Please enter a restaurant name or keyword."
            );

            return;
        }


        try {

            setAdding(true);


            const response = await fetch(
                `${API_URL}/watchlist`,
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json",
                    },

                    body: JSON.stringify({
                        keyword: value,
                    }),
                }
            );


            const json = await response.json();


            console.log(
                "ADD WATCHLIST:",
                json
            );


            if (!response.ok) {

                throw new Error(
                    json.detail ||
                    "Could not add restaurant."
                );
            }


            // Clear input
            setKeyword("");


            // Refresh list
            await loadWatchlist();

        } catch (error) {

            console.log(
                "ADD WATCHLIST ERROR:",
                error
            );

            Alert.alert(
                "Error",
                "Could not add restaurant to watchlist."
            );

        } finally {

            setAdding(false);
        }
    }


    // --------------------------------------------------
    // DELETE /watchlist/{keyword}
    // --------------------------------------------------

    async function removeKeyword(
        value: string
    ) {

        try {

            const response = await fetch(
                `${API_URL}/watchlist/${encodeURIComponent(
                    value
                )}`,
                {
                    method: "DELETE",
                }
            );


            const json = await response.json();


            console.log(
                "REMOVE WATCHLIST:",
                json
            );


            if (!response.ok) {

                throw new Error(
                    json.detail ||
                    "Could not remove restaurant."
                );
            }


            // Refresh list
            await loadWatchlist();

        } catch (error) {

            console.log(
                "REMOVE WATCHLIST ERROR:",
                error
            );

            Alert.alert(
                "Error",
                "Could not remove restaurant."
            );
        }
    }


    // --------------------------------------------------
    // Confirm before removing
    // --------------------------------------------------

    function confirmRemove(
        value: string
    ) {

        Alert.alert(
            "Remove from watchlist?",
            value,
            [
                {
                    text: "Cancel",
                    style: "cancel",
                },

                {
                    text: "Remove",
                    style: "destructive",

                    onPress: () =>
                        removeKeyword(value),
                },
            ]
        );
    }


    // --------------------------------------------------
    // Loading
    // --------------------------------------------------

    if (loading) {

        return (

            <View style={styles.center}>

                <ActivityIndicator
                    size="large"
                    color="#007AFF"
                />

                <Text style={styles.loadingText}>
                    Loading Watchlist...
                </Text>

            </View>
        );
    }


    // --------------------------------------------------
    // Screen
    // --------------------------------------------------

    return (

        <View style={styles.container}>

            <Text style={styles.title}>
                Watchlist
            </Text>


            <Text style={styles.subtitle}>
                Get notified when a restaurant
                receives a new inspection.
            </Text>


            {/* ---------------------------------------- */}
            {/* Add restaurant */}
            {/* ---------------------------------------- */}

            <View style={styles.inputRow}>

                <TextInput
                    style={styles.input}

                    placeholder="Restaurant or keyword"

                    placeholderTextColor="#999"

                    value={keyword}

                    onChangeText={
                        setKeyword
                    }

                    autoCapitalize="words"

                    returnKeyType="done"

                    onSubmitEditing={
                        addKeyword
                    }
                />


                <TouchableOpacity

                    style={[
                        styles.addButton,

                        adding &&
                        styles.disabledButton,
                    ]}

                    onPress={
                        addKeyword
                    }

                    disabled={adding}
                >

                    {adding ? (

                        <ActivityIndicator
                            color="#fff"
                        />

                    ) : (

                        <Text
                            style={styles.addText}
                        >
                            Add
                        </Text>

                    )}

                </TouchableOpacity>

            </View>


            {/* ---------------------------------------- */}
            {/* Count */}
            {/* ---------------------------------------- */}

            <Text style={styles.count}>

                {watchlist.length === 1
                    ? "1 restaurant watched"
                    : `${watchlist.length} restaurants watched`
                }

            </Text>


            {/* ---------------------------------------- */}
            {/* Watchlist */}
            {/* ---------------------------------------- */}

            <FlatList

                data={watchlist}

                keyExtractor={(item) =>
                    item
                }

                showsVerticalScrollIndicator={
                    false
                }

                ListEmptyComponent={

                    <View
                        style={styles.emptyContainer}
                    >

                        <Text
                            style={styles.emptyIcon}
                        >
                            ★
                        </Text>

                        <Text
                            style={styles.emptyTitle}
                        >
                            Your watchlist is empty
                        </Text>

                        <Text
                            style={styles.emptyText}
                        >
                            Add a restaurant above to
                            start watching it.
                        </Text>

                    </View>
                }


                renderItem={({ item }) => (

                    <View
                        style={styles.card}
                    >

                        <View
                            style={styles.cardLeft}
                        >

                            <Text
                                style={styles.star}
                            >
                                ★
                            </Text>


                            <Text
                                style={styles.keyword}
                                numberOfLines={2}
                            >
                                {item}
                            </Text>

                        </View>


                        <TouchableOpacity

                            style={
                                styles.removeButton
                            }

                            onPress={() =>
                                confirmRemove(
                                    item
                                )
                            }
                        >

                            <Text
                                style={
                                    styles.removeText
                                }
                            >
                                Remove
                            </Text>

                        </TouchableOpacity>

                    </View>

                )}

            />

        </View>
    );
}


// --------------------------------------------------
// Styles
// --------------------------------------------------

const styles = StyleSheet.create({

    container: {
        flex: 1,
        padding: 20,
        paddingTop: 60,
        backgroundColor: "#f5f5f5",
    },


    center: {
        flex: 1,
        justifyContent: "center",
        alignItems: "center",
        backgroundColor: "#f5f5f5",
    },


    loadingText: {
        marginTop: 10,
        color: "#666",
    },


    title: {
        fontSize: 32,
        fontWeight: "bold",
        color: "#111",
        marginBottom: 5,
    },


    subtitle: {
        fontSize: 15,
        color: "#666",
        marginBottom: 20,
    },


    inputRow: {
        flexDirection: "row",
        marginBottom: 12,
    },


    input: {
        flex: 1,

        backgroundColor: "#fff",

        borderWidth: 1,
        borderColor: "#ddd",

        borderRadius: 10,

        paddingHorizontal: 15,
        paddingVertical: 12,

        fontSize: 16,

        marginRight: 10,
    },


    addButton: {
        backgroundColor: "#007AFF",

        borderRadius: 10,

        minWidth: 70,

        justifyContent: "center",
        alignItems: "center",

        paddingHorizontal: 15,
    },


    disabledButton: {
        opacity: 0.6,
    },


    addText: {
        color: "#fff",
        fontSize: 16,
        fontWeight: "bold",
    },


    count: {
        color: "#777",
        fontSize: 14,
        marginBottom: 12,
    },


    card: {
        backgroundColor: "#fff",

        padding: 15,

        borderRadius: 12,

        marginBottom: 10,

        flexDirection: "row",

        alignItems: "center",

        justifyContent: "space-between",
    },


    cardLeft: {
        flex: 1,

        flexDirection: "row",

        alignItems: "center",

        marginRight: 10,
    },


    star: {
        color: "#FFB300",
        fontSize: 20,
        marginRight: 10,
    },


    keyword: {
        flex: 1,

        fontSize: 17,

        fontWeight: "600",

        color: "#222",
    },


    removeButton: {
        backgroundColor: "#ff3b30",

        paddingHorizontal: 12,
        paddingVertical: 8,

        borderRadius: 8,
    },


    removeText: {
        color: "#fff",

        fontSize: 14,

        fontWeight: "bold",
    },


    emptyContainer: {
        alignItems: "center",

        marginTop: 70,

        paddingHorizontal: 30,
    },


    emptyIcon: {
        fontSize: 40,

        color: "#ccc",

        marginBottom: 10,
    },


    emptyTitle: {
        fontSize: 20,

        fontWeight: "bold",

        color: "#444",

        marginBottom: 5,
    },


    emptyText: {
        textAlign: "center",

        color: "#888",

        fontSize: 15,
    },
});

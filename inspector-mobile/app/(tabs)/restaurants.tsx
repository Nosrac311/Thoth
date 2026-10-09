import React, { useEffect, useState } from "react";
import {
    View,
    Text,
    TextInput,
    FlatList,
    StyleSheet,
    ActivityIndicator,
} from "react-native";

const API_URL = "https://thoth-u72b.onrender.com";

type Inspection = {
    restaurant: string;
    date: string;
    score: string | null;
    grade: string | null;
    source: string;
    location: string | null;
    inspector_id: string | null;
    state_id: string;
    adress: string;
};

export default function Restaurants() {
    const [search, setSearch] = useState("");
    const [results, setResults] = useState<Inspection[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    useEffect(() => {
        const name = search.trim();

        if (!name) {
            setResults([]);
            setError("");
            setLoading(false);
            return;
        }

        let cancelled = false;

        const timer = setTimeout(async () => {
            setLoading(true);
            setError("");

            try {
                const response = await fetch(
                    `${API_URL}/restaurants/search?name=${encodeURIComponent(name)}&limit=30`
                );

                if (!response.ok) {
                    throw new Error("Search failed");
                }

                const data = await response.json();

                if (!cancelled) {
                    setResults(data.results ?? []);
                }
            } catch {
                if (!cancelled) {
                    setError(
                        "Couldn't load inspections. Please try again."
                    );
                    setResults([]);
                }
            } finally {
                if (!cancelled) {
                    setLoading(false);
                }
            }
        }, 300);

        return () => {
            cancelled = true;
            clearTimeout(timer);
        };
    }, [search]);

    return (
        <View style={styles.container}>
            <Text style={styles.title}>Restaurants</Text>

            <Text style={styles.subtitle}>
                Search restaurants and their inspection records.
            </Text>

            <TextInput
                style={styles.search}
                placeholder="Search restaurant name..."
                value={search}
                onChangeText={setSearch}
                autoCapitalize="none"
                autoCorrect={false}
                clearButtonMode="while-editing"
                accessibilityLabel="Search restaurants"
            />

            {loading && (
                <ActivityIndicator
                    style={styles.loader}
                    color="#2563EB"
                />
            )}

            {!!error && (
                <Text style={styles.error}>{error}</Text>
            )}

            {!loading && !error && search.trim() !== "" && (
                <Text style={styles.count}>
                    {results.length} inspection record(s) found
                </Text>
            )}

            <FlatList
                data={results}
                keyExtractor={(item, index) =>
                    `${item.source}-${item.state_id}-${item.date}-${item.adress}-${index}`
                }
                keyboardShouldPersistTaps="handled"
                contentContainerStyle={styles.list}
                ListEmptyComponent={
                    !loading && !error && search.trim() !== "" ? (
                        <Text style={styles.empty}>
                            No matching inspections found.
                        </Text>
                    ) : null
                }
                renderItem={({ item }) => (
                    <View style={styles.card}>
                        <Text style={styles.restaurant}>
                            {item.restaurant}
                        </Text>

                        {!!item.location && (
                            <Text style={styles.location}>
                                {item.location}
                            </Text>
                        )}

                        <View style={styles.details}>
                            <View style={styles.detail}>
                                <Text style={styles.label}>
                                    Inspection date
                                </Text>
                                <Text style={styles.value}>
                                    {item.date || "N/A"}
                                </Text>
                            </View>

                            <View style={styles.detail}>
                                <Text style={styles.label}>
                                    Score
                                </Text>
                                <Text style={styles.score}>
                                    {item.score || "N/A"}
                                </Text>
                            </View>
                        </View>

                        <View style={styles.details}>
                            <View style={styles.detail}>
                                <Text style={styles.label}>
                                    Grade
                                </Text>
                                <Text style={styles.value}>
                                    {item.grade || "N/A"}
                                </Text>
                            </View>

                            <View style={styles.detail}>
                                <Text style={styles.label}>
                                    Source
                                </Text>
                                <Text style={styles.value}>
                                    {item.source || "N/A"}
                                </Text>
                            </View>

                            <View style={styles.detail}>
                                <Text style={styles.label}>
                                    Location
                                </Text>
                                <Text style={styles.value}>
                                    {item.adress || "N/A"}
                                </Text>
                            </View>
                        </View>
                    </View>
                )}
            />
        </View>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        padding: 20,
        paddingTop: 60,
        backgroundColor: "#F8FAFC",
    },
    title: {
        fontSize: 32,
        fontWeight: "bold",
        color: "#111827",
    },
    subtitle: {
        marginTop: 8,
        marginBottom: 20,
        color: "#6B7280",
        fontSize: 15,
    },
    search: {
        height: 50,
        borderWidth: 1,
        borderColor: "#D1D5DB",
        borderRadius: 12,
        paddingHorizontal: 15,
        backgroundColor: "#FFFFFF",
        fontSize: 16,
    },
    loader: {
        marginTop: 16,
    },
    count: {
        marginTop: 16,
        color: "#6B7280",
        fontSize: 13,
    },
    error: {
        marginTop: 16,
        color: "#B91C1C",
    },
    list: {
        paddingTop: 16,
        paddingBottom: 30,
    },
    card: {
        padding: 16,
        marginBottom: 12,
        backgroundColor: "#FFFFFF",
        borderRadius: 14,
        borderWidth: 1,
        borderColor: "#E5E7EB",
    },
    restaurant: {
        fontSize: 18,
        fontWeight: "bold",
        color: "#111827",
    },
    location: {
        marginTop: 5,
        color: "#6B7280",
        fontSize: 14,
    },
    details: {
        flexDirection: "row",
        marginTop: 16,
    },
    detail: {
        flex: 1,
    },
    label: {
        marginBottom: 5,
        color: "#6B7280",
        fontSize: 12,
    },
    value: {
        color: "#374151",
        fontSize: 14,
    },
    score: {
        color: "#15803D",
        fontSize: 20,
        fontWeight: "bold",
    },
    empty: {
        textAlign: "center",
        marginTop: 24,
        color: "#6B7280",
    },
});
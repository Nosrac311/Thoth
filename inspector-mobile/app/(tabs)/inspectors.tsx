import { useEffect, useState } from "react";
import {
    View,
    Text,
    FlatList,
    StyleSheet
} from "react-native";


const API = "http://192.168.0.4:8000";


export default function Inspectors() {

    const [data, setData] = useState<any>(null);


    useEffect(() => {
        loadInspector();
    }, []);


    async function loadInspector() {
        try {
            const response = await fetch(
                `${API}/inspectors/12345`
            );

            console.log("STATUS:", response.status);

            const json = await response.json();

            console.log(json);

            setData(json);

        } catch (error) {
            console.log("INSPECTOR ERROR:", error);
        }
    }


    if (!data) {
        return (
            <View style={styles.center}>
                <Text>
                    Loading Inspector...
                </Text>
            </View>
        );
    }


    return (

        <View style={styles.container}>

            <Text style={styles.title}>
                Inspector {data.inspector_id}
            </Text>


            <View style={styles.card}>

                <Text style={styles.heading}>
                    Statistics
                </Text>

                <Text>
                    Total Inspections:
                    {" "}
                    {data.statistics.total_inspections}
                </Text>

                <Text>
                    Average Score:
                    {" "}
                    {data.statistics.average_score}
                </Text>

            </View>



            <Text style={styles.heading}>
                Recent Inspections
            </Text>


            <FlatList

                data={data.history}

                renderItem={({ item }) => (

                    <View style={styles.card}>

                        <Text style={styles.restaurant}>
                            {item.restaurant}
                        </Text>

                        <Text>
                            Date: {item.date}
                        </Text>

                        <Text>
                            Score: {item.score}
                        </Text>

                        <Text>
                            Grade: {item.grade}
                        </Text>

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
        paddingTop: 60
    },

    center: {
        flex: 1,
        justifyContent: "center",
        alignItems: "center"
    },

    title: {
        fontSize: 30,
        fontWeight: "bold"
    },

    heading: {
        fontSize: 22,
        fontWeight: "bold",
        marginVertical: 10
    },

    card: {
        backgroundColor: "#fff",
        padding: 15,
        borderRadius: 12,
        marginBottom: 10
    },

    restaurant: {
        fontSize: 18,
        fontWeight: "bold"
    }

});
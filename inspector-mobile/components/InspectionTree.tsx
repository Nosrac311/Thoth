import { useState } from "react";
import {
    View,
    Text,
    Pressable,
    FlatList,
    StyleSheet
} from "react-native";


type Inspection = {
    restaurant: string;
    date: string;
    score: number;
    grade: string;
    source: string;
    county: string;
    inspector_id: string;
};


export default function InspectionTree({
    inspections
}: {
    inspections: Inspection[];
}) {


    const grouped = groupByCounty(inspections);


    return (

        <FlatList

            data={Object.entries(grouped)}

            keyExtractor={([county]) => county}

            renderItem={({ item }) => (

                <CountyNode
                    county={item[0]}
                    inspections={item[1]}
                />

            )}

        />

    );
}



function groupByCounty(
    inspections: Inspection[]
) {

    const counties: any = {};


    inspections.forEach(item => {

        if (!counties[item.county]) {
            counties[item.county] = [];
        }

        counties[item.county].push(item);

    });


    return counties;

}



function CountyNode({
    county,
    inspections
}: any) {


    const [open, setOpen] = useState(false);


    const inspectors = groupByInspector(
        inspections
    );


    return (

        <View>

            <Pressable
                style={styles.county}
                onPress={() => setOpen(!open)}
            >

                <Text>
                    {open ? "▼" : "▶"} {county}
                    ({inspections.length})
                </Text>

            </Pressable>


            {open &&

                Object.entries(inspectors).map(
                    ([id, rows]: any) => (

                        <InspectorNode
                            key={id}
                            id={id}
                            inspections={rows}
                        />

                    ))

            }

        </View>

    );

}



function groupByInspector(
    inspections: Inspection[]
) {

    const result: any = {};


    inspections.forEach(item => {

        if (!result[item.inspector_id]) {
            result[item.inspector_id] = [];
        }

        result[item.inspector_id].push(item);

    });


    return result;

}




function InspectorNode({
    id,
    inspections
}: any) {

    const [open, setOpen] = useState(false);


    return (

        <View style={styles.inspector}>

            <Pressable
                onPress={() => setOpen(!open)}
            >

                <Text>
                    {open ? "▼" : "▶"}
                    Inspector {id}
                    ({inspections.length})
                </Text>

            </Pressable>


            {open && inspections.map(
                (item: Inspection, index: number) => (

                    <View
                        key={index}
                        style={styles.inspection}
                    >

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

                        <Text>
                            Inspector: {item.inspector_id}
                        </Text>


                    </View>

                ))}


        </View>

    );

}




const styles = StyleSheet.create({

    county: {
        backgroundColor: "#ddd",
        padding: 15,
        marginBottom: 5,
        borderRadius: 8
    },

    inspector: {
        paddingLeft: 20,
        paddingVertical: 10
    },

    inspection: {
        backgroundColor: "#fff",
        padding: 12,
        marginLeft: 20,
        marginTop: 8,
        borderRadius: 10
    },

    restaurant: {
        fontWeight: "bold",
        fontSize: 16
    }

});
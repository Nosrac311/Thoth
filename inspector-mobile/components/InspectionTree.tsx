import { useEffect, useState } from "react";
import {
  View,
  Text,
  Pressable,
  FlatList,
  StyleSheet,
} from "react-native";

type Inspection = {
  restaurant: string;
  date: string;
  score: number;
  grade: string;
  source: string;
  county: string;
  inspector_id: string;
  location: string;
};

type InspectionTreeProps = {
  inspections: Inspection[];
  expandAll: boolean;
};

export default function InspectionTree({
  inspections,
  expandAll,
}: InspectionTreeProps) {
  const grouped = groupByCounty(inspections);

  return (
    <FlatList
      data={Object.entries(grouped)}
      keyExtractor={([county]) => county}
      renderItem={({ item }) => (
        <CountyNode
          county={item[0]}
          inspections={item[1]}
          expandAll={expandAll}
        />
      )}
    />
  );
}

function groupByCounty(inspections: Inspection[]) {
  const counties: Record<string, Inspection[]> = {};

  inspections.forEach((item) => {
    const county = item.county || "Unknown County";

    if (!counties[county]) {
      counties[county] = [];
    }

    counties[county].push(item);
  });

  return counties;
}

function groupByInspector(inspections: Inspection[]) {
  const result: Record<string, Inspection[]> = {};

  inspections.forEach((item) => {
    const id = item.inspector_id || "Unknown";

    if (!result[id]) {
      result[id] = [];
    }

    result[id].push(item);
  });

  return result;
}

function CountyNode({
  county,
  inspections,
  expandAll,
}: {
  county: string;
  inspections: Inspection[];
  expandAll: boolean;
}) {
  const [open, setOpen] = useState(false);
  const inspectors = groupByInspector(inspections);

  useEffect(() => {
    setOpen(expandAll);
  }, [expandAll]);

  return (
    <View>
      <Pressable
        style={styles.county}
        onPress={() => setOpen((previous) => !previous)}
      >
        <Text style={styles.nodeText}>
          {open ? "▼" : "▶"} {county} ({inspections.length})
        </Text>
      </Pressable>

      {open &&
        Object.entries(inspectors).map(([id, rows]) => (
          <InspectorNode
            key={id}
            id={id}
            inspections={rows}
            expandAll={expandAll}
          />
        ))}
    </View>
  );
}

function InspectorNode({
  id,
  inspections,
  expandAll,
}: {
  id: string;
  inspections: Inspection[];
  expandAll: boolean;
}) {
  const [open, setOpen] = useState(false);

  useEffect(() => {
    setOpen(expandAll);
  }, [expandAll]);

  return (
    <View style={styles.inspector}>
      <Pressable
        onPress={() => setOpen((previous) => !previous)}
        style={styles.inspectorHeader}
      >
        <Text style={styles.nodeText}>
          {open ? "▼" : "▶"} Inspector {id} ({inspections.length})
        </Text>
      </Pressable>

      {open &&
        inspections.map((item, index) => (
          <View
            key={`${item.restaurant}-${item.date}-${index}`}
            style={styles.inspection}
          >
            <Text style={styles.restaurant}>{item.restaurant}</Text>
            <Text>Date: {item.date}</Text>
            <Text>Score: {item.score}</Text>
            <Text>Grade: {item.grade}</Text>
            <Text>Inspector: {item.inspector_id}</Text>
            <Text>
            Location: {item.location || "Location unavailable"}
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
    borderRadius: 8,
  },
  inspector: {
    paddingLeft: 20,
    paddingVertical: 10,
  },
  inspectorHeader: {
    paddingVertical: 5,
  },
  inspection: {
    backgroundColor: "#fff",
    padding: 12,
    marginLeft: 20,
    marginTop: 8,
    borderRadius: 10,
  },
  restaurant: {
    fontWeight: "bold",
    fontSize: 16,
  },
  nodeText: {
    fontSize: 15,
  },
});
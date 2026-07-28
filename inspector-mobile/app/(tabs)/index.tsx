import InspectionTree from "@/components/InspectionTree";
import { useEffect, useState } from "react";
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  ActivityIndicator,
} from "react-native";


const API_URL = "http://192.168.0.4:8000";

type Inspection = {
  restaurant: string;
  date: string;
  score: number;
  grade: string;
  county: string;
  inspector_id: string;
};

export default function Dashboard() {
  const [total, setTotal] = useState(0);
  const [inspections, setInspections] = useState<Inspection[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboard();
  }, []);

  async function loadDashboard() {
    try {
      const statsResponse = await fetch(`${API_URL}/stats`);
      const stats = await statsResponse.json();

      setTotal(stats.total_inspections);

      const inspectionsResponse = await fetch(
        `${API_URL}/inspections/latest`
      );

      const inspectionData = await inspectionsResponse.json();

      setInspections(inspectionData.inspections);

    } catch (error) {
      console.log("API ERROR:", error);
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" />
      </View>
    );
  }

  return (
    <View style={styles.container}>

      <Text style={styles.title}>
        Thoth Dashboard
      </Text>

      <View style={styles.card}>
        <Text style={styles.label}>
          Total Inspections
        </Text>

        <Text style={styles.number}>
          {total}
        </Text>
      </View>


      <Text style={styles.section}>
        Latest Inspections
      </Text>


      <InspectionTree
        inspections={inspections}
      />

    </View>
  );
}


const styles = StyleSheet.create({

  container: {
    flex: 1,
    padding: 20,
    backgroundColor: "#f5f5f5",
    paddingTop: 60,
  },

  center: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
  },

  title: {
    fontSize: 32,
    fontWeight: "bold",
    marginBottom: 20,
  },

  card: {
    backgroundColor: "white",
    padding: 20,
    borderRadius: 15,
    marginBottom: 20,
  },

  label: {
    fontSize: 16,
    color: "#666",
  },

  number: {
    fontSize: 40,
    fontWeight: "bold",
  },

  section: {
    fontSize: 22,
    fontWeight: "bold",
    marginBottom: 10,
  },

  inspection: {
    backgroundColor: "white",
    padding: 15,
    borderRadius: 10,
    marginBottom: 10,
  },

  restaurant: {
    fontSize: 18,
    fontWeight: "bold",
  },

});
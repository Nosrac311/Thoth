import { useEffect, useState } from "react";
import {
    getLatest,
    getStats,
    searchRestaurant,
} from "../services/api";

export default function Dashboard() {
    const [stats, setStats] = useState(null);
    const [inspections, setInspections] = useState([]);
    const [search, setSearch] = useState("");
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    useEffect(() => {
        loadDashboard();
    }, []);

    async function loadDashboard() {
        try {
            setLoading(true);

            const [statsData, latestData] = await Promise.all([
                getStats(),
                getLatest(),
            ]);

            setStats(statsData);
            setInspections(latestData.inspections);
        } catch (err) {
            console.error(err);
            setError("Failed to load dashboard.");
        } finally {
            setLoading(false);
        }
    }

    async function handleSearch(e) {
        e.preventDefault();

        if (!search.trim()) {
            loadDashboard();
            return;
        }

        try {
            const data = await searchRestaurant(search);
            setInspections(data.results);
        } catch (err) {
            console.error(err);
        }
    }

    if (loading) {
        return <h2>Loading...</h2>;
    }

    return (
        <div className="container">
            <h1>Restaurant Inspection Dashboard</h1>

            <p>
                Browse the latest inspections and search inspection history by
                restaurant.
            </p>

            {error && <p className="error">{error}</p>}

            <div className="stats">
                <div className="card">
                    <h2>{stats?.total_inspections ?? 0}</h2>
                    <p>Inspections</p>
                </div>
            </div>

            <form onSubmit={handleSearch} className="search-form">
                <input
                    type="text"
                    placeholder="Search for a restaurant..."
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                />

                <button type="submit">Search</button>
            </form>

            <h2>Latest Inspections</h2>

            <table>
                <thead>
                    <tr>
                        <th>Restaurant</th>
                        <th>Date</th>
                        <th>Score</th>
                        <th>Grade</th>
                        <th>Source</th>
                    </tr>
                </thead>

                <tbody>
                    {inspections.map((inspection, index) => (
                        <tr key={index}>
                            <td>{inspection.restaurant}</td>
                            <td>{inspection.date}</td>
                            <td>{inspection.score}</td>
                            <td>
                                <span className={`grade grade-${inspection.grade}`}>
                                    {inspection.grade}
                                </span>
                            </td>
                            <td>{inspection.source}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}
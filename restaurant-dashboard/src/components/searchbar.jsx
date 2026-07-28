const [query, setQuery] = useState("");
const [results, setResults] = useState([]);

async function search() {
    const data = await searchRestaurants(query);
    setResults(data.results);
}
// App.jsx
import { useEffect, useState } from "react";
import MarketPulse from "./Components/MarketPuls";
import "./App.css";

function App() {
  const [data, setData] = useState("");

  useEffect(() => {
    fetch("http://127.0.0.1:8000/api/greet")
      .then((response) => response.json())
      .then((data) => setData(data.message))
      .catch((error) => console.error(error));
  }, []);

  return (
    <>
      <MarketPulse></MarketPulse>
    </>
  );
}

export default App;

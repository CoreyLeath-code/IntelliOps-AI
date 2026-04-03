import React, { useState } from "react";

interface PredictionResult {
  prediction: number | number[];
}

function App() {
  const [result, setResult] = useState<PredictionResult | null>(null);

  const sendRequest = async () => {
    const res = await fetch("http://localhost:8080/predict", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        features: [1, 2, 3, 4],
      }),
    });

    const data: PredictionResult = await res.json();
    setResult(data);
  };

  return (
    <div style={{ padding: "20px" }}>
      <h1>IntelliOps AI Dashboard</h1>
      <button onClick={sendRequest}>Run Prediction</button>
      <pre>{JSON.stringify(result, null, 2)}</pre>
    </div>
  );
}

export default App;

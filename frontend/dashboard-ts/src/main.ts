async function predict() {
  const res = await fetch("http://localhost:8080/predict", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ features: [5.1, 3.5, 1.4, 0.2] })
  });
  const data = await res.json();
  const el = document.getElementById("result");
  if (el) el.innerText = JSON.stringify(data);
}

(window as any).predict = predict;

import streamlit as st
import requests
import pandas as pd

st.title("📊 IntelliOps AI Dashboard")

st.write("Run real-time predictions and view results")

# Input fields
f1 = st.number_input("Feature 1", value=5.1)
f2 = st.number_input("Feature 2", value=3.5)
f3 = st.number_input("Feature 3", value=1.4)
f4 = st.number_input("Feature 4", value=0.2)

if st.button("Predict"):
    response = requests.post(
        "http://localhost:8080/predict",
        json={"features": [f1, f2, f3, f4]}
    )
    result = response.json()
    st.success(f"Prediction: {result['prediction']}")

# Simple history (mock for now)
data = pd.DataFrame({
    "Feature1": [f1],
    "Prediction": [str(result['prediction'])] if 'result' in locals() else ["N/A"]
})

st.write("Recent Predictions")
st.dataframe(data)

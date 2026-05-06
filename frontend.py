import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="AI Sentiment Analysis", page_icon="🚀", layout="centered")

st.title("🚀 AI Sentiment Analysis App")
st.write("Analyze text sentiment and monitor system performance in real-time.")

st.info(
    "⚠️ **Model Limitation:** This model was trained on product and movie reviews. "
    "It is not suitable for personal, demographic, or identity-related statements and may produce biased or inaccurate results for such inputs."
)

user_input = st.text_area("Enter your text:", height=150, placeholder="e.g., The product quality is amazing!")

API_BASE_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

if st.button("Analyze Sentiment", use_container_width=True):
    if user_input.strip() == "":
        st.warning("Please enter some text.")
    else:
        with st.spinner("AI is processing..."):
            try:
                response = requests.post(f"{API_BASE_URL}/analyze", json={"text": user_input})
                if response.status_code == 200:
                    result = response.json()
                    st.success("Analysis Complete!")
                    label = result["label"]
                    score = result["score"]
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Sentiment", value=f"🟢 {label}" if label == "POSITIVE" else f"🔴 {label}")
                    with col2:
                        st.metric("Confidence Score", value=f"{score:.4f}")
                else:
                    st.error(f"API Error: {response.status_code}")
            except requests.exceptions.ConnectionError:
                st.error(f"Connection Error: Could not connect to the backend API at {API_BASE_URL}. Ensure the FastAPI server is running.")
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")

st.divider()

st.subheader("📊 Analytics Dashboard")

try:
    stats_response = requests.get(f"{API_BASE_URL}/stats")
    logs_response = requests.get(f"{API_BASE_URL}/logs")

    if stats_response.status_code == 200 and logs_response.status_code == 200:
        stats = stats_response.json()
        logs = logs_response.json()

        if stats:
            counts = pd.DataFrame(list(stats.items()), columns=["Sentiment", "Count"])
            fig = px.pie(
                counts, values="Count", names="Sentiment",
                color="Sentiment",
                color_discrete_map={"POSITIVE": "#00CC96", "NEGATIVE": "#EF553B"},
                hole=0.4,
                title="Total Sentiment Distribution"
            )
            st.plotly_chart(fig, use_container_width=True)

            if logs:
                st.write("---")
                st.subheader("📜 Recent History")
                df = pd.DataFrame(logs)
                st.table(df)
        else:
            st.info("No data available yet. Run an analysis to see results!")
    else:
        st.error("Could not load analytics data from the API.")
except requests.exceptions.ConnectionError:
    st.warning("Analytics unavailable: backend is not reachable.")
except Exception as e:
    st.error(f"Dashboard Error: {e}")

import os
import chromadb
import streamlit as st
from google import genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

client_ai = genai.Client(api_key=api_key)

st.set_page_config(
    page_title="Customer Insights Assistant",
    layout="wide",
    initial_sidebar_state="collapsed"
)

client_db = chromadb.PersistentClient(path="./chroma_db")
collection = client_db.get_collection("customer_insights")

st.set_page_config(
    page_title="AI Customer Insights Assistant",
    page_icon="📊",
    layout="wide"
)

st.title("AI Customer Insights Assistant")
st.caption("Customer Segmentation + Churn Prediction + RAG")

question = st.text_input(
    "Ask a business question",
    placeholder="Which segment contributes most revenue?"
)

if st.button("Analyze") and question:

    with st.spinner("Analyzing..."):

        docs = collection.get()

        context = "\n\n---\n\n".join(
            docs["documents"]
        )

        prompt = f"""
You are a customer analytics assistant.

Use ONLY the provided context.

Context:
{context}

Question:
{question}

Provide:
1. Direct Answer
2. Supporting Metrics
3. Recommended Action
4. Source Segments Used
"""

        response = client_ai.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        st.markdown(response.text)

        st.divider()

        st.subheader("Knowledge Sources")

        for source in docs["ids"]:
            st.write(source)
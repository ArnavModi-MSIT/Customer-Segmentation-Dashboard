import os
import sys
import chromadb
from google import genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("Error: GEMINI_API_KEY not found in .env file")
    sys.exit(1)

client_ai = genai.Client(api_key=api_key)

try:
    client_db = chromadb.PersistentClient(path="./chroma_db")
    collection = client_db.get_collection("customer_insights")
except Exception as e:
    print("Error: Vector database not initialized.")
    print(f"Details: {e}")
    sys.exit(1)


def retrieve_documents():
    try:
        results = collection.get()

        documents = results["documents"]
        document_ids = results["ids"]

        return documents, document_ids

    except Exception as e:
        print(f"Error retrieving documents: {e}")
        return [], []


def generate_answer(query, documents):
    if not documents:
        return "No documents found in knowledge base."

    context = "\n\n---\n\n".join(documents)

    prompt = f"""
You are a customer analytics assistant for an e-commerce company.

Use ONLY the provided context.

Rules:
- Do not invent information.
- Compare numerical values when answering.
- Use Revenue Share, Customer Count, Monetary Value,
  Frequency, Recency and RFM Score when available.
- If the user asks for the highest, largest, best or most,
  compare all relevant values and select the correct one.
- If information is unavailable, clearly state that.

Context:
{context}

Question:
{query}

Return:

1. Direct Answer
2. Supporting Metrics
3. Recommended Action
4. Source Segments Used
"""

    try:
        response = client_ai.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        return response.text

    except Exception as e:
        return f"Error generating response: {e}"


def main():
    print("\n=== Customer Insights RAG System ===\n")

    documents, document_ids = retrieve_documents()

    if not documents:
        print("No knowledge base documents found.")
        return

    print(f"Loaded {len(documents)} documents.\n")

    while True:
        query = input("Ask a question (or 'exit' to quit): ").strip()

        if query.lower() == "exit":
            break

        if not query:
            print("Please enter a valid question.\n")
            continue

        print("\nGenerating answer...\n")

        answer = generate_answer(query, documents)

        print("=" * 60)
        print("ANSWER")
        print("=" * 60)
        print(answer)

        print("\n" + "=" * 60)
        print("AVAILABLE SOURCES")
        print("=" * 60)

        for doc_id in document_ids:
            print(f"- {doc_id}")

        print("=" * 60 + "\n")


if __name__ == "__main__":
    main()

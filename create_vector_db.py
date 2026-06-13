import chromadb
from chromadb.utils import embedding_functions
from pathlib import Path
import sys

try:
    client = chromadb.PersistentClient(path="./chroma_db")
    
    # Use BGE-small embedding function (free, local)
    embedding_fn = embedding_functions.DefaultEmbeddingFunction()
    
    collection = client.get_or_create_collection(
        name="customer_insights",
        embedding_function=embedding_fn
    )
    
    knowledge_dir = Path("knowledge_base")
    
    if not knowledge_dir.exists():
        print(f"Error: {knowledge_dir} directory not found.")
        sys.exit(1)
    
    files = list(knowledge_dir.glob("*.txt"))
    if not files:
        print(f"Error: No .txt files found in {knowledge_dir}")
        sys.exit(1)
    
    for file in files:
        with open(file, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Extract segment name from filename or document
        doc_id = file.stem
        doc_type = "segment" if "churn" not in doc_id else "churn_report"
        
        collection.add(
            documents=[content],
            metadatas=[{"doc_type": doc_type, "source": doc_id}],
            ids=[doc_id]
        )
    
    print(f"Successfully loaded {collection.count()} documents to ChromaDB")
    print(f"Collection: {collection.name}")
    
except Exception as e:
    print(f"Error: Failed to create vector database: {e}")
    sys.exit(1)
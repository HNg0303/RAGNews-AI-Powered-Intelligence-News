from langchain_huggingface import HuggingFaceEmbeddings
from typing import List

class Embedder():
    def __init__(self, model_name = "BAAI/bge-base-en-v1.5"):
        """Constructor: Initializing an embedder class (containing an Langchain embeddings interface)"""
        self.embeddings = HuggingFaceEmbeddings(model_name=model_name)
    
    def embed_documents(self, documents: List[str]) -> List[List[float]]:
        doc_embeddings = self.embeddings.embed_documents(documents)
        print(f"Number of docs: {len(doc_embeddings)}")
        print(f"\n Embedding dim: {len(doc_embeddings[0])}")
        return doc_embeddings
    
    def embed_query(self, query: str) -> List[float]:
        query_embedding = self.embeddings.embed_query(query)
        print(f"\n Embedding dim: {len(query_embedding)}")
        return query_embedding

if __name__ == "__main__":
    """
        Example Usage
    """
    model_name = "BAAI/bge-base-en-v1.5"
    print(f"Testing embedding model: {model_name}")
    embedder = Embedder(model_name=model_name)
    docs = [
        "Hello, My name is Grace.",
        "I am from Greece !"
    ]
    doc_embs = embedder.embed_documents(documents=docs)
    print(doc_embs)





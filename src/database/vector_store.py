from src.database.embedder import Embedder
from langchain_community.vectorstores import Zilliz
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from uuid import uuid4
import os

class VectorStore():
    """
    Define a VectorStore class that is initialized and integrated with Milvus:
        - Store vector database
        - Indexing documents with embedding function
        - Perform similarity search with cosine
    """
    def __init__(self, 
                 ZILLIZ_URI: str, 
                 ZILLIZ_API_KEY: str,
                 embedding_model: str = "BAAI/bge-base-en-v1.5"):
        self.vector_store = Zilliz(
            embedding_function=Embedder(model_name=embedding_model).embeddings,
            collection_name = "langchain_milvus",
            connection_args={
                "uri": ZILLIZ_URI,
                "token": ZILLIZ_API_KEY,
                "secure": True
            }
        )

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size = 500,
            chunk_overlap = 100
        )
    
    def add_documents(self, articles: list[dict]):
        """
            Convert list of dict of type: {
                id, title, content
            } -> Langchain Document: page_content and metadata.
        """
        documents = [
            Document(
            page_content = doc["content"],
            metadata = {
                "title": doc['title'],
                "id": doc["id"]
                }
        ) for doc in articles if doc is not None]

        all_splits = self.text_splitter.split_documents(documents)

        ids = [str(uuid4()) for _ in all_splits]
        self.vector_store.add_documents(documents = all_splits, ids = ids)

    def delete_documents(self, id: uuid4):
        """
            Delete a document based on id
        """
        self.vector_store.delete(ids = id)

    def similarity_search(self, query: str, topk: int):
        """
            Perform similarity search on vector database
            Output: List of Langchain Documents
        """
        results = self.vector_store.similarity_search(
            query = query,
            k = topk
        )
        return results

    def similarity_search_with_score(self, query: str, topk: int):
        """
            Perform similarity search on vector databases with score.
            Output: List of tuples(Langchain Document, score)
        """
        results = self.vector_store.similarity_search_with_score(
            query = query,
            k =topk
        )
        return results
    
if __name__ == "__main__":
    """
        Example usage
    """
    from dotenv import load_dotenv
    load_dotenv()
    # Connect to CLOUD ZILLIZ built upon Milvus.
    ZILLIZ_CLOUD_URI = os.getenv("ZILLIZ_CLOUD_URI")
    ZILLIZ_CLOUD_API_KEY = os.getenv("ZILLIZ_CLOUD_API_KEY")

    vs = VectorStore(ZILLIZ_URI = ZILLIZ_CLOUD_URI, ZILLIZ_API_KEY=ZILLIZ_CLOUD_API_KEY)
    print(f"Successfully Connect to Zilliz Cloud VB\n\n")

    #Indexing with raw data
    

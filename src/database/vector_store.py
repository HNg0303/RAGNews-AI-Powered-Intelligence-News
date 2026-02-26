from embedder import Embedder
from langchain_milvus import Milvus
from langchain_core.documents import Document

from uuid import uuid4

class VectorStore():
    """
    Define a VectorStore class that is initialized and integrated with Milvus:
        - Store vector database
        - Indexing documents with embedding function
        - Perform similarity search with cosine
    """
    def __init__(self, URI: str = "./milvus.db"):
        self.URI = URI
        self.vector_store = Milvus(
            embedding_function=Embedder().embeddings,
            collection_name = "langchain_milvus",
            connection_args={"uri": self.URI}
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
                "source": doc["src"]
                }
        ) for doc in articles]

        ids = [str(uuid4()) for _ in articles]
        self.vector_store.add_documents(documents = documents, ids = ids)

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
    vs = VectorStore()
    vs.add_documents([
        {
            "src": "CNN",
            "content": "Paris is France's Capital",
            "title": "France"
        }
    ])
    results = vs.similarity_search("Capital", topk = 1)
    print(results)
    

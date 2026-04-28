from src.database.vector_store import VectorStore
from langchain_classic.retrievers.contextual_compression import ContextualCompressionRetriever
from langchain_classic.retrievers.document_compressors import CrossEncoderReranker
from langchain_community.cross_encoders import HuggingFaceCrossEncoder

from langchain_core.documents import Document

class Retriever():
    """
        Two stage retrieval pipeline:
        - Vector Store as retriever for initial retrieval with embedding similarity.
        - Reranker processes each (query, doc) pair for reorder documents retrieved base on query's relevance.
    """
    def __init__(self, embedding_model: str, reranking_model: str, URI: str, API_KEY: str):
        self.vector_store = VectorStore(ZILLIZ_URI = URI, ZILLIZ_API_KEY=API_KEY, embedding_model=embedding_model)
        self.reranker = CrossEncoderReranker(model=HuggingFaceCrossEncoder(model_name = reranking_model), top_n = 5)
        self.compressor_retriever = ContextualCompressionRetriever(
            base_compressor=self.reranker,
            base_retriever=self.vector_store.vector_store.as_retriever(search_kwargs={"k": 20})
        )

    def retrieve(self, query: str) -> list[Document]:
        results = self.compressor_retriever.invoke(query)
        print(f"Number of top relevant documents retrieved: {len(results)}")
        print(f"Samples: {results}")
        return results

from src.engine.generation import ChatModel
from src.engine.retriever import Retriever

from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

from dotenv import load_dotenv
import os

"""
    Building a RAG Chain by stacking Runnable Objects to automatically invoke.
"""

def format_docs(docs: list[Document]):
        '''
            Format list of Langchain Document objects into a single context.
        '''
        return {"context": "/n/n".join(doc.page_content for doc in docs) }


class RAGChain():
    def __init__(self, embedding_model: str, reranking_model: str, chat_model: str, cloud_uri: str, cloud_api_key: str, google_api_key: str):
        self.retriever = Retriever(
            embedding_model=embedding_model,
            reranking_model=reranking_model,
            URI=cloud_uri,
            API_KEY=cloud_api_key
        )
        self.chat_model = ChatModel(
            model_name=chat_model,
            google_api_key = google_api_key
        )

        self.system_message = (
            "You are a helpful news assistant. Use the following pieces of "
            "retrieved context to answer the user's question. If you don't know "
            "the answer, just say that you don't know. Always cite your sources."
        )
        self.init_chain()
    

    def init_chain(self):
        # 1. 'context' is populated by the retriever + formatter
        # 2. 'question' is passed through from the initial input
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_message),
            ("human", "Context: {context}\n\nQuestion: {question}")
        ])

        self.chain = (
            {"context": self.retriever.compressor_retriever | RunnableLambda(format_docs), 
             "question": RunnablePassthrough()}
            | prompt
            | self.chat_model.chat_model
            | StrOutputParser()
        )

    def invoke(self, query: str):
        """
        Executes the RAG pipeline.
        Returns a string containing the generated answer based on newspaper sources.
        """
        try:
            return self.chain.invoke(query)
        except Exception as e:
            return f"Error processing query: {str(e)}"
        
if __name__ == "__main__":
    load_dotenv()
    ZILLIZ_CLOUD_URI = os.getenv("ZILLIZ_CLOUD_URI")
    ZILLIZ_CLOUD_API_KEY = os.getenv("ZILLIZ_CLOUD_API_KEY")

    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

    rag_agent = RAGChain(embedding_model="BAAI/bge-base-en-v1.5",
                         reranking_model="BAAI/bge-reranker-base",
                         chat_model="gemini-2.5-flash",
                         cloud_uri = ZILLIZ_CLOUD_URI,
                         cloud_api_key=ZILLIZ_CLOUD_API_KEY,
                         google_api_key = GOOGLE_API_KEY)
    rag_agent.init_chain()
    print("RAG Agent setup successfully !")
    query = "What is Trump planning to do today ?"
    result = rag_agent.invoke(query)
    print(f"Question: {query} \n\n\n Answer: {result}")
    







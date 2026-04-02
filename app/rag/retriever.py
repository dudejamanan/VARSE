from vector_store import faiss_store

def get_retriever(k=10):
    return faiss_store.vectorstore.as_retriever(search_kwargs={"k": k})
from langchain_community.vectorstores import FAISS
from core.embeddings import embedding

vectorstore = None
def build_vectorstore(all_chunks):
    global vectorstore

    vectorstore = FAISS.from_documents(all_chunks,embedding)
    return vectorstore


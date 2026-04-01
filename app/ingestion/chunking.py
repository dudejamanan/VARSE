from langchain_text_splitters import RecursiveCharacterTextSplitter
import numpy as np

def split_text(transcript):
    
    splitter = RecursiveCharacterTextSplitter(
    chunk_size=700,
    chunk_overlap=150
)

    chunks = splitter.create_documents([transcript])
    return chunks

def sample_chunks_evenly(chunks, num_samples=15):
    if len(chunks) <= num_samples:
        return "\n\n".join(chunk.page_content for chunk in chunks)

    indices = np.linspace(0, len(chunks) - 1, num_samples, dtype=int)
    sampled_texts = [chunks[i].page_content for i in indices]

    return "\n\n".join(sampled_texts)
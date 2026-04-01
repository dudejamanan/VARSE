
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain_ollama import OllamaLLM
import re
from urllib.parse import urlparse, parse_qs
from langchain_huggingface import HuggingFaceEmbeddings
import numpy as np


#step1 - extract yt video id from link
def extract_youtube_video_id(url: str) -> str:
    """
    Extracts the YouTube video ID from different types of YouTube URLs.
    Returns None if no valid ID is found.
    """

    # Case 1: Standard URL (youtube.com/watch?v=...)
    parsed_url = urlparse(url)
    
    if parsed_url.hostname in ["www.youtube.com", "youtube.com"]:
        query_params = parse_qs(parsed_url.query)
        if "v" in query_params:
            return query_params["v"][0]

    # Case 2: Short URL (youtu.be/...)
    if parsed_url.hostname == "youtu.be":
        return parsed_url.path.lstrip("/")

    # Case 3: Embedded URL (/embed/...)
    match = re.search(r"(?:embed\/|v\/|shorts\/)([a-zA-Z0-9_-]{11})", url)
    if match:
        return match.group(1)

    return None

url1 = "https://www.youtube.com/watch?v=K5KVEU3aaeQ"
url2 = "https://www.youtube.com/watch?v=_uQrJ0TkZlc"

video_id1 = extract_youtube_video_id(url1)
video_id2 = extract_youtube_video_id(url2)


#step2 - document ingestion

yt_api = YouTubeTranscriptApi()
try:
    transcript_list1= yt_api.fetch(video_id1,languages=["en"])
    transcript_list2= yt_api.fetch(video_id2,languages=["en"])

    transcript1 = " ".join(chunk.text for chunk in transcript_list1)
    transcript2 = " ".join(chunk.text for chunk in transcript_list2)

except TranscriptsDisabled:
    print("No captions available for this video")




#step3 - text splitting 


splitter = RecursiveCharacterTextSplitter(
    chunk_size=700,
    chunk_overlap=150
)

chunks1 = splitter.create_documents([transcript1])
chunks2 = splitter.create_documents([transcript2])



def sample_chunks_evenly(chunks, num_samples=15):
    indices = np.linspace(0, len(chunks) - 1, num_samples, dtype=int)
    
    sampled_texts = [chunks[i].page_content for i in indices]
    
    return "\n\n".join(sampled_texts)




analysis_prompt = PromptTemplate(
    template="""
You are an expert educator.

Analyze the following transcript and return STRICT JSON.

DO NOT GUESS missing topics.
ONLY extract what is present.

Return in this format:

{{
  "topics": ["topic1", "topic2", ...],
  "subtopics": ["sub1", "sub2"],
  "depth": "Beginner/Intermediate/Advanced",
  "clarity": "Low/Medium/High",
  "structure": "Well-structured/Scattered"
}}

Transcript:
{text}
""",
    input_variables=["text"]
)


comparision_prompt = PromptTemplate(
    template="""
You are an expert learning advisor.

You MUST make a clear decision.

Video 1 Analysis:
{analysis1}

Video 2 Analysis:
{analysis2}

Compare the two videos strictly based on:
- number of topics covered
- depth
- clarity
- structure

Rules:
- Be consistent (no contradictions)
- Do NOT be vague
- Choose ONLY ONE best video

Return in this format:

Comparison:
- Topics coverage: ...
- Depth: ...
- Clarity: ...
- Structure: ...

Winner:
<Video 1 or Video 2>

Reason:
<clear justification>
""",
input_variables=["analysis1","analysis2"]
)

llm = OllamaLLM(model="llama3.2")

sampled_text1=sample_chunks_evenly(chunks1)
sampled_text2=sample_chunks_evenly(chunks2)

analysis_prompt_final1 = analysis_prompt.invoke({"text":sampled_text1})
analysis_prompt_final2 = analysis_prompt.invoke({"text":sampled_text2})
analysis_answer1 = llm.invoke(analysis_prompt_final1)
analysis_answer2 = llm.invoke(analysis_prompt_final2)



comparision_prompt_final = comparision_prompt.invoke({"analysis1":analysis_answer1,"analysis2":analysis_answer2})
comparision = llm.invoke(comparision_prompt_final)
print(comparision)

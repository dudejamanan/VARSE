from core.llm import llm
from ingestion.chunking import sample_chunks_evenly
from analysis.prompts import analysis_prompt

def analyze_chunks(chunks):
    sampled_text = sample_chunks_evenly(chunks)
    prompt = analysis_prompt.invoke({"text": sampled_text})
    response = llm.invoke(prompt)
    return response
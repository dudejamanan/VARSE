from core.llm import llm
from ingestion.chunking import sample_chunks_evenly
from analysis.prompts import analysis_prompt
import json
from schemas.response import AnalysisResponse


def analyze_chunks(chunks):
    sampled_text = sample_chunks_evenly(chunks)

    prompt = analysis_prompt.invoke({"text": sampled_text})

    for attempt in range(2):  # retry once
        response = llm.invoke(prompt)

        try:
            parsed = json.loads(response)
            validated = AnalysisResponse(**parsed)
            analysis_dict = validated.model_dump()

            # normalize text fields
            analysis_dict["key_strengths"] = [s.lower() for s in analysis_dict["key_strengths"]]
            analysis_dict["key_weaknesses"] = [s.lower() for s in analysis_dict["key_weaknesses"]]
            analysis_dict["topics"] = [t.lower() for t in analysis_dict["topics"]]
            analysis_dict["subtopics"] = [s.lower() for s in analysis_dict["subtopics"]]
            
            return analysis_dict

        except Exception as e:
            print(f"Attempt {attempt+1} failed:", e)

    raise ValueError("LLM failed to return valid JSON after retries")
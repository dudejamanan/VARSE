from core.llm import llm
from ingestion.chunking import sample_chunks_evenly
from analysis.prompts import analysis_prompt
import json
from schemas.response import AnalysisResponse


# 🔹 CLEANER (robust)
def clean_json_response(response: str):
    response = response.strip()

    # remove markdown blocks
    if "```" in response:
        parts = response.split("```")
        for part in parts:
            if "{" in part and "}" in part:
                response = part
                break

    # extract JSON only
    start = response.find("{")
    end = response.rfind("}")

    if start != -1 and end != -1:
        response = response[start:end+1]

    return response


# 🔹 FIX learning_style
def fix_learning_style(parsed):
    allowed = {"theory", "hands_on", "visual", "code_along"}

    mapping = {
        "practical": "hands_on",
        "hands-on": "hands_on",
        "coding": "code_along",
        "implementation": "hands_on"
    }

    fixed = []

    for item in parsed.get("learning_style", []):
        item = str(item).lower()

        if item in allowed:
            fixed.append(item)
        elif item in mapping:
            fixed.append(mapping[item])
        else:
            fixed.append("theory")  # safe fallback

    parsed["learning_style"] = list(set(fixed))

    return parsed


def analyze_chunks(chunks):
    sampled_text = sample_chunks_evenly(chunks)

    prompt = analysis_prompt.invoke({"text": sampled_text})

    for attempt in range(2):
        response = llm.invoke(prompt)

        try:
            # 🔥 CLEAN first
            cleaned = clean_json_response(response)

            parsed = json.loads(cleaned)

            # 🔥 NORMALIZE
            parsed = fix_learning_style(parsed)

            validated = AnalysisResponse(**parsed)

            analysis_dict = validated.model_dump()

            # 🔹 normalize text fields
            analysis_dict["key_strengths"] = [
                str(s).lower() for s in analysis_dict.get("key_strengths", [])
            ]

            analysis_dict["key_weaknesses"] = [
                str(s).lower() for s in analysis_dict.get("key_weaknesses", [])
            ]

            analysis_dict["topics"] = [
                str(t).lower() for t in analysis_dict.get("topics", [])
            ]

            analysis_dict["subtopics"] = [
                str(s).lower() for s in analysis_dict.get("subtopics", [])
            ]

            return analysis_dict

        except Exception as e:
            print(f"Attempt {attempt+1} failed:", e)
            print("Raw response:", response)

            prompt = f"""
You FAILED to return valid JSON.

STRICT RULES:
- ONLY return JSON
- no markdown
- no explanation
- enums must match exactly
- learning_style must be from: theory, hands_on, visual, code_along

Fix this:

{response}
"""

    raise ValueError("LLM failed to return valid JSON after retries")
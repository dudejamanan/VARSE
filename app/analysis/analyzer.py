from core.llm import llm
from ingestion.chunking import sample_chunks_evenly
from analysis.prompts import analysis_prompt
import json
from schemas.response import AnalysisResponse


def repair_json(response: str):
    open_braces = response.count("{")
    close_braces = response.count("}")

    if close_braces < open_braces:
        response += "}" * (open_braces - close_braces)

    return response

def fix_missing_analysis_fields(parsed):
    parsed.setdefault("topics", [])
    parsed.setdefault("subtopics", [])
    parsed.setdefault("examples_present", False)

    parsed.setdefault("depth", "intermediate")
    parsed.setdefault("depth_score", 5)

    parsed.setdefault("content_type", "mixed")

    parsed.setdefault("clarity", "medium")
    parsed.setdefault("clarity_score", 5)
    parsed.setdefault("clarity_reason", "")

    parsed.setdefault("structure", "moderate")
    parsed.setdefault("structure_score", 5)

    parsed.setdefault("flow", "mixed")
    parsed.setdefault("repetition", "medium")
    parsed.setdefault("pace", "moderate")

    parsed.setdefault("information_density", "medium")
    parsed.setdefault("information_density_score", 5)

    parsed.setdefault("audience_level", "intermediate")

    parsed.setdefault("learning_style", ["theory"])

    parsed.setdefault("prerequisites_required", "medium")

    parsed.setdefault("engagement_level", "medium")
    parsed.setdefault("engagement_score", 5)

    parsed.setdefault("key_strengths", [])
    parsed.setdefault("key_weaknesses", [])

    return parsed


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
            cleaned = clean_json_response(response)
            cleaned = repair_json(cleaned)

            parsed = json.loads(cleaned)

            parsed = fix_missing_analysis_fields(parsed)
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
YOU FAILED.

STRICT RULES:
- ONLY return JSON
- NO markdown
- NO explanation
- ALL fields MUST be present
- NO null values
- learning_style must be from: theory, hands_on, visual, code_along

Fix this JSON:

{response}
"""

    raise ValueError("LLM failed to return valid JSON after retries")
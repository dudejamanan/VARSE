from analysis.prompts import qa_prompt
from core.llm import llm
from schemas.response import QAResponse
import json

def repair_json(response: str):
    open_braces = response.count("{")
    close_braces = response.count("}")

    if close_braces < open_braces:
        response += "}" * (open_braces - close_braces)

    return response

def fix_missing_qa_fields(parsed):
    parsed.setdefault("answer", "This topic relates to React concepts explained in the videos.")
    parsed.setdefault("best_video", "")

    parsed.setdefault("video_recommendations", [])
    parsed.setdefault("comparison_summary", "")

    parsed.setdefault("topic_explanations", {})

    parsed.setdefault("confidence", "medium")

    return parsed


def fix_qa_output(parsed):
    
    # 🔹 Fix video_recommendations
    if "video_recommendations" in parsed:
        fixed = []
        for item in parsed["video_recommendations"]:
            if isinstance(item, dict):
                # extract video_id from url
                url = item.get("url", "")
                if "v=" in url:
                    vid = url.split("v=")[-1]
                    fixed.append(vid)
                else:
                    fixed.append(item.get("title", ""))
            else:
                fixed.append(item)

        parsed["video_recommendations"] = fixed

    # 🔹 Fix topic_explanations
    if "topic_explanations" in parsed:
        fixed_topics = {}
        for key, value in parsed["topic_explanations"].items():
            if isinstance(value, dict):
                # convert dict → string summary
                desc = value.get("description", "")
                features = value.get("features", [])

                combined = desc
                if features:
                    combined += " Features: " + ", ".join(features)

                fixed_topics[key] = combined.strip()
            else:
                fixed_topics[key] = str(value)

        parsed["topic_explanations"] = fixed_topics

    # 🔹 Fix missing confidence
    if "confidence" not in parsed:
        parsed["confidence"] = "medium"

    return parsed

def clean_json_response(response: str):
    response = response.strip()

    # handle markdown blocks robustly
    if "```" in response:
        parts = response.split("```")
        for part in parts:
            if "{" in part and "}" in part:
                response = part
                break

    # extract JSON safely
    start = response.find("{")
    end = response.rfind("}")

    if start != -1 and end != -1:
        response = response[start:end+1]

    return response


def answer_query(docs, query):

    # 🔹 Step 1: Group by video
    grouped = {}
    for doc in docs:
        vid = doc.metadata["video_id"]

        if vid not in grouped:
            grouped[vid] = []

        grouped[vid].append(doc.page_content)

    # 🔹 Step 2: Build context
    context = ""

    for vid, texts in grouped.items():
        context += f"\nFrom Video {vid}:\n"

        for t in texts:
            context += t + "\n"

        context += "\n"

    # 🔹 Step 3: LLM call
    prompt = qa_prompt.invoke({
        "context": context,
        "question": query
    })

    for attempt in range(2):
        response = llm.invoke(prompt)

        try:
            cleaned = clean_json_response(response)
            cleaned = repair_json(cleaned)

            parsed = json.loads(cleaned)

            parsed = fix_missing_qa_fields(parsed)
            parsed = fix_qa_output(parsed)

            validated = QAResponse(**parsed)

            return validated.model_dump()

        except Exception as e:
            print(f"Attempt {attempt+1} failed:", e)
            print("Raw response:", response)

            # 🔥 Retry correction
            prompt = f"""
YOU FAILED.

STRICT RULES:
- ONLY return JSON
- NO markdown
- NO explanation
- NO null values
- ALL fields must exist
- "answer" MUST NOT be empty

Fix this:

{response}
"""

    raise ValueError("QA failed after retries")
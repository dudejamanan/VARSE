from analysis.prompts import qa_prompt
from core.llm import llm
from schemas.response import QAResponse
import json


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


# 🔹 CLEANER (same pattern as comparison)
def clean_json_response(response: str):
    response = response.strip()

    # remove markdown
    if "```" in response:
        response = response.split("```")[1]

    # remove ellipsis
    response = response.replace("...", "")

    # extract JSON only
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
            parsed = json.loads(cleaned)
            parsed = fix_qa_output(parsed)

            validated = QAResponse(**parsed)

            return validated.model_dump()

        except Exception as e:
            print(f"Attempt {attempt+1} failed:", e)
            print("Raw response:", response)

            # 🔥 Retry correction
            prompt = f"""
You FAILED to return valid JSON.

STRICT RULES:
- ONLY return JSON
- NO explanation
- ALL fields required

Fix this output:

{response}
"""

    raise ValueError("QA failed after retries")
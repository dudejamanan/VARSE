from core.llm import llm
from analysis.prompts import comparision_prompt
import json
from schemas.response import ComparisonResponse
from rag.qa_chain import clean_json_response

def fix_topic_wise_best(parsed):
    if "topic_wise_best" in parsed:
        fixed = {}

        for topic, value in parsed["topic_wise_best"].items():

            # if already correct
            if isinstance(value, str):
                fixed[topic] = value

            # if dict like {video_id: true/false}
            elif isinstance(value, dict):
                # pick the one with True
                chosen = None
                for vid, flag in value.items():
                    if flag:
                        chosen = vid
                        break

                # fallback → pick first key
                if not chosen and value:
                    chosen = list(value.keys())[0]

                fixed[topic] = chosen

        parsed["topic_wise_best"] = fixed

    return parsed

def fix_time_recommendation(parsed):
    if "time_based_recommendation" not in parsed or parsed["time_based_recommendation"] is None:
        parsed["time_based_recommendation"] = {
            "video_id": "",
            "reason": ""
        }
        return parsed

    # 🔥 FIX NULL video_id
    if parsed["time_based_recommendation"].get("video_id") is None:
        parsed["time_based_recommendation"]["video_id"] = ""

    return parsed

def fix_missing_fields(parsed):
    for video in parsed.get("video_evaluations", []):
        scores = video.get("scores", {})

        # ensure all required fields exist
        scores.setdefault("clarity", 5)
        scores.setdefault("depth", 5)
        scores.setdefault("structure", 5)
        scores.setdefault("engagement", 5)
        scores.setdefault("information_density", 5)

        video["scores"] = scores

    return parsed

def normalize_unique_topics(parsed):
    if "unique_topics" in parsed:
        new_map = {}

        for key, value in parsed["unique_topics"].items():
            if key.isdigit():
                idx = int(key)
                if idx < len(parsed["video_evaluations"]):
                    vid = parsed["video_evaluations"][idx]["video_id"]
                    new_map[vid] = value
            else:
                new_map[key] = value

        parsed["unique_topics"] = new_map

    return parsed

def repair_json(response: str):
    response = response.strip()

    # count braces
    open_braces = response.count("{")
    close_braces = response.count("}")

    # if missing closing braces → add them
    if close_braces < open_braces:
        response += "}" * (open_braces - close_braces)

    return response

def fix_comparison_output(parsed):

    # 🔹 Fix unique_topics (dict → list)
    if "unique_topics" in parsed:
        fixed = {}
        for key, value in parsed["unique_topics"].items():
            if isinstance(value, dict):
                fixed[key] = value.get("topics", [])
            else:
                fixed[key] = value
        parsed["unique_topics"] = fixed

    # 🔹 Fix recommendations nulls
    if "recommendations" in parsed:
        rec = parsed["recommendations"]
        for k in ["best_for_depth", "best_for_quick_learning"]:
            if rec.get(k) is None:
                rec[k] = ""

    # 🔹 Fix topic_wise_best nulls
    if "topic_wise_best" in parsed:
        fixed = {}
        for topic, value in parsed["topic_wise_best"].items():
            if value is None:
                fixed[topic] = ""
            else:
                fixed[topic] = value
        parsed["topic_wise_best"] = fixed

    # 🔹 Ensure overall_reason exists
    if "overall_reason" not in parsed or not parsed["overall_reason"]:
        parsed["overall_reason"] = ""

    return parsed

def compare_videos(videos):


    prompt = comparision_prompt.invoke({
        "all_videos": json.dumps(videos, indent=2)
    })

    for attempt in range(2):
        response = llm.invoke(prompt)

        try:
            cleaned = clean_json_response(response)
            cleaned = repair_json(cleaned)

            parsed = json.loads(cleaned)

            parsed = fix_missing_fields(parsed)
            parsed = normalize_unique_topics(parsed)

            parsed = fix_comparison_output(parsed)

            parsed = fix_topic_wise_best(parsed)
            parsed = fix_time_recommendation(parsed)

            validated = ComparisonResponse(**parsed)
            return validated.model_dump()

        except Exception as e:
            print(f"Attempt {attempt+1} failed:", e)
            print("Raw response:", response)

            prompt = f"""
You FAILED to follow instructions.

STRICT RULES:
- ONLY return JSON
- NO explanation
- NO code
- NO markdown
- MUST match schema EXACTLY

Fix this output:

{response}
"""

    raise ValueError("Comparison failed after retries")


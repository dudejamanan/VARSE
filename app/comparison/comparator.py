from core.llm import llm
from analysis.prompts import comparision_prompt
import json
from schemas.response import ComparisonResponse
from rag.qa_chain import clean_json_response
from comparison.topic_engine import compute_topic_analysis

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

def fix_time_recommendation_with_duration(parsed, videos):
    if not videos:
        return parsed

    shortest = min(videos, key=lambda v: v.get("duration_sec", 999999))

    parsed["time_based_recommendation"] = {
        "video_id": shortest["video_id"],
        "reason": "shortest duration"
    }

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

def fix_top_level_fields(parsed):
    
    parsed.setdefault("domain_valid", True)
    parsed.setdefault("domain_reason", "")

    parsed.setdefault("common_topics", [])
    parsed.setdefault("unique_topics", {})
    parsed.setdefault("missing_topics", [])

    parsed.setdefault("video_evaluations", [])
    parsed.setdefault("ranking", [])

    parsed.setdefault("recommendations", {
        "best_overall": "",
        "best_for_beginners": "",
        "best_for_depth": "",
        "best_for_quick_learning": ""
    })

    parsed.setdefault("topic_wise_best", {})

    parsed.setdefault("time_based_recommendation", {
        "video_id": "",
        "reason": ""
    })

    parsed.setdefault("overall_reason", "")

    return parsed

def fix_ranking(parsed):
    if not parsed.get("ranking"):
        rankings = []

        for i, vid in enumerate(parsed.get("video_evaluations", [])):
            rankings.append({
                "video_id": vid.get("video_id", ""),
                "rank": i + 1,
                "final_score": vid.get("final_score", 0)
            })

        parsed["ranking"] = rankings

    return parsed



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

def fix_recommendations(parsed):
    ranking = parsed.get("ranking", [])
    
    if ranking:
        top_video = ranking[0]["video_id"]

        # force consistency
        parsed["recommendations"]["best_overall"] = top_video

    return parsed

def fix_ranking_by_score(parsed):
    videos = parsed.get("video_evaluations", [])

    # sort by score DESC
    videos_sorted = sorted(
        videos,
        key=lambda x: x.get("final_score", 0),
        reverse=True
    )

    ranking = []
    for i, v in enumerate(videos_sorted):
        ranking.append({
            "video_id": v["video_id"],
            "rank": i + 1,
            "final_score": v["final_score"]
        })

    parsed["ranking"] = ranking

    return parsed

def fix_invalid_scores(parsed):
    for video in parsed.get("video_evaluations", []):
        val = video.get("final_score")

        # if it's not a number → reset
        if not isinstance(val, (int, float)):
            video["final_score"] = 0

    return parsed


def compute_final_scores(parsed):
    for video in parsed.get("video_evaluations", []):
        scores = video.get("scores", {})

        clarity = scores.get("clarity", 0)
        depth = scores.get("depth", 0)
        structure = scores.get("structure", 0)
        engagement = scores.get("engagement", 0)
        density = scores.get("information_density", 0)

        final_score = (
            clarity * 0.25 +
            depth * 0.25 +
            structure * 0.2 +
            engagement * 0.15 +
            density * 0.15
        )

        # convert to integer (important for schema)
        video["final_score"] = int(final_score * 10)

    return parsed

def fix_topic_wise_best_with_scores(parsed, topic_presence):
    result = {}

    scores_map = {
        v["video_id"]: v["final_score"]
        for v in parsed.get("video_evaluations", [])
    }

    for topic, vids in topic_presence.items():
        if not vids:
            continue

        # only compare among videos that HAVE the topic
        best_vid = max(vids, key=lambda v: scores_map.get(v, 0))
        result[topic] = best_vid

    parsed["topic_wise_best"] = result
    return parsed

def fix_quick_learning(parsed):
    best = max(
        parsed.get("video_evaluations", []),
        key=lambda v: (
            v["scores"].get("clarity", 0) +
            v["scores"].get("information_density", 0)
        ),
        default=None
    )

    if best:
        parsed["recommendations"]["best_for_quick_learning"] = best["video_id"]

    return parsed

def fix_recommendation_fields(parsed):
    videos = parsed.get("video_evaluations", [])

    if not videos:
        return parsed

    # beginners → clarity
    beginner = max(videos, key=lambda v: v["scores"].get("clarity", 0))
    parsed["recommendations"]["best_for_beginners"] = beginner["video_id"]

    # depth → depth + density
    depth = max(
        videos,
        key=lambda v: (
            v["scores"].get("depth", 0) +
            v["scores"].get("information_density", 0)
        )
    )
    parsed["recommendations"]["best_for_depth"] = depth["video_id"]

    return parsed

def fix_best_for(parsed):
    for video in parsed.get("video_evaluations", []):

        scores = video.get("scores", {})

        best_for = []

        if scores.get("clarity", 0) >= 8:
            best_for.append("beginner")

        if scores.get("depth", 0) >= 7:
            best_for.append("depth")

        if scores.get("information_density", 0) >= 7:
            best_for.append("quick_learning")

        video["best_for"] = best_for

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

# ---------------------------
# 1. BASIC FIXES (LLM cleanup)
# ---------------------------
            parsed = fix_top_level_fields(parsed)
            parsed = fix_missing_fields(parsed)
            parsed = normalize_unique_topics(parsed)
            parsed = fix_comparison_output(parsed)
            parsed = fix_topic_wise_best(parsed)
            parsed = fix_time_recommendation(parsed)

# ---------------------------
# 2. SYSTEM LOGIC (override LLM)
# ---------------------------

            parsed = fix_invalid_scores(parsed)      # 🔥 NEW
            parsed = compute_final_scores(parsed) 
            parsed = fix_ranking_by_score(parsed)        # ✅ correct ranking   
            parsed = fix_recommendations(parsed)         # ✅ best_overall aligned
            parsed = fix_best_for(parsed)                # ✅ tags per video
            parsed = fix_quick_learning(parsed)          # ✅ quick learning
            parsed = fix_recommendation_fields(parsed)
            parsed = fix_recommendation_fields(parsed)
            parsed = fix_time_recommendation_with_duration(parsed, videos)
# ---------------------------
# 3. TOPIC ENGINE (NEW CORE)
# ---------------------------
            common, unique, missing, topic_presence = compute_topic_analysis(videos)

            parsed["common_topics"] = common
            parsed["unique_topics"] = unique
            parsed["missing_topics"] = missing

# 🔥 THIS WAS MISSING
            parsed = fix_topic_wise_best_with_scores(parsed, topic_presence)

# ---------------------------
# FINAL VALIDATION
# ---------------------------
            validated = ComparisonResponse(**parsed)
            return validated.model_dump()

        except Exception as e:
            print(f"Attempt {attempt+1} failed:", e)
            print("Raw response:", response)

            prompt = f"""
YOU FAILED.

STRICT RULES:
- ONLY return JSON
- NO explanation
- NO markdown
- NO null values
- ALL fields must exist
- scores must be integers (1-10)

Return FULL valid JSON.

Fix this:

{response}
"""

    raise ValueError("Comparison failed after retries")


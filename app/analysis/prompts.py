from langchain_core.prompts import PromptTemplate

analysis_prompt = PromptTemplate(
    template="""
You are an expert educator and content analyst.

Analyze the following transcript and return STRICT JSON.

IMPORTANT RULES:
- DO NOT guess anything not present in the transcript
- DO NOT add external knowledge
- Follow ENUM values EXACTLY as specified
- Ensure all numeric scores are between 1 and 10
- Output ONLY valid JSON

----------------------------------------
IMPORTANT:
- You MUST use EXACT enum values
- DO NOT use hyphens (-), spaces, or slashes (/)
- ONLY use the following values:

content_type: conceptual | mixed | practical

structure: well_structured | moderate | scattered

learning_style: theory | hands_on | visual | code_along

If you output anything else, the response will FAIL.

Return in this format:

{{
  "topics": ["list ALL main topics covered"],

  "subtopics": ["list important subtopics if present"],

  "examples_present": true/false,

  "depth": "beginner/intermediate/advanced",
  "depth_score": number,

  "content_type": "conceptual/mixed/practical",

  "clarity": "low/medium/high",
  "clarity_score": number,
  "clarity_reason": "short explanation",

  "structure": "well_structured/moderate/scattered",
  "structure_score": number,

  "flow": "sequential/jumping/mixed",

  "repetition": "low/medium/high",

  "pace": "slow/moderate/fast",

  "information_density": "low/medium/high",
  "information_density_score": number,

  "audience_level": "beginner/intermediate/advanced",

  "learning_style": ["theory/hands_on/visual/code_along"],

  "prerequisites_required": "low/medium/high",

  "engagement_level": "low/medium/high",
  "engagement_score": number,

  "key_strengths": ["2-4 strengths"],

  "key_weaknesses": ["2-4 weaknesses"]
}}

----------------------------------------

Transcript:
{text}
""",
    input_variables=["text"]
)



comparision_prompt = PromptTemplate(
    template="""
You are an expert learning advisor and content evaluator.

You are given structured analysis of multiple videos.

{all_videos}

----------------------------------------
YOU ARE A JSON GENERATOR.

- DO NOT explain
- DO NOT write code
- DO NOT use markdown
- DO NOT wrap output in ```
- DO NOT add any text before or after JSON

ONLY output valid JSON.

If you fail, the system will break.

STRICT RULES:
- Output MUST be valid JSON ONLY
- DO NOT add any text outside JSON
- ALL scores must be integers (1-10)
- video_id must match input exactly
- use lowercase for all enums
- DO NOT skip any field
- DO NOT hallucinate topics not present in input

----------------------------------------

TASKS:

1. DOMAIN CHECK
- Check if all videos belong to same domain
- If not:
  return:
  {{
    "domain_valid": false,
    "domain_reason": "..."
  }}
- If yes:
  continue

----------------------------------------

2. TOPIC ANALYSIS
- Find:
  - common_topics
  - unique_topics per video
  - missing_topics (based only on comparison)

----------------------------------------

3. VIDEO SCORING

For each video compute:

final_score = weighted combination of:
- clarity_score
- depth_score
- structure_score
- engagement_score
- information_density_score

IMPORTANT:
- Be consistent across all videos
- Use relative comparison, not absolute judgment

----------------------------------------

4. RANKING
- Rank all videos based on final_score

----------------------------------------

5. RECOMMENDATIONS

Choose:
- best_overall
- best_for_beginners (low prerequisites + high clarity)
- best_for_depth (high depth_score + density)
- best_for_quick_learning (high clarity + low duration + high density)

----------------------------------------

6. TOPIC-WISE BEST
- Map key topics → best video

----------------------------------------

7. TIME EFFICIENCY
- Recommend best video for limited time

----------------------------------------
ALL score fields MUST be present:
- clarity
- depth
- structure
- engagement
- information_density

RETURN EXACTLY THIS JSON:

{{
  "domain_valid": true,
  "domain_reason": "",

  "common_topics": [],

  "unique_topics": {{}},

  "missing_topics": [],

  "video_evaluations": [
    {{
      "video_id": "",

      "scores": {{
        "clarity": 0,
        "depth": 0,
        "structure": 0,
        "engagement": 0,
        "information_density": 0
      }},

      "final_score": 0,

      "strength_summary": "",
      "weakness_summary": "",

      "best_for": []
    }}
  ],

  "ranking": [
    {{
      "video_id": "",
      "rank": 1,
      "final_score": 0
    }}
  ],

  "recommendations": {{
    "best_overall": "",
    "best_for_beginners": "",
    "best_for_depth": "",
    "best_for_quick_learning": ""
  }},

  "topic_wise_best": {{}},

  "time_based_recommendation": {{
    "video_id": "",
    "reason": ""
  }},

  "overall_reason": ""
}}
""",
    input_variables=["all_videos"]
)


qa_prompt = PromptTemplate(
    template="""
YOU ARE A JSON GENERATOR.

STRICT RULES:
- ONLY return JSON
- NO explanation outside JSON
- DO NOT use markdown
- DO NOT skip any field

----------------------------------------

You are an expert programming tutor.

You are given explanations from multiple videos.

Context:
{context}

Question:
{question}

----------------------------------------

TASKS:

1. Answer the question clearly for a learner
2. Compare explanations across videos
3. Identify the BEST video
4. Recommend relevant videos
5. Explain key concepts (like routing if asked)

----------------------------------------
- "answer" MUST NOT be empty

RETURN EXACTLY THIS JSON:

{{
  "answer": "",

  "best_video": "",

  "video_recommendations": [],

  "comparison_summary": "",

  "topic_explanations": {{}},

  "confidence": "high/medium/low"
}}
""",
    input_variables=["context", "question"]
)
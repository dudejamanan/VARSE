from langchain_core.prompts import PromptTemplate

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

You are given analysis of multiple videos.

{all_videos}

Your task:
- Compare ALL videos
- Rank them based on:
  - number of topics covered
  - depth
  - clarity
  - structure

Rules:
- Be consistent
- Do NOT be vague
- Give a clear ranking

Return in this format:

Ranking:
1. Video X (ID: ...)
2. Video Y (ID: ...)
3. Video Z (ID: ...)

Best for beginners:
...

Best for depth:
...

Best for clarity:
...

Reason:
<clear explanation>
""",
    input_variables=["all_videos"]
)
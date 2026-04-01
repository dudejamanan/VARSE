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

You MUST make a clear decision.

Video 1 Analysis:
{analysis1}

Video 2 Analysis:
{analysis2}

Compare the two videos strictly based on:
- number of topics covered
- depth
- clarity
- structure

Rules:
- Be consistent (no contradictions)
- Do NOT be vague
- Choose ONLY ONE best video

Return in this format:

Comparison:
- Topics coverage: ...
- Depth: ...
- Clarity: ...
- Structure: ...

Winner:
<Video 1 or Video 2>

Reason:
<clear justification>
""",
input_variables=["analysis1","analysis2"]
)
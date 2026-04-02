from langchain_core.prompts import PromptTemplate

analysis_prompt = PromptTemplate(
    template="""
You are an expert educator and content analyst.

Analyze the following transcript and return STRICT JSON.

IMPORTANT RULES:
- DO NOT guess anything not present in the transcript
- DO NOT add external knowledge
- Be precise and structured

----------------------------------------

Return in this format:

{{
  "topics": ["list ALL main topics covered"],
  
  "subtopics": ["list important subtopics if present"],
  
  "examples_present": "Yes/No",
  
  "depth": "Beginner/Intermediate/Advanced",
  
  "conceptual_vs_practical": "Mostly Conceptual / Mixed / Mostly Practical",
  
  "clarity": "Low/Medium/High",
  
  "clarity_reason": "short explanation",
  
  "structure": "Well-structured / Moderately structured / Scattered",
  
  "flow": "Sequential / Jumping / Mixed",
  
  "repetition": "Low/Medium/High",
  
  "pace": "Slow / Moderate / Fast",
  
  "information_density": "Low/Medium/High",
  
  "audience_level": "Beginner / Intermediate / Advanced",
  
  "key_strengths": ["list 2-4 strengths observed"],
  
  "key_weaknesses": ["list 2-4 weaknesses based ONLY on transcript"]
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

Your tasks:

### 1. Domain Check (VERY IMPORTANT)
- Determine if all videos belong to the SAME domain/topic.
- If videos are from completely different domains (e.g., music vs programming, Python vs Node.js):
  - Clearly state: "Videos are NOT comparable"
  - Explain why
  - STOP further comparison

----------------------------------------

### 2. Topic Analysis
- List:
  - Common topics across videos
  - Unique topics per video
- Identify missing important topics (ONLY based on comparison, do NOT guess external topics)

----------------------------------------

### 3. Quality Evaluation
For each video evaluate:
- Depth (Beginner / Intermediate / Advanced)
- Clarity (Low / Medium / High)
- Structure (Well-structured / Scattered)
- Topic coverage (number + diversity of topics)

----------------------------------------

### 4. Ranking
Rank ALL videos based on:
- coverage
- depth
- clarity
- structure

Be STRICT and consistent.

----------------------------------------

### 5. Recommendations

Provide:

- 🏆 Best Overall Video
- 📚 Best for Beginners
- 🧠 Best for Deep Understanding
- ⚡ Best for Quick Learning (least time, most value)

----------------------------------------

### 6. Topic-wise Guidance (VERY IMPORTANT)
For key topics:
- Mention which video explains that topic best

Example:
- Recursion → Video X
- OOP → Video Y

----------------------------------------

### 7. Time-Based Decision
If user has limited time:
- Recommend the most efficient video
- Justify based on clarity + density

----------------------------------------

### OUTPUT FORMAT:

Domain Check:
...

Common Topics:
...

Unique Topics:
- Video X:
- Video Y:

Missing Topics:
...

Ranking:
1. Video X (ID: ...)
2. Video Y (ID: ...)

Recommendations:
- Best Overall:
- Best for Beginners:
- Best for Depth:
- Best for Quick Learning:

Topic-wise Best:
- Topic → Video

Reason:
<clear, strict justification>
""",
    input_variables=["all_videos"]
)


qa_prompt = PromptTemplate(
    template="""
You are an expert programming tutor.

You are given explanations from multiple videos.

{context}

Question:
{question}

Instructions:
- Answer clearly
- Compare explanations from different videos
- Mention which video explains better (if applicable)
- Keep it simple for learners

Answer:
""",
    input_variables=["context", "question"]
)
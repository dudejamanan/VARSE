from analysis.prompts import qa_prompt
from core.llm import llm

def answer_query(docs, query):
    
    # Step 1: Group by video
    grouped = {}
    for doc in docs:
        vid = doc.metadata["video_id"]

        if vid not in grouped:
            grouped[vid] = []

        grouped[vid].append(doc.page_content)

    # Step 2: Build context
    context = ""

    for vid, texts in grouped.items():
        context += f"\nFrom Video {vid}:\n"

        for t in texts:
            context += t + "\n"

        context += "\n"

    # Step 3: LLM call
    final_prompt = qa_prompt.invoke({
        "context": context,
        "question": query
    })

    answer = llm.invoke(final_prompt)

    return answer
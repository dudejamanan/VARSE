from core.llm import llm
from analysis.prompts import comparision_prompt

def compare_videos(analysis1, analysis2):
    prompt = comparision_prompt.invoke({
        "analysis1": analysis1,
        "analysis2": analysis2
    })
    result = llm.invoke(prompt)
    return result
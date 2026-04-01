from core.llm import llm
from analysis.prompts import comparision_prompt


def compare_videos(videos):
    # Build dynamic text
    combined_analysis = ""

    for i, video in enumerate(videos):
        combined_analysis += f"\nVideo {i+1} (ID: {video['video_id']}):\n"
        combined_analysis += f"{video['analysis']}\n"

    prompt = comparision_prompt.invoke({
        "all_videos": combined_analysis
    })

    result = llm.invoke(prompt)
    return result
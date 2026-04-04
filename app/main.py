from ingestion.youtube import extract_video_id
from ingestion.transcript import fetch_transcript
from ingestion.chunking import split_text,sample_chunks_evenly

from analysis.analyzer import analyze_chunks
from comparison.comparator import compare_videos

from vector_store.faiss_store import build_vectorstore
from rag.retriever import get_retriever
from rag.qa_chain import answer_query


def run():
    urls = ["https://www.youtube.com/watch?v=LDB4uaJ87e0&t=57s","https://www.youtube.com/watch?v=TtPXvEcE11E&pp=ygUUcmVhY3QganMgZnVsbCBjb3Vyc2U%3D","https://www.youtube.com/watch?v=Wt3isV2irrA"]
    videos = []
    all_chunks = []
    for url in urls:
        video_id = extract_video_id(url)
        print(f"Processing Video:{video_id}")

        transcript = fetch_transcript(video_id)
        chunks = split_text(transcript,video_id)
        all_chunks.extend(chunks)
        analysis = analyze_chunks(chunks)
       

        videos.append({
            "video_id": video_id,
            "analysis": analysis
        })
    
    build_vectorstore(all_chunks)
    print("Vectorstore built!")

    print("\n--- ALL ANALYSES DONE ---\n")

    retriever = get_retriever(k=10)

    query = '''Module:6 ReactJS 2 hours
React Environment Setup - ReactJS Basics - React JSX - React Components: React
Component API - React Component Life Cycle - React Constructors - React Dev Tools -
React Native vs ReactJS.
Module:7 Advanced ReactJS 2 hours
React Dataflow: React State - React Props - React Props Validation - Styling React - Hooks
and Routing - Deploying React - Case Studies for building dynamic web applications. 


this is my syllabus, suggest me the video which teaches me all of them clearly and also tell what is routing
'''
    docs = retriever.invoke(query)

    answer = answer_query(docs, query)
    

    #Compare all videos
    result = compare_videos(videos)

    print("\n=== FINAL RANKING ===\n")
    print(result)


    

    print("\n=== FINAL ANSWER ===\n")
    print(answer)
    



if __name__ == "__main__":
    run()
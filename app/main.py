from ingestion.youtube import extract_video_id
from ingestion.transcript import fetch_transcript
from ingestion.chunking import split_text,sample_chunks_evenly
from ingestion.youtube_metadata import get_video_metadata, convert_duration

from analysis.analyzer import analyze_chunks
from comparison.comparator import compare_videos

from vector_store.faiss_store import build_vectorstore
from rag.retriever import get_retriever
from rag.qa_chain import answer_query



def run():
    urls = ["https://youtu.be/K5KVEU3aaeQ?si=BHmwae2gqk-21joz","https://youtu.be/_uQrJ0TkZlc?si=WbqQ-_Uux0djqZhr","https://youtu.be/ix9cRaBkVe0?si=DJG209EVoHp133tM"]
    videos = []
    all_chunks = []
    for url in urls:
        video_id = extract_video_id(url)
        print(f"Processing Video:{video_id}")

        try:
            metadata = get_video_metadata(video_id)

            if metadata is None:
                print(f"Skipping video {video_id} (no metadata)")
                continue

            views = metadata.get("views", 0)
            likes = metadata.get("likes", 0)
            duration_sec = convert_duration(metadata.get("duration", "PT0S"))

            transcript = fetch_transcript(video_id)

            if not transcript:
                print(f"Skipping video {video_id} (no transcript)")
                continue

            chunks = split_text(transcript, video_id)

            if not chunks:
                print(f"Skipping video {video_id} (no chunks)")
                continue

            all_chunks.extend(chunks)

            try:
                analysis = analyze_chunks(chunks)
            except Exception as e:
                print(f"Analysis failed for {video_id}:", e)
                continue

            analysis["video_id"] = video_id
            analysis["duration_sec"] = duration_sec
            analysis["views"] = views
            analysis["likes"] = likes
            analysis["engagement_ratio"] = likes / views if views > 0 else 0

            videos.append(analysis)

        except Exception as e:
            print(f"Error processing video {video_id}:", e)
            continue
    
    if not all_chunks:
        raise ValueError("No valid chunks found. Cannot build vectorstore.")

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

    if docs:
        answer = answer_query(docs, query)
    else:
        answer = {"answer": "No relevant content found.", "confidence": "low"}
    
    
    #Compare all videos
    result = compare_videos(videos)

    print("\n=== FINAL RANKING ===\n")
    print(result)


    

    print("\n=== FINAL ANSWER ===\n")
    print(answer)
    



if __name__ == "__main__":
    run()
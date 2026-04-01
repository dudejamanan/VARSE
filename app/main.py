from ingestion.youtube import extract_video_id
from ingestion.transcript import fetch_transcript
from ingestion.chunking import split_text

from analysis.analyzer import analyze_chunks
from comparison.comparator import compare_videos


def run():
    url1 = "https://www.youtube.com/watch?v=K5KVEU3aaeQ"
    url2 = "https://www.youtube.com/watch?v=_uQrJ0TkZlc"

    # Step 1: Extract IDs
    video_id1 = extract_video_id(url1)
    video_id2 = extract_video_id(url2)

    print("Video IDs:", video_id1, video_id2)

    # Step 2: Fetch transcripts
    transcript1 = fetch_transcript(video_id1)
    transcript2 = fetch_transcript(video_id2)

    print("Fetched transcripts")

    # Step 3: Chunking
    chunks1 = split_text(transcript1)
    chunks2 = split_text(transcript2)

    print("Chunking done")

    # Step 4: Analysis
    analysis1 = analyze_chunks(chunks1)
    analysis2 = analyze_chunks(chunks2)

    print("\n--- Analysis 1 ---\n", analysis1)
    print("\n--- Analysis 2 ---\n", analysis2)

    # Step 5: Comparison
    comparison = compare_videos(analysis1, analysis2)

    print("\n=== FINAL COMPARISON ===\n")
    print(comparison)


if __name__ == "__main__":
    run()
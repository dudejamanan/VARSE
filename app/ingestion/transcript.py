from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled

def fetch_transcript(video_id): 
    yt_api = YouTubeTranscriptApi()
    try:
        transcript_list= yt_api.fetch(video_id,languages=["en"])
        transcript = " ".join(chunk.text for chunk in transcript_list)
        return transcript

    except TranscriptsDisabled:
        return "No captions available for this video"

    
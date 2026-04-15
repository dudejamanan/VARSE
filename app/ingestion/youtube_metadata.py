from googleapiclient.discovery import build

import isodate

API_KEY = "AIzaSyDH9fPi3PJiDFepkHHujd3OZ7ialiUzwJ0"


def get_video_metadata(video_id):
    youtube = build("youtube", "v3", developerKey=API_KEY)

    request = youtube.videos().list(
        part="contentDetails,statistics",
        id=video_id
    )

    response = request.execute()

    items = response.get("items", [])

    if not items:
        return None

    data = items[0]

    stats = data["statistics"]
    details = data["contentDetails"]

    views = int(stats.get("viewCount", 0))
    likes = int(stats.get("likeCount", 0))

    duration_iso = details["duration"]

    return {
        "views": views,
        "likes": likes,
        "duration": duration_iso
    }



def convert_duration(duration_iso):
    duration = isodate.parse_duration(duration_iso)
    return int(duration.total_seconds())
from core.embeddings import embedding
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def normalize_topic(text: str) -> str:
    text = text.lower().strip()

    # remove symbols
    for ch in ["-", "_", ":", ",", ".", "(", ")"]:
        text = text.replace(ch, " ")

    # remove extra spaces
    text = " ".join(text.split())

    return text

def collect_topics(videos):
    topic_items = []

    for video in videos:
        vid = video["video_id"]

        for topic in video.get("topics", []):
            normalized = normalize_topic(topic)
            sub_topics = split_topic(normalized)

            for t in sub_topics:
                topic_items.append((vid, t))

    return topic_items


def embed_topics(topic_items):
    texts = [t for _, t in topic_items]

    embeddings = embedding.embed_documents(texts)

    return embeddings

def split_topic(topic: str):
    topic = topic.lower().strip()

    # keep original phrase
    parts = [topic]

    # split only on commas (not spaces)
    if "," in topic:
        parts.extend([t.strip() for t in topic.split(",")])

    return list(set(parts))

def cluster_topics(topic_items, embeddings, threshold=0.7):
    clusters = []

    for i in range(len(topic_items)):
        placed = False

        for cluster in clusters:
            center_idx = cluster["center"]

            sim = cosine_similarity(
    [np.array(embeddings[i])],
    [np.array(embeddings[center_idx])]
)[0][0]

            if sim >= threshold:
                cluster["members"].append(i)
                placed = True
                break

        if not placed:
            clusters.append({
                "center": i,
                "members": [i]
            })

    return clusters

def canonicalize_clusters(clusters, topic_items):
    canonical = []

    for cluster in clusters:
        members = [topic_items[i][1] for i in cluster["members"]]

        # pick shortest phrase
        label = min(members, key=len)

        canonical.append((label, cluster["members"]))

    return canonical

def build_topic_presence(topic_items, canonical):
    topic_presence = {}

    # index → video_id mapping
    idx_to_vid = [vid for vid, _ in topic_items]

    for label, members in canonical:
        vids = set()

        for idx in members:
            vids.add(idx_to_vid[idx])

        topic_presence[label] = vids

    return topic_presence

def get_common_topics(topic_presence, video_ids):
    return [
        topic for topic, vids in topic_presence.items()
        if len(vids) == len(video_ids)
    ]

def get_unique_topics(topic_presence, video_ids):
    unique = {vid: [] for vid in video_ids}

    for topic, vids in topic_presence.items():
        if len(vids) == 1:
            vid = list(vids)[0]
            unique[vid].append(topic)

    return unique

def get_missing_topics(topic_presence, video_ids):
    return [
        topic for topic, vids in topic_presence.items()
        if len(vids) == len(video_ids) - 1
    ]

def compute_topic_analysis(videos):
    video_ids = [v["video_id"] for v in videos]

    topic_items = collect_topics(videos)

    if not topic_items:
        return [], {}, []

    embeddings = embed_topics(topic_items)

    clusters = cluster_topics(topic_items, embeddings)

    canonical = canonicalize_clusters(clusters, topic_items)

    topic_presence = build_topic_presence(topic_items, canonical)

    common_topics = get_common_topics(topic_presence, video_ids)

    unique_topics = get_unique_topics(topic_presence, video_ids)

    missing_topics = get_missing_topics(topic_presence, video_ids)

    return common_topics, unique_topics, missing_topics,topic_presence
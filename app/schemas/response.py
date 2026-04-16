from pydantic import BaseModel, Field
from typing import List, Literal, Dict, Optional


# =========================
# ANALYSIS
# =========================
class AnalysisResponse(BaseModel):
    topics: List[str] = []
    subtopics: List[str] = []

    examples_present: bool = False

    depth: str  # relax Literal
    depth_score: int = Field(default=5, ge=1, le=10)

    content_type: str

    clarity: str
    clarity_score: int = Field(default=5, ge=1, le=10)
    clarity_reason: str = ""

    structure: str
    structure_score: int = Field(default=5, ge=1, le=10)

    flow: str
    repetition: str
    pace: str

    information_density: str
    information_density_score: int = Field(default=5, ge=1, le=10)

    audience_level: str

    learning_style: List[str] = []

    prerequisites_required: str

    engagement_level: str
    engagement_score: int = Field(default=5, ge=1, le=10)

    key_strengths: List[str] = []
    key_weaknesses: List[str] = []

    analysis_summary: str


# =========================
# COMPARISON
# =========================
class VideoScore(BaseModel):
    clarity: int = 5
    depth: int = 5
    structure: int = 5
    engagement: int = 5
    information_density: int = 5


class VideoEvaluation(BaseModel):
    video_id: str
    scores: VideoScore
    final_score: int = 0
    strength_summary: str = ""
    weakness_summary: str = ""
    best_for: List[str] = []


class RankingItem(BaseModel):
    video_id: str
    rank: int
    final_score: int


class Recommendation(BaseModel):
    best_overall: str = ""
    best_for_beginners: str = ""
    best_for_depth: str = ""
    best_for_quick_learning: str = ""


class TimeRecommendation(BaseModel):
    video_id: str = ""
    reason: str = ""


class ComparisonResponse(BaseModel):
    domain_valid: bool
    domain_reason: str = ""

    common_topics: List[str] = []
    unique_topics: Dict[str, List[str]] = {}
    missing_topics: List[str] = []

    video_evaluations: List[VideoEvaluation] = []
    ranking: List[RankingItem] = []

    recommendations: Recommendation = Recommendation()
    topic_wise_best: Dict[str, str] = {}

    time_based_recommendation: TimeRecommendation = TimeRecommendation()

    overall_reason: str = ""


# =========================
# QA
# =========================
class QAResponse(BaseModel):
    answer: str = ""

    best_video: str = ""

    video_recommendations: List[str] = []

    comparison_summary: str = ""

    topic_explanations: Dict[str, str] = {}

    confidence: Literal["high", "medium", "low"] = "medium"
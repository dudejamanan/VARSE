from pydantic import BaseModel, Field
from typing import List, Literal
from typing import Dict



class AnalysisResponse(BaseModel):
    topics: List[str]
    subtopics: List[str]

    examples_present: bool

    depth: Literal["beginner", "intermediate", "advanced"]
    depth_score: int = Field(ge=1, le=10)

    content_type: Literal["conceptual", "mixed", "practical"]

    clarity: Literal["low", "medium", "high"]
    clarity_score: int = Field(ge=1, le=10)
    clarity_reason: str

    structure: Literal["well_structured", "moderate", "scattered"]
    structure_score: int = Field(ge=1, le=10)

    flow: Literal["sequential", "jumping", "mixed"]

    repetition: Literal["low", "medium", "high"]

    pace: Literal["slow", "moderate", "fast"]

    information_density: Literal["low", "medium", "high"]
    information_density_score: int = Field(ge=1, le=10)

    audience_level: Literal["beginner", "intermediate", "advanced"]

    learning_style: List[Literal["theory", "hands_on", "visual", "code_along"]]

    prerequisites_required: Literal["low", "medium", "high"]

    engagement_level: Literal["low", "medium", "high"]
    engagement_score: int = Field(ge=1, le=10)

    key_strengths: List[str]
    key_weaknesses: List[str]




class VideoScore(BaseModel):
    clarity: int
    depth: int
    structure: int
    engagement: int
    information_density: int


class VideoEvaluation(BaseModel):
    video_id: str
    scores: VideoScore
    final_score: int
    strength_summary: str
    weakness_summary: str
    best_for: List[str]


class RankingItem(BaseModel):
    video_id: str
    rank: int
    final_score: int


class Recommendation(BaseModel):
    best_overall: str
    best_for_beginners: str
    best_for_depth: str
    best_for_quick_learning: str


class TimeRecommendation(BaseModel):
    video_id: str
    reason: str


class ComparisonResponse(BaseModel):
    domain_valid: bool
    domain_reason: str

    common_topics: List[str]
    unique_topics: Dict[str, List[str]]
    missing_topics: List[str]

    video_evaluations: List[VideoEvaluation]
    ranking: List[RankingItem]

    recommendations: Recommendation
    topic_wise_best: Dict[str, str]

    time_based_recommendation: TimeRecommendation

    overall_reason: str


class QAResponse(BaseModel):
    answer: str

    best_video: str

    video_recommendations: List[str]

    comparison_summary: str

    topic_explanations: Dict[str, str]

    confidence: Literal["high", "medium", "low"]
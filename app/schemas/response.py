from pydantic import BaseModel, Field
from typing import List, Literal


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
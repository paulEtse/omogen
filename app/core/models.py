from pydantic import BaseModel, Field
from typing import Optional


class CriteriaScores(BaseModel):
    skills: int = Field(ge=0, le=100)
    experience: int = Field(ge=0, le=100)
    location: int = Field(ge=0, le=100)
    education: int = Field(ge=0, le=100)
    certifications: int = Field(ge=0, le=100)


class MatchResult(BaseModel):
    match: bool
    overall_score: int = Field(ge=0, le=100)
    criteria_scores: CriteriaScores
    explanation: str
    cached: bool = False
    processing_time_ms: Optional[int] = None
    error: bool = False

"""Pydantic models for the application."""
from typing import Literal

from pydantic import BaseModel, Field


class AskQuestionRequest(BaseModel):
    """Request model for the ask-question endpoint."""
    user_question: str


class AskQuestionResponse(BaseModel):
    """Response model for the ask-question endpoint."""
    source: str
    matched_question: str
    answer: str


class QuestionRoute(BaseModel):
    """Route classification for user questions."""

    category: Literal["it", "non_it"] = Field(
        ...,
        description="Classify the question as 'it' for IT-related questions or 'non_it' for non-IT questions"
    )

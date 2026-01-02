from __future__ import annotations
from typing import List
from pydantic import BaseModel
from uuid import UUID


class QuizAnswerDTO(BaseModel):
    question_id: UUID
    selected_option: str  # "A" | "B" | "C"


class QuizSubmissionDTO(BaseModel):
    answers: List[QuizAnswerDTO]


class QuizSubmissionResponseDTO(BaseModel):
    total_questions: int
    correct_answers: int
    points_earned: int
    total_points: int
    rank: str

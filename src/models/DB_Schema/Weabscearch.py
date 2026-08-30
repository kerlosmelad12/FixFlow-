from pydantic import BaseModel, Field
from typing import List
from ..Enums.Webscearchenums import Webscearchenums

class WeabscearchAnswers(BaseModel):
    question_id: int
    answer_id: int
    body: str
    score: int
    is_accepted: bool


class WeabscearchQuestion(BaseModel):
    question_id: int
    title: str
    body: str
    tags: List[str]
    url: str
    score: int
    answer_count: int


class WeabscearchResult(BaseModel):
    source: str = Webscearchenums.STACK_OVERFLOW.value
    question: WeabscearchQuestion
    answers: List[WeabscearchAnswers]


class WeabscearchSearchResponse(BaseModel):
    results: List[WeabscearchResult]


class RetriveSimiler(BaseModel):
    question: WeabscearchQuestion
    answers:list[WeabscearchAnswers]
    score:float
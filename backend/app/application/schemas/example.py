from pydantic import BaseModel


class QAExampleRead(BaseModel):
    category: str
    question: str
    ideal_answer: str


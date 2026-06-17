from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.application.schemas.example import QAExampleRead
from app.application.schemas.qa import AskQuestionRequest, AskQuestionResponse
from app.application.services.example_service import ExampleService
from app.application.services.qa_service import QAService
from app.infrastructure.db.models import User
from app.infrastructure.db.session import get_db

router = APIRouter(prefix="/qa", tags=["Question Answering"])


@router.post("/ask", response_model=AskQuestionResponse)
async def ask_question(
    payload: AskQuestionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AskQuestionResponse:
    return await QAService(db).ask(payload.question, current_user)


@router.get("/examples", response_model=list[QAExampleRead])
def list_examples(current_user: User = Depends(get_current_user)) -> list[QAExampleRead]:
    return ExampleService().list_examples()

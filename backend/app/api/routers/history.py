from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.application.schemas.history import HistoryItem
from app.application.services.history_service import HistoryService
from app.infrastructure.db.models import User
from app.infrastructure.db.session import get_db

router = APIRouter(prefix="/history", tags=["Question History"])


@router.get("", response_model=list[HistoryItem])
def list_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[HistoryItem]:
    return HistoryService(db).list_my_history(current_user)


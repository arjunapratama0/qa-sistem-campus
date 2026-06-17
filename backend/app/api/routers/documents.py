from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session

from app.api.dependencies import require_roles
from app.application.schemas.document import DocumentCreateRequest, DocumentRead, DocumentUploadResponse
from app.application.services.document_service import DocumentService
from app.infrastructure.db.models import User
from app.infrastructure.db.session import get_db

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.get("", response_model=list[DocumentRead])
def list_documents(
    current_user: User = Depends(require_roles("staff", "admin")),
    db: Session = Depends(get_db),
) -> list[DocumentRead]:
    return DocumentService(db).list_documents()


@router.post("", response_model=DocumentRead, status_code=201)
async def create_document(
    payload: DocumentCreateRequest,
    current_user: User = Depends(require_roles("staff", "admin")),
    db: Session = Depends(get_db),
) -> DocumentRead:
    return await DocumentService(db).create_document(payload, current_user)


@router.post("/upload", response_model=DocumentUploadResponse, status_code=201)
async def upload_document_pdf(
    file: UploadFile = File(...),
    title: str | None = Form(default=None),
    current_user: User = Depends(require_roles("staff", "admin")),
    db: Session = Depends(get_db),
) -> DocumentUploadResponse:
    return await DocumentService(db).upload_pdf(file=file, current_user=current_user, title=title)

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ai_core.gemini_generator import GeminiDocumentGenerator

router = APIRouter()
generator = None


class DocumentRequest(BaseModel):
    document_type: str = Field(..., min_length=1)
    parties: str = Field(..., min_length=1)
    terms: str = Field(..., min_length=1)
    dates: str = Field(..., min_length=1)


def get_generator() -> GeminiDocumentGenerator:
    global generator
    if generator is None:
        generator = GeminiDocumentGenerator()
    return generator


@router.post("/generate")
def generate_document(request: DocumentRequest):
    try:
        generated_text = get_generator().generate_document(
            document_type=request.document_type,
            parties=request.parties,
            terms=request.terms,
            dates=request.dates,
        )
        return {"document": generated_text}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

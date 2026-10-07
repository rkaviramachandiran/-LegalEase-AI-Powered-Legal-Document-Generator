import os

import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()


class GeminiDocumentGenerator:
    """Gemini-powered legal document generator."""

    FALLBACK_MODELS = ["gemini-2.5-flash", "gemini-2.5-pro", "gemini-flash-latest"]

    def __init__(self, model_name: str = None):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY is not configured in the .env file.")

        genai.configure(api_key=api_key)
        self.model_name = model_name or os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    def generate_document(
        self,
        document_type: str,
        parties: str,
        terms: str,
        dates: str,
    ) -> str:
        prompt = f"""
You are a professional legal-document drafting assistant.

Create a structured, formal {document_type} using exactly the information supplied by
the user. Do not invent names, dates, addresses, payment amounts, jurisdictions,
obligations, or other material facts that were not supplied.

Document Type:
{document_type}

Parties Involved:
{parties}

Terms & Conditions:
{terms}

Effective Date:
{dates}

Write the document in a professional legal format suitable for editing.
Use clear section headings and numbered clauses where appropriate.
Include the supplied parties, terms, and effective date.
Do not add markdown code fences.
Return only the document text.
"""

        candidate_models = [self.model_name] + [m for m in self.FALLBACK_MODELS if m != self.model_name]
        last_exception = None

        for model_name in candidate_models:
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(prompt)
                text = getattr(response, "text", None)
                if text:
                    return text.strip()
            except Exception as exc:
                last_exception = exc
                if "404" in str(exc) or "not found" in str(exc).lower():
                    continue
                raise exc

        if last_exception:
            raise last_exception
        raise RuntimeError("Gemini returned an empty response.")


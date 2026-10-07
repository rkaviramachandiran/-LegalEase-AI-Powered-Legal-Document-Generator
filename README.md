# LegalEase: AI-Powered Legal Document Generator

LegalEase follows the project documentation architecture:

- Frontend: Streamlit
- Backend: FastAPI
- AI Core: Google Gemini through `google-generativeai`
- Document generation: TXT, DOCX, PDF
- Editable text preview
- Branded logo and footer
- Terms table in DOCX
- Dark HTML preview

## Project structure

```text
LegalEase/
├── ai_core/
│   ├── __init__.py
│   ├── gemini_generator.py
│   └── generator.py
├── docs/
├── frontend/
│   ├── __init__.py
│   └── app.py
├── Image/
│   ├── Logo.png
│   └── inverseLogo.png
├── legalEaseAPI/
│   ├── __init__.py
│   ├── main.py
│   └── routes.py
├── .env
├── .env.example
├── .gitignore
├── config.py
├── requirements.txt
└── run.sh
```

## VS Code setup

1. Open this folder in VS Code.
2. Create a virtual environment:

### Windows

```powershell
python -m venv venv
venv\Scripts\activate
```

### macOS/Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Copy `.env.example` to `.env`.
5. Put your Google Gemini API key in `.env`.

```env
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash
BACKEND_URL=http://localhost:8000
```

## Run

Open two VS Code terminals.

### Terminal 1 - FastAPI

```bash
uvicorn legalEaseAPI.main:app --reload
```

Backend:
`http://localhost:8000`

API documentation:
`http://localhost:8000/docs`

### Terminal 2 - Streamlit

```bash
streamlit run frontend/app.py
```

The Streamlit terminal will show the local frontend URL.

## Test

1. Enter a document type, for example `Freelance Work Contract`.
2. Enter the parties.
3. Enter terms separated with semicolons.
4. Enter the effective date.
5. Click `Generate Document`.
6. Review the dark HTML preview.
7. Click `Click to Edit Document`.
8. Download TXT, DOCX, or PDF.

## API test

POST to:

```text
http://localhost:8000/generate
```

Example JSON:

```json
{
  "document_type": "Freelance Work Contract",
  "parties": "Jane Doe (Service Provider), TechNova Inc. (Client)",
  "terms": "Payment to be made within 30 days of invoice; The provider agrees to deliver work by the agreed deadline; Confidentiality must be maintained at all times",
  "dates": "April 10, 2025"
}
```

## Notes

The default model is configured as `gemini-2.5-flash`. The backend also includes automatic fallback to other active models (`gemini-2.5-pro`, `gemini-flash-latest`) should a requested model be retired or unsupported by your Google API account.

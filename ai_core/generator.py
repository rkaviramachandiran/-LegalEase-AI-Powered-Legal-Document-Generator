import html
import re
from io import BytesIO
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.shared import Inches, Pt
from fpdf import FPDF

BASE_DIR = Path(__file__).resolve().parent.parent
LOGO_PATH = BASE_DIR / "Image" / "Logo.png"


def sanitize_text(text: str) -> str:
    """Remove typographic/special characters that can break document formatting."""
    replacements = {
        "‘": "'",
        "’": "'",
        "“": '"',
        "”": '"',
        "–": "-",
        "—": "-",
        "…": "...",
        " ": " ",
        "•": "-",
        "®": "(R)",
        "™": "(TM)",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)

    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", text).strip()
    return text.encode("latin-1", "replace").decode("latin-1")


def _split_document(text: str):
    lines = [line.strip() for line in sanitize_text(text).splitlines()]
    return [line for line in lines if line]


def _extract_terms(text: str):
    terms = []
    in_terms = False

    for line in _split_document(text):
        upper = line.upper()
        if "TERMS & CONDITIONS" in upper or "TERMS AND CONDITIONS" in upper:
            in_terms = True
            continue

        if in_terms:
            if re.match(r"^(ARTICLE|SECTION|CLAUSE)\s+\d+", upper):
                break
            if line.startswith(("-", "*", "•")):
                value = line.lstrip("-*• ").strip()
                if value:
                    terms.append(value)
            elif re.match(r"^\d+[.)]\s+", line):
                value = re.sub(r"^\d+[.)]\s+", "", line).strip()
                if value:
                    terms.append(value)

    return terms


def format_docx(text: str, doc_type: str) -> bytes:
    """Create a branded Word document with logo, headings, terms table and footer."""
    document = Document()
    section = document.sections[0]
    section.top_margin = Inches(0.75)
    section.bottom_margin = Inches(0.75)
    section.left_margin = Inches(0.85)
    section.right_margin = Inches(0.85)

    styles = document.styles
    styles["Normal"].font.name = "Times New Roman"
    styles["Normal"].font.size = Pt(12)

    if LOGO_PATH.exists():
        paragraph = document.add_paragraph()
        paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = paragraph.add_run()
        run.add_picture(str(LOGO_PATH), width=Inches(1.65))

    title = document.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = title.add_run(sanitize_text(doc_type).upper())
    run.bold = True
    run.font.name = "Times New Roman"
    run.font.size = Pt(16)

    for line in _split_document(text):
        if re.match(r"^(ARTICLE|SECTION|CLAUSE)\s+\d+", line, re.I):
            p = document.add_paragraph()
            run = p.add_run(line)
            run.bold = True
            run.font.name = "Times New Roman"
            run.font.size = Pt(12)
        elif line.startswith(("-", "*", "•")):
            p = document.add_paragraph(style="List Bullet")
            p.add_run(line.lstrip("-*• ").strip())
        else:
            p = document.add_paragraph(line)
            p.paragraph_format.space_after = Pt(6)

    terms = _extract_terms(text)
    if terms:
        heading = document.add_paragraph()
        run = heading.add_run("Terms")
        run.bold = True
        table = document.add_table(rows=1, cols=2)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        table.style = "Table Grid"
        table.rows[0].cells[0].text = "No."
        table.rows[0].cells[1].text = "Term"
        for index, term in enumerate(terms, start=1):
            cells = table.add_row().cells
            cells[0].text = str(index)
            cells[1].text = term
            cells[0].vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER

    footer = section.footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    footer.add_run("LegalEase - AI-Powered Legal Document Generator").font.name = "Times New Roman"

    output = BytesIO()
    document.save(output)
    return output.getvalue()


class BrandedPDF(FPDF):
    def __init__(self, doc_type: str):
        super().__init__()
        self.doc_type = sanitize_text(doc_type)
        self.set_auto_page_break(auto=True, margin=18)

    def header(self):
        if LOGO_PATH.exists():
            self.image(str(LOGO_PATH), x=85, y=8, w=40)
            self.ln(18)
        self.set_font("Helvetica", "B", 14)
        self.cell(0, 8, self.doc_type.upper(), align="C")
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 8, "LegalEase - AI-Powered Legal Document Generator", align="C")


def format_pdf(text: str, doc_type: str) -> bytes:
    """Create a branded PDF with logo, bold section headings, bullets and footer."""
    pdf = BrandedPDF(doc_type)
    pdf.add_page()

    for line in _split_document(text):
        if re.match(r"^(ARTICLE|SECTION|CLAUSE)\s+\d+", line, re.I):
            pdf.set_font("Helvetica", "B", 11)
            pdf.multi_cell(0, 7, line)

        elif line.startswith(("-", "*", "•")):
            pdf.set_font("Helvetica", "", 11)
            pdf.multi_cell(0, 6, "- " + line.lstrip("-*• ").strip())

        else:
            pdf.set_font("Helvetica", "", 11)
            pdf.multi_cell(0, 6, line)

        pdf.ln(1)

    # fpdf handles output via dest='S' for string/bytes or direct output in fpdf2
    try:
        out = pdf.output(dest="S")
    except (TypeError, ValueError):
        out = pdf.output()

    if isinstance(out, bytes):
        return out

    if isinstance(out, bytearray):
        return bytes(out)

    if isinstance(out, str):
        return out.encode("latin-1", "replace")

    return bytes(out)
def format_html_preview(text: str) -> str:
    """Convert generated output to styled HTML blocks for Streamlit preview."""
    blocks = []
    lines = _split_document(text)
    
    for line in lines:
        safe = html.escape(line)
        upper = line.upper()
        
        # Match Article, Section, Clause, or ALL CAPS headers
        if re.match(r"^(ARTICLE|SECTION|CLAUSE)\s+\d+", line, re.I) or (len(line) < 60 and line.isupper() and not line.endswith(".")):
            blocks.append(f'<div class="doc-section-header"><span class="header-icon">§</span> {safe}</div>')
        elif line.startswith(("-", "*", "•")):
            term_content = html.escape(line.lstrip("-*• ").strip())
            blocks.append(f'<div class="doc-bullet-item"><span class="bullet-dot">•</span> {term_content}</div>')
        elif re.match(r"^\d+[.)]\s+", line):
            blocks.append(f'<div class="doc-numbered-item">{safe}</div>')
        elif "IN WITNESS WHEREOF" in upper or "EXECUTED AS OF" in upper:
            blocks.append(f'<div class="doc-witness-block">{safe}</div>')
        else:
            # Highlight dates or party terms if present
            safe_highlighted = re.sub(
                r'(\b\d{1,2}(?:st|nd|rd|th)?\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b)',
                r'<span class="doc-date-highlight">\1</span>',
                safe,
                flags=re.IGNORECASE
            )
            blocks.append(f'<p class="doc-paragraph">{safe_highlighted}</p>')

    return "\n".join(blocks)


def analyze_legal_document(text: str) -> dict:
    """Analyze document structure and extract risk assessment & key clauses."""
    upper = text.upper()
    
    clauses = [
        {
            "name": "Confidentiality & Non-Disclosure",
            "detected": any(k in upper for k in ["CONFIDENTIAL", "NON-DISCLOSURE", "PROPRIETARY INFORMATION"]),
            "icon": "🔒",
            "importance": "High",
            "summary": "Protects trade secrets and proprietary data."
        },
        {
            "name": "Termination & Notice",
            "detected": any(k in upper for k in ["TERMINATION", "TERMINATE", "NOTICE PERIOD", "EXPIRATION"]),
            "icon": "🚪",
            "importance": "High",
            "summary": "Defines rules and timeframe for ending the agreement."
        },
        {
            "name": "Governing Law & Jurisdiction",
            "detected": any(k in upper for k in ["GOVERNING LAW", "JURISDICTION", "LAWS OF", "COURTS OF"]),
            "icon": "⚖️",
            "importance": "Critical",
            "summary": "Specifies legal jurisdiction and enforcement court."
        },
        {
            "name": "Payment & Compensation",
            "detected": any(k in upper for k in ["PAYMENT", "COMPENSATION", "FEES", "INVOICE", "CONSIDERATION"]),
            "icon": "💰",
            "importance": "High",
            "summary": "Outlines financial obligations and schedules."
        },
        {
            "name": "Intellectual Property Ownership",
            "detected": any(k in upper for k in ["INTELLECTUAL PROPERTY", "WORK MADE FOR HIRE", "COPYRIGHT", "OWNERSHIP"]),
            "icon": "💡",
            "importance": "Medium",
            "summary": "Clarifies rights to created assets and IP."
        },
        {
            "name": "Limitation of Liability & Indemnity",
            "detected": any(k in upper for k in ["INDEMNIF", "LIMITATION OF LIABILITY", "HOLD HARMLESS", "DAMAGES"]),
            "icon": "🛡️",
            "importance": "High",
            "summary": "Shields parties against catastrophic legal liabilities."
        }
    ]
    
    detected_count = sum(1 for c in clauses if c["detected"])
    total_count = len(clauses)
    compliance_score = int((detected_count / total_count) * 100)
    
    words = len(text.split())
    read_time_min = max(1, round(words / 200, 1))
    
    return {
        "word_count": words,
        "character_count": len(text),
        "read_time_min": read_time_min,
        "compliance_score": compliance_score,
        "clauses": clauses
    }


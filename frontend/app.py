import html
import re

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import requests
import streamlit as st

from ai_core.generator import (
    format_docx,
    format_html_preview,
    format_pdf,
    sanitize_text,
)

API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="LegalEase",
    page_icon="⚖️",
    layout="wide",
)

st.markdown(
    """
    <style>
    .block-container { max-width: 1100px; padding-top: 2rem; }
    .title { text-align: center; font-size: 42px; font-weight: 800; margin-bottom: 0; }
    .subtitle { text-align: center; color: #9ca3af; margin-bottom: 2rem; }
    .preview-card {
        background: #111827;
        border: 1px solid #374151;
        border-radius: 14px;
        padding: 24px;
        max-height: 520px;
        overflow-y: auto;
        color: #f3f4f6;
        line-height: 1.65;
    }
    .preview-card h3 { color: #ffffff; margin-top: 22px; }
    .preview-card .term { margin: 8px 0; }
    </style>
    """,
    unsafe_allow_html=True,
)

if "generated_text" not in st.session_state:
    st.session_state.generated_text = ""
if "show_edit" not in st.session_state:
    st.session_state.show_edit = False

left, center, right = st.columns([1, 2, 1])
with center:
    try:
        st.image("Image/Logo.png", width=180)
    except Exception:
        st.markdown("<h1 class='title'>LegalEase</h1>", unsafe_allow_html=True)

st.markdown("<div class='title'>LegalEase</div>", unsafe_allow_html=True)
st.markdown(
    "<div class='subtitle'>AI-Powered Legal Document Generator</div>",
    unsafe_allow_html=True,
)

document_type = st.text_input("Document Type")
parties = st.text_area("Parties Involved")
terms = st.text_area("Terms & Conditions (Use semicolons for bullet points)")
dates = st.text_input("Effective Date")

if st.button("Generate Document", type="primary", use_container_width=True):
    if not all([document_type.strip(), parties.strip(), terms.strip(), dates.strip()]):
        st.error("Please provide document type, parties, terms, and effective date.")
    else:
        payload = {
            "document_type": document_type,
            "parties": parties,
            "terms": terms,
            "dates": dates,
        }
        try:
            response = requests.post(
                f"{API_URL}/generate",
                json=payload,
                timeout=120,
            )
            response.raise_for_status()
            st.session_state.generated_text = sanitize_text(
                response.json()["document"]
            )
            st.session_state.show_edit = False
        except requests.RequestException as exc:
            st.error(f"Could not connect to the FastAPI backend: {exc}")
        except (KeyError, ValueError) as exc:
            st.error(f"Invalid backend response: {exc}")

if st.session_state.generated_text:
    st.subheader("Document Generated")

    styled_html = format_html_preview(st.session_state.generated_text)
    st.markdown(
        f'<div class="preview-card">{styled_html}</div>',
        unsafe_allow_html=True,
    )

    if st.button("✏️ Click to Edit Document", use_container_width=True):
        st.session_state.show_edit = True

    if st.session_state.show_edit:
        edited_text = st.text_area(
            "Edit Document Below:",
            st.session_state.generated_text,
            height=300,
        )
        st.session_state.generated_text = edited_text

    generated_text = st.session_state.generated_text

    st.download_button(
        "📄 Download as TXT",
        data=generated_text,
        file_name=f"{document_type.replace(' ', '_').lower()}.txt",
        mime="text/plain",
        use_container_width=True,
    )

    st.download_button(
        "📝 Download as DOCX",
        data=format_docx(generated_text, document_type),
        file_name=f"{document_type.replace(' ', '_').lower()}.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        use_container_width=True,
    )

    st.download_button(
        "📕 Download as PDF",
        data=format_pdf(generated_text, document_type),
        file_name=f"{document_type.replace(' ', '_').lower()}.pdf",
        mime="application/pdf",
        use_container_width=True,
    )

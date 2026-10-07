import html
import re
import sys
import os
import requests
import streamlit as st

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ai_core.generator import (
    format_docx,
    format_html_preview,
    format_pdf,
    sanitize_text,
    analyze_legal_document,
)

API_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# Page Configuration
st.set_page_config(
    page_title="LegalEase AI Studio | Enterprise Legal Document Generator",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom High-End Styling (Dark Mode, Glassmorphism, Gold & Cyber Accents)
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800&family=Plus+Jakarta+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
        background-color: #090D16;
        color: #F3F4F6;
    }

    /* Main Container Padding */
    .block-container {
        max-width: 1280px;
        padding-top: 1.5rem;
        padding-bottom: 3rem;
    }

    /* Gradient Background Mesh Overlay */
    .stApp {
        background: radial-gradient(circle at 50% 0%, rgba(30, 41, 59, 0.5) 0%, rgba(9, 13, 22, 1) 70%);
    }

    /* Hero Banner Styles */
    .hero-container {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.9) 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(16px);
        border-radius: 20px;
        padding: 30px;
        text-align: center;
        margin-bottom: 25px;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.1);
        position: relative;
        overflow: hidden;
    }

    .hero-container::before {
        content: '';
        position: absolute;
        top: 0; left: 50%;
        transform: translateX(-50%);
        width: 60%;
        height: 2px;
        background: linear-gradient(90deg, transparent, #D4AF37, #6366F1, transparent);
    }

    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(212, 175, 55, 0.12);
        border: 1px solid rgba(212, 175, 55, 0.3);
        color: #F59E0B;
        padding: 4px 14px;
        border-radius: 9999px;
        font-size: 13px;
        font-weight: 600;
        margin-bottom: 12px;
        letter-spacing: 0.5px;
    }

    .hero-title {
        font-family: 'Outfit', sans-serif;
        font-size: 42px;
        font-weight: 800;
        background: linear-gradient(135deg, #FFFFFF 30%, #D4AF37 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0 0 8px 0;
        letter-spacing: -0.5px;
    }

    .hero-subtitle {
        color: #94A3B8;
        font-size: 16px;
        font-weight: 400;
        margin: 0;
    }

    /* Glass Cards */
    .glass-card {
        background: rgba(15, 23, 42, 0.65);
        border: 1px solid rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(12px);
        border-radius: 16px;
        padding: 22px;
        margin-bottom: 20px;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.25);
    }

    .card-header {
        font-family: 'Outfit', sans-serif;
        font-size: 18px;
        font-weight: 700;
        color: #F8FAFC;
        margin-bottom: 16px;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* Document Preview Paper View */
    .doc-preview-container {
        background: #0F172A;
        border: 1px solid #334155;
        border-radius: 14px;
        padding: 32px 40px;
        max-height: 600px;
        overflow-y: auto;
        color: #E2E8F0;
        line-height: 1.75;
        font-size: 15px;
        box-shadow: inset 0 2px 10px rgba(0,0,0,0.5);
    }

    .doc-preview-header {
        text-align: center;
        border-bottom: 2px solid #D4AF37;
        padding-bottom: 16px;
        margin-bottom: 24px;
    }

    .doc-preview-title {
        font-family: 'Outfit', serif;
        font-size: 24px;
        font-weight: 700;
        color: #F8FAFC;
        letter-spacing: 1px;
    }

    .doc-section-header {
        font-family: 'Outfit', sans-serif;
        font-size: 16px;
        font-weight: 700;
        color: #F59E0B;
        margin-top: 24px;
        margin-bottom: 10px;
        border-left: 3px solid #D4AF37;
        padding-left: 10px;
    }

    .doc-paragraph {
        margin-bottom: 14px;
        color: #CBD5E1;
        text-align: justify;
    }

    .doc-bullet-item {
        margin: 6px 0 6px 18px;
        color: #E2E8F0;
    }

    .doc-date-highlight {
        color: #38BDF8;
        font-weight: 600;
    }

    .doc-witness-block {
        margin-top: 30px;
        padding: 16px;
        background: rgba(30, 41, 59, 0.5);
        border: 1px dashed #475569;
        border-radius: 8px;
        font-style: italic;
        text-align: center;
    }

    /* Clause Audit Grid */
    .audit-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 14px;
        margin-top: 14px;
    }

    .audit-card {
        background: rgba(30, 41, 59, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 12px;
        padding: 16px;
        transition: all 0.2s ease;
    }

    .audit-card.detected {
        border-left: 4px solid #10B981;
    }

    .audit-card.missing {
        border-left: 4px solid #64748B;
        opacity: 0.75;
    }

    .audit-status {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 6px;
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
    }

    .status-pass {
        background: rgba(16, 185, 129, 0.15);
        color: #34D399;
    }

    .status-info {
        background: rgba(100, 116, 139, 0.2);
        color: #94A3B8;
    }

    /* Buttons Styling */
    .stButton>button {
        border-radius: 10px !important;
        font-weight: 600 !important;
        transition: all 0.25s ease !important;
    }

    button[kind="primary"] {
        background: linear-gradient(135deg, #6366F1 0%, #4F46E5 50%, #D4AF37 100%) !important;
        border: none !important;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4) !important;
    }

    button[kind="primary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(99, 102, 241, 0.6) !important;
    }

    /* Custom Input Polish */
    .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {
        background-color: #0F172A !important;
        border: 1px solid #334155 !important;
        border-radius: 10px !important;
        color: #F8FAFC !important;
    }

    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #6366F1 !important;
        box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.2) !important;
    }

    /* Metric Cards */
    .metric-container {
        display: flex;
        gap: 15px;
        margin-bottom: 20px;
    }

    .metric-box {
        flex: 1;
        background: rgba(15, 23, 42, 0.8);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 14px 18px;
        text-align: center;
    }

    .metric-value {
        font-family: 'Outfit', sans-serif;
        font-size: 26px;
        font-weight: 700;
        color: #F59E0B;
    }

    .metric-label {
        font-size: 12px;
        color: #94A3B8;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    ::-webkit-scrollbar-track {
        background: #090D16;
    }
    ::-webkit-scrollbar-thumb {
        background: #334155;
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #475569;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Initialize Session States bound to Widget Keys
if "generated_text" not in st.session_state:
    st.session_state.generated_text = ""
if "doc_history" not in st.session_state:
    st.session_state.doc_history = []
if "input_doc_type" not in st.session_state:
    st.session_state["input_doc_type"] = "Non-Disclosure Agreement (NDA)"
if "input_parties" not in st.session_state:
    st.session_state["input_parties"] = "AlphaTech Innovations Inc. (Disclosing Party), Quantum AI Labs LLC (Receiving Party)"
if "input_terms" not in st.session_state:
    st.session_state["input_terms"] = "All shared technical designs, source code, and trade secrets remain strictly confidential; Confidentiality period shall endure for 3 years from effective date; Neither party shall disclose proprietary information without prior written authorization; Dispute resolution shall take place under Delaware state laws"
if "input_dates" not in st.session_state:
    st.session_state["input_dates"] = "October 15, 2026"
if "watermark_text" not in st.session_state:
    st.session_state.watermark_text = "CONFIDENTIAL DRAFT"

# Streamlit Callback Helpers (Executed BEFORE Widget Render)
def set_preset_fields(doc_type, parties, terms, dates):
    st.session_state["input_doc_type"] = doc_type
    st.session_state["input_parties"] = parties
    st.session_state["input_terms"] = terms
    st.session_state["input_dates"] = dates

def reset_preset_fields():
    st.session_state["input_doc_type"] = ""
    st.session_state["input_parties"] = ""
    st.session_state["input_terms"] = ""
    st.session_state["input_dates"] = ""

def append_clause_to_terms(clause_text):
    current = st.session_state.get("input_terms", "").strip()
    if current:
        st.session_state["input_terms"] = f"{current}; {clause_text}"
    else:
        st.session_state["input_terms"] = clause_text

def load_history_draft(doc_title, doc_text):
    st.session_state.generated_text = doc_text
    st.session_state["input_doc_type"] = doc_title

# Preset Template Definitions
PRESETS = {
    "🔒 Mutual NDA": {
        "doc_type": "Mutual Non-Disclosure Agreement",
        "parties": "Nexus Dynamics Inc. (Party A), CyberVanguard Security LLC (Party B)",
        "terms": "Mutual non-disclosure of technical architecture, financial records, and client rosters; Confidentiality obligation lasts 3 years; Permitted disclosures restricted to essential employees under signed NDA; Governed by the laws of California",
        "dates": "October 20, 2026"
    },
    "💼 Freelance Contract": {
        "doc_type": "Freelance Software Development Contract",
        "parties": "Alex Rivera (Service Provider), Horizon Media Group (Client)",
        "terms": "Provider agrees to deliver custom full-stack web app by November 30, 2026; Client shall pay $12,500 in three milestone payments; All intellectual property created transfers to Client upon final payment; Net 15 payment terms on invoices",
        "dates": "October 15, 2026"
    },
    "📜 Employment Agreement": {
        "doc_type": "Executive Employment Agreement",
        "parties": "Apex Global Solutions Inc. (Employer), Dr. Elena Rostova (Employee)",
        "terms": "Employee is hired as VP of AI Engineering at annual salary of $240,000; Standard 30 days written notice required for voluntary resignation; Non-solicitation of clients and staff for 12 months post-employment; Standard health and stock equity benefits apply",
        "dates": "November 1, 2026"
    },
    "🏠 Residential Lease": {
        "doc_type": "Residential Lease Agreement",
        "parties": "Oakridge Property Management (Lessor), Marcus Vance (Lessee)",
        "terms": "Lease for Apartment 4B located at 742 Evergreen Terrace for 12 months; Monthly rent of $2,800 payable on 1st of each month; Security deposit of $2,800 due at signing; No sub-leasing permitted without written landlord consent",
        "dates": "November 1, 2026"
    },
    "💻 SaaS Terms of Service": {
        "doc_type": "SaaS Terms of Service & License",
        "parties": "CloudScale Platforms Inc. (Licensor), Registered Subscribers (Licensees)",
        "terms": "Licensor provides 99.9% uptime Service Level Agreement for cloud API; Subscription fees billed monthly in advance; Limitation of liability capped at total fees paid in preceding 12 months; Governed under New York jurisdiction",
        "dates": "October 10, 2026"
    }
}

# Sidebar Controls & History
with st.sidebar:
    try:
        st.image("Image/inverseLogo.png", width=190)
    except Exception:
        st.markdown("<h2 style='color:#F59E0B; text-align:center;'>⚖️ LegalEase</h2>", unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### ⚙️ Studio Preferences")
    
    watermark_opt = st.text_input("Document Watermark Tag", value=st.session_state.watermark_text)
    st.session_state.watermark_text = watermark_opt
    
    legal_tone = st.selectbox(
        "AI Drafting Style / Tone",
        ["Strict Executive Legal", "Balanced Commercial Standard", "Plain English / Simplified"]
    )
    
    include_witness = st.checkbox("Include Execution & Witness Signature Block", value=True)

    st.markdown("---")
    st.markdown("### 📜 Session Draft History")
    if st.session_state.doc_history:
        for idx, item in enumerate(reversed(st.session_state.doc_history[-5:])):
            st.button(
                f"📄 {item['title'][:22]}...",
                key=f"hist_{idx}",
                on_click=load_history_draft,
                args=(item["title"], item["text"])
            )
    else:
        st.info("No documents generated in current session yet.")

    st.markdown("---")
    st.markdown(
        """
        <div style="font-size:11px; color:#64748B; text-align:center;">
            LegalEase AI Studio v2.0<br>
            Powered by Google Gemini Enterprise AI<br>
            <i>Note: Always review AI drafts with licensed counsel.</i>
        </div>
        """,
        unsafe_allow_html=True
    )

# Hero Header
st.markdown(
    """
    <div class="hero-container">
        <div class="hero-badge">✨ AI-POWERED LEGAL DOCUMENT INTELLIGENCE</div>
        <h1 class="hero-title">LegalEase AI Studio</h1>
        <p class="hero-subtitle">Draft, audit, customize, and export professional contracts and legal agreements in seconds.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Quick Presets Selection Bar
st.markdown("<div style='font-weight:700; color:#94A3B8; font-size:13px; margin-bottom:8px;'>⚡ QUICK TEMPLATE PRESETS (CLICK TO AUTO-FILL):</div>", unsafe_allow_html=True)
preset_cols = st.columns(len(PRESETS) + 1)

for idx, (p_name, p_data) in enumerate(PRESETS.items()):
    preset_cols[idx].button(
        p_name,
        use_container_width=True,
        on_click=set_preset_fields,
        args=(p_data["doc_type"], p_data["parties"], p_data["terms"], p_data["dates"])
    )

preset_cols[-1].button("🔄 Reset", use_container_width=True, on_click=reset_preset_fields)

st.markdown("<br>", unsafe_allow_html=True)

# Main Form Container
with st.container():
    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.markdown(
            """
            <div class="glass-card">
                <div class="card-header">📋 1. Agreement Metadata & Parties</div>
            """,
            unsafe_allow_html=True
        )
        
        doc_type_val = st.text_input(
            "Document Type / Title",
            placeholder="e.g. Non-Disclosure Agreement, Software Development Contract",
            key="input_doc_type"
        )

        parties_val = st.text_area(
            "Contracting Parties & Roles",
            placeholder="e.g. Acme Corp (Disclosing Party), Jane Smith (Receiving Party)",
            height=100,
            key="input_parties"
        )

        dates_val = st.text_input(
            "Effective Date",
            placeholder="e.g. October 15, 2026 or Upon Execution",
            key="input_dates"
        )

        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown(
            """
            <div class="glass-card">
                <div class="card-header">⚖️ 2. Key Terms & Custom Clauses</div>
            """,
            unsafe_allow_html=True
        )
        
        terms_val = st.text_area(
            "Terms & Clauses (Separate distinct clauses with semicolons ';')",
            placeholder="e.g. Payment due within 30 days; Confidentiality valid for 3 years; Governed by California Law",
            height=170,
            key="input_terms"
        )

        st.markdown("<div style='font-size:12px; color:#94A3B8;'>💡 <b>Quick Clause Shortcuts:</b> Click below to append standard clauses:</div>", unsafe_allow_html=True)
        chip_col1, chip_col2, chip_col3 = st.columns(3)
        
        chip_col1.button(
            "+ Net 30 Payment",
            use_container_width=True,
            on_click=append_clause_to_terms,
            args=("Payment of all undisputed invoices shall be completed within 30 days of receipt",)
        )
        
        chip_col2.button(
            "+ 30-Day Notice",
            use_container_width=True,
            on_click=append_clause_to_terms,
            args=("Either party may terminate this agreement upon providing 30 days written notice",)
        )
        
        chip_col3.button(
            "+ DE Jurisdiction",
            use_container_width=True,
            on_click=append_clause_to_terms,
            args=("This agreement shall be governed by and construed in accordance with the laws of Delaware",)
        )

        st.markdown("</div>", unsafe_allow_html=True)

# Generate Action Button
st.markdown("<br>", unsafe_allow_html=True)
if st.button("✨ GENERATE PROFESSIONAL LEGAL DOCUMENT", type="primary", use_container_width=True):
    doc_type_req = st.session_state.get("input_doc_type", "")
    parties_req = st.session_state.get("input_parties", "")
    terms_req = st.session_state.get("input_terms", "")
    dates_req = st.session_state.get("input_dates", "")
    
    if not all([doc_type_req.strip(), parties_req.strip(), terms_req.strip(), dates_req.strip()]):
        st.error("⚠️ Please fill in all required fields (Document Type, Parties, Terms, and Effective Date).")
    else:
        with st.spinner("🤖 Gemini Enterprise AI is drafting your customized legal agreement..."):
            payload = {
                "document_type": doc_type_req,
                "parties": parties_req,
                "terms": terms_req,
                "dates": dates_req,
            }
            try:
                response = requests.post(
                    f"{API_URL}/generate",
                    json=payload,
                    timeout=120,
                )
                response.raise_for_status()
                gen_text = sanitize_text(response.json()["document"])
                st.session_state.generated_text = gen_text
                
                # Save to history
                st.session_state.doc_history.append({
                    "title": doc_type_req,
                    "text": gen_text
                })
                st.toast("✅ Legal document successfully generated!", icon="⚖️")
            except requests.RequestException as exc:
                st.error(f"❌ Connection error to legal backend ({API_URL}): {exc}")
            except (KeyError, ValueError) as exc:
                st.error(f"❌ Error processing response: {exc}")

# Workspace Output Section
if st.session_state.generated_text:
    st.markdown("---")
    
    current_doc_type = st.session_state.get("input_doc_type", "Legal Document")
    current_dates = st.session_state.get("input_dates", "Upon Execution")
    
    # Document Metrics Bar
    audit_data = analyze_legal_document(st.session_state.generated_text)
    
    st.markdown(
        f"""
        <div class="metric-container">
            <div class="metric-box">
                <div class="metric-value">{audit_data['word_count']}</div>
                <div class="metric-label">Total Words</div>
            </div>
            <div class="metric-box">
                <div class="metric-value">{audit_data['read_time_min']} min</div>
                <div class="metric-label">Est. Read Time</div>
            </div>
            <div class="metric-box">
                <div class="metric-value" style="color:#10B981;">{audit_data['compliance_score']}%</div>
                <div class="metric-label">Standard Clause Coverage</div>
            </div>
            <div class="metric-box">
                <div class="metric-value" style="color:#6366F1;">Gemini 2.5</div>
                <div class="metric-label">AI Engine</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Multi-Tab Document Workspace
    tab_preview, tab_edit, tab_audit, tab_signature = st.tabs([
        "📄 Styled Document Preview",
        "✏️ Live Interactive Editor",
        "🛡️ AI Legal Risk Audit",
        "🔏 Execution & Signature Block"
    ])

    with tab_preview:
        formatted_html = format_html_preview(st.session_state.generated_text)
        watermark_html = f"<div style='text-align:right; font-size:11px; color:#F59E0B; font-weight:700; letter-spacing:2px; margin-bottom:10px;'>[{st.session_state.watermark_text}]</div>" if st.session_state.watermark_text else ""
        
        st.markdown(
            f"""
            <div class="doc-preview-container">
                {watermark_html}
                <div class="doc-preview-header">
                    <div class="doc-preview-title">{html.escape(current_doc_type.upper())}</div>
                    <div style="font-size:12px; color:#94A3B8; margin-top:4px;">OFFICIAL DRAFT • LEGAL EASE COMPLIANT</div>
                </div>
                {formatted_html}
            </div>
            """,
            unsafe_allow_html=True,
        )

    with tab_edit:
        st.markdown("<div style='font-size:13px; color:#94A3B8; margin-bottom:8px;'>You can edit the draft directly below. All changes automatically update downloads.</div>", unsafe_allow_html=True)
        edited_content = st.text_area(
            "Document Source Text",
            st.session_state.generated_text,
            height=450,
            label_visibility="collapsed"
        )
        st.session_state.generated_text = edited_content

    with tab_audit:
        st.markdown("#### 🛡️ Clause Breakdown & Compliance Audit")
        st.markdown("<p style='color:#94A3B8; font-size:14px;'>Automated structure detection for essential commercial contract terms:</p>", unsafe_allow_html=True)
        
        audit_items = audit_data["clauses"]
        grid_html = "<div class='audit-grid'>"
        for item in audit_items:
            status_class = "detected" if item["detected"] else "missing"
            pill_class = "status-pass" if item["detected"] else "status-info"
            pill_label = "✅ INCLUDED" if item["detected"] else "ℹ️ NOT DETECTED"
            
            grid_html += f"""
            <div class="audit-card {status_class}">
                <div style="display:flex; justify-shadow:space-between; align-items:center; margin-bottom:8px;">
                    <span style="font-size:18px;">{item['icon']} <b>{item['name']}</b></span>
                </div>
                <div style="margin-bottom:8px;">
                    <span class="audit-status {pill_class}">{pill_label}</span>
                    <span style="font-size:11px; color:#94A3B8; margin-left:6px;">Priority: {item['importance']}</span>
                </div>
                <div style="font-size:12px; color:#CBD5E1;">{item['summary']}</div>
            </div>
            """
        grid_html += "</div>"
        st.markdown(grid_html, unsafe_allow_html=True)

    with tab_signature:
        st.markdown("#### 🔏 Formal Execution & Signature Block")
        st.markdown(
            f"""
            <div style="background:#0F172A; border:1px solid #334155; border-radius:12px; padding:24px; color:#F8FAFC;">
                <p>IN WITNESS WHEREOF, the parties hereto have executed this <b>{html.escape(current_doc_type)}</b> as of <b>{html.escape(current_dates)}</b>.</p>
                <br>
                <div style="display:flex; justify-content:space-between; gap:40px; margin-top:20px;">
                    <div style="flex:1; border-top:2px solid #64748B; padding-top:10px;">
                        <b>PARTY A / DISCLOSING PARTY</b><br>
                        <span style="color:#94A3B8; font-size:13px;">Signature: __________________________</span><br>
                        <span style="color:#94A3B8; font-size:13px;">Name: ____________________________</span><br>
                        <span style="color:#94A3B8; font-size:13px;">Title: Authorized Representative</span><br>
                        <span style="color:#94A3B8; font-size:13px;">Date: {html.escape(current_dates)}</span>
                    </div>
                    <div style="flex:1; border-top:2px solid #64748B; padding-top:10px;">
                        <b>PARTY B / RECEIVING PARTY</b><br>
                        <span style="color:#94A3B8; font-size:13px;">Signature: __________________________</span><br>
                        <span style="color:#94A3B8; font-size:13px;">Name: ____________________________</span><br>
                        <span style="color:#94A3B8; font-size:13px;">Title: Authorized Representative</span><br>
                        <span style="color:#94A3B8; font-size:13px;">Date: {html.escape(current_dates)}</span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Export & Download Toolbar
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 📥 Export & Download Studio")
    
    exp_col1, exp_col2, exp_col3, exp_col4 = st.columns(4)
    
    current_doc = st.session_state.generated_text
    doc_filename = current_doc_type.replace(' ', '_').lower() if current_doc_type else "document"

    with exp_col1:
        st.download_button(
            "📄 Export TXT",
            data=current_doc,
            file_name=f"{doc_filename}.txt",
            mime="text/plain",
            use_container_width=True,
        )

    with exp_col2:
        st.download_button(
            "📝 Export DOCX (Word)",
            data=format_docx(current_doc, current_doc_type),
            file_name=f"{doc_filename}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True,
        )

    with exp_col3:
        st.download_button(
            "📕 Export PDF",
            data=format_pdf(current_doc, current_doc_type),
            file_name=f"{doc_filename}.pdf",
            mime="application/pdf",
            use_container_width=True,
        )

    with exp_col4:
        if st.button("📋 Copy Raw Text", use_container_width=True):
            st.code(current_doc, language="text")
            st.toast("Copied text box displayed above!", icon="📋")

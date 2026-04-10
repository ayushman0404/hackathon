import streamlit as st
import pdfplumber
import fitz  # PyMuPDF
import json
import google.generativeai as genai
from PIL import Image
import io
import time
import os
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


# ================= PAGE CONFIG =================
st.set_page_config(page_title="AI PDF Intelligence Engine", layout="wide", initial_sidebar_state="collapsed")

# ================= CUSTOM 3D ANIMATED CSS =================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;400;600&display=swap');

/* ── GLOBAL RESET ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [data-testid="stAppViewContainer"] {
    background: #020408 !important;
    color: #e0f0ff !important;
    font-family: 'Rajdhani', sans-serif !important;
    overflow-x: hidden;
}

[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(ellipse 80% 50% at 20% -10%, rgba(0,200,255,0.12) 0%, transparent 60%),
        radial-gradient(ellipse 60% 40% at 80% 110%, rgba(120,0,255,0.10) 0%, transparent 60%),
        #020408 !important;
}

/* Animated grid background */
[data-testid="stAppViewContainer"]::before {
    content: '';
    position: fixed;
    inset: 0;
    background-image:
        linear-gradient(rgba(0,200,255,0.04) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,200,255,0.04) 1px, transparent 1px);
    background-size: 60px 60px;
    animation: gridScroll 20s linear infinite;
    pointer-events: none;
    z-index: 0;
}

@keyframes gridScroll {
    0%   { background-position: 0 0, 0 0; }
    100% { background-position: 0 60px, 60px 0; }
}

/* Floating orbs */
[data-testid="stAppViewContainer"]::after {
    content: '';
    position: fixed;
    width: 600px; height: 600px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(0,220,255,0.07) 0%, transparent 70%);
    top: -200px; left: -200px;
    animation: orbFloat 15s ease-in-out infinite alternate;
    pointer-events: none;
    z-index: 0;
}

@keyframes orbFloat {
    0%   { transform: translate(0,0) scale(1); }
    100% { transform: translate(300px, 200px) scale(1.3); }
}

/* Hide Streamlit chrome */
#MainMenu, footer, header { visibility: hidden !important; }
[data-testid="stToolbar"] { display: none !important; }
[data-testid="stDecoration"] { display: none !important; }
.stDeployButton { display: none !important; }

/* Main content wrapper */
[data-testid="stMain"] > div { padding: 0 !important; }
.block-container {
    padding: 2rem 3rem 4rem !important;
    max-width: 1200px !important;
    margin: 0 auto !important;
    position: relative;
    z-index: 1;
}

/* ── HERO TITLE ── */
.hero-wrapper {
    text-align: center;
    padding: 3rem 0 2.5rem;
    position: relative;
}

.hero-label {
    font-family: 'Orbitron', monospace;
    font-size: 0.7rem;
    letter-spacing: 0.5em;
    color: #00d4ff;
    text-transform: uppercase;
    margin-bottom: 1rem;
    animation: fadeSlideDown 0.8s ease both;
}

.hero-title {
    font-family: 'Orbitron', monospace;
    font-size: clamp(2.2rem, 5vw, 4rem);
    font-weight: 900;
    line-height: 1.1;
    background: linear-gradient(135deg, #ffffff 0%, #00d4ff 40%, #7b2fff 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    animation: fadeSlideDown 0.9s ease 0.1s both;
    text-shadow: none;
    position: relative;
}

/* Glitch effect on title */
.hero-title::before, .hero-title::after {
    content: attr(data-text);
    position: absolute;
    top: 0; left: 0; right: 0;
    background: linear-gradient(135deg, #ffffff 0%, #00d4ff 40%, #7b2fff 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.hero-title::before {
    animation: glitch1 8s infinite;
    clip-path: polygon(0 0, 100% 0, 100% 35%, 0 35%);
}
.hero-title::after {
    animation: glitch2 8s infinite;
    clip-path: polygon(0 65%, 100% 65%, 100% 100%, 0 100%);
}

@keyframes glitch1 {
    0%,95%,100% { transform: translate(0); opacity: 0; }
    96% { transform: translate(-3px, 1px); opacity: 0.8; }
    97% { transform: translate(3px, -1px); opacity: 0.8; }
    98% { transform: translate(0); opacity: 0; }
}
@keyframes glitch2 {
    0%,93%,100% { transform: translate(0); opacity: 0; }
    94% { transform: translate(3px, 2px); opacity: 0.6; }
    95% { transform: translate(-2px, -1px); opacity: 0.6; }
}

.hero-sub {
    font-size: 1.1rem;
    color: rgba(180,210,255,0.65);
    letter-spacing: 0.08em;
    margin-top: 0.8rem;
    animation: fadeSlideDown 1s ease 0.2s both;
}

/* Animated line under hero */
.hero-line {
    display: flex; align-items: center; gap: 1rem;
    margin: 2rem auto 0;
    max-width: 500px;
    animation: fadeSlideDown 1s ease 0.35s both;
}
.hero-line span { flex: 1; height: 1px; background: linear-gradient(90deg, transparent, #00d4ff, transparent); }
.hero-line i { font-size: 0.6rem; color: #00d4ff; letter-spacing: 0.4em; font-style: normal; font-family: 'Orbitron'; }

@keyframes fadeSlideDown {
    from { opacity: 0; transform: translateY(-20px); }
    to   { opacity: 1; transform: translateY(0); }
}

/* ── STATS BAR ── */
.stats-bar {
    display: flex; gap: 1.5rem; justify-content: center;
    margin: 2rem 0;
    flex-wrap: wrap;
    animation: fadeSlideDown 1s ease 0.5s both;
}
.stat-chip {
    background: rgba(0,200,255,0.06);
    border: 1px solid rgba(0,200,255,0.2);
    border-radius: 2px;
    padding: 0.5rem 1.5rem;
    font-family: 'Orbitron', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.15em;
    color: rgba(0,200,255,0.8);
    text-transform: uppercase;
    position: relative;
    overflow: hidden;
    transition: all 0.3s;
}
.stat-chip::before {
    content: '';
    position: absolute;
    top: 0; left: -100%;
    width: 100%; height: 100%;
    background: linear-gradient(90deg, transparent, rgba(0,200,255,0.15), transparent);
    animation: shimmer 3s infinite;
}
@keyframes shimmer { 100% { left: 100%; } }
.stat-chip:hover {
    border-color: rgba(0,200,255,0.6);
    background: rgba(0,200,255,0.12);
    box-shadow: 0 0 20px rgba(0,200,255,0.2), inset 0 0 20px rgba(0,200,255,0.05);
}

/* ── UPLOAD PANEL ── */
.upload-section {
    background: rgba(5,15,30,0.8);
    border: 1px solid rgba(0,200,255,0.15);
    border-radius: 4px;
    padding: 2.5rem;
    position: relative;
    overflow: hidden;
    margin-bottom: 2rem;
    animation: panelReveal 1s ease 0.6s both;
    box-shadow:
        0 0 0 1px rgba(0,200,255,0.05) inset,
        0 30px 80px rgba(0,0,0,0.6),
        0 0 60px rgba(0,100,255,0.05);
}

/* Corner decorations */
.upload-section::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 60px; height: 60px;
    border-top: 2px solid rgba(0,200,255,0.5);
    border-left: 2px solid rgba(0,200,255,0.5);
    pointer-events: none;
}
.upload-section::after {
    content: '';
    position: absolute;
    bottom: 0; right: 0;
    width: 60px; height: 60px;
    border-bottom: 2px solid rgba(123,47,255,0.5);
    border-right: 2px solid rgba(123,47,255,0.5);
    pointer-events: none;
}

@keyframes panelReveal {
    from { opacity: 0; transform: translateY(30px); }
    to   { opacity: 1; transform: translateY(0); }
}

/* Section label */
.section-label {
    font-family: 'Orbitron', monospace;
    font-size: 0.6rem;
    letter-spacing: 0.4em;
    color: rgba(0,200,255,0.6);
    text-transform: uppercase;
    margin-bottom: 1.2rem;
    display: flex; align-items: center; gap: 0.8rem;
}
.section-label::before {
    content: '';
    display: inline-block;
    width: 20px; height: 1px;
    background: rgba(0,200,255,0.5);
}
.section-label::after {
    content: '';
    flex: 1; height: 1px;
    background: linear-gradient(90deg, rgba(0,200,255,0.3), transparent);
}

/* ── FILE UPLOADER ── */
[data-testid="stFileUploader"] {
    background: rgba(0,200,255,0.03) !important;
    border: 1px dashed rgba(0,200,255,0.25) !important;
    border-radius: 3px !important;
    transition: all 0.4s ease !important;
}
[data-testid="stFileUploader"]:hover {
    border-color: rgba(0,200,255,0.6) !important;
    background: rgba(0,200,255,0.06) !important;
    box-shadow: 0 0 30px rgba(0,200,255,0.1) inset, 0 0 30px rgba(0,200,255,0.05) !important;
}
[data-testid="stFileUploader"] label {
    color: rgba(180,210,255,0.8) !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-size: 1.05rem !important;
    letter-spacing: 0.05em !important;
}
[data-testid="stFileUploaderDropzoneInstructions"] { color: rgba(0,200,255,0.7) !important; }
[data-testid="stFileUploaderDropzone"] svg { fill: rgba(0,200,255,0.5) !important; }

/* ── BUTTON ── */
.stButton > button {
    width: 100% !important;
    background: linear-gradient(135deg, rgba(0,180,255,0.15) 0%, rgba(123,47,255,0.15) 100%) !important;
    border: 1px solid rgba(0,200,255,0.4) !important;
    border-radius: 2px !important;
    color: #00d4ff !important;
    font-family: 'Orbitron', monospace !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.25em !important;
    font-weight: 700 !important;
    padding: 1rem 2rem !important;
    text-transform: uppercase !important;
    cursor: pointer !important;
    position: relative !important;
    overflow: hidden !important;
    transition: all 0.4s ease !important;
    box-shadow: 0 0 20px rgba(0,200,255,0.1), inset 0 0 20px rgba(0,0,0,0.2) !important;
    margin-top: 1.5rem !important;
}
.stButton > button::before {
    content: '' !important;
    position: absolute !important;
    top: 0; left: -100% !important;
    width: 100% !important; height: 100% !important;
    background: linear-gradient(90deg, transparent, rgba(0,200,255,0.3), transparent) !important;
    transition: left 0.5s ease !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, rgba(0,200,255,0.25) 0%, rgba(123,47,255,0.25) 100%) !important;
    border-color: #00d4ff !important;
    box-shadow:
        0 0 40px rgba(0,200,255,0.3),
        0 0 80px rgba(0,200,255,0.1),
        inset 0 0 30px rgba(0,200,255,0.1) !important;
    transform: translateY(-2px) !important;
    color: #ffffff !important;
}
.stButton > button:hover::before { left: 100% !important; }
.stButton > button:active { transform: translateY(0) !important; }

/* ── SUCCESS / INFO / SPINNER ── */
.stSuccess {
    background: rgba(0,255,150,0.06) !important;
    border: 1px solid rgba(0,255,150,0.3) !important;
    border-radius: 2px !important;
    color: rgba(0,255,180,0.9) !important;
    font-family: 'Rajdhani', sans-serif !important;
    letter-spacing: 0.05em !important;
}
.stInfo {
    background: rgba(0,180,255,0.06) !important;
    border: 1px solid rgba(0,180,255,0.25) !important;
    border-radius: 2px !important;
    color: rgba(100,200,255,0.85) !important;
    font-family: 'Rajdhani', sans-serif !important;
    letter-spacing: 0.05em !important;
}
[data-testid="stStatusWidget"],
.stSpinner > div {
    color: #00d4ff !important;
    font-family: 'Orbitron', monospace !important;
    font-size: 0.75rem !important;
    letter-spacing: 0.2em !important;
}

/* ── JSON OUTPUT ── */
[data-testid="stJson"],
.stJson {
    background: rgba(2,8,18,0.9) !important;
    border: 1px solid rgba(0,200,255,0.2) !important;
    border-radius: 4px !important;
    font-family: 'Courier New', monospace !important;
    font-size: 0.8rem !important;
    box-shadow: 0 0 40px rgba(0,100,255,0.05), inset 0 0 60px rgba(0,0,0,0.5) !important;
    color: #7ee8fa !important;
}

/* ── DOWNLOAD BUTTON ── */
[data-testid="stDownloadButton"] > button {
    background: linear-gradient(135deg, rgba(123,47,255,0.15), rgba(200,0,255,0.15)) !important;
    border: 1px solid rgba(123,47,255,0.5) !important;
    color: #b47fff !important;
    font-family: 'Orbitron', monospace !important;
    font-size: 0.75rem !important;
    letter-spacing: 0.2em !important;
    border-radius: 2px !important;
    padding: 0.8rem 2rem !important;
    transition: all 0.3s !important;
    text-transform: uppercase !important;
}
[data-testid="stDownloadButton"] > button:hover {
    border-color: #b47fff !important;
    box-shadow: 0 0 30px rgba(123,47,255,0.3), inset 0 0 20px rgba(123,47,255,0.1) !important;
    color: #ffffff !important;
    transform: translateY(-2px) !important;
}

/* ── FEATURE CARDS ── */
.features-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1.2rem;
    margin: 2rem 0;
    animation: panelReveal 1s ease 0.8s both;
}
@media (max-width: 768px) { .features-grid { grid-template-columns: 1fr; } }

.feat-card {
    background: rgba(5,15,30,0.7);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 3px;
    padding: 1.5rem;
    position: relative;
    overflow: hidden;
    transition: transform 0.4s ease, box-shadow 0.4s ease, border-color 0.4s ease;
    perspective: 1000px;
}
.feat-card:hover {
    transform: translateY(-6px) rotateX(2deg);
    border-color: rgba(0,200,255,0.35);
    box-shadow: 0 20px 60px rgba(0,0,0,0.5), 0 0 30px rgba(0,200,255,0.08);
}
.feat-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    background: linear-gradient(135deg, rgba(0,200,255,0.04) 0%, transparent 60%);
    pointer-events: none;
}
.feat-icon {
    font-size: 1.8rem;
    margin-bottom: 0.8rem;
    display: block;
}
.feat-title {
    font-family: 'Orbitron', monospace;
    font-size: 0.7rem;
    letter-spacing: 0.15em;
    color: rgba(0,200,255,0.85);
    margin-bottom: 0.5rem;
    text-transform: uppercase;
}
.feat-desc {
    font-size: 0.9rem;
    color: rgba(180,200,240,0.6);
    line-height: 1.5;
    letter-spacing: 0.02em;
}

/* ── SCROLLBAR ── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: rgba(0,200,255,0.03); }
::-webkit-scrollbar-thumb { background: rgba(0,200,255,0.2); border-radius: 2px; }
::-webkit-scrollbar-thumb:hover { background: rgba(0,200,255,0.4); }

/* ── FOOTER ── */
.hud-footer {
    text-align: center;
    padding: 2rem 0;
    font-family: 'Orbitron', monospace;
    font-size: 0.55rem;
    letter-spacing: 0.35em;
    color: rgba(0,200,255,0.25);
    text-transform: uppercase;
    margin-top: 3rem;
    border-top: 1px solid rgba(0,200,255,0.06);
}

/* ── PULSE RING ── */
.pulse-wrapper {
    display: flex;
    justify-content: center;
    margin: 1.5rem 0;
}
.pulse-ring {
    width: 12px; height: 12px;
    border-radius: 50%;
    background: #00d4ff;
    box-shadow: 0 0 10px #00d4ff;
    position: relative;
}
.pulse-ring::before, .pulse-ring::after {
    content: '';
    position: absolute;
    inset: 0;
    border-radius: 50%;
    border: 1px solid rgba(0,200,255,0.5);
    animation: pulseRing 2s ease-out infinite;
}
.pulse-ring::after { animation-delay: 1s; }
@keyframes pulseRing {
    from { transform: scale(1); opacity: 1; }
    to   { transform: scale(4); opacity: 0; }
}
</style>
""", unsafe_allow_html=True)

# ================= HERO SECTION =================
st.markdown("""
<div class="hero-wrapper">
    <div class="hero-label">Neural Document Processing System v2.0</div>
    <div class="hero-title" data-text="AI PDF Intelligence Engine">AI PDF Intelligence Engine</div>
    <div class="hero-sub">Extract · Analyze · Transform · Understand</div>
    <div class="hero-line"><span></span><i>◆ ONLINE ◆</i><span></span></div>
</div>

<div class="stats-bar">
    <div class="stat-chip">⬡ Gemini 2.5 Flash</div>
    <div class="stat-chip">⬡ Multi-Page Analysis</div>
    <div class="stat-chip">⬡ Vision + OCR</div>
    <div class="stat-chip">⬡ Smart JSON Output</div>
</div>
""", unsafe_allow_html=True)

# ================= FEATURE CARDS =================
st.markdown("""
<div class="features-grid">
    <div class="feat-card">
        <span class="feat-icon">🔍</span>
        <div class="feat-title">Deep Text Extraction</div>
        <div class="feat-desc">Precision parsing of all textual content with structured numerical extraction and semantic analysis.</div>
    </div>
    <div class="feat-card">
        <span class="feat-icon">🖼️</span>
        <div class="feat-title">Vision Intelligence</div>
        <div class="feat-desc">AI-powered image understanding — detects text, objects, diagrams, and mixed visual content per page.</div>
    </div>
    <div class="feat-card">
        <span class="feat-icon">⚡</span>
        <div class="feat-title">Page Summaries</div>
        <div class="feat-desc">Generates concise AI summaries per page combining both textual and visual signals into one insight.</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ================= UPLOAD PANEL =================
st.markdown("""
<div class="upload-section">
    <div class="section-label">Document Upload Interface</div>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "Drop your PDF here or click to browse",
    type=["pdf"],
    help="Supports multi-page PDFs with mixed text and images"
)

if uploaded_file:
    st.success(f"✦ File locked: **{uploaded_file.name}** ({uploaded_file.size // 1024} KB) — Ready for processing")
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        run_btn = st.button("⟁ INITIATE NEURAL SCAN", key="run")
else:
    st.info("⟐ Awaiting document input — upload a PDF to begin intelligence extraction")
    run_btn = False

st.markdown("</div>", unsafe_allow_html=True)

# ================= FUNCTIONS =================

def process_text_simple(text):
    return {
        "raw_text": text,
        "numbers": [int(s) for s in text.split() if s.isdigit()]
    }

def process_with_gemini(image):
    prompt = """
    Analyze this image carefully.
    Step 1: Check if the image contains readable text (numbers, alphabets, handwritten or printed).
    Step 2:
    - If ONLY text → return: {"type": "text", "content": "extracted text"}
    - If ONLY visual (object/person/scene) → return: {"type": "visual", "description": "what is in the image"}
    - If BOTH text + visual → return: {"type": "mixed", "text": "extracted text", "description": "what is in image"}
    IMPORTANT: Return ONLY valid JSON. No explanation outside JSON.
    """
    try:
        response = model.generate_content([prompt, image])
        return response.text
    except Exception as e:
        return json.dumps({"error": str(e)})

def safe_json_parse(text):
    try:
        return json.loads(text)
    except:
        return {"raw_output": text}

def extract_pdf(pdf_bytes):
    output = []
    with open("temp.pdf", "wb") as f:
        f.write(pdf_bytes)
    pdf = pdfplumber.open("temp.pdf")
    doc = fitz.open("temp.pdf")
    total = len(pdf.pages)
    progress = st.progress(0, text="Initializing scan sequence...")

    for i, page in enumerate(pdf.pages):
        progress.progress((i + 1) / total, text=f"⟁ Scanning page {i+1} of {total}...")
        page_data = {
            "page": i + 1,
            "text_data": None,
            "image_analysis": None,
            "summary": None
        }
        text = page.extract_text()
        if text and text.strip():
            page_data["text_data"] = process_text_simple(text)
        try:
            page_fitz = doc.load_page(i)
            pix = page_fitz.get_pixmap()
            img_bytes = pix.tobytes("png")
            image = Image.open(io.BytesIO(img_bytes))
            result = process_with_gemini(image)
            page_data["image_analysis"] = safe_json_parse(result)
        except Exception as e:
            page_data["image_analysis"] = {"error": str(e)}
        try:
            summary_prompt = f"""
            Based on: TEXT: {page_data['text_data']} IMAGE: {page_data['image_analysis']}
            Generate a short summary of this page in 1-2 lines.
            Return JSON: {{"summary": "..."}}
            """
            summary_res = model.generate_content(summary_prompt)
            page_data["summary"] = safe_json_parse(summary_res.text)
        except:
            page_data["summary"] = {"summary": "Not available"}
        output.append(page_data)
        time.sleep(2)

    progress.empty()
    return output

# ================= RUN =================
if uploaded_file and run_btn:
    st.markdown('<div class="pulse-wrapper"><div class="pulse-ring"></div></div>', unsafe_allow_html=True)
    
    with st.spinner("Neural scan in progress — analyzing document structure..."):
        result = extract_pdf(uploaded_file.read())

    st.markdown("""
    <div style="
        text-align:center; padding:1.5rem;
        background:rgba(0,255,150,0.04);
        border:1px solid rgba(0,255,150,0.2);
        border-radius:3px; margin: 1.5rem 0;
        font-family:'Orbitron',monospace;
        font-size:0.75rem; letter-spacing:0.3em;
        color:rgba(0,255,150,0.9);">
        ✦ SCAN COMPLETE — INTELLIGENCE EXTRACTED ✦
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""<div class="upload-section" style="margin-top:2rem;">
        <div class="section-label">JSON Intelligence Output</div>
    """, unsafe_allow_html=True)
    st.json(result)
    st.markdown("</div>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.download_button(
            "⬇  EXPORT INTELLIGENCE REPORT",
            data=json.dumps(result, indent=4),
            file_name="neural_output.json",
            mime="application/json"
        )

# ================= FOOTER =================
st.markdown("""
<div class="hud-footer">
    ◆ AI PDF Intelligence Engine ◆ Powered by Gemini 2.5 Flash ◆ Neural Vision System ◆
</div>
""", unsafe_allow_html=True)

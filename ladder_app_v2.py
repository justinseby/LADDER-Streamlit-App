"""
LADDER · Gene Set Annotator
Literature-Assisted Dual-annotation and Documentation & Evidence-based Reasoning
Live PubMed Validation + Grounded Chat
"""
from datetime import date
import streamlit as st
import os, re, time, requests, json
import pandas as pd
import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime
from rapidfuzz import process as fuzz_process
import gseapy as gp

# ─── Page Config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="LADDER · Gene Set Annotator",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Design System ────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400;0,500;0,600;0,700;1,400;1,500&family=Source+Sans+3:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;1,9..40,300;1,9..40,400&family=JetBrains+Mono:wght@300;400;500&display=swap');

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   PALETTE  — crisp white + slate + red accent
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
:root {
    --bg:       #ffffff;
    --surface:  #ffffff;
    --surface2: #f8f9fa;
    --surface3: #e9ecef;
    --border:   #ced4da;
    --border2:  #adb5bd;
    --ink:      #0d0d0d;
    --text:     #1a1a2e;
    --sub:      #343a40;
    --muted:    #495057;
    --faint:    #868e96;
    --accent:   #c92a2a;
    --accent2:  #1864ab;
    --green:    #2b8a3e;
    --amber:    #e67700;
    --rule:     #dee2e6;
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   GLOBAL — force dark text everywhere, always
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
html, body { background: #ffffff !important; color: #1a1a2e !important; }

.stApp,
.stApp > div,
.block-container,
.block-container > div { background: #ffffff !important; }

/* Every text node Streamlit might own */
p, span, div, li, label, h1, h2, h3, h4, h5, h6,
td, th, caption, figcaption, summary, legend, small {
    color: #1a1a2e !important;
}

/* Streamlit's own markdown and label classes */
.stMarkdown, .stMarkdown p, .stMarkdown span,
.stMarkdown li, .stMarkdown h1, .stMarkdown h2,
.stMarkdown h3, .stMarkdown h4, .stMarkdown strong,
.stMarkdown em, .stMarkdown a { color: #1a1a2e !important; }

[data-testid="stMarkdownContainer"],
[data-testid="stMarkdownContainer"] * { color: #1a1a2e !important; }

/* Widget labels */
.stTextInput label, .stTextArea label,
.stSelectbox label, .stMultiSelect label,
.stSlider label, .stCheckbox label,
.stRadio label, .stNumberInput label,
[data-testid="stWidgetLabel"],
[data-testid="stWidgetLabel"] * { color: #1a1a2e !important; }

/* Sidebar text */
section[data-testid="stSidebar"],
section[data-testid="stSidebar"] *,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] label {
    color: #1a1a2e !important;
    background: #f8f9fa !important;
}
section[data-testid="stSidebar"] {
    border-right: 1px solid var(--border) !important;
}

/* Expander text */
div[data-testid="stExpander"] summary,
div[data-testid="stExpander"] summary *,
div[data-testid="stExpander"] p,
div[data-testid="stExpander"] span { color: #1a1a2e !important; }

/* Tab text */
.stTabs [data-baseweb="tab"] { color: #495057 !important; }
.stTabs [aria-selected="true"] { color: #0d0d0d !important; font-weight: 600 !important; }

/* Status / spinner text */
div[data-testid="stStatus"] *,
div[data-testid="stStatusLabel"],
div[data-testid="stStatusLabel"] * { color: #1a1a2e !important; }

/* Alert text (override per type below) */
.stInfo *, .stSuccess *, .stWarning *, .stError * { color: inherit !important; }

/* Scrollbar */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: var(--surface2); }
::-webkit-scrollbar-thumb { background: var(--border2); border-radius: 2px; }

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   HEADER
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
.ladder-header {
    padding: 2.4rem 2.8rem 2rem;
    margin-bottom: 1.8rem;
    background: #ffffff;
    border-top: 4px solid var(--accent);
    border-bottom: 1px solid var(--border);
}
.ladder-logo {
    font-family: 'EB Garamond', serif !important;
    font-size: 2.6rem;
    font-weight: 700;
    color: var(--ink) !important;
    margin: 0;
    line-height: 1;
    letter-spacing: -0.5px;
}
.ladder-logo span { color: var(--accent) !important; }
.ladder-sub {
    font-family: 'Source Sans 3', sans-serif !important;
    font-size: 0.86rem;
    color: var(--sub) !important;
    margin-top: 0.5rem;
    font-weight: 400;
    line-height: 1.55;
}
.ladder-sub strong { color: var(--accent) !important; font-weight: 700; }
.context-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    margin-top: 0.9rem;
    background: #fff5f5;
    border: 1px solid #ffa8a8;
    color: var(--accent) !important;
    padding: 4px 14px;
    border-radius: 20px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.74rem;
    letter-spacing: 0.02em;
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   STEP TRAIL
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
.step-trail {
    display: flex;
    align-items: center;
    margin-bottom: 2rem;
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 0.55rem 1.2rem;
}
.step-node {
    display: flex;
    align-items: center;
    gap: 6px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    color: var(--muted) !important;
    padding: 4px 10px;
    border-radius: 4px;
    flex: 1;
    justify-content: center;
    letter-spacing: 0.02em;
}
.step-node.active {
    background: #fff5f5;
    color: var(--accent) !important;
    border: 1px solid #ffa8a8;
    font-weight: 600;
}
.step-node.done {
    background: #ebfbee;
    color: var(--green) !important;
    border: 1px solid #b2f2bb;
}
.step-arrow { color: var(--border2); font-size: 0.7rem; flex-shrink: 0; }

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   INPUTS
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
.stTextArea > div > div > textarea {
    background: #ffffff !important;
    border: 1px solid var(--border) !important;
    border-radius: 6px !important;
    color: #1a1a2e !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.82rem !important;
    line-height: 1.75 !important;
    box-shadow: none !important;
}
.stTextArea > div > div > textarea::placeholder { color: var(--faint) !important; }
.stTextArea > div > div > textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(201,42,42,0.1) !important;
}
.stTextInput > div > div > input {
    background: #ffffff !important;
    border: 1px solid var(--border) !important;
    border-radius: 6px !important;
    color: #1a1a2e !important;
    font-family: 'Source Sans 3', sans-serif !important;
    font-size: 0.9rem !important;
    box-shadow: none !important;
}
.stTextInput > div > div > input::placeholder { color: var(--faint) !important; }
.stTextInput > div > div > input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(201,42,42,0.1) !important;
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   BUTTONS
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
.stButton > button {
    background: #ffffff !important;
    border: 1px solid var(--border) !important;
    color: #1a1a2e !important;
    border-radius: 6px !important;
    font-family: 'Source Sans 3', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.88rem !important;
    box-shadow: none !important;
}
.stButton > button:hover {
    background: var(--surface2) !important;
    border-color: var(--border2) !important;
}
.stButton[data-testid="baseButton-primary"] > button,
.stButton > button[kind="primary"] {
    background: var(--accent) !important;
    border: 1px solid var(--accent) !important;
    color: #ffffff !important;
    font-weight: 600 !important;
}
.stButton[data-testid="baseButton-primary"] > button:hover,
.stButton > button[kind="primary"]:hover {
    background: #a61e1e !important;
    border-color: #a61e1e !important;
}
.stDownloadButton > button {
    background: #ffffff !important;
    border: 1px solid var(--border) !important;
    color: #1a1a2e !important;
    border-radius: 6px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.74rem !important;
    width: 100%;
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   EXPANDER
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
div[data-testid="stExpander"] {
    background: #ffffff !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    margin-bottom: 1rem !important;
    overflow: hidden !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06) !important;
}
div[data-testid="stExpander"] summary {
    background: #ffffff !important;
    color: #1a1a2e !important;
    font-family: 'Source Sans 3', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.93rem !important;
    padding: 0.9rem 1.2rem !important;
}
div[data-testid="stExpander"] summary:hover { background: var(--surface2) !important; }
div[data-testid="stExpander"] > div[role="region"] {
    background: #ffffff !important;
    border-top: 1px solid var(--border) !important;
    padding: 1.2rem 1.4rem !important;
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   TABS
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 2px solid var(--border) !important;
    padding: 0 !important;
    gap: 0 !important;
    border-radius: 0 !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: var(--muted) !important;
    border-radius: 0 !important;
    border-bottom: 2px solid transparent !important;
    margin-bottom: -2px !important;
    font-family: 'Source Sans 3', sans-serif !important;
    font-size: 0.87rem !important;
    font-weight: 400 !important;
    padding: 8px 18px !important;
}
.stTabs [aria-selected="true"] {
    background: transparent !important;
    color: var(--ink) !important;
    border-bottom: 2px solid var(--accent) !important;
    font-weight: 600 !important;
}
.stTabs [data-baseweb="tab-panel"] {
    background: transparent !important;
    padding: 1.2rem 0 !important;
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   SELECTBOX
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
.stSelectbox > div > div {
    background: #ffffff !important;
    border: 1px solid var(--border) !important;
    color: #1a1a2e !important;
    border-radius: 6px !important;
    box-shadow: none !important;
}
.stSelectbox > div > div * { color: #1a1a2e !important; }

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   ALERTS
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
.stInfo > div {
    background: #e7f5ff !important;
    border: 1px solid #74c0fc !important;
    border-left: 4px solid var(--accent2) !important;
    border-radius: 6px !important;
    color: #1864ab !important;
}
.stInfo > div * { color: #1864ab !important; }
.stSuccess > div {
    background: #ebfbee !important;
    border: 1px solid #8ce99a !important;
    border-left: 4px solid var(--green) !important;
    border-radius: 6px !important;
    color: #2b8a3e !important;
}
.stSuccess > div * { color: #2b8a3e !important; }
.stWarning > div {
    background: #fff9db !important;
    border: 1px solid #ffe066 !important;
    border-left: 4px solid var(--amber) !important;
    border-radius: 6px !important;
    color: #e67700 !important;
}
.stWarning > div * { color: #e67700 !important; }
.stError > div {
    background: #fff5f5 !important;
    border: 1px solid #ffa8a8 !important;
    border-left: 4px solid var(--accent) !important;
    border-radius: 6px !important;
    color: #c92a2a !important;
}
.stError > div * { color: #c92a2a !important; }

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   STATUS WIDGET
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
div[data-testid="stStatus"] {
    background: #ffffff !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    box-shadow: none !important;
}
div[data-testid="stStatus"] * { color: #1a1a2e !important; }

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   PROGRESS BAR
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
.stProgress > div { background: var(--surface3) !important; border-radius: 4px !important; }
.stProgress > div > div > div { background: var(--accent) !important; border-radius: 4px !important; }

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   DIVIDER
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
hr { border: none !important; border-top: 1px solid var(--rule) !important; margin: 1.5rem 0 !important; }

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   CUSTOM COMPONENTS — all text hardcoded dark
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
.section-label {
    font-family: 'Source Sans 3', sans-serif;
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: var(--faint) !important;
    margin-bottom: 6px;
    display: block;
}

.gene-chip {
    display: inline-block;
    background: #e7f5ff;
    border: 1px solid #74c0fc;
    color: #1864ab !important;
    padding: 1px 8px;
    border-radius: 4px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.71rem;
    margin: 2px;
}
.enrichment-chip {
    display: inline-block;
    background: #ebfbee;
    border: 1px solid #8ce99a;
    color: #2b8a3e !important;
    padding: 2px 9px;
    border-radius: 4px;
    font-size: 0.72rem;
    margin: 2px;
    font-family: 'Source Sans 3', sans-serif;
}

.conf-bar-wrap { margin: 5px 0 10px; }
.conf-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    color: var(--sub) !important;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 4px;
    display: flex;
    justify-content: space-between;
}
.conf-bar { height: 5px; background: var(--surface3); border-radius: 3px; overflow: hidden; }
.conf-bar-fill { height: 100%; transition: width 0.3s ease; border-radius: 3px; }

.process-heading {
    font-family: 'EB Garamond', serif;
    font-size: 1.05rem;
    font-weight: 500;
    color: var(--ink) !important;
    margin: 4px 0 10px;
    line-height: 1.45;
}
.final-process {
    font-family: 'EB Garamond', serif;
    font-size: 1.2rem;
    font-weight: 600;
    margin: 4px 0 10px;
    line-height: 1.3;
    color: var(--ink) !important;
}

.badge {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 0.72rem;
    font-weight: 600;
    font-family: 'JetBrains Mono', monospace;
}
.badge-conflict { background: #fff9db; color: #e67700 !important; border: 1px solid #ffe066; }
.badge-ok       { background: #ebfbee; color: #2b8a3e !important; border: 1px solid #8ce99a; }
.badge-paper    { background: #e7f5ff; color: #1864ab !important; border: 1px solid #74c0fc; }
.badge-star     { background: #fff5f5; color: #c92a2a !important; border: 1px solid #ffa8a8; }

.paper-card {
    background: #ffffff;
    border: 1px solid var(--border);
    border-left: 3px solid var(--border2);
    border-radius: 6px;
    padding: 0.9rem 1rem;
    margin-bottom: 0.65rem;
}
.paper-card.top-journal { border-left-color: var(--accent2); }
.paper-title {
    font-family: 'EB Garamond', serif;
    font-weight: 500;
    font-size: 0.97rem;
    color: var(--ink) !important;
    margin-bottom: 4px;
    line-height: 1.5;
}
.paper-meta {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    color: var(--muted) !important;
    margin-bottom: 6px;
}
.paper-abstract {
    font-size: 0.83rem;
    color: var(--sub) !important;
    line-height: 1.7;
    font-family: 'Source Sans 3', sans-serif;
}
.paper-scroll { max-height: 540px; overflow-y: auto; padding-right: 6px; }

.metrics-row { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; margin-bottom: 10px; }
.metric-box {
    background: #ffffff;
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 0.85rem 0.9rem;
    text-align: center;
}
.metric-num {
    font-family: 'EB Garamond', serif;
    font-size: 1.75rem;
    font-weight: 600;
    color: var(--ink) !important;
    line-height: 1;
}
.metric-lbl {
    font-family: 'Source Sans 3', sans-serif;
    font-size: 0.64rem;
    font-weight: 700;
    color: var(--faint) !important;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-top: 3px;
}

.chat-wrap {
    background: #ffffff;
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1.4rem 1.5rem;
    margin-top: 1rem;
}
.chat-bubble-user {
    background: #fff5f5;
    border: 1px solid #ffa8a8;
    color: var(--ink) !important;
    padding: 9px 14px;
    border-radius: 8px 8px 2px 8px;
    margin: 6px 0;
    margin-left: 15%;
    font-size: 0.88rem;
    line-height: 1.65;
    font-family: 'Source Sans 3', sans-serif;
}
.chat-bubble-bot {
    background: var(--surface2);
    border: 1px solid var(--border);
    color: var(--ink) !important;
    padding: 11px 14px;
    border-radius: 8px 8px 8px 2px;
    margin: 6px 0;
    margin-right: 10%;
    font-size: 0.88rem;
    line-height: 1.75;
    font-family: 'Source Sans 3', sans-serif;
}
.chat-role {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.63rem;
    color: var(--faint) !important;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 3px;
}
.grounding-note {
    display: flex;
    align-items: flex-start;
    gap: 8px;
    background: #e7f5ff;
    border: 1px solid #74c0fc;
    border-left: 4px solid var(--accent2);
    border-radius: 6px;
    padding: 9px 13px;
    font-family: 'Source Sans 3', sans-serif;
    font-size: 0.83rem;
    color: #1864ab !important;
    margin-bottom: 1rem;
    line-height: 1.55;
}

/* ── Chat input ── */
div[data-testid="stChatInput"] > div {
    background: #ffffff !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    box-shadow: none !important;
}
div[data-testid="stChatInput"] textarea {
    background: transparent !important;
    color: #1a1a2e !important;
    font-family: 'Source Sans 3', sans-serif !important;
}

/* ── Code blocks (Streamlit st.code override) ── */
.stCode > div, code, pre {
    background: #f8f9fa !important;
    border: 1px solid var(--border) !important;
    color: var(--ink) !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.78rem !important;
    border-radius: 6px !important;
}

/* ── Raw output pre blocks ── */
.raw-output-block {
    background: #1e2030;
    border: 1px solid #373d4a;
    border-radius: 6px;
    padding: 1rem 1.2rem;
    overflow-x: auto;
    overflow-y: auto;
    max-height: 600px;
    margin-bottom: 1rem;
}
.raw-output-block pre {
    margin: 0;
    white-space: pre-wrap;
    word-break: break-word;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    line-height: 1.75;
    color: #cdd6f4 !important;
    background: transparent;
    border: none !important;
}
.raw-output-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.66rem;
    font-weight: 600;
    color: var(--faint) !important;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin: 0 0 6px;
    display: flex;
    align-items: center;
    gap: 8px;
}
.raw-output-label::after {
    content: '';
    flex: 1;
    height: 1px;
    background: var(--border);
}

/* ── Column rule ── */
.result-divider { border-left: 1px solid var(--rule); }
</style>
""", unsafe_allow_html=True)

# ─── Constants ────────────────────────────────────────────────────────────────
DEEPSEEK_URL  = "https://api.deepseek.com/v1/chat/completions"
NCBI_BASE     = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
JOURNAL_FILE  = "complete_high_tqcc_journals.txt"

# ─── Session State ────────────────────────────────────────────────────────────
_DEFAULTS = {
    "api_key": "",
    "context": "Acute Myeloid Leukemia (AML)",
    "results": [],
    "step": 0,
    "chat_history": {},   # {comm_id: [{"role": ..., "content": ...}]}
    "running": False,
}
for k, v in _DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ─── Load Top Journals (local file, cached) ───────────────────────────────────
@st.cache_resource
def load_top_journals() -> Dict[str, int]:
    """
    Returns {normalized_journal_name: rank} where rank=1 is highest priority.
    Parses lines like:  #1 | CA-A Cancer Journal for Clinicians | TQCC: 503.1
    """
    try:
        with open(JOURNAL_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
        journals: Dict[str, int] = {}
        for line in lines:
            line = line.strip()
            if not line or "Complete List" in line or "===" in line or "Total journals" in line:
                continue
            if "|" in line:
                parts = line.split("|")
                if len(parts) >= 3:
                    rank_str = parts[0].strip().lstrip("#")   # "1", "2", …
                    name     = parts[1].strip()
                    if name and rank_str.isdigit():
                        norm = normalize_journal(name)
                        if norm:
                            journals[norm] = int(rank_str)
        return journals
    except FileNotFoundError:
        defaults = [
            "nature", "science", "cell", "nature medicine", "nature genetics",
            "blood", "leukemia", "cancer cell", "nature cancer", "cancer research",
            "journal of clinical oncology", "haematologica",
        ]
        return {normalize_journal(j): i + 1 for i, j in enumerate(defaults)}


def normalize_journal(name: str) -> str:
    if not name:
        return ""
    name = str(name).lower()
    name = re.sub(r"[^\w\s]", "", name)
    name = re.sub(r"\s+", " ", name)
    return name.strip()


# Initialise after normalize_journal is defined
TOP_JOURNALS: Dict[str, int] = load_top_journals()
TOP_JOURNALS_NORMALIZED: set  = set(TOP_JOURNALS.keys())


def get_journal_rank(journal_name: str) -> int:
    """
    Return the TQCC rank of a journal (lower = higher priority).
    Returns 99999 for journals not in the list.
    Uses fuzzy matching to handle minor name variants.
    """
    norm  = normalize_journal(journal_name)
    match = fuzz_process.extractOne(norm, TOP_JOURNALS_NORMALIZED, score_cutoff=85)
    if match:
        return TOP_JOURNALS.get(match[0], 99999)
    return 99999


# ─── Helpers ──────────────────────────────────────────────────────────────────
def conf_bar_html(score: float, label: str, delta_icon: str = "") -> str:
    """Render a confidence bar as HTML."""
    pct = int(score * 100)
    if score >= 0.70:
        color = "#4dac26"
    elif score >= 0.40:
        color = "#f59e0b"
    else:
        color = "#ca0020"
    return f"""
    <div class="conf-bar-wrap">
        <div class="conf-label">
            <span>{label}</span>
            <span style="color:{color}">{score:.2f} {delta_icon}</span>
        </div>
        <div class="conf-bar">
            <div class="conf-bar-fill" style="width:{pct}%; background:{color}"></div>
        </div>
    </div>"""

def delta_icon(before: float, after: float) -> str:
    d = after - before
    if d > 0.05:   return "↑"
    if d < -0.05:  return "↓"
    return "→"

def gene_chips(genes: List[str]) -> str:
    return " ".join(f'<span class="gene-chip">{g}</span>' for g in genes)

def enrich_chips(pathways: List[str]) -> str:
    return " ".join(f'<span class="enrichment-chip">{p[:60]}{"…" if len(p)>60 else ""}</span>' for p in pathways[:12])

# ─── Community Parser ─────────────────────────────────────────────────────────
def parse_communities(text: str) -> Dict[str, List[str]]:
    """
    Flexible parser for gene set input. Accepts multiple formats:

        Gene Set 1: BRCA1, TP53, MDM2
        Set 1: BRCA1, TP53
        1: BRCA1, TP53
        Community 1: BRCA1, TP53
        Refined Community 1: ['BRCA1', 'TP53']   ← pipeline internal format also works

    Lines that do not match any pattern are ignored.
    Gene lists may optionally be wrapped in [ ] brackets and/or quoted.
    Entries that span multiple lines (bracket not yet closed) are merged first.
    """
    # ── Step 1: merge continuation lines (bracket wrapping that spans lines) ──
    joined_lines: List[str] = []
    buffer = ""
    for raw_line in text.split("\n"):
        stripped = raw_line.strip()
        if re.match(
            r"(?:Refined\s+)?(?:Community|Gene\s*Set|Set)\s*\d+\s*:|^\d+\s*:",
            stripped, re.IGNORECASE
        ):
            if buffer:
                joined_lines.append(buffer)
            buffer = stripped
        elif buffer:
            buffer += " " + stripped
        else:
            joined_lines.append(stripped)
        if buffer and ("[" not in buffer or "]" in buffer):
            joined_lines.append(buffer)
            buffer = ""
    if buffer:
        joined_lines.append(buffer)

    # ── Step 2: parse each merged line ───────────────────────────────────────
    PATTERN = re.compile(
        r"(?:(?:Refined\s+)?(?:Community|Gene\s*Set|Set)\s*)?(\d+)\s*:\s*\[?(.+?)\]?$",
        re.IGNORECASE,
    )
    communities: Dict[str, List[str]] = {}
    auto_idx = 1
    for line in joined_lines:
        if not line:
            continue
        m = PATTERN.match(line)
        if m:
            comm_id = m.group(1)
            raw     = m.group(2)
        else:
            if "," in line and re.search(r"\b[A-Z][A-Z0-9]{1,}", line):
                comm_id = str(auto_idx)
                raw     = line
                auto_idx += 1
            else:
                continue
        genes = [
            g.strip().strip("'\"\'").strip()
            for g in raw.split(",")
            if g.strip().strip("'\"\'").strip()
        ]
        if genes:
            communities[comm_id] = genes
    return communities

# ─── Enrichment ───────────────────────────────────────────────────────────────
def perform_enrichment(genes: List[str]) -> List[str]:
    try:
        dbs = ["GO_Biological_Process_2021", "Reactome_2022", "KEGG_2021_Human"]
        out = []
        time.sleep(1.2)
        for db in dbs:
            enr = gp.enrichr(gene_list=genes, gene_sets=[db], organism="human",
                             outdir=None, no_plot=True, cutoff=0.01)
            df = enr.results
            if not df.empty:
                df = df.sort_values("Adjusted P-value")
                out += list(df.head(5)["Term"])
        return list(set(out))
    except Exception as e:
        st.error(f"Enrichment error ({db}): {type(e).__name__}: {e}")
    

# ─── DeepSeek calls ───────────────────────────────────────────────────────────
def _ds_system(context: str) -> str:
    return (f"You are a bioinformatics expert. Focus on {context}. "
            "Provide detailed pathway analysis with scientific literature support. "
            "Always cite specific papers when discussing pathway relationships.")

def _ds_call(api_key: str, system: str, prompt: str, max_tokens: int = 4000) -> str:
    hdrs = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    body = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system",  "content": system},
            {"role": "user",    "content": prompt},
        ],
        "temperature": 0,
        "max_tokens":   max_tokens,
    }
    r = requests.post(DEEPSEEK_URL, headers=hdrs, json=body, timeout=180)
    if r.status_code == 200:
        return r.json()["choices"][0]["message"]["content"]
    raise Exception(f"DeepSeek {r.status_code}: {r.text[:300]}")

# ─── Annotation Prompt ────────────────────────────────────────────────────────
def create_all_in_one_prompt(genes: List[str], enrichment_pathways: List[str]) -> str:
    enrichment_section = ""
    if enrichment_pathways:
        enrichment_section = "\nEnrichment Analysis Results:\n" + "\n".join(f"- {p}" for p in enrichment_pathways)
    genes_str = ", ".join(genes)
    enrichment_instruction = "Using the enrichment pathways above (if any), provide an analysis of the gene set"

    return f"""You are a bioinformatics expert conducting pathway analysis of gene sets. For the gene set: [{genes_str}]{enrichment_section}

Please perform analysis in clearly labeled sections:

===== SECTION 1: ANALYSIS WITH ENRICHMENT =====
{enrichment_instruction}:
1. Propose a concise, descriptive name for the biological process
2. Assign a confidence score (0.00-1.00) for this process
3. Provide explicit reasoning for choosing this pathway/process
4. List the specific genes from the gene set that contribute to the process
5. IMPORTANT: A minimum of TWO genes from the gene set MUST be associated with a common biological process to annotate it as a valid pathway
6. If there isn't sufficient evidence or fewer than two genes are associated with a common pathway, label as "Unknown Pathway" with a low confidence score

Output format for this section:
PROCESS WITH ENRICHMENT: [Process Name] ([Confidence Score])

PATHWAY REASONING WITH ENRICHMENT:
[Your explicit reasoning for choosing this pathway/process]

CONTRIBUTING GENES WITH ENRICHMENT:
[Comma-separated list of contributing genes]

ANALYSIS TEXT WITH ENRICHMENT:
[Detailed analysis text explaining the biological significance and mechanisms of this process, without citations]

===== SECTION 2: ANALYSIS WITHOUT ENRICHMENT =====
Based SOLELY on your knowledge of these genes, without considering the enrichment results:
1. Propose a concise, descriptive name for the biological process
2. Assign a confidence score (0.00-1.00) for this process
3. List the specific genes from the gene set that are involved in the process
4. IMPORTANT: A minimum of TWO genes from the gene set MUST be associated with a common biological process to annotate it as a valid pathway
5. IMPORTANT: If there isn't sufficient evidence or fewer than two genes share a common biological function, label as "Unknown Pathway" with a low confidence score

Output format for this section:
PROCESS WITHOUT ENRICHMENT: [Process Name] ([Confidence Score])

CONTRIBUTING GENES WITHOUT ENRICHMENT:
[Comma-separated list of contributing genes]

PATHWAY REASONING WITHOUT ENRICHMENT:
[Your explicit reasoning for choosing this pathway/process]

ANALYSIS TEXT WITHOUT ENRICHMENT:
[Detailed analysis text explaining the biological significance and mechanisms of this process, without citations]

===== SECTION 3: FINAL PROCESS SELECTION =====
Compare both analyses and provide:
1. Which process (with or without enrichment) has higher confidence and why
2. Final reasoning for the chosen process

Output format for this section:
FINAL PROCESS REASONING:
[Detailed explanation of why you chose the final process, comparing both analyses and explaining which one provides stronger evidence]

Analytical Guidelines:
- Be concise and avoid unnecessary words
- Be factual without editorializing
- Be specific, avoiding overly general statements
- Avoid listing individual protein facts
- Group proteins by similar functions
- Discuss their interplay, synergistic or antagonistic effects
- Focus on functional integration within the system
- Include at least 2-3 specific paper citations when discussing established pathway relationships

Confidence Score Instructions:
- Assign a score from 0.00 to 1.00
- 0.00 indicates lowest confidence
- 1.00 reflects highest confidence
- Base the score on the proportion of genes participating in the identified process"""

# ─── Validation Prompt ────────────────────────────────────────────────────────
def create_validation_prompt(
        gene_set_id: str, genes: List[str],
        proc_with: str, conf_with: float,
        proc_without: str, conf_without: float,
        analysis_with: str, analysis_without: str,
        papers: List[Dict]) -> str:

    genes_str = ", ".join(genes)
    papers_section = ""
    for i, p in enumerate(papers, 1):
        papers_section += (f"PAPER {i}:\n"
                           f"Title: {p['title']}\n"
                           f"Authors: {p['authors']}\n"
                           f"Journal: {p['journal']} ({p['year']})\n"
                           f"Genes Mentioned: {', '.join(p['genes_mentioned'])}\n"
                           f"Abstract: {p['abstract']}\n\n")

    return f"""You are a scientific expert in genomics and bioinformatics tasked with validating gene set analysis results using ONLY the provided literature.

GENE SET ID: {gene_set_id}
GENES: {genes_str}

ORIGINAL ANALYSIS WITH ENRICHMENT:
Process Name: {proc_with}
Original Confidence Score: {conf_with}
Analysis: {analysis_with[:1000]}...

ORIGINAL ANALYSIS WITHOUT ENRICHMENT:
Process Name: {proc_without}
Original Confidence Score: {conf_without}
Analysis: {analysis_without[:1000]}...

PROVIDED LITERATURE (USE ONLY THESE STUDIES):
{papers_section}

VALIDATION TASK:
Based STRICTLY on the provided literature above, evaluate both analyses and provide updated confidence scores.

**ABSOLUTE REQUIREMENT FOR PAPER CITATIONS:**
Throughout your entire response, whenever you reference any paper by number, you MUST immediately provide the complete paper information in this exact format:
"Paper X: 'Full Paper Title', Complete Author List"
NEVER use abbreviated citations like "Paper X: Author et al." or "Papers X-Y: Author1, Author2"
ALWAYS include the full title in quotes and complete author names.

CRITICAL REQUIREMENTS:
1. Use ONLY the provided papers - do not add external knowledge
2. For each process, check if the genes are supported by the literature
3. Provide updated confidence scores based on evidence strength
4. Select the better-supported process as the final choice
5. **MANDATORY: When referencing papers by number in any analysis text, you MUST include the COMPLETE paper details (FULL TITLE, ALL AUTHORS) immediately after the paper number.**

FORMAT YOUR RESPONSE EXACTLY AS FOLLOWS:

VALIDATION OF ENRICHMENT ANALYSIS:
Evidence Assessment: [Detailed assessment based strictly on provided papers]
Original Confidence: {conf_with}
Updated Confidence: [Your revised score 0.00-1.00 based on literature evidence]
Supporting Papers: [List paper numbers that support this process]

VALIDATION OF DIRECT ANALYSIS:
Evidence Assessment: [Detailed assessment based strictly on provided papers]
Original Confidence: {conf_without}
Updated Confidence: [Your revised score 0.00-1.00 based on literature evidence]
Supporting Papers: [List paper numbers that support this process]

FINAL PROCESS SELECTION:
Selected Process: [Choose the better-supported process name]
Final Confidence: [The updated confidence score for your selected process]
Selection Reasoning: [Explain why this process has stronger literature support]

CONFLICT ANALYSIS:
Review all papers for contradictory evidence about gene functions, pathway assignments, or experimental results.
CONFLICTING_EVIDENCE_FOUND: [TRUE/FALSE]
CONFLICT_DESCRIPTION: [Brief description of any conflicts found, or "No conflicts detected"]

SUPPORTING CITATIONS:
[List citations in format: "Title, Authors" for papers that support the final selected process]

VALIDATION ANALYSIS TEXT:
[Comprehensive summary of all changes made, reasoning for confidence adjustments, and evidence from the provided studies that led to the final process selection.
**MANDATORY CITATION FORMAT: When mentioning any paper numbers, you MUST include the COMPLETE citation with FULL TITLES AND AUTHORS - NOT JUST PARTIAL CITATIONS**]
"""

# ─── Response Parsers ─────────────────────────────────────────────────────────
def _clean(text: str) -> str:
    if not text or not isinstance(text, str):
        return text or ""
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"\*([^*]+)\*",     r"\1", text)
    text = re.sub(r"(?<!\w)\*(?!\w)", "",    text)
    return text.strip()

def _extract_section(text: str, section_name: str) -> str:
    patterns = [
        rf"{re.escape(section_name)}:\s*(.*?)(?=\n\n[\w\s]+:|===|$)",
        rf"{re.escape(section_name)}:\s*(.*?)(?=\n[A-Z][A-Z\s]+:|$)",
        rf"{re.escape(section_name)}:\s*(.*?)(?=\n\*\*|$)",
    ]
    for pat in patterns:
        m = re.search(pat, text, re.DOTALL | re.IGNORECASE)
        if m:
            result = m.group(1).strip()
            if result:
                return _clean(result)
    return f"{section_name} not found"

def _extract_process_info(text: str, prefix: str) -> Tuple[str, float]:
    patterns = [
        rf"PROCESS {prefix} ENRICHMENT:\s*([^(]+?)\s*\(([0-9.]+)\)",
        rf"PROCESS {prefix} ENRICHMENT:\s*([^(]*?)\s*\(\s*([0-9.]+)\s*\)",
        rf"PROCESS {prefix} ENRICHMENT:\s*(.*?)\s*\(\s*Confidence Score:\s*([0-9.]+)\s*\)",
    ]
    for pat in patterns:
        m = re.search(pat, text, re.IGNORECASE | re.DOTALL)
        if m:
            name  = _clean(m.group(1).strip())
            try:
                conf = float(m.group(2))
                if name and conf >= 0:
                    return name, conf
            except ValueError:
                continue
    simple = rf"PROCESS {prefix} ENRICHMENT:\s*(.*?)(?=\n|$)"
    m = re.search(simple, text, re.IGNORECASE)
    if m:
        name = _clean(re.sub(r"\s*\([^)]*$", "", m.group(1)).strip())
        return name, 0.0
    return f"Unknown Process {prefix} Enrichment", 0.0

def _parse_validation(response: str) -> Dict[str, Any]:
    res: Dict[str, Any] = {}
    m = re.search(r"VALIDATION OF ENRICHMENT ANALYSIS:.*?Updated Confidence:\s*([\d.]+)", response, re.DOTALL)
    if m: res["conf_with_after"]    = float(m.group(1))
    m = re.search(r"VALIDATION OF DIRECT ANALYSIS:.*?Updated Confidence:\s*([\d.]+)",    response, re.DOTALL)
    if m: res["conf_without_after"] = float(m.group(1))
    m = re.search(r"Selected Process:\s*(.+?)(?=\n|$)", response)
    if m: res["final_process"]  = m.group(1).strip()
    m = re.search(r"Final Confidence:\s*([\d.]+)", response)
    if m: res["final_conf"]     = float(m.group(1))
    m = re.search(r"CONFLICTING_EVIDENCE_FOUND:\s*(TRUE|FALSE)", response, re.IGNORECASE)
    res["conflict"] = (m.group(1).upper() == "TRUE") if m else False
    m = re.search(r"CONFLICT_DESCRIPTION:\s*(.+?)(?=\n\n|SUPPORTING CITATIONS:|$)", response, re.DOTALL)
    res["conflict_desc"] = m.group(1).strip() if m else "No conflicts detected"
    m = re.search(r"SUPPORTING CITATIONS:\s*(.+?)(?=\n\n|VALIDATION ANALYSIS TEXT:|$)", response, re.DOTALL)
    res["citations"] = [l.strip() for l in m.group(1).strip().split("\n") if l.strip()] if m else []
    m = re.search(r"VALIDATION ANALYSIS TEXT:\s*(.+?)$", response, re.DOTALL)
    res["validation_text"] = m.group(1).strip() if m else response
    return res


# ─── PubMed Fetching ──────────────────────────────────────────────────────────
def fetch_pubmed_papers(genes: List[str], context: str, max_papers: int = 50) -> List[Dict]:
    """
    Fetch up to max_papers unique papers from PubMed.

    Selection logic:
      1. Build a query from gene names (up to 15) + disease context.
      2. esearch returns up to 200 PMIDs ranked by PubMed relevance.
      3. efetch retrieves full XML for those PMIDs.
      4. Parse every article — no gene-mention filter. Only skip if no abstract.
      5. Deduplicate by PMID.
      6. Sort by TQCC journal rank (asc), then by how many query genes appear
         in the abstract (desc) as a secondary tiebreaker.
      7. Return the top max_papers.
    """
    gene_terms = " OR ".join(f'"{g}"[Title/Abstract]' for g in genes)
    ctx_clean  = re.sub(r"[()]+", "", context).strip()
    query      = f"({gene_terms}) AND ({ctx_clean}[Title/Abstract])"
    today      = date.today().strftime("%Y/%m/%d")

    # 1. esearch
    try:
        time.sleep(0.34)
        r = requests.get(f"{NCBI_BASE}/esearch.fcgi", params={
            "db":       "pubmed",
            "term":     query,
            "retmax":   300,
            "retmode":  "json",
            "sort":     "relevance",
            "datetype": "pdat",
            "mindate":  "2015/01/01",
            "maxdate":  today,
        }, timeout=30)
        pmids = r.json().get("esearchresult", {}).get("idlist", [])
    except Exception:
        return []

    if not pmids:
        return []

    # 2. efetch XML
    try:
        time.sleep(0.34)
        r2 = requests.get(f"{NCBI_BASE}/efetch.fcgi", params={
            "db":      "pubmed",
            "id":      ",".join(pmids[:300]),
            "rettype": "abstract",
            "retmode": "xml",
        }, timeout=60)
        root = ET.fromstring(r2.content)
    except Exception:
        return []

    seen_pmids: set  = set()
    papers: List[Dict] = []

    for art in root.findall(".//PubmedArticle"):
        try:
            # PMID — deduplicate
            pm   = art.find(".//PMID")
            pmid = pm.text.strip() if pm is not None and pm.text else ""
            if pmid in seen_pmids:
                continue
            seen_pmids.add(pmid)

            # Abstract — skip if absent
            abs_parts = art.findall(".//AbstractText")
            abstract  = " ".join("".join(p.itertext()) for p in abs_parts).strip()
            if not abstract:
                continue

            # Title
            te    = art.find(".//ArticleTitle")
            title = "".join(te.itertext()).strip() if te is not None else "No title"

            # Journal
            je      = art.find(".//Journal/Title")
            journal = je.text.strip() if je is not None and je.text else "Unknown"

            # Year
            ye   = art.find(".//PubDate/Year")
            year = ye.text if ye is not None else "Unknown"

            # Authors (up to 6 + et al.)
            auth_els = art.findall(".//Author")
            names    = []
            for a in auth_els[:6]:
                ln = a.findtext("LastName", "")
                fn = a.findtext("ForeName", "")
                if ln:
                    names.append(f"{ln} {fn}".strip())
            authors = ", ".join(names) + (" et al." if len(auth_els) > 6 else "")

            # Genes mentioned in abstract (informational only — not a filter)
            mentioned = [
                g for g in genes
                if re.search(rf"\b{re.escape(g)}\b", abstract, re.IGNORECASE)
            ]

            # Journal rank from TQCC list
            j_rank  = get_journal_rank(journal)
            is_top  = j_rank < 99999

            papers.append({
                "title":           title,
                "authors":         authors,
                "journal":         journal,
                "year":            year,
                "pmid":            pmid,
                "abstract":        abstract[:700] + ("…" if len(abstract) > 700 else ""),
                "genes_mentioned": mentioned,
                "gene_count":      len(mentioned),
                "journal_rank":    j_rank,
                "is_top_journal":  is_top,
            })
        except Exception:
            continue

    # 3. Sort: best TQCC rank first; within same rank, more gene mentions first
    papers.sort(key=lambda x: (x["journal_rank"], -x["gene_count"]))

    return papers[:max_papers]


# ─── Grounded Chat ────────────────────────────────────────────────────────────
def chat_grounded(question: str, result: Dict, history: List[Dict], api_key: str) -> str:
    papers_ctx = ""
    for i, p in enumerate(result.get("papers", [])[:25], 1):
        papers_ctx += (f"[Paper {i}] {p['title']} | {p['journal']} ({p['year']})\n"
                       f"Genes: {', '.join(p['genes_mentioned'])}\n"
                       f"Abstract: {p['abstract']}\n\n")

    system = f"""You are a scientific assistant answering questions about one specific gene set.

STRICT RULES:
1. Answer ONLY from the analysis data and papers provided below.
2. If the answer is not in the context, respond: "I don't have sufficient evidence from this community's analysis to answer that."
3. Do NOT use external knowledge or speculate beyond the provided text.
4. When citing papers, include the full title and journal.

=== GENE SET {result['community_id']} ANALYSIS ===
Genes: {', '.join(result['genes'])}
Final Process: {result.get('final_process', 'Unknown')}
Final Confidence: {result.get('final_conf', 0)}

Analysis (with enrichment): {result.get('analysis_with', '')[:900]}

Analysis (without enrichment): {result.get('analysis_without', '')[:900]}

Validation summary: {result.get('validation_text', '')[:900]}

Supporting citations:
{chr(10).join(result.get('citations', [])[:10])}

=== FETCHED PAPERS ===
{papers_ctx}"""

    messages = [{"role": "system", "content": system}]
    for h in history[-6:]:
        messages.append({"role": h["role"], "content": h["content"]})
    messages.append({"role": "user", "content": question})

    hdrs = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    body = {"model": "deepseek-chat", "messages": messages,
            "temperature": 0, "max_tokens": 1200}
    r = requests.post(DEEPSEEK_URL, headers=hdrs, json=body, timeout=60)
    if r.status_code == 200:
        return r.json()["choices"][0]["message"]["content"]
    return f"⚠️ API error {r.status_code}. Please try again."

# ─── Main Pipeline ────────────────────────────────────────────────────────────
def run_pipeline(communities: Dict[str, List[str]], api_key: str, context: str) -> List[Dict]:
    results = []
    system  = _ds_system(context)
    total   = len(communities)

    for idx, (comm_id, genes) in enumerate(communities.items(), 1):
        with st.status(f"Community {comm_id}  ·  {len(genes)} genes  ({idx}/{total})", expanded=True) as status:
            r: Dict[str, Any] = {"community_id": comm_id, "genes": genes}

            # 1 — Enrichment
            status.update(label=f"Community {comm_id} · 🔬 Enrichment analysis…")
            r["enrichment"] = perform_enrichment(genes)

            # 2 — Annotation
            status.update(label=f"Community {comm_id} · 🤖 LLM annotation…")
            prompt       = create_all_in_one_prompt(genes, r["enrichment"])
            full_text    = _ds_call(api_key, system, prompt, max_tokens=4000)
            r["full_text"] = full_text

            proc_with,    conf_with    = _extract_process_info(full_text, "WITH")
            proc_without, conf_without = _extract_process_info(full_text, "WITHOUT")
            r.update({
                "proc_with":        proc_with,
                "conf_with":        conf_with,
                "proc_without":     proc_without,
                "conf_without":     conf_without,
                "analysis_with":    _extract_section(full_text, "ANALYSIS TEXT WITH ENRICHMENT"),
                "analysis_without": _extract_section(full_text, "ANALYSIS TEXT WITHOUT ENRICHMENT"),
                "genes_with":       _extract_section(full_text, "CONTRIBUTING GENES WITH ENRICHMENT"),
                "genes_without":    _extract_section(full_text, "CONTRIBUTING GENES WITHOUT ENRICHMENT"),
                "reason_with":      _extract_section(full_text, "PATHWAY REASONING WITH ENRICHMENT"),
                "reason_without":   _extract_section(full_text, "PATHWAY REASONING WITHOUT ENRICHMENT"),
            })

            # 3 — PubMed
            status.update(label=f"Community {comm_id} · 📚 Fetching PubMed papers…")
            papers      = fetch_pubmed_papers(genes, context, max_papers=50)
            r["papers"] = papers
            top_j       = sum(1 for p in papers if p["is_top_journal"])

            # 4 — Validation
            status.update(label=f"Community {comm_id} · ✅ Validating against {len(papers)} papers…")
            if papers:
                val_prompt = create_validation_prompt(
                    comm_id, genes,
                    proc_with,    conf_with,
                    proc_without, conf_without,
                    r["analysis_with"], r["analysis_without"],
                    papers,
                )
                val_raw = _ds_call(api_key, system, val_prompt, max_tokens=8000)
                parsed  = _parse_validation(val_raw)
                r.update({
                    "val_raw":            val_raw,
                    "conf_with_after":    parsed.get("conf_with_after",    conf_with),
                    "conf_without_after": parsed.get("conf_without_after", conf_without),
                    "final_process":      parsed.get("final_process",      proc_with),
                    "final_conf":         parsed.get("final_conf",         conf_with),
                    "validation_text":    parsed.get("validation_text",    ""),
                    "citations":          parsed.get("citations",          []),
                    "conflict":           parsed.get("conflict",           False),
                    "conflict_desc":      parsed.get("conflict_desc",      "No conflicts detected"),
                })
            else:
                final = proc_with if conf_with >= conf_without else proc_without
                r.update({
                    "val_raw":            "",
                    "conf_with_after":    conf_with,
                    "conf_without_after": conf_without,
                    "final_process":      final,
                    "final_conf":         max(conf_with, conf_without),
                    "validation_text":    "No PubMed papers found for these genes.",
                    "citations":          [],
                    "conflict":           False,
                    "conflict_desc":      "No papers available.",
                })

            status.update(
                label=f"Community {comm_id} · ✔ Done — {len(papers)} papers, {top_j} top-journal",
                state="complete",
            )
        results.append(r)
        if comm_id not in st.session_state.chat_history:
            st.session_state.chat_history[comm_id] = []

    return results

# ════════════════════════════════════════════════════════════════════════════════
#   UI
# ════════════════════════════════════════════════════════════════════════════════

# ─── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<span class="section-label">API Key</span>', unsafe_allow_html=True)
    ak = st.text_input("DeepSeek API Key", type="password",
                        value=st.session_state.api_key, placeholder="sk-…",
                        label_visibility="collapsed")
    if ak:
        st.session_state.api_key = ak

    st.markdown("---")
    st.markdown('<span class="section-label">Disease / Context</span>', unsafe_allow_html=True)
    ctx = st.text_input("Biological context",
                         value=st.session_state.context,
                         placeholder="e.g., Acute Myeloid Leukemia (AML)",
                         label_visibility="collapsed",
                         help="Injected into every system prompt. Change to redirect the analysis focus.")
    if ctx:
        st.session_state.context = ctx

    st.markdown("---")
    st.markdown("---")

    if st.session_state.results:
        total  = len(st.session_state.results)
        hi     = sum(1 for r in st.session_state.results if r.get("final_conf", 0) >= 0.7)
        confl  = sum(1 for r in st.session_state.results if r.get("conflict", False))
        avg_cf = sum(r.get("final_conf", 0) for r in st.session_state.results) / total

        st.markdown('<span class="section-label">Session Summary</span>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="metrics-row">
          <div class="metric-box"><div class="metric-num">{total}</div><div class="metric-lbl">Communities</div></div>
          <div class="metric-box"><div class="metric-num">{hi}</div><div class="metric-lbl">High Conf.</div></div>
          <div class="metric-box"><div class="metric-num">{confl}</div><div class="metric-lbl">Conflicts</div></div>
        </div>
        <div class="metric-box" style="margin-bottom:12px">
          <div class="metric-num">{avg_cf:.2f}</div><div class="metric-lbl">Avg. Final Conf.</div>
        </div>
        """, unsafe_allow_html=True)

        # CSV export
        rows = []
        for r in st.session_state.results:
            rows.append({
                "Community":                  r["community_id"],
                "Genes":                      ", ".join(r.get("genes", [])),
                "Enrichment_Pathways":        "; ".join(r.get("enrichment", [])),
                "Process_With_Enrichment":    r.get("proc_with", ""),
                "Confidence_With_Before":     r.get("conf_with", 0),
                "Confidence_With_After":      r.get("conf_with_after", 0),
                "Process_Without_Enrichment": r.get("proc_without", ""),
                "Confidence_Without_Before":  r.get("conf_without", 0),
                "Confidence_Without_After":   r.get("conf_without_after", 0),
                "Final_Process":              r.get("final_process", ""),
                "Final_Confidence":           r.get("final_conf", 0),
                "Conflicting_Evidence":       r.get("conflict", False),
                "Conflict_Description":       r.get("conflict_desc", ""),
                "Papers_Total":               len(r.get("papers", [])),
                "Papers_Top_Journal":         sum(1 for p in r.get("papers", []) if p.get("is_top_journal")),
                "Supporting_Citations":       " | ".join(r.get("citations", [])),
                "Analysis_With_Enrichment":   r.get("analysis_with", ""),
                "Analysis_Without_Enrichment":r.get("analysis_without", ""),
                "Validation_Text":            r.get("validation_text", ""),
            })
        csv_data = pd.DataFrame(rows).to_csv(index=False)
        st.download_button(
            label="📥 Download Full Results CSV",
            data=csv_data,
            file_name=f"LADDER_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
        )

# ─── Header ──────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="ladder-header">
  <p class="ladder-logo"><span>L</span>ADDER</p>
  <p class="ladder-sub"><strong>L</strong>iterature-<strong>A</strong>ssisted <strong>D</strong>ual-annotation &amp; <strong>E</strong>vidence-based <strong>R</strong>easoning &ensp;·&ensp; Live PubMed Validation</p>
  <span class="context-pill">Context: {st.session_state.context}</span>
</div>
""", unsafe_allow_html=True)

# ─── Step Trail ───────────────────────────────────────────────────────────────
STEPS = [("📝", "Input"), ("🔬", "Enrichment"), ("🤖", "Annotation"),
          ("📚", "PubMed"), ("✅", "Validation"), ("🗂️", "Results")]
step  = st.session_state.step

trail_html = '<div class="step-trail">'
for i, (icon, label) in enumerate(STEPS):
    cls = "done" if step > i else ("active" if step == i else "")
    trail_html += f'<div class="step-node {cls}">{icon} {label}</div>'
    if i < len(STEPS) - 1:
        trail_html += '<span class="step-arrow">›</span>'
trail_html += "</div>"
st.markdown(trail_html, unsafe_allow_html=True)

# ─── Input Panel ─────────────────────────────────────────────────────────────
if not st.session_state.results:
    st.markdown(
        '<h4 style="font-family:\'EB Garamond\',serif;font-size:1.25rem;font-weight:500;'
        'color:var(--ink);margin:0 0 0.3rem">Paste gene sets</h4>',
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='font-family:JetBrains Mono,monospace;font-size:0.78rem;color:var(--muted)'>"
        "Any of these formats work &nbsp;·&nbsp; one set per line</p>",
        unsafe_allow_html=True,
    )

    community_text = st.text_area(
        "community_input",
        height=220,
        placeholder=(
            "Gene Set 1: SLC19A2, SLC19A1, MIEN1, EFS, TRIM25, ASAH1, FUT8, TEAD4\n"
            "Gene Set 2: TP53, MDM2, CDKN1A, BAX, BCL2, CASP3\n"
            "\n"
            "# short forms also work:\n"
            "1: SLC19A2, SLC19A1, MIEN1\n"
            "2: TP53, MDM2, CDKN1A"
        ),
        label_visibility="collapsed",
    )

    parsed = {}
    if community_text:
        parsed = parse_communities(community_text)

    c1, c2, _ = st.columns([1.2, 1.5, 3])
    run_btn = c1.button("  Run Analysis", type="primary",
                         disabled=not (community_text and st.session_state.api_key),
                         use_container_width=True)
    if parsed:
        c2.info(f"**{len(parsed)}** gene set(s) · **{sum(len(v) for v in parsed.values())}** genes total")

    if not st.session_state.api_key:
        st.warning("Enter your DeepSeek API key in the sidebar to proceed.")

    if run_btn and parsed:
        st.session_state.step = 1
        results = run_pipeline(parsed, st.session_state.api_key, st.session_state.context)
        st.session_state.results = results
        st.session_state.step    = 5
        st.rerun()

# ─── Results Panel ────────────────────────────────────────────────────────────
if st.session_state.results:
    rc1, rc2 = st.columns([5, 1])
    rc1.markdown(
        '<h3 style="font-family:\'EB Garamond\',serif;font-size:1.55rem;font-weight:600;'
        'color:var(--ink);margin:0 0 0.5rem">Results</h3>',
        unsafe_allow_html=True,
    )
    if rc2.button("🔄 New run", use_container_width=True):
        st.session_state.results      = []
        st.session_state.chat_history = {}
        st.session_state.step         = 0
        st.rerun()

    for result in st.session_state.results:
        comm_id      = result["community_id"]
        final_proc   = result.get("final_process", "Unknown")
        final_conf   = result.get("final_conf", 0)
        conf_color   = "#2b8a3e" if final_conf >= 0.7 else ("#e67700" if final_conf >= 0.4 else "#c92a2a")
        has_conflict = result.get("conflict", False)
        papers       = result.get("papers", [])
        top_j_count  = sum(1 for p in papers if p.get("is_top_journal"))

        exp_label = (f"Gene Set {comm_id}  ·  {final_proc[:55]}"
                     f"{'…' if len(final_proc) > 55 else ''}  ·  {final_conf:.2f}")
        with st.expander(exp_label, expanded=(len(st.session_state.results) == 1)):

            # Badge row
            badge_html = (
                f'<span class="badge badge-paper">📄 {len(papers)} papers</span> '
                f'<span class="badge badge-star">⭐ {top_j_count} top-journal</span> '
            )
            badge_html += (
                '<span class="badge badge-conflict">⚠️ Conflict</span>'
                if has_conflict else
                '<span class="badge badge-ok">✅ No conflicts</span>'
            )
            st.markdown(badge_html, unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)

            # ── Confidence Grid ──────────────────────────────────────────────
            g1, g2, g3 = st.columns(3)

            with g1:
                st.markdown(
                    '<div style="font-size:0.72rem;font-weight:600;color:var(--muted);'
                    'text-transform:uppercase;letter-spacing:.09em;margin-bottom:6px">'
                    'With Enrichment</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="process-heading">{result.get("proc_with","—")}</div>',
                            unsafe_allow_html=True)
                b1, a1 = result.get("conf_with", 0), result.get("conf_with_after", 0)
                st.markdown(conf_bar_html(a1, f"{b1:.2f} → {a1:.2f}", delta_icon(b1, a1)),
                            unsafe_allow_html=True)

            with g2:
                st.markdown(
                    '<div style="font-size:0.72rem;font-weight:600;color:var(--muted);'
                    'text-transform:uppercase;letter-spacing:.09em;margin-bottom:6px">'
                    'Without Enrichment</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="process-heading">{result.get("proc_without","—")}</div>',
                            unsafe_allow_html=True)
                b2, a2 = result.get("conf_without", 0), result.get("conf_without_after", 0)
                st.markdown(conf_bar_html(a2, f"{b2:.2f} → {a2:.2f}", delta_icon(b2, a2)),
                            unsafe_allow_html=True)

            with g3:
                st.markdown(
                    '<div style="font-size:0.72rem;font-weight:600;color:var(--muted);'
                    'text-transform:uppercase;letter-spacing:.09em;margin-bottom:6px">'
                    '✨ Final · Validated</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="final-process" style="color:{conf_color}">{final_proc}</div>',
                            unsafe_allow_html=True)
                st.markdown(conf_bar_html(final_conf, "Validated confidence", ""),
                            unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # ── Detail Tabs ──────────────────────────────────────────────────
            t1, t2, t3, t4, t5 = st.tabs([
                "🧬 Genes & Enrichment",
                "📝 Analysis",
                "📚 Papers",
                "⚠️ Conflicts & Citations",
                "🔎 Raw LLM Output",
            ])

            with t1:
                st.markdown("**Genes**")
                st.markdown(gene_chips(result.get("genes", [])), unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)
                enrich = result.get("enrichment", [])
                if enrich:
                    st.markdown(f"**Enrichment pathways** ({len(enrich)} total, top 12 shown)")
                    st.markdown(enrich_chips(enrich), unsafe_allow_html=True)
                else:
                    st.info("No significant enrichment pathways found.")

            with t2:
                st.markdown("##### With enrichment")
                st.markdown(result.get("analysis_with", "—"))
                st.markdown("**Reasoning:** " + result.get("reason_with", "—"))
                st.markdown("**Contributing genes:** " + result.get("genes_with", "—"))
                st.divider()
                st.markdown("##### Without enrichment")
                st.markdown(result.get("analysis_without", "—"))
                st.markdown("**Reasoning:** " + result.get("reason_without", "—"))
                st.markdown("**Contributing genes:** " + result.get("genes_without", "—"))
                st.divider()
                st.markdown("##### Validation summary")
                st.markdown(result.get("validation_text", "—"))

            with t3:
                if papers:
                    st.markdown(
                        f"**{len(papers)} papers fetched** — {top_j_count} from top-priority journals "
                        f"· sorted by TQCC rank"
                    )
                    st.markdown('<div class="paper-scroll">', unsafe_allow_html=True)
                    for i, p in enumerate(papers, 1):
                        rank_label = (f"#{p['journal_rank']}" if p["is_top_journal"] else "—")
                        star       = f"★ [{rank_label}] " if p["is_top_journal"] else ""
                        card_cls   = "paper-card top-journal" if p["is_top_journal"] else "paper-card"
                        pmid_link  = (
                            f' · <a href="https://pubmed.ncbi.nlm.nih.gov/{p["pmid"]}/" '
                            f'target="_blank" style="color:var(--accent2);font-size:0.68rem;'
                            f'font-family:monospace">PMID {p["pmid"]}</a>'
                            if p.get("pmid") else ""
                        )
                        genes_str = " ".join(
                            f'<span class="gene-chip">{g}</span>'
                            for g in p["genes_mentioned"]
                        ) if p["genes_mentioned"] else "<span style='color:var(--faint);font-size:0.72rem'>no query genes in abstract</span>"
                        st.markdown(f"""
<div class="{card_cls}">
  <div class="paper-title">{i}. {star}{p['title']}</div>
  <div class="paper-meta">{p['journal']} · {p['year']} · {p['authors']}{pmid_link}</div>
  <div style="margin:5px 0">{genes_str}</div>
  <details><summary style="font-family:JetBrains Mono,monospace;font-size:0.72rem;color:var(--muted);cursor:pointer">Abstract ▾</summary>
  <div class="paper-abstract" style="margin-top:8px">{p['abstract']}</div></details>
</div>""", unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                else:
                    st.info("No PubMed papers found for this gene set.")

            with t4:
                if has_conflict:
                    st.error(f"**Conflict detected:** {result.get('conflict_desc', '')}")
                else:
                    st.success("No conflicting evidence found across the fetched papers.")

                citations = result.get("citations", [])
                if citations:
                    st.markdown("**Supporting citations:**")
                    for c in citations:
                        if c.strip():
                            st.markdown(f"- {c}")
                else:
                    st.info("No supporting citations extracted.")

            with t5:
                ann_text     = result.get("full_text", "— no annotation output stored —")
                val_raw_text = result.get("val_raw", "") or "— no validation output (no papers fetched) —"
                import html as _html
                ann_escaped = _html.escape(ann_text)
                val_escaped = _html.escape(val_raw_text)
                st.markdown(
                    f'<div class="raw-output-label">① Annotation output</div>'
                    f'<div class="raw-output-block"><pre>{ann_escaped}</pre></div>'
                    f'<div class="raw-output-label" style="margin-top:16px">② Validation output</div>'
                    f'<div class="raw-output-block"><pre>{val_escaped}</pre></div>',
                    unsafe_allow_html=True,
                )

    # ─── Chat Section ─────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown(
        '<h3 style="font-family:\'EB Garamond\',serif;font-size:1.45rem;font-weight:600;'
        'color:var(--ink);margin:0 0 0.3rem">Ask About a Gene Set</h3>',
        unsafe_allow_html=True,
    )
    st.markdown("""
    <div class="grounding-note">
      🔒 Responses are strictly grounded in the community's analysis and fetched papers.
      External knowledge is disabled — if the evidence isn't there, the model says so.
    </div>
    """, unsafe_allow_html=True)

    comm_options = {r["community_id"]: r for r in st.session_state.results}
    selected_id  = st.selectbox(
        "Select community",
        options=list(comm_options.keys()),
        format_func=lambda x: f"Gene Set {x}  ·  {comm_options[x].get('final_process', '')[:60]}",
        label_visibility="collapsed",
    )
    sel = comm_options[selected_id]

    # Chat history display
    history = st.session_state.chat_history.get(selected_id, [])
    if history:
        chat_html = ""
        for msg in history:
            if msg["role"] == "user":
                chat_html += (
                    f'<div class="chat-role" style="text-align:right;color:var(--accent)">you</div>'
                    f'<div class="chat-bubble-user">{msg["content"]}</div>'
                )
            else:
                chat_html += (
                    f'<div class="chat-role" style="color:var(--accent2)">ladder</div>'
                    f'<div class="chat-bubble-bot">{msg["content"]}</div>'
                )
        st.markdown(f'<div class="chat-wrap">{chat_html}</div>', unsafe_allow_html=True)

    if history:
        if st.button("🗑️ Clear chat", key=f"clear_{selected_id}"):
            st.session_state.chat_history[selected_id] = []
            st.rerun()

    q = st.chat_input(
        placeholder=f"Why is {sel.get('genes', ['?'])[0]} contributing to this pathway?",
        key=f"chat_{selected_id}",
    )
    if q:
        with st.spinner("Generating grounded response…"):
            answer = chat_grounded(q, sel, history, st.session_state.api_key)
        st.session_state.chat_history.setdefault(selected_id, [])
        st.session_state.chat_history[selected_id].append({"role": "user",      "content": q})
        st.session_state.chat_history[selected_id].append({"role": "assistant", "content": answer})
        st.rerun()
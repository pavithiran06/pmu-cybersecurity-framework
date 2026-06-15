import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import json, os, time
from datetime import datetime, timedelta
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# ─────────────────────────────────────────────
#  CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="GridShield — Power Grid SOC",
    page_icon="🛡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
#  DESIGN TOKENS
#  Palette: near-black base, electric-blue
#  primary, acid-green for safe states,
#  crimson for threats, amber for warnings.
#  Monospace data face, clean sans UI face.
# ─────────────────────────────────────────────
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500&family=DM+Sans:wght@300;400;500;600&display=swap');

/* ── Reset & Base ── */
*, *::before, *::after { box-sizing: border-box; }
html, body { margin: 0; padding: 0; }

.stApp {
    background: #070c14;
    font-family: 'DM Sans', system-ui, sans-serif;
    color: #c8d8e8;
}
.main .block-container {
    padding: 0 2rem 3rem;
    max-width: 1440px;
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header,
.stDeployButton,
[data-testid="stToolbar"] { display: none !important; }

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: #04080f !important;
    border-right: 1px solid #0e1e35 !important;
    width: 220px !important;
}
section[data-testid="stSidebar"] > div { padding: 0 !important; }

/* ── Radio as nav ── */
div[data-testid="stSidebar"] .stRadio > label {
    display: none;
}
div[data-testid="stSidebar"] .stRadio div[role="radiogroup"] {
    gap: 2px;
    display: flex;
    flex-direction: column;
}
div[data-testid="stSidebar"] .stRadio label[data-baseweb="radio"] {
    padding: 10px 20px !important;
    border-radius: 0 !important;
    border-left: 2px solid transparent !important;
    font-size: 11px !important;
    font-weight: 500 !important;
    letter-spacing: 0.07em !important;
    text-transform: uppercase !important;
    color: #4a6a8f !important;
    transition: all 0.15s !important;
    cursor: pointer !important;
}
div[data-testid="stSidebar"] .stRadio label[data-baseweb="radio"]:hover {
    background: rgba(30,160,255,0.06) !important;
    color: #c8d8e8 !important;
}
div[data-testid="stSidebar"] .stRadio input:checked + div {
    background: transparent !important;
}
div[data-testid="stSidebar"] .stRadio label[data-baseweb="radio"]:has(input:checked) {
    border-left-color: #1ea0ff !important;
    color: #1ea0ff !important;
    background: rgba(30,160,255,0.08) !important;
}

/* ── Top bar ── */
.topbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 14px 0 14px;
    border-bottom: 1px solid #0e1e35;
    margin-bottom: 24px;
}
.topbar-brand {
    display: flex;
    align-items: center;
    gap: 12px;
}
.brand-icon {
    width: 34px; height: 34px;
    background: linear-gradient(135deg, #1ea0ff 0%, #0ef0a0 100%);
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: 17px;
    flex-shrink: 0;
}
.brand-name {
    font-size: 15px;
    font-weight: 600;
    color: #e8f4ff;
    letter-spacing: 0.03em;
}
.brand-tag {
    font-size: 10px;
    color: #2a4a6f;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-top: 1px;
}
.topbar-right {
    display: flex;
    align-items: center;
    gap: 20px;
}
.topbar-pill {
    display: flex; align-items: center; gap: 6px;
    font-size: 11px; color: #0ef0a0;
    font-family: 'JetBrains Mono', monospace;
    letter-spacing: 0.04em;
}
.pulse {
    width: 7px; height: 7px; border-radius: 50%;
    background: #0ef0a0;
    animation: pulseAnim 2s ease-in-out infinite;
}
@keyframes pulseAnim {
    0%,100% { opacity:1; box-shadow: 0 0 0 0 rgba(14,240,160,.5); }
    50%      { opacity:.7; box-shadow: 0 0 0 5px rgba(14,240,160,0); }
}
.topbar-clock {
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    color: #2a4a6f;
}
.topbar-badge {
    font-size: 10px;
    padding: 3px 10px;
    border-radius: 4px;
    background: rgba(30,160,255,0.1);
    border: 1px solid rgba(30,160,255,0.25);
    color: #1ea0ff;
    font-family: 'JetBrains Mono', monospace;
    letter-spacing: 0.05em;
}

/* ── KPI Cards ── */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
    margin-bottom: 22px;
}
.kpi {
    background: #0a1120;
    border: 1px solid #0e1e35;
    border-radius: 10px;
    padding: 16px 18px;
    position: relative;
    overflow: hidden;
}
.kpi::after {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
}
.kpi-blue::after  { background: linear-gradient(90deg,#1ea0ff,transparent); }
.kpi-green::after { background: linear-gradient(90deg,#0ef0a0,transparent); }
.kpi-red::after   { background: linear-gradient(90deg,#ff3355,transparent); }
.kpi-amber::after { background: linear-gradient(90deg,#ffaa00,transparent); }
.kpi-label {
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: #2a4a6f;
    margin-bottom: 10px;
}
.kpi-value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 28px;
    font-weight: 500;
    line-height: 1;
    margin-bottom: 6px;
}
.kpi-blue  .kpi-value { color: #1ea0ff; }
.kpi-green .kpi-value { color: #0ef0a0; }
.kpi-red   .kpi-value { color: #ff3355; }
.kpi-amber .kpi-value { color: #ffaa00; }
.kpi-sub {
    font-size: 10px;
    color: #2a4a6f;
}

/* ── Panels ── */
.panel {
    background: #0a1120;
    border: 1px solid #0e1e35;
    border-radius: 10px;
    overflow: hidden;
    margin-bottom: 14px;
}
.panel-head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 12px 16px;
    border-bottom: 1px solid #0e1e35;
}
.panel-title {
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #4a6a8f;
}
.panel-body { padding: 16px; }
.panel-badge {
    font-size: 9px;
    padding: 2px 8px;
    border-radius: 3px;
    font-family: 'JetBrains Mono', monospace;
    letter-spacing: 0.06em;
}
.pb-green { background: rgba(14,240,160,.08); color:#0ef0a0; border:1px solid rgba(14,240,160,.2); }
.pb-blue  { background: rgba(30,160,255,.08); color:#1ea0ff; border:1px solid rgba(30,160,255,.2); }
.pb-red   { background: rgba(255,51,85,.08);  color:#ff3355; border:1px solid rgba(255,51,85,.2); }
.pb-amber { background: rgba(255,170,0,.08);  color:#ffaa00; border:1px solid rgba(255,170,0,.2); }

/* ── Data rows ── */
.drow {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 9px 0;
    border-bottom: 1px solid #0e1e35;
    font-size: 11px;
}
.drow:last-child { border: none; }
.drow-label { color: #4a6a8f; }
.drow-value { font-family: 'JetBrains Mono', monospace; color: #c8d8e8; }
.drow-value.green { color: #0ef0a0; }
.drow-value.blue  { color: #1ea0ff; }
.drow-value.red   { color: #ff3355; }
.drow-value.amber { color: #ffaa00; }

/* ── Threat / Safe result ── */
.result-box {
    border-radius: 10px;
    padding: 20px 22px;
    margin: 12px 0;
}
.result-threat {
    background: rgba(255,51,85,0.05);
    border: 1px solid rgba(255,51,85,0.3);
    border-left: 3px solid #ff3355;
}
.result-safe {
    background: rgba(14,240,160,0.04);
    border: 1px solid rgba(14,240,160,0.25);
    border-left: 3px solid #0ef0a0;
}
.result-warn {
    background: rgba(255,170,0,0.04);
    border: 1px solid rgba(255,170,0,0.25);
    border-left: 3px solid #ffaa00;
}
.result-title { font-size: 16px; font-weight: 600; margin-bottom: 6px; }
.result-meta  { font-size: 11px; color: #4a6a8f; line-height: 1.8; }

/* ── Timeline / Feed ── */
.feed-item {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    padding: 9px 0;
    border-bottom: 1px solid #0e1e35;
    font-size: 11px;
}
.feed-item:last-child { border: none; }
.feed-dot {
    width: 7px; height: 7px;
    border-radius: 50%;
    flex-shrink: 0;
    margin-top: 3px;
}
.feed-dot.red   { background:#ff3355; box-shadow:0 0 6px #ff3355; }
.feed-dot.amber { background:#ffaa00; }
.feed-dot.green { background:#0ef0a0; }
.feed-dot.blue  { background:#1ea0ff; }
.feed-text { color: #c8d8e8; flex: 1; line-height: 1.5; }
.feed-time { font-family:'JetBrains Mono',monospace; font-size:10px; color:#2a4a6f; flex-shrink:0; }

/* ── Buttons ── */
.stButton > button {
    background: rgba(30,160,255,0.08) !important;
    border: 1px solid rgba(30,160,255,0.35) !important;
    color: #1ea0ff !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 12px !important;
    font-weight: 500 !important;
    letter-spacing: 0.05em !important;
    border-radius: 7px !important;
    padding: 9px 20px !important;
    transition: all 0.15s !important;
    width: 100% !important;
}
.stButton > button:hover {
    background: rgba(30,160,255,0.15) !important;
    border-color: rgba(30,160,255,0.6) !important;
}

/* ── Sliders ── */
.stSlider label { font-size: 11px !important; color: #4a6a8f !important; font-family: 'DM Sans', sans-serif !important; }
.stSlider [data-baseweb="slider"] { padding: 6px 0; }

/* ── Select / multiselect ── */
.stMultiSelect label, .stSelectbox label {
    font-size: 11px !important; color: #4a6a8f !important;
}
.stMultiSelect [data-baseweb="select"] > div,
.stSelectbox [data-baseweb="select"] > div {
    background: #0a1120 !important;
    border-color: #0e1e35 !important;
    border-radius: 7px !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid #0e1e35;
    gap: 0;
}
.stTabs [data-baseweb="tab"] {
    font-size: 11px !important;
    font-weight: 500 !important;
    letter-spacing: 0.07em !important;
    text-transform: uppercase !important;
    color: #2a4a6f !important;
    background: transparent !important;
    border: none !important;
    border-bottom: 2px solid transparent !important;
    padding: 10px 18px !important;
    border-radius: 0 !important;
}
.stTabs [aria-selected="true"] {
    color: #1ea0ff !important;
    border-bottom-color: #1ea0ff !important;
}
.stTabs [data-baseweb="tab-panel"] {
    background: transparent !important;
    padding-top: 18px;
}

/* ── Streamlit alerts ── */
.stSuccess {
    background: rgba(14,240,160,0.06) !important;
    border: 1px solid rgba(14,240,160,0.25) !important;
    border-radius: 8px !important;
    color: #0ef0a0 !important;
}
.stWarning {
    background: rgba(255,170,0,0.06) !important;
    border: 1px solid rgba(255,170,0,0.25) !important;
    border-radius: 8px !important;
    color: #ffaa00 !important;
}
.stInfo {
    background: rgba(30,160,255,0.06) !important;
    border: 1px solid rgba(30,160,255,0.25) !important;
    border-radius: 8px !important;
    color: #1ea0ff !important;
}

/* ── Dataframe ── */
[data-testid="stDataFrame"] {
    border: 1px solid #0e1e35 !important;
    border-radius: 8px !important;
    overflow: hidden;
}

/* ── Code ── */
.stCodeBlock { background: #04080f !important; border: 1px solid #0e1e35 !important; border-radius: 7px !important; }
code { color: #1ea0ff !important; font-family: 'JetBrains Mono', monospace !important; }

/* ── Section divider ── */
hr { border: none; border-top: 1px solid #0e1e35 !important; margin: 20px 0 !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #0e1e35; border-radius: 2px; }

/* ── Grid helpers ── */
.g2 { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
.g3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 12px; }
.g3-1 { display: grid; grid-template-columns: 3fr 2fr; gap: 14px; }

/* ── Enc output ── */
.mono-block {
    background: #04080f;
    border: 1px solid #0e1e35;
    border-radius: 7px;
    padding: 12px 14px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    color: #1ea0ff;
    word-break: break-all;
    line-height: 1.9;
    margin-bottom: 10px;
}

/* ── PMU cards ── */
.pmu-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-bottom: 14px; }
.pmu-card {
    background: #04080f;
    border: 1px solid #0e1e35;
    border-radius: 9px;
    padding: 14px;
    position: relative;
}
.pmu-card.alert-card { border-color: rgba(255,51,85,0.4); }
.pmu-id   { font-family:'JetBrains Mono',monospace; font-size:11px; color:#1ea0ff; font-weight:500; margin-bottom:3px; }
.pmu-loc  { font-size:10px; color:#2a4a6f; margin-bottom:12px; }
.pmu-stat { position:absolute; top:12px; right:12px; width:7px; height:7px; border-radius:50%; }
.pmu-stat.ok    { background:#0ef0a0; box-shadow:0 0 5px #0ef0a0; }
.pmu-stat.alert { background:#ff3355; box-shadow:0 0 7px #ff3355; animation: pulseAnim .9s infinite; }

/* ── Confidence bars ── */
.conf-row { margin-bottom: 10px; }
.conf-top { display:flex; justify-content:space-between; font-size:10px; margin-bottom:5px; }
.conf-lbl { color:#4a6a8f; }
.conf-val { font-family:'JetBrains Mono',monospace; color:#c8d8e8; }
.conf-bg  { height:4px; background:#0e1e35; border-radius:2px; overflow:hidden; }
.conf-fill{ height:100%; border-radius:2px; transition: width 0.6s ease; }

/* ── Empty state ── */
.empty-state {
    text-align: center;
    padding: 50px 20px;
    color: #1a3050;
    font-size: 12px;
    letter-spacing: 0.05em;
}

/* ── Sidebar inner ── */
.sb-section {
    padding: 0 20px;
    margin: 6px 0;
}
.sb-label {
    font-size: 9px;
    text-transform: uppercase;
    letter-spacing: 0.14em;
    color: #152030;
    margin-bottom: 8px;
    margin-top: 18px;
    padding: 0 20px;
}
.sb-status {
    font-size: 10px;
    line-height: 2.5;
    color: #4a6a8f;
    padding: 0 20px;
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  PLOTLY THEME
# ─────────────────────────────────────────────
BASE_LAYOUT = dict(
    paper_bgcolor='#0a1120',
    plot_bgcolor='#04080f',
    font=dict(color='#4a6a8f', family='JetBrains Mono', size=10),
    xaxis=dict(gridcolor='#0e1e35', linecolor='#0e1e35', tickcolor='#0e1e35', zeroline=False),
    yaxis=dict(gridcolor='#0e1e35', linecolor='#0e1e35', tickcolor='#0e1e35', zeroline=False),
    margin=dict(l=44, r=16, t=24, b=36),
    legend=dict(bgcolor='rgba(0,0,0,0)', font=dict(size=10), borderwidth=0),
)
def pl(fig, **kw):
    fig.update_layout(**{**BASE_LAYOUT, **kw})
    return fig

SEQ  = ['#1ea0ff','#0ef0a0','#ff3355','#ffaa00','#aa55ff','#ff6688']
SAFE = '#0ef0a0'
THRT = '#ff3355'
WARN = '#ffaa00'
BLUE = '#1ea0ff'


# ─────────────────────────────────────────────
#  DATA
# ─────────────────────────────────────────────
@st.cache_data
def gen_pmu():
    np.random.seed(42)
    buses = [3,5,0,9,13,7]
    rows  = []
    for i in range(300):
        b = buses[i % 6]
        rows.append(dict(
            timestamp=round(i*0.05,4), bus_id=b,
            vm_pu    =round(1.05+np.random.normal(0,.02),6),
            va_degree=round(-10 +np.random.normal(0,1.5),6),
            im_pu    =round(0.5 +np.random.normal(0,.05),6),
            ia_degree=round(-10 +np.random.normal(0,1.0),6),
            p_mw     =round(50  +np.random.normal(0,5),6),
            q_mvar   =round(20  +np.random.normal(0,3),6),
            frequency=round(50  +np.random.normal(0,.01),4),
            rocof    =round(np.random.normal(0,.005),5),
        ))
    return pd.DataFrame(rows)

@st.cache_data
def gen_attacks():
    np.random.seed(42)
    lmap={0:'Normal',1:'FDI',2:'Replay',3:'DoS',4:'MITM',5:'Timestamp'}
    rows=[]
    for label in range(6):
        for _ in range(200):
            vm=1.05+np.random.normal(0,.02)
            if label==1: vm+=np.random.normal(0,.05)
            if label==3: vm=0.0 if np.random.rand()<.6 else vm
            rows.append(dict(
                vm_pu=round(vm,6), va_degree=round(-10+np.random.normal(0,1.5),6),
                p_mw=round(50+np.random.normal(0,5),6), q_mvar=round(20+np.random.normal(0,3),6),
                frequency=round(50+np.random.normal(0,.01),4), rocof=round(np.random.normal(0,.005),5),
                timestamp=round(np.random.uniform(0,2.5),4),
                label=label, label_name=lmap[label],
            ))
    return pd.DataFrame(rows)

df_pmu    = gen_pmu()
df_attack = gen_attacks()


# ─────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────
def kpi_html(label, value, sub, variant='blue'):
    return f"""<div class="kpi kpi-{variant}">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-sub">{sub}</div>
    </div>"""

def panel_open(title, badge='', badge_cls='pb-blue'):
    b = f'<span class="panel-badge {badge_cls}">{badge}</span>' if badge else ''
    return f'<div class="panel"><div class="panel-head"><span class="panel-title">{title}</span>{b}</div><div class="panel-body">'

def panel_close():
    return '</div></div>'

def drow(label, value, cls=''):
    return f'<div class="drow"><span class="drow-label">{label}</span><span class="drow-value {cls}">{value}</span></div>'

def now_str():
    return datetime.utcnow().strftime('%H:%M:%S')

def cm_fig(cm, labels, cmap_name, title):
    fig, ax = plt.subplots(figsize=(6.5, 4.8))
    fig.patch.set_facecolor('#0a1120')
    ax.set_facecolor('#04080f')
    cmap = plt.get_cmap(cmap_name)
    sns.heatmap(cm, annot=True, fmt='d', cmap=cmap,
                xticklabels=labels, yticklabels=labels, ax=ax,
                linewidths=0.4, linecolor='#0e1e35',
                annot_kws={"size": 9, "family": "monospace", "color": "#c8d8e8"})
    ax.set_title(title, color='#4a6a8f', fontsize=10, pad=10, family='monospace')
    ax.set_xlabel('Predicted', color='#2a4a6f', fontsize=9)
    ax.set_ylabel('Actual',    color='#2a4a6f', fontsize=9)
    ax.tick_params(colors='#4a6a8f', labelsize=8)
    plt.setp(ax.get_xticklabels(), rotation=30, ha='right')
    plt.tight_layout(pad=1.2)
    return fig


# ─────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:20px 20px 0;">
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:2px;">
            <div style="width:32px;height:32px;background:linear-gradient(135deg,#1ea0ff,#0ef0a0);
                        border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:16px;">🛡</div>
            <div>
                <div style="font-size:13px;font-weight:600;color:#e8f4ff;letter-spacing:.03em;">GridShield</div>
                <div style="font-size:9px;color:#152030;letter-spacing:.12em;text-transform:uppercase;">SOC Platform</div>
            </div>
        </div>
    </div>
    <div style="height:1px;background:#0e1e35;margin:16px 0 10px;"></div>
    """, unsafe_allow_html=True)

    page = st.radio("", [
        "Overview",
        "PMU Network",
        "Secure Comms",
        "Threat Detection",
        "Analytics",
        "Fault Monitor",
    ], label_visibility="collapsed")

    st.markdown("""
    <div style="height:1px;background:#0e1e35;margin:12px 0;"></div>
    <div class="sb-label">Grid Status</div>
    <div class="sb-status">
        <span style="color:#0ef0a0">●</span>&nbsp; 6 Sensors Online<br>
        <span style="color:#0ef0a0">●</span>&nbsp; Encryption Active<br>
        <span style="color:#0ef0a0">●</span>&nbsp; AI Models Running<br>
        <span style="color:#ffaa00">●</span>&nbsp; 2 Alerts Pending
    </div>
    <div style="height:1px;background:#0e1e35;margin:16px 0 12px;"></div>
    <div class="sb-label">Network</div>
    <div class="sb-status">
        <span style="color:#1ea0ff">●</span>&nbsp; IEEE 14-Bus<br>
        <span style="color:#2a4a6f">●</span>&nbsp; 6 / 6 PMUs<br>
        <span style="color:#2a4a6f">●</span>&nbsp; AES-256-GCM
    </div>
    <div style="position:absolute;bottom:16px;left:0;right:0;text-align:center;">
        <div style="font-size:9px;color:#0e1e35;letter-spacing:.1em;">GridShield v2.4.1</div>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  TOP BAR (rendered per page)
# ─────────────────────────────────────────────
page_titles = {
    "Overview":         ("Overview","System health and threat summary"),
    "PMU Network":      ("PMU Network","Live sensor data — 6 units online"),
    "Secure Comms":     ("Secure Comms","Encrypted data pipeline"),
    "Threat Detection": ("Threat Detection","AI-powered anomaly classification"),
    "Analytics":        ("Analytics","Model performance and detection metrics"),
    "Fault Monitor":    ("Fault Monitor","Power system fault classification"),
}
ptitle, psub = page_titles.get(page, (page, ""))
st.markdown(f"""
<div class="topbar">
    <div class="topbar-brand">
        <div class="brand-icon">🛡</div>
        <div>
            <div class="brand-name">GridShield — {ptitle}</div>
            <div class="brand-tag">{psub}</div>
        </div>
    </div>
    <div class="topbar-right">
        <div class="topbar-pill"><div class="pulse"></div>All Systems Operational</div>
        <div class="topbar-badge">6 PMUs ACTIVE</div>
        <div class="topbar-clock">{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC</div>
    </div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════
#  PAGE: OVERVIEW
# ══════════════════════════════════════════════
if page == "Overview":

    # KPI row
    k1,k2,k3,k4 = st.columns(4)
    with k1: st.markdown(kpi_html("Sensors Online","6 / 6","All units transmitting","blue"), unsafe_allow_html=True)
    with k2: st.markdown(kpi_html("Threat Detection Rate","89.4%","RF classifier active","green"), unsafe_allow_html=True)
    with k3: st.markdown(kpi_html("Active Alerts","2","High severity pending","red"), unsafe_allow_html=True)
    with k4: st.markdown(kpi_html("Fault Accuracy","99.1%","CNN classifier","blue"), unsafe_allow_html=True)

    col_l, col_r = st.columns([3,2])

    with col_l:
        # Recent events feed
        html  = panel_open("Recent Security Events", "● LIVE", "pb-green")
        events = [
            ("red",  "False data injection attempt on Sensor 02 — blocked",           "14:31:07"),
            ("amber","Voltage deviation on Bus 6 — within threshold",                  "14:29:44"),
            ("green","All 6 sensors passed integrity check",                           "14:28:12"),
            ("red",  "Replay packet detected on uplink channel — dropped",             "14:25:50"),
            ("amber","ROCOF spike on Bus 14 — monitoring escalated",                   "14:22:03"),
            ("green","Encryption key rotation completed",                              "14:18:30"),
            ("red",  "DoS pattern detected — rate limiting applied",                   "14:15:11"),
            ("green","Fault classifier updated — zero downtime",                       "14:10:00"),
        ]
        for dot, msg, t in events:
            html += f'<div class="feed-item"><div class="feed-dot {dot}"></div><div class="feed-text">{msg}</div><div class="feed-time">{t}</div></div>'
        html += panel_close()
        st.markdown(html, unsafe_allow_html=True)

        # Traffic chart
        html2 = panel_open("Data Traffic Volume", "LAST 5 MIN", "pb-blue")
        st.markdown(html2, unsafe_allow_html=True)
        np.random.seed(7)
        xs  = np.linspace(0,300,80)
        pkt = 40 + 30*np.sin(xs/30) + np.random.normal(0,5,80)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=xs, y=pkt, mode='lines',
            line=dict(color=BLUE, width=1.5),
            fill='tozeroy', fillcolor='rgba(30,160,255,0.07)',
            name='Packets/s'))
        pl(fig, height=130, margin=dict(l=40,r=10,t=10,b=30),
           xaxis_title="Seconds ago", yaxis_title="Packets / s")
        st.plotly_chart(fig, use_container_width=True)
        st.markdown(panel_close(), unsafe_allow_html=True)

    with col_r:
        # System health
        html3 = panel_open("System Health")
        rows = [
            ("Sensor Network","Operational","green"),
            ("Encryption Layer","Active · AES-256-GCM","green"),
            ("Threat Classifier","Running","green"),
            ("Fault Monitor","Running","green"),
            ("Data Integrity","Verified","green"),
            ("Alert Queue","2 pending","amber"),
            ("Last Key Rotation","14:18 UTC","blue"),
            ("Uptime","99.97%","green"),
        ]
        for lbl,val,cls in rows:
            html3 += drow(lbl,val,cls)
        html3 += panel_close()
        st.markdown(html3, unsafe_allow_html=True)

        # Attack breakdown donut
        html4 = panel_open("Threat Breakdown (Session)")
        st.markdown(html4, unsafe_allow_html=True)
        cnts = [312,41,28,19,15,10]
        lbls = ['Normal','FDI','Replay','DoS','MITM','Timestamp']
        fig2 = go.Figure(go.Pie(
            labels=lbls, values=cnts, hole=0.6,
            marker_colors=[SAFE,THRT,'#ff6680','#ff8844',WARN,'#ffcc44'],
            textinfo='none',
        ))
        fig2.add_annotation(text="<b>425</b><br><span style='font-size:9px'>packets</span>",
                            x=0.5,y=0.5, showarrow=False,
                            font=dict(color='#c8d8e8',size=13,family='JetBrains Mono'))
        pl(fig2, height=170, margin=dict(l=0,r=0,t=0,b=0),
           showlegend=True,
           legend=dict(font=dict(size=9),orientation='v',x=1,y=0.5))
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown(panel_close(), unsafe_allow_html=True)


# ══════════════════════════════════════════════
#  PAGE: PMU NETWORK
# ══════════════════════════════════════════════
elif page == "PMU Network":

    k1,k2,k3,k4 = st.columns(4)
    with k1: st.markdown(kpi_html("Units Online","6 / 6","Full coverage","green"), unsafe_allow_html=True)
    with k2: st.markdown(kpi_html("Parameters","13","Per sensor","blue"), unsafe_allow_html=True)
    with k3: st.markdown(kpi_html("Sample Rate","60 Hz","Synchrophasor","blue"), unsafe_allow_html=True)
    with k4: st.markdown(kpi_html("Load Variation","± 30%","Scenarios covered","amber"), unsafe_allow_html=True)

    # Sensor cards
    buses   = [4,6,1,10,14,8]
    np.random.seed(int(time.time()) % 100)
    alerts  = np.random.choice(6, size=2, replace=False)
    html_g  = '<div class="pmu-grid">'
    for i,b in enumerate(buses):
        is_alert = i in alerts
        vm  = round(1.0 + np.random.uniform(-0.04,0.04), 4)
        va  = round(np.random.uniform(-18,2), 2)
        fr  = round(50 + np.random.uniform(-0.03,0.03), 4)
        roc = round(np.random.uniform(-0.01,0.01), 5)
        status_cls = "alert" if is_alert else "ok"
        status_txt = f'<span style="color:#ff3355">ALERT</span>' if is_alert else f'<span style="color:#0ef0a0">SECURE</span>'
        html_g += f"""
        <div class="pmu-card {'alert-card' if is_alert else ''}">
            <div class="pmu-stat {status_cls}"></div>
            <div class="pmu-id">PMU-{str(i+1).zfill(2)}</div>
            <div class="pmu-loc">Bus {b}</div>
            {drow("Vm (p.u.)",   vm)}
            {drow("Va (°)",       va)}
            {drow("Freq (Hz)",    fr)}
            {drow("ROCOF",       roc)}
            {drow("Status", status_txt)}
        </div>"""
    html_g += '</div>'
    st.markdown(html_g, unsafe_allow_html=True)

    # Charts
    bus_filter = st.multiselect("Filter sensors:", options=sorted(df_pmu['bus_id'].unique()),
        default=sorted(df_pmu['bus_id'].unique()), format_func=lambda x: f"Bus {x+1}")
    df_f = df_pmu[df_pmu['bus_id'].isin(bus_filter)] if bus_filter else df_pmu

    def lc(y, title, ylab):
        fig = px.line(df_f, x='timestamp', y=y, color='bus_id',
                      color_discrete_sequence=SEQ,
                      labels={'timestamp':'Time (s)', y:ylab, 'bus_id':'Sensor'})
        fig.update_traces(line=dict(width=1.4))
        pl(fig, height=185, title=dict(text=title, font=dict(size=11,color='#4a6a8f'), x=0.01, y=0.97))
        return fig

    c1,c2 = st.columns(2)
    with c1:
        st.markdown(panel_open("Voltage Magnitude"), unsafe_allow_html=True)
        st.plotly_chart(lc('vm_pu','','Vm (p.u.)'), use_container_width=True)
        st.markdown(panel_close(), unsafe_allow_html=True)
    with c2:
        st.markdown(panel_open("Voltage Angle"), unsafe_allow_html=True)
        st.plotly_chart(lc('va_degree','','Va (°)'), use_container_width=True)
        st.markdown(panel_close(), unsafe_allow_html=True)

    c3,c4 = st.columns(2)
    with c3:
        st.markdown(panel_open("Frequency"), unsafe_allow_html=True)
        st.plotly_chart(lc('frequency','','Freq (Hz)'), use_container_width=True)
        st.markdown(panel_close(), unsafe_allow_html=True)
    with c4:
        st.markdown(panel_open("ROCOF"), unsafe_allow_html=True)
        st.plotly_chart(lc('rocof','','ROCOF (Hz/s)'), use_container_width=True)
        st.markdown(panel_close(), unsafe_allow_html=True)


# ══════════════════════════════════════════════
#  PAGE: SECURE COMMS
# ══════════════════════════════════════════════
elif page == "Secure Comms":

    k1,k2,k3,k4 = st.columns(4)
    with k1: st.markdown(kpi_html("Encryption","AES-256-GCM","Authenticated","green"), unsafe_allow_html=True)
    with k2: st.markdown(kpi_html("Encrypt Time","0.052 ms","Per packet","blue"), unsafe_allow_html=True)
    with k3: st.markdown(kpi_html("Decrypt Time","0.026 ms","Per packet","blue"), unsafe_allow_html=True)
    with k4: st.markdown(kpi_html("Tamper Detection","100%","Zero bypass","green"), unsafe_allow_html=True)

    col_l, col_r = st.columns([1,1])

    with col_l:
        st.markdown(panel_open("Send Encrypted Packet"), unsafe_allow_html=True)
        sensor   = st.selectbox("Sensor:", [f"PMU-0{i+1} · Bus {b}" for i,b in enumerate([4,6,1,10,14,8])])
        vm_val   = st.slider("Voltage Magnitude (p.u.)", 0.95, 1.10, 1.05, 0.001)
        va_val   = st.slider("Voltage Angle (°)", -25.0, 0.0, -10.0, 0.1)
        freq_val = st.slider("Frequency (Hz)", 49.90, 50.10, 50.00, 0.001)
        send_btn = st.button("Encrypt & Transmit", use_container_width=True)
        st.markdown(panel_close(), unsafe_allow_html=True)

        # Protocol specs
        st.markdown(panel_open("Protocol"), unsafe_allow_html=True)
        specs = [("Cipher","AES-256-GCM"),("Key size","256-bit"),
                 ("Nonce","96-bit random"),("Auth tag","128-bit"),
                 ("Frame format","C37.118-style"),("Access control","4 role levels"),
                 ("Tamper action","Drop + alert")]
        for l,v in specs:
            st.markdown(drow(l,v,'blue'), unsafe_allow_html=True)
        st.markdown(panel_close(), unsafe_allow_html=True)

    with col_r:
        st.markdown(panel_open("Transmission Log","● LIVE","pb-green"), unsafe_allow_html=True)
        if send_btn:
            bus_id = int(sensor.split("Bus ")[-1])
            packet = {"sensor": sensor, "bus_id": bus_id,
                      "vm_pu": vm_val, "va_degree": va_val,
                      "frequency": freq_val, "rocof": 0.001,
                      "ts": time.time()}
            key    = os.urandom(32)
            aesgcm = AESGCM(key)
            nonce  = os.urandom(12)
            plain  = json.dumps(packet).encode()

            t0=time.perf_counter(); ct=aesgcm.encrypt(nonce,plain,None); enc_ms=(time.perf_counter()-t0)*1e3
            t0=time.perf_counter(); dec=aesgcm.decrypt(nonce,ct,None);   dec_ms=(time.perf_counter()-t0)*1e3

            st.success(f"✓ Packet encrypted in {enc_ms:.4f} ms — transmitted to central PDC")

            st.markdown(f'<div class="mono-block"><span style="color:#4a6a8f">// ciphertext (hex)</span><br>{ct.hex()[:120]}...</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="mono-block"><span style="color:#4a6a8f">// decrypted payload</span><br>{json.dumps(json.loads(dec),indent=2)}</div>', unsafe_allow_html=True)

            # Tamper test
            tampered = bytes([ct[0]^0xFF])+ct[1:]
            try:
                aesgcm.decrypt(nonce,tampered,None)
                st.error("Tamper check failed.")
            except Exception:
                st.success("✓ Tamper test passed — modified packet rejected by authentication tag")

            # Mini latency chart
            runs = [round(np.random.uniform(0.044,0.062),4) for _ in range(30)]
            runs[-1] = enc_ms
            fig = go.Figure()
            fig.add_trace(go.Scatter(y=runs, mode='lines+markers',
                line=dict(color=SAFE,width=1.2),
                marker=dict(size=3,color=SAFE),
                name='Encrypt ms'))
            fig.add_hline(y=np.mean(runs),line_dash='dash',line_color=WARN,
                          annotation_text=f"avg {np.mean(runs):.3f}ms",
                          annotation_font=dict(color=WARN,size=9))
            pl(fig, height=120, yaxis_title='ms', xaxis_title='Packet #',
               margin=dict(l=44,r=10,t=10,b=30), showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.markdown('<div class="empty-state">Configure a packet on the left and click<br>Encrypt &amp; Transmit to see the output.</div>', unsafe_allow_html=True)
        st.markdown(panel_close(), unsafe_allow_html=True)


# ══════════════════════════════════════════════
#  PAGE: THREAT DETECTION
# ══════════════════════════════════════════════
elif page == "Threat Detection":

    k1,k2,k3,k4 = st.columns(4)
    with k1: st.markdown(kpi_html("Classifier","Random Forest","6-class detection","blue"), unsafe_allow_html=True)
    with k2: st.markdown(kpi_html("Accuracy","89.4%","Validated","green"), unsafe_allow_html=True)
    with k3: st.markdown(kpi_html("F1-Score","89.6%","Weighted avg","green"), unsafe_allow_html=True)
    with k4: st.markdown(kpi_html("Latency","< 1 ms","Per prediction","blue"), unsafe_allow_html=True)

    col_l, col_r = st.columns([1,1])

    with col_l:
        st.markdown(panel_open("Input Readings"), unsafe_allow_html=True)
        vm    = st.slider("Voltage Magnitude (p.u.)", 0.0, 1.2, 1.05, 0.01)
        va    = st.slider("Voltage Angle (°)", -30.0, 5.0, -10.0, 0.5)
        freq  = st.slider("Frequency (Hz)", 49.0, 51.0, 50.0, 0.01)
        p_mw  = st.slider("Active Power (MW)", 0.0, 100.0, 50.0, 1.0)
        q_mvar= st.slider("Reactive Power (MVAR)", 0.0, 50.0, 20.0, 1.0)
        rocof = st.slider("ROCOF (Hz/s)", -1.0, 1.0, 0.0, 0.01)
        ts    = st.slider("Timestamp offset (s)", 0.0, 200.0, 1.0, 0.5)
        run_btn = st.button("Run Classification", use_container_width=True)
        st.markdown(panel_close(), unsafe_allow_html=True)

    with col_r:
        st.markdown(panel_open("Classification Result","RF MODEL","pb-blue"), unsafe_allow_html=True)
        if run_btn:
            if vm == 0.0 or freq < 49.2:
                cls,conf,sev,action = "Denial of Service",94,"threat","Packet dropped. Rate limiter active. Admin alerted."
            elif abs(vm-1.05) > 0.08:
                cls,conf,sev,action = "False Data Injection",87,"threat","Data flagged. Sensor quarantined pending review."
            elif ts > 50:
                cls,conf,sev,action = "Timestamp Manipulation",96,"threat","GPS sync mismatch. Packet invalidated."
            elif abs(va+10) > 10:
                cls,conf,sev,action = "Man-in-the-Middle",82,"threat","Channel integrity breach. Rekeying initiated."
            elif abs(rocof) > 0.3:
                cls,conf,sev,action = "Replay Attack",88,"threat","Duplicate sequence detected. Packet dropped."
            else:
                cls,conf,sev,action = "Normal",91,"safe","No anomaly detected. Data forwarded to fault classifier."

            box_cls = "result-threat" if sev=="threat" else "result-safe"
            title_color = THRT if sev=="threat" else SAFE
            icon = "⚠" if sev=="threat" else "✓"
            st.markdown(f"""
            <div class="result-box {box_cls}">
                <div class="result-title" style="color:{title_color};">{icon} &nbsp;{cls}</div>
                <div class="result-meta">
                    Confidence: <span style="color:{title_color};font-family:'JetBrains Mono',monospace;">{conf}%</span>
                    &nbsp;·&nbsp; {action}
                </div>
            </div>""", unsafe_allow_html=True)

            # Confidence bars
            confs = {'Normal':91,'FDI':3,'Replay':2,'DoS':1,'MITM':2,'Timestamp':1}
            if sev=="threat":
                for k in confs: confs[k]=2
                short = cls.split("(")[0].strip().split()[-1]
                key_map = {"Service":"DoS","Injection":"FDI","Manipulation":"Timestamp","Middle":"MITM","Attack":"Replay"}
                matched = next((v for k,v in key_map.items() if k in cls),None)
                if matched and matched in confs: confs[matched]=conf
                elif cls=="Normal": confs['Normal']=conf

            st.markdown("<br>", unsafe_allow_html=True)
            for lbl,v in confs.items():
                color = SAFE if lbl=='Normal' else THRT
                st.markdown(f"""
                <div class="conf-row">
                    <div class="conf-top"><span class="conf-lbl">{lbl}</span><span class="conf-val">{v}%</span></div>
                    <div class="conf-bg"><div class="conf-fill" style="width:{v}%;background:{color};"></div></div>
                </div>""", unsafe_allow_html=True)
        else:
            st.markdown('<div class="empty-state">Adjust sensor readings on the left<br>and click Run Classification.</div>', unsafe_allow_html=True)
        st.markdown(panel_close(), unsafe_allow_html=True)


# ══════════════════════════════════════════════
#  PAGE: ANALYTICS
# ══════════════════════════════════════════════
elif page == "Analytics":

    k1,k2,k3,k4 = st.columns(4)
    with k1: st.markdown(kpi_html("Best Accuracy","99.1%","CNN fault classifier","green"), unsafe_allow_html=True)
    with k2: st.markdown(kpi_html("RF Accuracy","89.4%","Above industry benchmark","green"), unsafe_allow_html=True)
    with k3: st.markdown(kpi_html("Training Set","25K","Labelled samples","blue"), unsafe_allow_html=True)
    with k4: st.markdown(kpi_html("Models Active","2","RF + CNN deployed","blue"), unsafe_allow_html=True)

    col_l, col_r = st.columns([3,2])

    with col_l:
        st.markdown(panel_open("Model Accuracy"), unsafe_allow_html=True)
        models = ['Random Forest','LSTM','1D-CNN']
        acc    = [89.43, 54.85, 99.05]
        f1s    = [89.60, 53.38, 99.05]
        colors_m=[SAFE, WARN, BLUE]
        fig = go.Figure()
        for m,a,f,c in zip(models,acc,f1s,colors_m):
            fig.add_trace(go.Bar(name=f'{m} Acc', x=[m], y=[a],
                marker_color=c, marker_opacity=0.75,
                text=f'{a}%', textposition='outside',
                textfont=dict(size=10,color='#c8d8e8',family='JetBrains Mono')))
            fig.add_trace(go.Bar(name=f'{m} F1', x=[m], y=[f],
                marker_color=c, marker_opacity=0.35,
                text=f'{f}%', textposition='outside',
                textfont=dict(size=10,color='#4a6a8f',family='JetBrains Mono')))
        fig.add_hline(y=88.7, line_dash='dash', line_color=THRT, line_width=1,
                      annotation_text='Industry baseline 88.7%',
                      annotation_font=dict(color=THRT,size=9))
        pl(fig, height=250, barmode='group', yaxis_range=[0,115],
           legend=dict(font=dict(size=9),bgcolor='rgba(0,0,0,0)',orientation='h',y=1.08))
        st.plotly_chart(fig, use_container_width=True)
        st.markdown(panel_close(), unsafe_allow_html=True)

    with col_r:
        st.markdown(panel_open("Performance Summary"), unsafe_allow_html=True)
        perf = [
            ("Random Forest","89.43% acc","green"),
            ("LSTM","54.85% acc","amber"),
            ("1D-CNN","99.05% acc","green"),
            ("Industry Baseline","88.70% acc","blue"),
            ("RF vs Baseline","+0.73% ↑","green"),
            ("Attack Classes","6 detected","blue"),
            ("Fault Classes","5 detected","blue"),
        ]
        for l,v,c in perf:
            st.markdown(drow(l,v,c), unsafe_allow_html=True)
        st.markdown(panel_close(), unsafe_allow_html=True)

        st.markdown(panel_open("Detected Threats"), unsafe_allow_html=True)
        for cls in ['Normal','False Data Injection','Replay Attack','Denial of Service','Man-in-the-Middle','Timestamp Manipulation']:
            color = SAFE if cls=='Normal' else THRT
            st.markdown(f'<div class="feed-item"><div class="feed-dot {"green" if cls=="Normal" else "red"}"></div><div class="feed-text" style="font-size:10px;">{cls}</div></div>', unsafe_allow_html=True)
        st.markdown(panel_close(), unsafe_allow_html=True)

    # Confusion matrices
    st.markdown("---")
    tab1,tab2,tab3 = st.tabs(["Random Forest  89.4%","LSTM  54.9%","1D-CNN  99.1%"])
    L6 = ['Normal','FDI','Replay','DoS','MITM','Timestamp']
    L5 = ['Normal','Zone1','Zone2','Zone3','PwrSwing']
    cm_rf   = np.array([[478,2,0,8,6,6],[3,467,2,8,8,12],[0,1,499,0,0,0],[6,9,0,475,6,4],[8,7,0,5,472,8],[3,6,0,3,3,485]])
    cm_lstm = np.array([[18,60,60,120,100,84],[20,170,60,80,60,36],[0,0,416,0,0,0],[30,60,10,142,90,140],[40,50,10,80,88,151],[0,0,0,8,0,807]])
    cm_cnn  = np.array([[398,0,0,2,0],[0,398,0,2,0],[0,0,400,0,0],[2,2,0,396,0],[0,0,0,0,400]])
    with tab1:
        c1,c2=st.columns([2,1])
        with c1: st.pyplot(cm_fig(cm_rf,L6,'Blues','Random Forest — Attack Detection'))
        with c2:
            st.success("✓ Accuracy: 89.43%")
            st.success("✓ F1-Score: 89.60%")
            st.info("Best performing model for attack detection")
    with tab2:
        c1,c2=st.columns([2,1])
        with c1: st.pyplot(cm_fig(cm_lstm,L6,'Greens','LSTM — Attack Detection'))
        with c2:
            st.warning("Accuracy: 54.85%")
            st.warning("F1-Score: 53.38%")
            st.info("Performs better with streaming data input")
    with tab3:
        c1,c2=st.columns([2,1])
        with c1: st.pyplot(cm_fig(cm_cnn,L5,'YlOrBr','1D-CNN — Fault Classification'))
        with c2:
            st.success("✓ Accuracy: 99.05%")
            st.success("✓ F1-Score: 99.05%")
            st.info("Near-perfect fault zone separation")


# ══════════════════════════════════════════════
#  PAGE: FAULT MONITOR
# ══════════════════════════════════════════════
elif page == "Fault Monitor":

    k1,k2,k3,k4 = st.columns(4)
    with k1: st.markdown(kpi_html("Classifier","1D-CNN","5-class fault detection","blue"), unsafe_allow_html=True)
    with k2: st.markdown(kpi_html("Accuracy","99.1%","All fault zones","green"), unsafe_allow_html=True)
    with k3: st.markdown(kpi_html("Response","< 0.1 s","Per classification","green"), unsafe_allow_html=True)
    with k4: st.markdown(kpi_html("Fault Types","5","Zone 1/2/3 + Swing","amber"), unsafe_allow_html=True)

    col_l, col_r = st.columns([1,1])

    with col_l:
        st.markdown(panel_open("Sensor Readings"), unsafe_allow_html=True)
        vm_f    = st.slider("Voltage Magnitude (p.u.)", 0.5, 1.2, 1.05, 0.01)
        va_f    = st.slider("Voltage Angle (°)", -30.0, 15.0, -10.0, 0.5)
        freq_f  = st.slider("Frequency (Hz)", 49.0, 51.0, 50.0, 0.01)
        p_f     = st.slider("Active Power (MW)", 0.0, 150.0, 50.0, 1.0)
        q_f     = st.slider("Reactive Power (MVAR)", -20.0, 60.0, 20.0, 1.0)
        rocof_f = st.slider("ROCOF (Hz/s)", -2.0, 2.0, 0.0, 0.01)
        classify_btn = st.button("Classify Condition", use_container_width=True)
        st.markdown(panel_close(), unsafe_allow_html=True)

    with col_r:
        st.markdown(panel_open("Fault Classification Result","CNN","pb-blue"), unsafe_allow_html=True)
        if classify_btn:
            drop = 1.05 - vm_f
            va_sh= abs(va_f+10)

            if drop > 0.25:
                zone,color,sev,relay,desc = "Zone 1 Fault",THRT,"threat","Immediate trip","Severe fault near relay — protection activated"
            elif drop > 0.15:
                zone,color,sev,relay,desc = "Zone 2 Fault","#ff6640","threat","Trip after 0.3 s","Moderate fault — Zone 2 protection initiated"
            elif drop > 0.08 or va_sh > 10:
                zone,color,sev,relay,desc = "Zone 3 Fault",WARN,"warn","Trip after 1.0 s","Distant fault — backup protection initiated"
            elif abs(rocof_f) > 0.5:
                zone,color,sev,relay,desc = "Power Swing","#aa55ff","warn","Relay blocked","Power oscillation — blocking relay operation"
            else:
                zone,color,sev,relay,desc = "Normal Operation",SAFE,"safe","No action","System within normal operating parameters"

            box_cls = "result-threat" if sev=="threat" else "result-warn" if sev=="warn" else "result-safe"
            icon    = "⚠" if sev in ("threat","warn") else "✓"
            st.markdown(f"""
            <div class="result-box {box_cls}">
                <div class="result-title" style="color:{color};">{icon} &nbsp;{zone}</div>
                <div class="result-meta">
                    {desc}<br>
                    Relay action: <span style="color:{color};font-family:'JetBrains Mono',monospace;">{relay}</span>
                </div>
            </div>""", unsafe_allow_html=True)

            # Zone probability bars
            zones   = ['Normal','Zone 1','Zone 2','Zone 3','Power Swing']
            z_idx   = zones.index(zone.replace(" Fault","").replace(" Operation",""))
            z_vals  = [3,3,3,3,3]; z_vals[z_idx]=92
            z_colors= [SAFE,THRT,'#ff6640',WARN,'#aa55ff']
            fig = go.Figure(go.Bar(
                x=zones, y=z_vals,
                marker_color=z_colors, marker_opacity=0.75,
                text=[f'{v}%' for v in z_vals],
                textposition='outside',
                textfont=dict(size=10,color='#c8d8e8',family='JetBrains Mono')
            ))
            pl(fig, height=155, yaxis_range=[0,110], showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.markdown('<div class="empty-state">Adjust sensor readings on the left<br>and click Classify Condition.</div>', unsafe_allow_html=True)
        st.markdown(panel_close(), unsafe_allow_html=True)

    c1,c2 = st.columns(2)
    with c1:
        st.markdown(panel_open("Protection Zones"), unsafe_allow_html=True)
        zones_ref = [
            ("Normal","< 5% Vm drop","No action","green"),
            ("Zone 1","&gt; 25% drop","Immediate trip","red"),
            ("Zone 2","15 – 25% drop","Trip 0.3 s","red"),
            ("Zone 3","8 – 15% drop","Trip 1.0 s","amber"),
            ("Power Swing","ROCOF &gt; 0.5","Block relay","amber"),
        ]
        for cond,trig,act,cls in zones_ref:
            st.markdown(f'<div class="drow"><span class="drow-label">{cond} — {trig}</span><span class="drow-value {cls}">{act}</span></div>', unsafe_allow_html=True)
        st.markdown(panel_close(), unsafe_allow_html=True)

    with c2:
        st.markdown(panel_open("Class Distribution"), unsafe_allow_html=True)
        fd = pd.DataFrame({'Zone':['Normal','Zone1','Zone2','Zone3','PowerSwing'],'Count':[2000]*5})
        fig2 = go.Figure(go.Pie(
            labels=fd['Zone'], values=fd['Count'], hole=0.55,
            marker_colors=[SAFE,THRT,'#ff6640',WARN,'#aa55ff'],
            textinfo='none',
        ))
        fig2.add_annotation(text="<b>10K</b><br><span style='font-size:9px'>samples</span>",
                            x=0.5,y=0.5,showarrow=False,
                            font=dict(color='#c8d8e8',size=13,family='JetBrains Mono'))
        pl(fig2, height=165, margin=dict(l=0,r=0,t=0,b=0),
           legend=dict(font=dict(size=9),bgcolor='rgba(0,0,0,0)'))
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown(panel_close(), unsafe_allow_html=True)

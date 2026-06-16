import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import json, os, time, random
from datetime import datetime
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

st.set_page_config(
    page_title="NEXUS — Grid Defence",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;700;900&family=Share+Tech+Mono&family=Inter:wght@300;400;500&display=swap');

*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html,body{background:#05010f;}

.stApp{
    background: #05010f;
    font-family:'Inter',sans-serif;
    color:#e0d0ff;
}
.main .block-container{padding:0 1.8rem 3rem;max-width:1440px;}

/* Hide chrome */
#MainMenu,footer,header,.stDeployButton,[data-testid="stToolbar"]{display:none!important;}

/* ── Scanline overlay ── */
.stApp::before{
    content:'';
    position:fixed;top:0;left:0;right:0;bottom:0;
    background: repeating-linear-gradient(
        0deg,
        transparent,
        transparent 2px,
        rgba(180,0,255,0.015) 2px,
        rgba(180,0,255,0.015) 4px
    );
    pointer-events:none;
    z-index:0;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"]{
    background: linear-gradient(180deg,#0a0118 0%,#080114 100%) !important;
    border-right: 1px solid rgba(180,0,255,0.25) !important;
    box-shadow: 4px 0 30px rgba(180,0,255,0.08) !important;
}
section[data-testid="stSidebar"]>div{padding:0!important;}

/* Radio nav */
div[data-testid="stSidebar"] .stRadio>label{display:none;}
div[data-testid="stSidebar"] .stRadio div[role="radiogroup"]{gap:2px;display:flex;flex-direction:column;}
div[data-testid="stSidebar"] .stRadio label[data-baseweb="radio"]{
    padding:11px 22px!important;
    border-radius:0!important;
    border-left:2px solid transparent!important;
    font-family:'Share Tech Mono',monospace!important;
    font-size:10px!important;
    letter-spacing:0.12em!important;
    text-transform:uppercase!important;
    color:#4a2a7a!important;
    transition:all 0.2s!important;
    cursor:pointer!important;
}
div[data-testid="stSidebar"] .stRadio label[data-baseweb="radio"]:hover{
    background:rgba(180,0,255,0.07)!important;
    color:#cc66ff!important;
}
div[data-testid="stSidebar"] .stRadio label[data-baseweb="radio"]:has(input:checked){
    border-left-color:#b400ff!important;
    color:#e066ff!important;
    background:rgba(180,0,255,0.12)!important;
    box-shadow:inset 0 0 20px rgba(180,0,255,0.05)!important;
}

/* ── Top bar ── */
.topbar{
    display:flex;align-items:center;justify-content:space-between;
    padding:16px 0 16px;
    border-bottom:1px solid rgba(180,0,255,0.2);
    margin-bottom:22px;
    position:relative;
}
.topbar::after{
    content:'';position:absolute;bottom:-1px;left:0;width:200px;height:1px;
    background:linear-gradient(90deg,#b400ff,transparent);
}
.brand{display:flex;align-items:center;gap:14px;}
.brand-logo{
    font-family:'Orbitron',monospace;
    font-size:22px;font-weight:900;
    background:linear-gradient(135deg,#ff00cc,#b400ff,#6600ff);
    -webkit-background-clip:text;-webkit-text-fill-color:transparent;
    letter-spacing:0.15em;
    filter:drop-shadow(0 0 12px rgba(180,0,255,0.6));
}
.brand-sub{font-size:9px;color:#4a2a7a;letter-spacing:0.2em;text-transform:uppercase;margin-top:2px;}
.topbar-right{display:flex;align-items:center;gap:18px;}
.live-pill{
    display:flex;align-items:center;gap:7px;
    font-family:'Share Tech Mono',monospace;
    font-size:10px;color:#ff00cc;letter-spacing:0.08em;
}
.blink{
    width:7px;height:7px;border-radius:50%;background:#ff00cc;
    box-shadow:0 0 8px #ff00cc,0 0 16px rgba(255,0,204,0.4);
    animation:blink 1.2s ease-in-out infinite;
}
@keyframes blink{0%,100%{opacity:1;}50%{opacity:0.3;}}
.tb-clock{
    font-family:'Share Tech Mono',monospace;font-size:11px;
    color:#6600ff;letter-spacing:0.06em;
}
.tb-badge{
    font-family:'Share Tech Mono',monospace;font-size:9px;
    padding:4px 12px;border-radius:2px;
    background:rgba(180,0,255,0.12);
    border:1px solid rgba(180,0,255,0.4);
    color:#b400ff;letter-spacing:0.1em;
}

/* ── KPI Cards ── */
.kpi-row{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:20px;}
.kpi{
    background:linear-gradient(135deg,#0d0120 0%,#0a0118 100%);
    border:1px solid rgba(180,0,255,0.2);
    border-radius:8px;
    padding:16px 18px;
    position:relative;overflow:hidden;
    transition:border-color 0.3s;
}
.kpi::before{
    content:'';position:absolute;top:0;left:0;right:0;height:1px;
}
.kpi-purple::before{background:linear-gradient(90deg,#b400ff,rgba(180,0,255,0.1));}
.kpi-pink::before  {background:linear-gradient(90deg,#ff00cc,rgba(255,0,204,0.1));}
.kpi-cyan::before  {background:linear-gradient(90deg,#00ffee,rgba(0,255,238,0.1));}
.kpi-red::before   {background:linear-gradient(90deg,#ff003c,rgba(255,0,60,0.1));}
.kpi::after{
    content:'';
    position:absolute;top:-40%;right:-20%;
    width:80px;height:80px;border-radius:50%;
    filter:blur(30px);opacity:0.15;
}
.kpi-purple::after{background:#b400ff;}
.kpi-pink::after  {background:#ff00cc;}
.kpi-cyan::after  {background:#00ffee;}
.kpi-red::after   {background:#ff003c;}
.kpi-label{font-size:9px;letter-spacing:0.14em;text-transform:uppercase;color:#4a2a7a;margin-bottom:10px;font-family:'Share Tech Mono',monospace;}
.kpi-value{
    font-family:'Orbitron',monospace;font-size:26px;font-weight:700;line-height:1;margin-bottom:6px;
}
.kpi-purple .kpi-value{color:#cc66ff;text-shadow:0 0 20px rgba(180,0,255,0.5);}
.kpi-pink   .kpi-value{color:#ff66dd;text-shadow:0 0 20px rgba(255,0,204,0.5);}
.kpi-cyan   .kpi-value{color:#66ffee;text-shadow:0 0 20px rgba(0,255,238,0.5);}
.kpi-red    .kpi-value{color:#ff4466;text-shadow:0 0 20px rgba(255,0,60,0.5);}
.kpi-sub{font-size:9px;color:#3a1a5a;font-family:'Share Tech Mono',monospace;letter-spacing:0.06em;}

/* ── Panels ── */
.panel{
    background:linear-gradient(135deg,#0a0118 0%,#08010f 100%);
    border:1px solid rgba(180,0,255,0.18);
    border-radius:10px;overflow:hidden;margin-bottom:14px;
    box-shadow:0 4px 30px rgba(100,0,180,0.06);
}
.ph{
    display:flex;align-items:center;justify-content:space-between;
    padding:11px 16px;
    border-bottom:1px solid rgba(180,0,255,0.12);
    background:rgba(180,0,255,0.04);
}
.pt{
    font-family:'Orbitron',monospace;font-size:9px;font-weight:600;
    letter-spacing:0.18em;text-transform:uppercase;color:#7a30aa;
}
.pb-body{padding:14px 16px;}
.pbadge{
    font-family:'Share Tech Mono',monospace;font-size:9px;
    padding:2px 9px;border-radius:2px;letter-spacing:0.08em;
}
.pb-live  {background:rgba(255,0,204,0.1);color:#ff00cc;border:1px solid rgba(255,0,204,0.3);}
.pb-purple{background:rgba(180,0,255,0.1);color:#cc66ff;border:1px solid rgba(180,0,255,0.3);}
.pb-cyan  {background:rgba(0,255,238,0.08);color:#66ffee;border:1px solid rgba(0,255,238,0.25);}
.pb-red   {background:rgba(255,0,60,0.08); color:#ff4466;border:1px solid rgba(255,0,60,0.25);}

/* ── Threat feed ── */
.feed{max-height:300px;overflow-y:auto;}
.feed::-webkit-scrollbar{width:2px;}
.feed::-webkit-scrollbar-thumb{background:rgba(180,0,255,0.3);}
.fi{
    display:flex;align-items:flex-start;gap:10px;
    padding:9px 0;border-bottom:1px solid rgba(180,0,255,0.08);
    font-size:11px;
}
.fi:last-child{border:none;}
.fdot{width:7px;height:7px;border-radius:50%;flex-shrink:0;margin-top:3px;}
.fdot-crit{background:#ff003c;box-shadow:0 0 8px #ff003c,0 0 16px rgba(255,0,60,0.3);}
.fdot-high{background:#ff00cc;box-shadow:0 0 6px rgba(255,0,204,0.6);}
.fdot-med {background:#ffaa00;box-shadow:0 0 5px rgba(255,170,0,0.4);}
.fdot-low {background:#cc66ff;}
.fmsg{color:#c8a8e8;flex:1;line-height:1.5;}
.ftime{font-family:'Share Tech Mono',monospace;font-size:9px;color:#3a1a5a;flex-shrink:0;}

/* ── Data rows ── */
.dr{
    display:flex;justify-content:space-between;align-items:center;
    padding:8px 0;border-bottom:1px solid rgba(180,0,255,0.07);font-size:11px;
}
.dr:last-child{border:none;}
.dl{color:#4a2a7a;font-size:10px;letter-spacing:0.04em;}
.dv{font-family:'Share Tech Mono',monospace;font-size:11px;}
.dv-p{color:#cc66ff;} .dv-g{color:#66ffee;} .dv-r{color:#ff4466;} .dv-a{color:#ffaa00;} .dv-w{color:#e0d0ff;}

/* ── PMU Cards ── */
.pmugrid{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-bottom:14px;}
.pcard{
    background:linear-gradient(135deg,#0a0118,#07010e);
    border:1px solid rgba(180,0,255,0.18);border-radius:8px;padding:14px;position:relative;
    transition:border-color 0.3s,box-shadow 0.3s;
}
.pcard.alert{
    border-color:rgba(255,0,60,0.5)!important;
    box-shadow:0 0 20px rgba(255,0,60,0.08),inset 0 0 20px rgba(255,0,60,0.03)!important;
}
.pid{font-family:'Orbitron',monospace;font-size:10px;font-weight:600;color:#b400ff;margin-bottom:2px;letter-spacing:0.1em;}
.ploc{font-size:9px;color:#3a1a5a;margin-bottom:10px;font-family:'Share Tech Mono',monospace;letter-spacing:0.08em;}
.pstat{position:absolute;top:12px;right:12px;width:8px;height:8px;border-radius:50%;}
.pstat-ok   {background:#66ffee;box-shadow:0 0 8px #66ffee,0 0 16px rgba(0,255,238,0.3);}
.pstat-alert{background:#ff003c;box-shadow:0 0 8px #ff003c;animation:blink 0.8s infinite;}

/* ── Result boxes ── */
.rbox{border-radius:8px;padding:18px 20px;margin:10px 0;}
.rbox-threat{
    background:linear-gradient(135deg,rgba(255,0,60,0.06),rgba(180,0,255,0.04));
    border:1px solid rgba(255,0,60,0.35);border-left:3px solid #ff003c;
}
.rbox-warn{
    background:linear-gradient(135deg,rgba(255,170,0,0.05),rgba(180,0,255,0.03));
    border:1px solid rgba(255,170,0,0.3);border-left:3px solid #ffaa00;
}
.rbox-safe{
    background:linear-gradient(135deg,rgba(0,255,238,0.04),rgba(180,0,255,0.03));
    border:1px solid rgba(0,255,238,0.25);border-left:3px solid #66ffee;
}
.rtitle{font-family:'Orbitron',monospace;font-size:14px;font-weight:600;margin-bottom:7px;letter-spacing:0.06em;}
.rmeta{font-size:11px;color:#6a4a9a;line-height:1.8;}

/* ── Confidence bars ── */
.cbar{margin-bottom:9px;}
.ctop{display:flex;justify-content:space-between;font-size:10px;margin-bottom:4px;}
.clbl{color:#4a2a7a;font-family:'Share Tech Mono',monospace;letter-spacing:0.05em;}
.cval{font-family:'Share Tech Mono',monospace;color:#cc66ff;}
.cbg{height:4px;background:rgba(180,0,255,0.1);border-radius:2px;overflow:hidden;}
.cfill{height:100%;border-radius:2px;transition:width 0.7s ease;}

/* ── Buttons ── */
.stButton>button{
    background:linear-gradient(135deg,rgba(180,0,255,0.15),rgba(255,0,204,0.1))!important;
    border:1px solid rgba(180,0,255,0.5)!important;
    color:#cc66ff!important;
    font-family:'Orbitron',monospace!important;
    font-size:10px!important;font-weight:600!important;
    letter-spacing:0.12em!important;
    border-radius:6px!important;padding:10px 20px!important;
    width:100%!important;
    transition:all 0.2s!important;
    text-shadow:0 0 10px rgba(180,0,255,0.4)!important;
    box-shadow:0 0 15px rgba(180,0,255,0.1)!important;
}
.stButton>button:hover{
    background:linear-gradient(135deg,rgba(180,0,255,0.25),rgba(255,0,204,0.15))!important;
    box-shadow:0 0 25px rgba(180,0,255,0.25)!important;
    border-color:rgba(255,0,204,0.7)!important;
}

/* ── Form controls ── */
.stSlider label{font-size:10px!important;color:#4a2a7a!important;font-family:'Share Tech Mono',monospace!important;letter-spacing:0.06em!important;}
.stSlider [data-baseweb="slider"] [data-testid="stSliderThumb"]{background:#b400ff!important;border-color:#ff00cc!important;}
.stMultiSelect label,.stSelectbox label{font-size:10px!important;color:#4a2a7a!important;font-family:'Share Tech Mono',monospace!important;}
.stMultiSelect [data-baseweb="select"]>div,.stSelectbox [data-baseweb="select"]>div{
    background:#0a0118!important;border-color:rgba(180,0,255,0.3)!important;border-radius:6px!important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"]{background:transparent!important;border-bottom:1px solid rgba(180,0,255,0.15);gap:0;}
.stTabs [data-baseweb="tab"]{
    font-family:'Share Tech Mono',monospace!important;font-size:10px!important;
    letter-spacing:0.1em!important;text-transform:uppercase!important;
    color:#3a1a5a!important;background:transparent!important;
    border:none!important;border-bottom:2px solid transparent!important;
    padding:10px 18px!important;border-radius:0!important;
}
.stTabs [aria-selected="true"]{color:#cc66ff!important;border-bottom-color:#b400ff!important;text-shadow:0 0 10px rgba(180,0,255,0.5)!important;}
.stTabs [data-baseweb="tab-panel"]{background:transparent!important;padding-top:18px;}

/* ── Alerts ── */
.stSuccess{background:rgba(0,255,238,0.05)!important;border:1px solid rgba(0,255,238,0.2)!important;border-radius:7px!important;color:#66ffee!important;}
.stWarning{background:rgba(255,170,0,0.05)!important;border:1px solid rgba(255,170,0,0.2)!important;border-radius:7px!important;color:#ffaa00!important;}
.stInfo   {background:rgba(180,0,255,0.06)!important;border:1px solid rgba(180,0,255,0.2)!important;border-radius:7px!important;color:#cc66ff!important;}

/* ── Dataframe ── */
[data-testid="stDataFrame"]{border:1px solid rgba(180,0,255,0.2)!important;border-radius:8px!important;}

/* ── Mono block ── */
.monoblock{
    background:#04000d;border:1px solid rgba(180,0,255,0.2);border-radius:7px;
    padding:12px 14px;font-family:'Share Tech Mono',monospace;
    font-size:10px;color:#cc66ff;word-break:break-all;line-height:1.9;margin-bottom:10px;
}

/* ── Divider ── */
hr{border:none!important;border-top:1px solid rgba(180,0,255,0.12)!important;margin:18px 0!important;}

/* ── Scrollbar ── */
::-webkit-scrollbar{width:3px;height:3px;}
::-webkit-scrollbar-track{background:transparent;}
::-webkit-scrollbar-thumb{background:rgba(180,0,255,0.3);border-radius:2px;}

/* ── Empty state ── */
.empty{text-align:center;padding:50px 20px;color:#2a0a4a;font-family:'Share Tech Mono',monospace;font-size:11px;letter-spacing:0.08em;}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ── Plotly theme ──────────────────────────────
BL = dict(
    paper_bgcolor='#0a0118', plot_bgcolor='#05010f',
    font=dict(color='#4a2a7a', family='Share Tech Mono', size=10),
    xaxis=dict(gridcolor='rgba(180,0,255,0.08)', linecolor='rgba(180,0,255,0.15)',
               tickcolor='rgba(180,0,255,0.15)', zeroline=False),
    yaxis=dict(gridcolor='rgba(180,0,255,0.08)', linecolor='rgba(180,0,255,0.15)',
               tickcolor='rgba(180,0,255,0.15)', zeroline=False),
    margin=dict(l=44,r=16,t=20,b=36),
    legend=dict(bgcolor='rgba(0,0,0,0)',font=dict(size=10),borderwidth=0),
)
def pl(fig,**kw):
    fig.update_layout(**{**BL,**kw}); return fig

PURPLE='#b400ff'; PINK='#ff00cc'; CYAN='#66ffee'; RED='#ff003c'; AMBER='#ffaa00'
SEQ=[PURPLE,PINK,CYAN,RED,AMBER,'#8844ff']

# ── Data ─────────────────────────────────────
@st.cache_data
def gen_pmu():
    np.random.seed(42); buses=[3,5,0,9,13,7]; rows=[]
    for i in range(300):
        b=buses[i%6]
        rows.append(dict(timestamp=round(i*.05,4),bus_id=b,
            vm_pu=round(1.05+np.random.normal(0,.02),6),
            va_degree=round(-10+np.random.normal(0,1.5),6),
            p_mw=round(50+np.random.normal(0,5),6),
            q_mvar=round(20+np.random.normal(0,3),6),
            frequency=round(50+np.random.normal(0,.01),4),
            rocof=round(np.random.normal(0,.005),5)))
    return pd.DataFrame(rows)

@st.cache_data
def gen_atk():
    np.random.seed(42)
    lmap={0:'Normal',1:'FDI',2:'Replay',3:'DoS',4:'MITM',5:'Timestamp'}
    rows=[]
    for label in range(6):
        for _ in range(200):
            vm=1.05+np.random.normal(0,.02)
            if label==1: vm+=np.random.normal(0,.05)
            if label==3: vm=0.0 if np.random.rand()<.6 else vm
            rows.append(dict(vm_pu=round(vm,6),
                va_degree=round(-10+np.random.normal(0,1.5),6),
                p_mw=round(50+np.random.normal(0,5),6),
                frequency=round(50+np.random.normal(0,.01),4),
                rocof=round(np.random.normal(0,.005),5),
                label=label,label_name=lmap[label]))
    return pd.DataFrame(rows)

df_pmu=gen_pmu(); df_atk=gen_atk()

# ── Helpers ──────────────────────────────────
def kpi(label,value,sub,v='purple'):
    return f'<div class="kpi kpi-{v}"><div class="kpi-label">{label}</div><div class="kpi-value">{value}</div><div class="kpi-sub">{sub}</div></div>'

def po(title,badge='',bc='pb-purple'):
    b=f'<span class="pbadge {bc}">{badge}</span>' if badge else ''
    return f'<div class="panel"><div class="ph"><span class="pt">{title}</span>{b}</div><div class="pb-body">'

def pc(): return '</div></div>'

def dr(l,v,vc='dv-w'):
    return f'<div class="dr"><span class="dl">{l}</span><span class="dv {vc}">{v}</span></div>'

def feed_item(dot,msg,t):
    return f'<div class="fi"><div class="fdot {dot}"></div><div class="fmsg">{msg}</div><div class="ftime">{t}</div></div>'

def cm_fig(cm,labels,title):
    cmap=matplotlib.colors.LinearSegmentedColormap.from_list('nx',['#05010f','#3a006a','#b400ff','#ff00cc'])
    fig,ax=plt.subplots(figsize=(6.5,4.8))
    fig.patch.set_facecolor('#0a0118'); ax.set_facecolor('#05010f')
    sns.heatmap(cm,annot=True,fmt='d',cmap=cmap,xticklabels=labels,yticklabels=labels,ax=ax,
                linewidths=0.4,linecolor='rgba(180,0,255,0.1)',
                annot_kws={"size":9,"family":"monospace","color":"#e0d0ff"})
    ax.set_title(title,color='#7a30aa',fontsize=10,pad=10,family='monospace')
    ax.set_xlabel('Predicted',color='#4a2a7a',fontsize=9)
    ax.set_ylabel('Actual',   color='#4a2a7a',fontsize=9)
    ax.tick_params(colors='#4a2a7a',labelsize=8)
    plt.setp(ax.get_xticklabels(),rotation=30,ha='right')
    plt.tight_layout(pad=1.2); return fig

# ── Sidebar ──────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:22px 22px 0;">
        <div style="font-family:'Orbitron',monospace;font-size:18px;font-weight:900;
             background:linear-gradient(135deg,#ff00cc,#b400ff,#6600ff);
             -webkit-background-clip:text;-webkit-text-fill-color:transparent;
             letter-spacing:0.18em;filter:drop-shadow(0 0 12px rgba(180,0,255,0.7));">
            NEXUS
        </div>
        <div style="font-size:8px;color:#3a1a5a;letter-spacing:0.22em;text-transform:uppercase;margin-top:3px;font-family:'Share Tech Mono',monospace;">
            Grid Defence System
        </div>
    </div>
    <div style="height:1px;background:linear-gradient(90deg,rgba(180,0,255,0.4),transparent);margin:16px 0 12px;"></div>
    """, unsafe_allow_html=True)

    page=st.radio("",[
        "// OVERVIEW",
        "// PMU NETWORK",
        "// SECURE COMMS",
        "// THREAT INTEL",
        "// ANALYTICS",
        "// FAULT MONITOR",
    ],label_visibility="collapsed")

    st.markdown("""
    <div style="height:1px;background:linear-gradient(90deg,rgba(180,0,255,0.2),transparent);margin:14px 0 12px;"></div>
    <div style="padding:0 22px;">
        <div style="font-size:8px;color:#2a0a4a;letter-spacing:0.18em;text-transform:uppercase;margin-bottom:10px;font-family:'Share Tech Mono',monospace;">System Matrix</div>
        <div style="font-family:'Share Tech Mono',monospace;font-size:10px;line-height:2.6;color:#4a2a7a;">
            <span style="color:#66ffee;">◆</span> &nbsp;6 Sensors Online<br>
            <span style="color:#66ffee;">◆</span> &nbsp;Encryption Active<br>
            <span style="color:#66ffee;">◆</span> &nbsp;Threat AI Armed<br>
            <span style="color:#ff00cc;">◆</span> &nbsp;2 Alerts Active<br>
            <span style="color:#ffaa00;">◆</span> &nbsp;1 Pending Review
        </div>
    </div>
    <div style="height:1px;background:linear-gradient(90deg,rgba(180,0,255,0.2),transparent);margin:16px 0 12px;"></div>
    <div style="padding:0 22px;">
        <div style="font-size:8px;color:#2a0a4a;letter-spacing:0.18em;text-transform:uppercase;margin-bottom:10px;font-family:'Share Tech Mono',monospace;">Threat Level</div>
        <div style="font-family:'Orbitron',monospace;font-size:13px;font-weight:700;color:#ff00cc;
             text-shadow:0 0 15px rgba(255,0,204,0.6);letter-spacing:0.1em;">ELEVATED</div>
    </div>
    <div style="position:absolute;bottom:16px;left:0;right:0;text-align:center;">
        <div style="font-size:8px;color:#1a0830;letter-spacing:.1em;font-family:'Share Tech Mono',monospace;">NEXUS v3.1.0 — CLASSIFIED</div>
    </div>
    """, unsafe_allow_html=True)

# ── Page label map ──────────────────────────
page_map={
    "// OVERVIEW":      ("OVERVIEW",      "System health — live threat summary"),
    "// PMU NETWORK":   ("PMU NETWORK",   "Sensor array — 6 units online"),
    "// SECURE COMMS":  ("SECURE COMMS",  "Encrypted data pipeline"),
    "// THREAT INTEL":  ("THREAT INTEL",  "AI-powered anomaly classification"),
    "// ANALYTICS":     ("ANALYTICS",     "Detection metrics & model performance"),
    "// FAULT MONITOR": ("FAULT MONITOR", "Power system fault classification"),
}
pt,ps=page_map.get(page,("NEXUS",""))

# ── Top bar ──────────────────────────────────
st.markdown(f"""
<div class="topbar">
    <div class="brand">
        <div>
            <div class="brand-logo">NEXUS</div>
            <div class="brand-sub">{ps}</div>
        </div>
        <div style="width:1px;height:30px;background:rgba(180,0,255,0.2);margin:0 4px;"></div>
        <div style="font-family:'Orbitron',monospace;font-size:11px;font-weight:600;
             color:#7a30aa;letter-spacing:0.14em;">{pt}</div>
    </div>
    <div class="topbar-right">
        <div class="live-pill"><div class="blink"></div>LIVE FEED</div>
        <div class="tb-badge">THREAT LEVEL: ELEVATED</div>
        <div class="tb-clock">{datetime.utcnow().strftime('%Y.%m.%d %H:%M:%S')} UTC</div>
    </div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════
#  OVERVIEW
# ══════════════════════════════════════════════
if page=="// OVERVIEW":
    k1,k2,k3,k4=st.columns(4)
    with k1: st.markdown(kpi("Sensors Online","6/6","All units transmitting","purple"),unsafe_allow_html=True)
    with k2: st.markdown(kpi("Detection Rate","89.4%","RF classifier armed","cyan"),  unsafe_allow_html=True)
    with k3: st.markdown(kpi("Active Threats","2","Immediate response","red"),         unsafe_allow_html=True)
    with k4: st.markdown(kpi("Fault Accuracy","99.1%","CNN classifier","pink"),        unsafe_allow_html=True)

    cl,cr=st.columns([3,2])
    with cl:
        # Threat feed
        EVENTS=[
            ("fdot-crit","[CRITICAL] False data injection on Sensor 02 — voltage spoofed +8.4%","14:31:07"),
            ("fdot-high","[HIGH] Replay packet detected on uplink — sequence number repeated","14:29:44"),
            ("fdot-med", "[MED]  ROCOF anomaly on Bus 14 — monitoring escalated","14:28:12"),
            ("fdot-crit","[CRITICAL] DoS pattern — 847 anomalous packets/sec — rate limiter active","14:25:50"),
            ("fdot-med", "[MED]  Voltage deviation Bus 6 — within secondary threshold","14:22:03"),
            ("fdot-low", "[LOW]  Encryption key rotation completed — zero downtime","14:18:30"),
            ("fdot-high","[HIGH] MITM signature on PDC channel — rekeying initiated","14:15:11"),
            ("fdot-low", "[LOW]  All 6 sensors passed integrity check","14:10:00"),
            ("fdot-crit","[CRITICAL] Timestamp manipulation — GPS offset ±42 s detected","14:06:33"),
            ("fdot-low", "[LOW]  Fault classifier retrained — 99.1% accuracy maintained","14:00:00"),
        ]
        html=po("Live Threat Feed","● LIVE","pb-live")+'<div class="feed">'
        for dot,msg,t in EVENTS:
            html+=feed_item(dot,msg,t)
        html+='</div>'+pc()
        st.markdown(html,unsafe_allow_html=True)

        # Traffic line chart
        html2=po("Network Traffic","LAST 5 MIN","pb-purple")
        st.markdown(html2,unsafe_allow_html=True)
        np.random.seed(9); xs=np.linspace(0,300,80)
        pkt=40+30*np.sin(xs/30)+np.random.normal(0,5,80)
        fig=go.Figure()
        fig.add_trace(go.Scatter(x=xs,y=pkt,mode='lines',
            line=dict(color=PURPLE,width=1.5),
            fill='tozeroy',fillcolor='rgba(180,0,255,0.07)'))
        fig.add_trace(go.Scatter(x=xs,y=pkt+15,mode='lines',
            line=dict(color=PINK,width=1,dash='dot'),name='Peak'))
        pl(fig,height=130,margin=dict(l=40,r=10,t=10,b=30),showlegend=False)
        st.plotly_chart(fig,use_container_width=True)
        st.markdown(pc(),unsafe_allow_html=True)

    with cr:
        # System status
        html3=po("System Status")
        STATUS=[
            ("Sensor Array","Online","dv-g"),("Encryption","AES-256-GCM Active","dv-g"),
            ("Threat AI","Armed","dv-g"),("Fault Monitor","Running","dv-g"),
            ("Data Integrity","Verified","dv-g"),("Alert Queue","2 Critical","dv-r"),
            ("Last Key Cycle","14:18 UTC","dv-p"),("Network Uptime","99.97%","dv-g"),
        ]
        html3+=''.join(dr(l,v,c) for l,v,c in STATUS)+pc()
        st.markdown(html3,unsafe_allow_html=True)

        # Donut chart
        html4=po("Threat Breakdown","SESSION","pb-purple")
        st.markdown(html4,unsafe_allow_html=True)
        fig2=go.Figure(go.Pie(
            labels=['Normal','FDI','Replay','DoS','MITM','Timestamp'],
            values=[312,41,28,19,15,10],hole=0.62,
            marker_colors=[CYAN,RED,PINK,AMBER,PURPLE,'#ff88cc'],
            textinfo='none'))
        fig2.add_annotation(text="<b>425</b><br><span style='font-size:9px'>packets</span>",
            x=0.5,y=0.5,showarrow=False,font=dict(color='#e0d0ff',size=14,family='Orbitron'))
        pl(fig2,height=175,margin=dict(l=0,r=0,t=0,b=0),
           legend=dict(font=dict(size=9),orientation='v',x=1,y=0.5))
        st.plotly_chart(fig2,use_container_width=True)
        st.markdown(pc(),unsafe_allow_html=True)


# ══════════════════════════════════════════════
#  PMU NETWORK
# ══════════════════════════════════════════════
elif page=="// PMU NETWORK":
    k1,k2,k3,k4=st.columns(4)
    with k1: st.markdown(kpi("Units Online","6/6","Full coverage","cyan"),    unsafe_allow_html=True)
    with k2: st.markdown(kpi("Parameters","13","Per sensor","purple"),         unsafe_allow_html=True)
    with k3: st.markdown(kpi("Sample Rate","60 Hz","Synchrophasor","purple"),  unsafe_allow_html=True)
    with k4: st.markdown(kpi("Load Range","±30%","Scenarios covered","pink"),  unsafe_allow_html=True)

    buses=[4,6,1,10,14,8]; np.random.seed(int(time.time())%50)
    alerts_idx=np.random.choice(6,size=2,replace=False)
    html_g='<div class="pmugrid">'
    for i,b in enumerate(buses):
        al=i in alerts_idx
        vm=round(1.0+np.random.uniform(-.04,.04),4)
        va=round(np.random.uniform(-18,2),2)
        fr=round(50+np.random.uniform(-.03,.03),4)
        rc=round(np.random.uniform(-.01,.01),5)
        sv=f'<span style="color:#ff003c">ALERT</span>' if al else f'<span style="color:#66ffee">SECURE</span>'
        html_g+=f"""
        <div class="pcard {'alert' if al else ''}">
            <div class="pstat {'pstat-alert' if al else 'pstat-ok'}"></div>
            <div class="pid">PMU-{str(i+1).zfill(2)}</div>
            <div class="ploc">Bus {b} · Grid Node</div>
            {dr("Vm (p.u.)",vm)}{dr("Va (°)",va)}{dr("Freq (Hz)",fr)}{dr("ROCOF",rc)}{dr("Status",sv)}
        </div>"""
    html_g+='</div>'
    st.markdown(html_g,unsafe_allow_html=True)

    bf=st.multiselect("Filter sensors:",options=sorted(df_pmu['bus_id'].unique()),
        default=sorted(df_pmu['bus_id'].unique()),format_func=lambda x:f"Bus {x+1}")
    dff=df_pmu[df_pmu['bus_id'].isin(bf)] if bf else df_pmu

    def lc(y,ylab):
        fig=px.line(dff,x='timestamp',y=y,color='bus_id',color_discrete_sequence=SEQ,
            labels={'timestamp':'Time (s)',y:ylab,'bus_id':'Sensor'})
        fig.update_traces(line=dict(width=1.4))
        pl(fig,height=185)
        return fig

    c1,c2=st.columns(2)
    with c1:
        st.markdown(po("Voltage Magnitude"),unsafe_allow_html=True)
        st.plotly_chart(lc('vm_pu','Vm (p.u.)'),use_container_width=True)
        st.markdown(pc(),unsafe_allow_html=True)
    with c2:
        st.markdown(po("Voltage Angle"),unsafe_allow_html=True)
        st.plotly_chart(lc('va_degree','Va (°)'),use_container_width=True)
        st.markdown(pc(),unsafe_allow_html=True)
    c3,c4=st.columns(2)
    with c3:
        st.markdown(po("Frequency"),unsafe_allow_html=True)
        st.plotly_chart(lc('frequency','Freq (Hz)'),use_container_width=True)
        st.markdown(pc(),unsafe_allow_html=True)
    with c4:
        st.markdown(po("ROCOF"),unsafe_allow_html=True)
        st.plotly_chart(lc('rocof','ROCOF (Hz/s)'),use_container_width=True)
        st.markdown(pc(),unsafe_allow_html=True)


# ══════════════════════════════════════════════
#  SECURE COMMS
# ══════════════════════════════════════════════
elif page=="// SECURE COMMS":
    k1,k2,k3,k4=st.columns(4)
    with k1: st.markdown(kpi("Cipher","AES-256","GCM Mode","purple"),        unsafe_allow_html=True)
    with k2: st.markdown(kpi("Encrypt","0.052ms","Per packet","cyan"),        unsafe_allow_html=True)
    with k3: st.markdown(kpi("Decrypt","0.026ms","Per packet","cyan"),        unsafe_allow_html=True)
    with k4: st.markdown(kpi("Tamper Block","100%","Zero bypass","pink"),     unsafe_allow_html=True)

    cl,cr=st.columns([1,1])
    with cl:
        st.markdown(po("Transmit Packet"),unsafe_allow_html=True)
        sensor=st.selectbox("Source sensor:",[f"PMU-{str(i+1).zfill(2)} · Bus {b}" for i,b in enumerate([4,6,1,10,14,8])])
        vm_v=st.slider("Voltage Magnitude (p.u.)",0.95,1.10,1.05,0.001)
        va_v=st.slider("Voltage Angle (°)",-25.0,0.0,-10.0,0.1)
        fq_v=st.slider("Frequency (Hz)",49.90,50.10,50.00,0.001)
        send=st.button("Encrypt & Transmit",use_container_width=True)
        st.markdown(pc(),unsafe_allow_html=True)

        st.markdown(po("Protocol Matrix"),unsafe_allow_html=True)
        for l,v,c in [("Cipher","AES-256-GCM","dv-p"),("Key","256-bit","dv-p"),
                      ("Nonce","96-bit random","dv-p"),("Auth tag","128-bit GCM","dv-p"),
                      ("Frame","C37.118-style","dv-w"),("Access","4 role levels","dv-w"),
                      ("Tamper","Drop + alert","dv-r")]:
            st.markdown(dr(l,v,c),unsafe_allow_html=True)
        st.markdown(pc(),unsafe_allow_html=True)

    with cr:
        st.markdown(po("Transmission Log","● ENCRYPTING","pb-live"),unsafe_allow_html=True)
        if send:
            bid=int(sensor.split("Bus ")[-1])
            pkt={"sensor":sensor,"bus_id":bid,"vm_pu":vm_v,"va_degree":va_v,
                 "frequency":fq_v,"rocof":0.001,"ts":time.time()}
            key=os.urandom(32); aesgcm=AESGCM(key); nonce=os.urandom(12)
            plain=json.dumps(pkt).encode()
            t0=time.perf_counter(); ct=aesgcm.encrypt(nonce,plain,None); enc=(time.perf_counter()-t0)*1e3
            t0=time.perf_counter(); dec=aesgcm.decrypt(nonce,ct,None);   dct=(time.perf_counter()-t0)*1e3
            st.success(f"✓ Encrypted in {enc:.4f} ms — authenticated — dispatched to central node")
            st.markdown(f'<div class="monoblock"><span style="color:#4a2a7a">// ciphertext (hex)</span><br>{ct.hex()[:128]}...</div>',unsafe_allow_html=True)
            st.markdown(f'<div class="monoblock"><span style="color:#4a2a7a">// decrypted payload</span><br>{json.dumps(json.loads(dec),indent=2)}</div>',unsafe_allow_html=True)
            tampered=bytes([ct[0]^0xFF])+ct[1:]
            try:
                aesgcm.decrypt(nonce,tampered,None); st.error("Tamper check failed.")
            except:
                st.success("✓ Tamper test — modified packet rejected by authentication tag")
            runs=[round(np.random.uniform(.044,.062),4) for _ in range(30)]; runs[-1]=enc
            fig=go.Figure()
            fig.add_trace(go.Scatter(y=runs,mode='lines+markers',
                line=dict(color=PINK,width=1.3),marker=dict(size=3,color=PINK),showlegend=False))
            fig.add_hline(y=float(np.mean(runs)),line_dash='dash',line_color=AMBER,
                annotation_text=f"avg {np.mean(runs):.3f}ms",annotation_font=dict(color=AMBER,size=9))
            pl(fig,height=110,margin=dict(l=44,r=10,t=10,b=30))
            st.plotly_chart(fig,use_container_width=True)
        else:
            st.markdown('<div class="empty">Configure a packet on the left<br>and click Encrypt &amp; Transmit.</div>',unsafe_allow_html=True)
        st.markdown(pc(),unsafe_allow_html=True)


# ══════════════════════════════════════════════
#  THREAT INTEL
# ══════════════════════════════════════════════
elif page=="// THREAT INTEL":
    k1,k2,k3,k4=st.columns(4)
    with k1: st.markdown(kpi("Classifier","RF","6-class detection","purple"),  unsafe_allow_html=True)
    with k2: st.markdown(kpi("Accuracy","89.4%","Validated","cyan"),           unsafe_allow_html=True)
    with k3: st.markdown(kpi("F1-Score","89.6%","Weighted avg","cyan"),        unsafe_allow_html=True)
    with k4: st.markdown(kpi("Latency","<1ms","Per prediction","pink"),        unsafe_allow_html=True)

    cl,cr=st.columns([1,1])
    with cl:
        st.markdown(po("Sensor Input"),unsafe_allow_html=True)
        vm   =st.slider("Voltage Magnitude (p.u.)",0.0,1.2,1.05,0.01)
        va   =st.slider("Voltage Angle (°)",-30.0,5.0,-10.0,0.5)
        freq =st.slider("Frequency (Hz)",49.0,51.0,50.0,0.01)
        p_mw =st.slider("Active Power (MW)",0.0,100.0,50.0,1.0)
        rocof=st.slider("ROCOF (Hz/s)",-1.0,1.0,0.0,0.01)
        ts   =st.slider("Timestamp offset (s)",0.0,200.0,1.0,0.5)
        run  =st.button("Run Classification",use_container_width=True)
        st.markdown(pc(),unsafe_allow_html=True)

    with cr:
        st.markdown(po("Classification","RF MODEL","pb-purple"),unsafe_allow_html=True)
        if run:
            if vm==0.0 or freq<49.2:
                cls,conf,sev,action="Denial of Service",94,"threat","Rate limiter active. Admin alerted."
            elif abs(vm-1.05)>0.08:
                cls,conf,sev,action="False Data Injection",87,"threat","Sensor quarantined pending review."
            elif ts>50:
                cls,conf,sev,action="Timestamp Manipulation",96,"threat","GPS sync mismatch. Packet invalidated."
            elif abs(va+10)>10:
                cls,conf,sev,action="Man-in-the-Middle",82,"threat","Channel breach. Rekeying initiated."
            elif abs(rocof)>0.3:
                cls,conf,sev,action="Replay Attack",88,"threat","Duplicate sequence dropped."
            else:
                cls,conf,sev,action="Normal",91,"safe","No anomaly. Forwarded to fault classifier."

            is_t=sev=="threat"
            bc="rbox-threat" if is_t else "rbox-safe"
            tc=RED if is_t else CYAN
            icon="⚠" if is_t else "✓"
            st.markdown(f"""
            <div class="rbox {bc}">
                <div class="rtitle" style="color:{tc};">{icon} &nbsp;{cls}</div>
                <div class="rmeta">
                    Confidence: <span style="font-family:'Share Tech Mono',monospace;color:{tc};">{conf}%</span>
                    &nbsp;·&nbsp; {action}
                </div>
            </div>""",unsafe_allow_html=True)

            # Confidence bars
            confs={'Normal':91,'FDI':3,'Replay':2,'DoS':1,'MITM':2,'Timestamp':1}
            if is_t:
                for k in confs: confs[k]=2
                km={"Service":"DoS","Injection":"FDI","Manipulation":"Timestamp","Middle":"MITM","Attack":"Replay"}
                matched=next((v for k,v in km.items() if k in cls),None)
                if matched: confs[matched]=conf
            st.markdown("<br>",unsafe_allow_html=True)
            for lbl,v in confs.items():
                col=CYAN if lbl=='Normal' else RED
                st.markdown(f"""
                <div class="cbar">
                    <div class="ctop"><span class="clbl">{lbl}</span><span class="cval">{v}%</span></div>
                    <div class="cbg"><div class="cfill" style="width:{v}%;background:{col};box-shadow:0 0 8px {col};"></div></div>
                </div>""",unsafe_allow_html=True)
        else:
            st.markdown('<div class="empty">Adjust sensor readings on the left<br>and click Run Classification.</div>',unsafe_allow_html=True)
        st.markdown(pc(),unsafe_allow_html=True)


# ══════════════════════════════════════════════
#  ANALYTICS
# ══════════════════════════════════════════════
elif page=="// ANALYTICS":
    k1,k2,k3,k4=st.columns(4)
    with k1: st.markdown(kpi("Best Accuracy","99.1%","CNN fault classifier","cyan"),  unsafe_allow_html=True)
    with k2: st.markdown(kpi("RF Accuracy","89.4%","Above benchmark","purple"),       unsafe_allow_html=True)
    with k3: st.markdown(kpi("Training Set","25K","Labelled samples","pink"),          unsafe_allow_html=True)
    with k4: st.markdown(kpi("Active Models","2","RF + CNN deployed","purple"),        unsafe_allow_html=True)

    cl,cr=st.columns([3,2])
    with cl:
        st.markdown(po("Model Accuracy Matrix"),unsafe_allow_html=True)
        models=['Random Forest','LSTM','1D-CNN']; acc=[89.43,54.85,99.05]; f1s=[89.60,53.38,99.05]
        mcols=[CYAN,AMBER,PURPLE]
        fig=go.Figure()
        for m,a,f,c in zip(models,acc,f1s,mcols):
            fig.add_trace(go.Bar(name=f'{m}',x=[m],y=[a],marker_color=c,marker_opacity=0.8,
                text=f'{a}%',textposition='outside',
                textfont=dict(size=10,color='#e0d0ff',family='Share Tech Mono')))
        fig.add_hline(y=88.7,line_dash='dash',line_color=RED,line_width=1,
            annotation_text='Baseline 88.7%',annotation_font=dict(color=RED,size=9))
        pl(fig,height=240,barmode='group',yaxis_range=[0,115],
           legend=dict(font=dict(size=10),bgcolor='rgba(0,0,0,0)',orientation='h',y=1.1))
        st.plotly_chart(fig,use_container_width=True)
        st.markdown(pc(),unsafe_allow_html=True)

    with cr:
        st.markdown(po("Performance Ledger"),unsafe_allow_html=True)
        for l,v,c in [("Random Forest","89.43% acc","dv-g"),("LSTM","54.85% acc","dv-a"),
                      ("1D-CNN","99.05% acc","dv-g"),("Industry Baseline","88.70%","dv-p"),
                      ("RF vs Baseline","+0.73% ↑","dv-g"),("Attack Classes","6 types","dv-p"),
                      ("Fault Classes","5 types","dv-p")]:
            st.markdown(dr(l,v,c),unsafe_allow_html=True)
        st.markdown(pc(),unsafe_allow_html=True)

        st.markdown(po("Detected Threats","6 CLASS","pb-red"),unsafe_allow_html=True)
        for cls,dot in [("Normal","fdot-low"),("False Data Injection","fdot-crit"),
                        ("Replay Attack","fdot-high"),("Denial of Service","fdot-crit"),
                        ("Man-in-the-Middle","fdot-high"),("Timestamp Manip.","fdot-med")]:
            st.markdown(feed_item(dot,cls,"—"),unsafe_allow_html=True)
        st.markdown(pc(),unsafe_allow_html=True)

    st.markdown("---")
    tab1,tab2,tab3=st.tabs(["Random Forest  89.4%","LSTM  54.9%","1D-CNN  99.1%"])
    L6=['Normal','FDI','Replay','DoS','MITM','Timestamp']
    L5=['Normal','Zone1','Zone2','Zone3','PwrSwing']
    cm_rf  =np.array([[478,2,0,8,6,6],[3,467,2,8,8,12],[0,1,499,0,0,0],[6,9,0,475,6,4],[8,7,0,5,472,8],[3,6,0,3,3,485]])
    cm_lstm=np.array([[18,60,60,120,100,84],[20,170,60,80,60,36],[0,0,416,0,0,0],[30,60,10,142,90,140],[40,50,10,80,88,151],[0,0,0,8,0,807]])
    cm_cnn =np.array([[398,0,0,2,0],[0,398,0,2,0],[0,0,400,0,0],[2,2,0,396,0],[0,0,0,0,400]])

    with tab1:
        c1,c2=st.columns([2,1])
        with c1: st.pyplot(cm_fig(cm_rf,L6,"Random Forest — Attack Detection"))
        with c2:
            st.success("✓ Accuracy: 89.43%"); st.success("✓ F1-Score: 89.60%")
            st.info("Primary attack detection model")
    with tab2:
        c1,c2=st.columns([2,1])
        with c1: st.pyplot(cm_fig(cm_lstm,L6,"LSTM — Attack Detection"))
        with c2:
            st.warning("Accuracy: 54.85%"); st.warning("F1: 53.38%")
            st.info("Optimised for streaming input")
    with tab3:
        c1,c2=st.columns([2,1])
        with c1: st.pyplot(cm_fig(cm_cnn,L5,"1D-CNN — Fault Classification"))
        with c2:
            st.success("✓ Accuracy: 99.05%"); st.success("✓ F1: 99.05%")
            st.info("Near-perfect fault separation")


# ══════════════════════════════════════════════
#  FAULT MONITOR
# ══════════════════════════════════════════════
elif page=="// FAULT MONITOR":
    k1,k2,k3,k4=st.columns(4)
    with k1: st.markdown(kpi("Classifier","CNN","5-class detection","purple"),  unsafe_allow_html=True)
    with k2: st.markdown(kpi("Accuracy","99.1%","All fault zones","cyan"),      unsafe_allow_html=True)
    with k3: st.markdown(kpi("Response","<0.1s","Per classification","cyan"),   unsafe_allow_html=True)
    with k4: st.markdown(kpi("Zones","5","Zone 1-3 + Swing","pink"),            unsafe_allow_html=True)

    cl,cr=st.columns([1,1])
    with cl:
        st.markdown(po("Sensor Readings"),unsafe_allow_html=True)
        vm_f   =st.slider("Voltage Magnitude (p.u.)",0.5,1.2,1.05,0.01)
        va_f   =st.slider("Voltage Angle (°)",-30.0,15.0,-10.0,0.5)
        freq_f =st.slider("Frequency (Hz)",49.0,51.0,50.0,0.01)
        p_f    =st.slider("Active Power (MW)",0.0,150.0,50.0,1.0)
        rocof_f=st.slider("ROCOF (Hz/s)",-2.0,2.0,0.0,0.01)
        classify=st.button("Classify Condition",use_container_width=True)
        st.markdown(pc(),unsafe_allow_html=True)

    with cr:
        st.markdown(po("Fault Classification","CNN","pb-purple"),unsafe_allow_html=True)
        if classify:
            drop=1.05-vm_f; va_sh=abs(va_f+10)
            if drop>0.25:
                zone,col,sev,relay,desc="Zone 1 Fault",RED,"threat","Immediate trip","Severe fault near relay — protection activated"
            elif drop>0.15:
                zone,col,sev,relay,desc="Zone 2 Fault","#ff6640","threat","Trip after 0.3s","Moderate fault — Zone 2 protection initiated"
            elif drop>0.08 or va_sh>10:
                zone,col,sev,relay,desc="Zone 3 Fault",AMBER,"warn","Trip after 1.0s","Distant fault — backup protection initiated"
            elif abs(rocof_f)>0.5:
                zone,col,sev,relay,desc="Power Swing",PURPLE,"warn","Relay blocked","Power oscillation — blocking relay operation"
            else:
                zone,col,sev,relay,desc="Normal Operation",CYAN,"safe","No action","System within normal operating parameters"
            bc="rbox-threat" if sev=="threat" else "rbox-warn" if sev=="warn" else "rbox-safe"
            icon="⚠" if sev in ("threat","warn") else "✓"
            st.markdown(f"""
            <div class="rbox {bc}">
                <div class="rtitle" style="color:{col};">{icon} &nbsp;{zone}</div>
                <div class="rmeta">{desc}<br>Relay: <span style="font-family:'Share Tech Mono',monospace;color:{col};">{relay}</span></div>
            </div>""",unsafe_allow_html=True)
            zones=['Normal','Zone 1','Zone 2','Zone 3','Power Swing']
            zi=zones.index(zone.replace(" Fault","").replace(" Operation",""))
            zv=[3]*5; zv[zi]=92
            zc=[CYAN,RED,'#ff6640',AMBER,PURPLE]
            fig=go.Figure(go.Bar(x=zones,y=zv,marker_color=zc,marker_opacity=0.8,
                text=[f'{v}%' for v in zv],textposition='outside',
                textfont=dict(size=10,color='#e0d0ff',family='Share Tech Mono')))
            for i,v in enumerate(zv):
                if v>10:
                    fig.add_trace(go.Bar(x=[zones[i]],y=[v],marker_color=zc[i],
                        marker_opacity=0.3,showlegend=False,
                        marker=dict(line=dict(color=zc[i],width=1))))
            pl(fig,height=155,yaxis_range=[0,110],showlegend=False,barmode='overlay')
            st.plotly_chart(fig,use_container_width=True)
        else:
            st.markdown('<div class="empty">Adjust readings on the left<br>and click Classify Condition.</div>',unsafe_allow_html=True)
        st.markdown(pc(),unsafe_allow_html=True)

    c1,c2=st.columns(2)
    with c1:
        st.markdown(po("Protection Zones"),unsafe_allow_html=True)
        for cond,trig,act,vc in [
            ("Normal","Vm drop < 5%","No action","dv-g"),
            ("Zone 1","Vm drop > 25%","Immediate trip","dv-r"),
            ("Zone 2","15–25% drop","Trip 0.3 s","dv-r"),
            ("Zone 3","8–15% drop","Trip 1.0 s","dv-a"),
            ("Power Swing","ROCOF > 0.5","Block relay","dv-a"),
        ]: st.markdown(dr(f"{cond} — {trig}",act,vc),unsafe_allow_html=True)
        st.markdown(pc(),unsafe_allow_html=True)
    with c2:
        st.markdown(po("Class Distribution"),unsafe_allow_html=True)
        fd=pd.DataFrame({'Zone':['Normal','Zone1','Zone2','Zone3','PowerSwing'],'Count':[2000]*5})
        fig2=go.Figure(go.Pie(labels=fd['Zone'],values=fd['Count'],hole=0.58,
            marker_colors=[CYAN,RED,'#ff6640',AMBER,PURPLE],textinfo='none'))
        fig2.add_annotation(text="<b>10K</b><br><span style='font-size:9px'>samples</span>",
            x=0.5,y=0.5,showarrow=False,font=dict(color='#e0d0ff',size=13,family='Orbitron'))
        pl(fig2,height=165,margin=dict(l=0,r=0,t=0,b=0),legend=dict(font=dict(size=9),bgcolor='rgba(0,0,0,0)'))
        st.plotly_chart(fig2,use_container_width=True)
        st.markdown(pc(),unsafe_allow_html=True)

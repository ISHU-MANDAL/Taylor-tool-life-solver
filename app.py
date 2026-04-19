"""
Taylor's Tool Life Equation Solver
====================================
Professional engineering calculator with animated background,
per-module documentation, session logging, and a conclusion page.

Taylor's Equation:  V · T^n = C
Extended Equation:  V · T^n · f^x · d^y = C_ext
"""

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from datetime import datetime

# ─────────────────────────────────────────────
#  Page configuration
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Taylor Tool Life Solver",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
#  Session state — calculation log
# ─────────────────────────────────────────────
if "calc_log" not in st.session_state:
    st.session_state.calc_log = []

def log_result(module_name, inputs: dict, outputs: dict, conclusion: str):
    st.session_state.calc_log.append({
        "module": module_name,
        "time": datetime.now().strftime("%H:%M:%S"),
        "inputs": inputs,
        "outputs": outputs,
        "conclusion": conclusion,
    })

# ─────────────────────────────────────────────
#  Background animation + global styles
# ─────────────────────────────────────────────
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Barlow:wght@400;500;600;700&family=Barlow+Condensed:wght@600;700&display=swap" rel="stylesheet">

<style>
/* ─── App reset ─────────────────────────────── */
.stApp { background: transparent !important; font-family: 'Barlow', sans-serif; }
section[data-testid="stSidebar"] { background: #0d1f35 !important; }
section[data-testid="stSidebar"] * { color: #a8c4e0 !important; }

/* ─── Fixed background ──────────────────────── */
.eng-bg {
    position: fixed; top: 0; left: 0;
    width: 100vw; height: 100vh;
    background: #edf1f7;
    z-index: -20;
    pointer-events: none;
    overflow: hidden;
}
.eng-bg::before {
    content: '';
    position: absolute; inset: 0;
    background-image: radial-gradient(circle, rgba(44,123,229,0.18) 1.5px, transparent 1.5px);
    background-size: 38px 38px;
}
.eng-bg::after {
    content: '';
    position: absolute; inset: 0;
    background-image:
        linear-gradient(rgba(44,123,229,0.04) 1px, transparent 1px),
        linear-gradient(90deg, rgba(44,123,229,0.04) 1px, transparent 1px);
    background-size: 76px 76px;
}

/* ─── Scanning line ─────────────────────────── */
@keyframes scan-down {
    0%   { top: -3px; opacity: 0; }
    5%   { opacity: 1; }
    95%  { opacity: 0.6; }
    100% { top: 100vh; opacity: 0; }
}
.scan-line {
    position: fixed; left: 0; width: 100%; height: 2px;
    background: linear-gradient(90deg, transparent 0%, rgba(44,123,229,0.25) 30%,
                rgba(44,123,229,0.55) 50%, rgba(44,123,229,0.25) 70%, transparent 100%);
    animation: scan-down 9s ease-in-out infinite;
    pointer-events: none; z-index: -1;
}

/* ─── Gears ─────────────────────────────────── */
@keyframes spin-cw  { to { transform: rotate(360deg);  } }
@keyframes spin-ccw { to { transform: rotate(-360deg); } }

.gear-wrap { position: fixed; pointer-events: none; z-index: -1; }
.gear-ring {
    border-radius: 50%;
    border: 2px solid rgba(44,123,229,0.18);
    animation: spin-cw 28s linear infinite;
    position: relative;
}
.gear-ring::before {
    content: ''; position: absolute;
    border-radius: 50%;
    border: 1px dashed rgba(44,123,229,0.12);
    animation: spin-ccw 18s linear infinite;
    inset: 10px;
}
.gear-ring::after {
    content: ''; position: absolute;
    border-radius: 50%;
    border: 1px solid rgba(44,123,229,0.08);
    inset: 20px;
    animation: spin-cw 12s linear infinite;
}

/* ─── Chip particles ────────────────────────── */
@keyframes chip-rise {
    0%   { transform: translate(0,0) rotate(0deg);   opacity: 0; }
    8%   { opacity: 0.75; }
    88%  { opacity: 0.4; }
    100% { transform: translate(var(--tx),var(--ty)) rotate(var(--rot)); opacity: 0; }
}
.chip {
    position: fixed;
    animation: chip-rise linear infinite;
    pointer-events: none; z-index: -1; opacity: 0;
    border-radius: 1px;
}

/* ─── Pulsing dots ──────────────────────────── */
@keyframes pulse-dot {
    0%, 100% { transform: scale(1);   opacity: 0.5; }
    50%       { transform: scale(1.7); opacity: 1;   }
}
.corner-dot {
    position: fixed; width: 6px; height: 6px;
    background: #2c7be5; border-radius: 50%;
    animation: pulse-dot 3s ease-in-out infinite;
    pointer-events: none; z-index: -1;
}

/* ─── Cards ─────────────────────────────────── */
.calc-card {
    background: #ffffff;
    border: 1px solid #d0dce8; border-radius: 8px;
    padding: 22px 26px; margin-bottom: 16px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}
.module-info-card {
    background: linear-gradient(135deg, #0d1f35 0%, #1a3a5c 100%);
    border: 1px solid #2c7be5; border-left: 4px solid #2c7be5;
    border-radius: 8px; padding: 20px 24px; margin-bottom: 22px;
}
.module-info-card h4 {
    margin: 0 0 10px 0;
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 1.15rem; letter-spacing: 0.05em;
    color: #7ec8ff; text-transform: uppercase;
}
.module-info-card p { margin: 4px 0; font-size: 0.88rem; line-height: 1.5; color: #c8e0f8; }
.info-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-top: 12px; }
.info-col  { background: rgba(255,255,255,0.06); border-radius: 5px; padding: 10px 14px; }
.info-col strong { display: block; font-size: 0.76rem; letter-spacing: 0.08em;
                   text-transform: uppercase; color: #4db8ff; margin-bottom: 5px; }
.info-col span { font-size: 0.84rem; color: #c0d8f0; line-height: 1.6; }

/* ─── Section titles ────────────────────────── */
.section-title {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 1rem; font-weight: 700; letter-spacing: 0.04em;
    color: #0d1f35; border-bottom: 2px solid #2c7be5;
    padding-bottom: 5px; margin-bottom: 14px; text-transform: uppercase;
}

/* ─── Page title ────────────────────────────── */
.page-title {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 2rem; font-weight: 700;
    color: #0d1f35; letter-spacing: 0.02em; margin-bottom: 2px;
}
.page-subtitle { font-size: 0.9rem; color: #5a7a9a; margin-bottom: 20px; }

/* ─── Formula box ───────────────────────────── */
.formula-box {
    background: #0d1f35; border: 1px solid #2c7be5; border-radius: 6px;
    padding: 10px 16px;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.95rem; color: #7ec8ff; margin-bottom: 16px; letter-spacing: 0.03em;
}

/* ─── Result / error / info boxes ──────────── */
.result-box {
    background: #f0f7ff; border-left: 4px solid #2c7be5; border-radius: 5px;
    padding: 14px 18px; margin-top: 14px;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.88rem; color: #0d2540; white-space: pre-wrap; line-height: 1.7;
}
.error-box {
    background: #fff0f0; border-left: 4px solid #d9534f; border-radius: 5px;
    padding: 12px 16px; margin-top: 12px; color: #a02020; font-size: 0.88rem;
}
.info-box {
    background: #f0fbf3; border-left: 4px solid #3cb371; border-radius: 5px;
    padding: 11px 15px; margin-top: 10px; font-size: 0.88rem; color: #1d5e30;
}

/* ─── Conclusion page ───────────────────────── */
.concl-header {
    background: linear-gradient(135deg, #0d1f35, #1a3a5c);
    border-radius: 8px; padding: 20px 26px; margin-bottom: 18px;
}
.concl-header h2 {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 1.5rem; letter-spacing: 0.04em;
    color: #7ec8ff; margin: 0 0 6px 0;
}
.log-entry {
    background: #fff; border: 1px solid #d0dce8; border-left: 4px solid #2c7be5;
    border-radius: 6px; padding: 16px 20px; margin-bottom: 14px;
}
.le-header {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 1.05rem; font-weight: 700; color: #0d1f35; margin-bottom: 8px;
}
.le-time { font-size: 0.75rem; color: #8aadcc; float: right; }
.log-kv { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-top: 8px; }
.log-kv-col { background: #f4f8ff; border-radius: 4px; padding: 8px 12px; }
.log-kv-col strong { display: block; font-size: 0.74rem; text-transform: uppercase;
                     letter-spacing: 0.07em; color: #2c7be5; margin-bottom: 3px; }
.log-kv-col span { font-family: 'Share Tech Mono', monospace; font-size: 0.82rem; color: #1a2e42; }
.concl-text {
    margin-top: 10px; background: #f0f7ff; border-radius: 4px;
    padding: 9px 12px; font-size: 0.85rem; color: #1a3a5c; font-style: italic;
}
.empty-state {
    text-align: center; padding: 52px; color: #8aadcc;
    font-family: 'Barlow Condensed', sans-serif; font-size: 1.1rem; letter-spacing: 0.05em;
}

/* ─── Buttons ───────────────────────────────── */
.stButton > button {
    background: #2c7be5 !important; color: #fff !important;
    border: none !important; border-radius: 5px !important;
    padding: 8px 22px !important; font-weight: 600 !important;
    font-family: 'Barlow', sans-serif !important;
    font-size: 0.88rem !important; letter-spacing: 0.03em !important;
}
.stButton > button:hover { background: #1a62c4 !important; }

/* ─── Input labels ──────────────────────────── */
label { font-size: 0.85rem !important; font-weight: 500 !important; color: #2a3f55 !important; }

/* ─── Data table ────────────────────────────── */
.data-table { width:100%; border-collapse:collapse; font-size:0.88rem; margin-top:8px; }
.data-table th { background:#2c7be5; color:#fff; padding:8px 12px; text-align:center; }
.data-table td { padding:6px 12px; border-bottom:1px solid #e0ebf4; text-align:center; }
.data-table tr:nth-child(even) td { background:#f4f8ff; }
hr { border-color: #ccd8e8 !important; }
</style>

<!-- Background DOM -->
<div class="eng-bg"></div>
<div class="scan-line"></div>

<!-- Rotating gears in corners -->
<div class="gear-wrap" style="top:-30px;left:-30px;">
  <div class="gear-ring" style="width:140px;height:140px;"></div>
</div>
<div class="gear-wrap" style="bottom:-30px;right:-30px;">
  <div class="gear-ring" style="width:100px;height:100px;animation-direction:reverse;"></div>
</div>
<div class="gear-wrap" style="top:120px;right:-20px;">
  <div class="gear-ring" style="width:60px;height:60px;animation-duration:20s;"></div>
</div>

<!-- Pulsing corner accent dots -->
<div class="corner-dot" style="top:12px;left:12px;animation-delay:0s;"></div>
<div class="corner-dot" style="top:12px;right:12px;animation-delay:1s;background:#e8820c;"></div>
<div class="corner-dot" style="bottom:12px;left:12px;animation-delay:2s;background:#3cb371;"></div>
<div class="corner-dot" style="bottom:12px;right:12px;animation-delay:0.5s;"></div>

<!-- 24 floating metal chip particles -->
<div class="chip" style="width:7px;height:2px;background:rgba(44,123,229,0.45);left:5%;top:92%;--tx:-28px;--ty:-480px;--rot:720deg;animation-duration:13s;animation-delay:0s;"></div>
<div class="chip" style="width:4px;height:2px;background:rgba(160,185,210,0.55);left:12%;top:88%;--tx:22px;--ty:-520px;--rot:-540deg;animation-duration:10s;animation-delay:1.8s;"></div>
<div class="chip" style="width:9px;height:2px;background:rgba(44,123,229,0.35);left:22%;top:94%;--tx:-18px;--ty:-460px;--rot:360deg;animation-duration:12s;animation-delay:3.2s;"></div>
<div class="chip" style="width:3px;height:3px;background:rgba(232,130,12,0.45);border-radius:50%;left:31%;top:89%;--tx:38px;--ty:-400px;--rot:180deg;animation-duration:9s;animation-delay:0.6s;"></div>
<div class="chip" style="width:6px;height:2px;background:rgba(100,160,230,0.5);left:42%;top:96%;--tx:-22px;--ty:-540px;--rot:900deg;animation-duration:14s;animation-delay:2.4s;"></div>
<div class="chip" style="width:8px;height:2px;background:rgba(140,175,215,0.5);left:53%;top:91%;--tx:32px;--ty:-450px;--rot:-720deg;animation-duration:11s;animation-delay:4.1s;"></div>
<div class="chip" style="width:4px;height:4px;background:rgba(232,130,12,0.35);border-radius:50%;left:61%;top:94%;--tx:-12px;--ty:-510px;--rot:1080deg;animation-duration:10.5s;animation-delay:1.1s;"></div>
<div class="chip" style="width:6px;height:2px;background:rgba(44,123,229,0.4);left:71%;top:87%;--tx:42px;--ty:-420px;--rot:-360deg;animation-duration:12.5s;animation-delay:3.7s;"></div>
<div class="chip" style="width:3px;height:2px;background:rgba(180,205,230,0.6);left:80%;top:92%;--tx:-18px;--ty:-470px;--rot:540deg;animation-duration:9.5s;animation-delay:0.9s;"></div>
<div class="chip" style="width:10px;height:2px;background:rgba(44,100,200,0.35);left:88%;top:85%;--tx:12px;--ty:-500px;--rot:-1080deg;animation-duration:15s;animation-delay:2.7s;"></div>
<div class="chip" style="width:5px;height:2px;background:rgba(200,215,230,0.5);left:17%;top:55%;--tx:-32px;--ty:-310px;--rot:720deg;animation-duration:11s;animation-delay:6.5s;"></div>
<div class="chip" style="width:4px;height:2px;background:rgba(44,123,229,0.4);left:38%;top:48%;--tx:27px;--ty:-260px;--rot:-360deg;animation-duration:8s;animation-delay:5.2s;"></div>
<div class="chip" style="width:6px;height:2px;background:rgba(160,195,230,0.45);left:63%;top:52%;--tx:-14px;--ty:-290px;--rot:540deg;animation-duration:9s;animation-delay:7.3s;"></div>
<div class="chip" style="width:3px;height:3px;background:rgba(60,179,113,0.4);border-radius:50%;left:76%;top:58%;--tx:28px;--ty:-330px;--rot:1080deg;animation-duration:8.5s;animation-delay:4.8s;"></div>
<div class="chip" style="width:5px;height:2px;background:rgba(44,123,229,0.35);left:91%;top:72%;--tx:-38px;--ty:-360px;--rot:-720deg;animation-duration:13s;animation-delay:1.4s;"></div>
<div class="chip" style="width:7px;height:2px;background:rgba(180,210,240,0.4);left:6%;top:62%;--tx:16px;--ty:-410px;--rot:360deg;animation-duration:12s;animation-delay:8.2s;"></div>
<div class="chip" style="width:4px;height:2px;background:rgba(232,130,12,0.3);left:28%;top:74%;--tx:-26px;--ty:-370px;--rot:-540deg;animation-duration:10s;animation-delay:6.8s;"></div>
<div class="chip" style="width:6px;height:2px;background:rgba(140,180,220,0.5);left:47%;top:68%;--tx:19px;--ty:-320px;--rot:720deg;animation-duration:11.5s;animation-delay:4.0s;"></div>
<div class="chip" style="width:3px;height:3px;background:rgba(44,123,229,0.4);border-radius:50%;left:68%;top:76%;--tx:-22px;--ty:-390px;--rot:900deg;animation-duration:9s;animation-delay:2.5s;"></div>
<div class="chip" style="width:8px;height:2px;background:rgba(100,160,230,0.4);left:84%;top:35%;--tx:32px;--ty:-210px;--rot:-360deg;animation-duration:8s;animation-delay:9.2s;"></div>
<div class="chip" style="width:5px;height:2px;background:rgba(220,232,245,0.55);left:95%;top:50%;--tx:-20px;--ty:-280px;--rot:540deg;animation-duration:10s;animation-delay:3.0s;"></div>
<div class="chip" style="width:4px;height:2px;background:rgba(44,123,229,0.3);left:3%;top:30%;--tx:15px;--ty:-200px;--rot:-720deg;animation-duration:7.5s;animation-delay:10s;"></div>
<div class="chip" style="width:6px;height:2px;background:rgba(232,130,12,0.35);left:55%;top:25%;--tx:-18px;--ty:-180px;--rot:360deg;animation-duration:6.5s;animation-delay:11s;"></div>
<div class="chip" style="width:3px;height:3px;background:rgba(60,179,113,0.35);border-radius:50%;left:74%;top:18%;--tx:25px;--ty:-150px;--rot:1080deg;animation-duration:7s;animation-delay:8.5s;"></div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  Core calculation functions
# ─────────────────────────────────────────────

def taylor_constant(V, T, n):
    """C = V * T^n"""
    return V * (T ** n)

def tool_life_from_C(V, C, n):
    """T = (C / V)^(1/n)"""
    return (C / V) ** (1.0 / n)

def cutting_speed_from_C(T, C, n):
    """V = C / T^n"""
    return C / (T ** n)

def find_n_and_C(speeds, lives):
    """Fit Taylor's equation via log-log regression. Returns (n, C, R²)."""
    log_T = np.log(np.array(lives))
    log_V = np.log(np.array(speeds))
    coeffs = np.polyfit(log_T, log_V, 1)
    b, a = coeffs   # slope=-n, intercept=log(C)
    n_fit = -b
    C_fit = np.exp(a)
    y_hat  = np.polyval(coeffs, log_T)
    ss_res = np.sum((log_V - y_hat) ** 2)
    ss_tot = np.sum((log_V - np.mean(log_V)) ** 2)
    r2 = 1 - ss_res / ss_tot if ss_tot != 0 else 1.0
    return n_fit, C_fit, r2

def extended_taylor(V0, T0, n, f0, d0, x, y, delta_V, delta_f, delta_d):
    """V·T^n·f^x·d^y = C_ext. Returns (T_new, C_ext, V1, f1, d1)."""
    C_ext = V0 * (T0 ** n) * (f0 ** x) * (d0 ** y)
    V1 = V0 * (1 + delta_V / 100)
    f1 = f0 * (1 + delta_f / 100)
    d1 = d0 * (1 + delta_d / 100)
    T1 = (C_ext / (V1 * (f1 ** x) * (d1 ** y))) ** (1.0 / n)
    return T1, C_ext, V1, f1, d1

def compare_crossover(nA, CA, nB, CB):
    """Numerical crossover speed where T_A = T_B."""
    V_vals = np.linspace(0.5, max(CA, CB) * 2, 8000)
    def diff(V):
        try:
            return tool_life_from_C(V, CA, nA) - tool_life_from_C(V, CB, nB)
        except Exception:
            return 0
    diffs = [diff(v) for v in V_vals]
    for i in range(len(diffs) - 1):
        if np.sign(diffs[i]) != np.sign(diffs[i+1]) and diffs[i] != 0:
            try:
                from scipy.optimize import brentq
                return brentq(diff, V_vals[i], V_vals[i+1])
            except Exception:
                return (V_vals[i] + V_vals[i+1]) / 2
    return None


# ─────────────────────────────────────────────
#  Plotting helpers
# ─────────────────────────────────────────────

PLOT_RC = {
    "figure.facecolor": "#f8fafd", "axes.facecolor": "#f8fafd",
    "axes.edgecolor": "#c0cede", "axes.grid": True,
    "grid.color": "#d0dce8", "grid.linestyle": "--", "grid.linewidth": 0.6,
    "axes.labelcolor": "#1a2e42", "axes.titlecolor": "#0d1f35",
    "xtick.color": "#4a6a8a", "ytick.color": "#4a6a8a",
}

def apply_style():
    plt.rcParams.update(PLOT_RC)

def make_loglog_plot(speeds, lives, n=None, C=None, title="log(V) vs log(T)"):
    apply_style()
    fig, ax = plt.subplots(figsize=(6.5, 4.2))
    ax.scatter(lives, speeds, color="#2c7be5", s=60, zorder=5, label="Data",
               edgecolors="#0d1f35", linewidths=0.5)
    if n is not None and C is not None:
        T_fit = np.linspace(min(lives)*0.5, max(lives)*1.6, 400)
        V_fit = [cutting_speed_from_C(t, C, n) for t in T_fit]
        ax.plot(T_fit, V_fit, color="#e8820c", lw=2, label=f"n={n:.4f}, C={C:.3f}")
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel("Tool Life  T  (min)", fontsize=10)
    ax.set_ylabel("Cutting Speed  V  (m/min)", fontsize=10)
    ax.set_title(title, fontsize=11, fontweight="bold")
    ax.legend(fontsize=9)
    ax.xaxis.set_major_formatter(ticker.ScalarFormatter())
    ax.yaxis.set_major_formatter(ticker.ScalarFormatter())
    fig.tight_layout()
    return fig

def make_comparison_plot(nA, CA, nB, CB, crossover=None):
    apply_style()
    V_max = max(CA, CB) * 1.2
    V_vals = np.linspace(0.5, V_max, 600)
    T_A = [tool_life_from_C(v, CA, nA) for v in V_vals]
    T_B = [tool_life_from_C(v, CB, nB) for v in V_vals]
    fig, ax = plt.subplots(figsize=(6.5, 4.2))
    ax.plot(V_vals, T_A, color="#2c7be5", lw=2, label="Tool A")
    ax.plot(V_vals, T_B, color="#e8820c", lw=2, label="Tool B")
    if crossover:
        ax.axvline(crossover, color="#3cb371", ls="--", lw=1.4,
                   label=f"Crossover  V = {crossover:.3f}")
    ax.set_xlabel("Cutting Speed V", fontsize=10)
    ax.set_ylabel("Tool Life T", fontsize=10)
    ax.set_title("Tool A vs Tool B — Life Comparison", fontsize=11, fontweight="bold")
    ax.legend(fontsize=9)
    fig.tight_layout()
    return fig

def make_bar_plot(labels, values, colors, ylabel, title):
    apply_style()
    fig, ax = plt.subplots(figsize=(4.5, 3.2))
    bars = ax.bar(labels, values, color=colors, width=0.45, edgecolor="#c0cede", lw=0.8)
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(values)*0.02,
                f"{val:.2f}", ha="center", va="bottom", fontsize=10, color="#1a2e42")
    ax.set_ylabel(ylabel, fontsize=10)
    ax.set_title(title, fontsize=11, fontweight="bold")
    ax.set_ylim(0, max(values) * 1.28)
    fig.tight_layout()
    return fig


# ─────────────────────────────────────────────
#  Sidebar
# ─────────────────────────────────────────────

with st.sidebar:
    st.markdown("## Taylor Tool Life\nSolver")
    st.markdown("---")
    module = st.radio("Select Module", [
        "1. Tool Comparison (A vs B)",
        "2. Tool Life Equation Solver",
        "3. Parameter Variation",
        "4. Find Constants from Data",
        "5. Graphical Solver",
        "6. Extended Taylor Equation",
        "7. Conclusion & Summary",
    ])
    st.markdown("---")
    st.markdown("**Core Equations**\n\n`V · T^n = C`\n\n`V · T^n · f^x · d^y = C`\n\n`n = −slope (log-log)`\n\n`C = exp(intercept)`")
    st.markdown("---")
    st.caption(f"Calculations logged: **{len(st.session_state.calc_log)}**")
    if st.button("Clear log"):
        st.session_state.calc_log = []
        st.rerun()


# ─────────────────────────────────────────────
#  Page header
# ─────────────────────────────────────────────

st.markdown('<div class="page-title">Taylor Tool Life Equation Solver</div>', unsafe_allow_html=True)
st.markdown('<div class="page-subtitle">Professional engineering calculator — machining analysis based on Taylor\'s Tool Life Equation</div>', unsafe_allow_html=True)
st.markdown("---")


# ═══════════════════════════════════════════════════════════
#  MODULE 1 — Tool Comparison
# ═══════════════════════════════════════════════════════════

if module.startswith("1"):
    st.markdown("### Module 1 — Tool Comparison (A vs B)")

    st.markdown("""
<div class="module-info-card">
  <h4>What this module does</h4>
  <p>Compares the tool life of two different cutting tools (Tool A and Tool B) under identical
     machining conditions using Taylor's tool life equation for each tool independently.
     It also finds the <em>crossover speed</em> — the exact cutting speed at which both tools
     deliver equal life. Below the crossover one tool is superior; above it the other takes over.</p>
  <div class="info-grid">
    <div class="info-col">
      <strong>Inputs</strong>
      <span>n_A — Taylor exponent for Tool A<br>
            C_A — Taylor constant for Tool A<br>
            n_B — Taylor exponent for Tool B<br>
            C_B — Taylor constant for Tool B<br>
            V   — Cutting speed to evaluate at</span>
    </div>
    <div class="info-col">
      <strong>Outputs</strong>
      <span>T_A — Tool life of Tool A at speed V<br>
            T_B — Tool life of Tool B at speed V<br>
            Better tool — which lasts longer<br>
            Crossover speed — where T_A = T_B<br>
            Life vs speed plot (both tools)</span>
    </div>
  </div>
</div>""", unsafe_allow_html=True)

    st.markdown('<div class="formula-box">Tool A: V · T^n_A = C_A     |     Tool B: V · T^n_B = C_B</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-title">Tool A</div>', unsafe_allow_html=True)
        nA = st.number_input("Exponent n_A", value=0.22, format="%.5f", key="nA")
        CA = st.number_input("Constant C_A", value=42.5, format="%.4f", key="CA")
    with col2:
        st.markdown('<div class="section-title">Tool B</div>', unsafe_allow_html=True)
        nB = st.number_input("Exponent n_B", value=0.45, format="%.5f", key="nB")
        CB = st.number_input("Constant C_B", value=88.6, format="%.4f", key="CB")

    st.markdown('<div class="section-title">Evaluation Speed</div>', unsafe_allow_html=True)
    V_eval = st.number_input("Cutting Speed V (m/s or m/min)", value=1.0, format="%.4f", key="V_eval")

    c1, _ = st.columns([1, 5])
    with c1:
        calc1 = st.button("Calculate", key="btn1")

    if calc1:
        try:
            if any(v <= 0 for v in [nA, CA, nB, CB, V_eval]):
                st.markdown('<div class="error-box">All values must be positive and non-zero.</div>', unsafe_allow_html=True)
            else:
                TA = tool_life_from_C(V_eval, CA, nA)
                TB = tool_life_from_C(V_eval, CB, nB)
                winner = "Tool A" if TA > TB else ("Tool B" if TB > TA else "Equal")
                crossover = compare_crossover(nA, CA, nB, CB)

                res = (
                    f"At V = {V_eval}:\n"
                    f"  Tool A life  T_A = ({CA}/{V_eval})^(1/{nA})  =  {TA:.4f}\n"
                    f"  Tool B life  T_B = ({CB}/{V_eval})^(1/{nB})  =  {TB:.4f}\n\n"
                    f"  Life difference : {abs(TA-TB):.4f}\n"
                    f"  Superior tool   : {winner}"
                )
                if crossover:
                    res += f"\n\n  Crossover speed : V = {crossover:.4f}  (T_A = T_B here)"
                st.markdown(f'<div class="result-box">{res}</div>', unsafe_allow_html=True)

                concl = (f"At V={V_eval}: T_A={TA:.3f}, T_B={TB:.3f}. {winner} is superior. "
                         + (f"Crossover at V={crossover:.3f}." if crossover else ""))
                log_result("1 — Tool Comparison",
                           {"n_A": nA, "C_A": CA, "n_B": nB, "C_B": CB, "V_eval": V_eval},
                           {"T_A": round(TA,4), "T_B": round(TB,4), "better_tool": winner,
                            "crossover_V": round(crossover,4) if crossover else "None"},
                           concl)

                fig = make_comparison_plot(nA, CA, nB, CB, crossover)
                st.pyplot(fig)

                if crossover:
                    ratio = max(TA, TB) / min(TA, TB)
                    st.markdown(f'<div class="info-box">At the evaluation speed, life ratio = {ratio:.3f}. '
                                f'Below V={crossover:.4f}, {"Tool A" if nA<nB else "Tool B"} is preferred; '
                                f'above it, {"Tool B" if nA<nB else "Tool A"} takes over.</div>', unsafe_allow_html=True)

        except Exception as e:
            st.markdown(f'<div class="error-box">Calculation error: {e}</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
#  MODULE 2 — Tool Life Equation Solver
# ═══════════════════════════════════════════════════════════

elif module.startswith("2"):
    st.markdown("### Module 2 — Tool Life Equation Solver")

    st.markdown("""
<div class="module-info-card">
  <h4>What this module does</h4>
  <p>Solves Taylor's fundamental equation <strong>V · T^n = C</strong> for any one unknown — 
     tool life T, cutting speed V, or Taylor's constant C — given the other two values and the
     exponent n. This is the most direct application of Taylor's model and is used to design
     cutting parameters that achieve a required tool life target in production.</p>
  <div class="info-grid">
    <div class="info-col">
      <strong>Inputs</strong>
      <span>n — Taylor's exponent (dimensionless)<br>
            Any two of: V (m/min), T (min), C</span>
    </div>
    <div class="info-col">
      <strong>Outputs</strong>
      <span>The missing third variable:<br>
            T = (C / V)^(1/n)<br>
            V = C / T^n<br>
            C = V · T^n</span>
    </div>
  </div>
</div>""", unsafe_allow_html=True)

    st.markdown('<div class="formula-box">V · T^n = C     =>     T = (C/V)^(1/n)   |   V = C/T^n   |   C = V·T^n</div>', unsafe_allow_html=True)

    solve_for = st.selectbox("Solve for", ["Tool Life  T", "Cutting Speed  V", "Constant  C"])
    col1, col2 = st.columns(2)

    with col1:
        n_val = st.number_input("Taylor exponent n", value=0.28, format="%.5f", key="n2")

    if solve_for.startswith("Tool Life"):
        with col1:
            V_in = st.number_input("Cutting Speed V (m/min)", value=28.0, format="%.4f", key="V2")
        with col2:
            C_in = st.number_input("Constant C", value=120.0, format="%.4f", key="C2")
        solve_target = "T"
    elif solve_for.startswith("Cutting Speed"):
        with col1:
            T_in2 = st.number_input("Tool Life T (min)", value=60.0, format="%.4f", key="T2v")
        with col2:
            C_in = st.number_input("Constant C", value=120.0, format="%.4f", key="C2v")
        solve_target = "V"
    else:
        with col1:
            V_in = st.number_input("Cutting Speed V (m/min)", value=28.0, format="%.4f", key="V2c")
        with col2:
            T_in2 = st.number_input("Tool Life T (min)", value=60.0, format="%.4f", key="T2c")
        solve_target = "C"

    c1, _ = st.columns([1, 5])
    with c1:
        calc2 = st.button("Calculate", key="btn2")

    if calc2:
        try:
            if n_val <= 0:
                st.markdown('<div class="error-box">Exponent n must be positive.</div>', unsafe_allow_html=True)
            elif solve_target == "T":
                if C_in <= 0 or V_in <= 0:
                    st.markdown('<div class="error-box">V and C must be positive.</div>', unsafe_allow_html=True)
                else:
                    T_out = tool_life_from_C(V_in, C_in, n_val)
                    res = (f"Formula : T = (C / V)^(1/n)\n"
                           f"        = ({C_in} / {V_in})^(1/{n_val})\n"
                           f"        = {T_out:.4f} min")
                    st.markdown(f'<div class="result-box">{res}</div>', unsafe_allow_html=True)
                    log_result("2 — Equation Solver (T)", {"V": V_in, "C": C_in, "n": n_val},
                               {"T": round(T_out,4)},
                               f"At V={V_in} m/min with C={C_in}, tool life T = {T_out:.4f} min.")

            elif solve_target == "V":
                if C_in <= 0 or T_in2 <= 0:
                    st.markdown('<div class="error-box">T and C must be positive.</div>', unsafe_allow_html=True)
                else:
                    V_out = cutting_speed_from_C(T_in2, C_in, n_val)
                    res = (f"Formula : V = C / T^n\n"
                           f"        = {C_in} / {T_in2}^{n_val}\n"
                           f"        = {V_out:.4f} m/min")
                    st.markdown(f'<div class="result-box">{res}</div>', unsafe_allow_html=True)
                    log_result("2 — Equation Solver (V)", {"T": T_in2, "C": C_in, "n": n_val},
                               {"V": round(V_out,4)},
                               f"For T={T_in2} min with C={C_in}, cutting speed V = {V_out:.4f} m/min.")

            else:
                if V_in <= 0 or T_in2 <= 0:
                    st.markdown('<div class="error-box">V and T must be positive.</div>', unsafe_allow_html=True)
                else:
                    C_out = taylor_constant(V_in, T_in2, n_val)
                    res = (f"Formula : C = V * T^n\n"
                           f"        = {V_in} * {T_in2}^{n_val}\n"
                           f"        = {C_out:.4f}")
                    st.markdown(f'<div class="result-box">{res}</div>', unsafe_allow_html=True)
                    log_result("2 — Equation Solver (C)", {"V": V_in, "T": T_in2, "n": n_val},
                               {"C": round(C_out,4)},
                               f"For V={V_in}, T={T_in2} min, Taylor constant C = {C_out:.4f}.")

        except Exception as e:
            st.markdown(f'<div class="error-box">Calculation error: {e}</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
#  MODULE 3 — Parameter Variation
# ═══════════════════════════════════════════════════════════

elif module.startswith("3"):
    st.markdown("### Module 3 — Parameter Variation Analysis")

    st.markdown("""
<div class="module-info-card">
  <h4>What this module does</h4>
  <p>Calculates the new tool life when machining parameters — cutting speed, feed rate, or depth
     of cut — change by a specified percentage from a known baseline. This answers the classic
     question: <em>"If speed is increased by 25%, how does tool life change?"</em> The relationship
     is strongly non-linear and governed by Taylor's exponent n; even a small speed increase
     can cause a dramatic drop in tool life for low values of n.</p>
  <div class="info-grid">
    <div class="info-col">
      <strong>Inputs</strong>
      <span>V0 — base cutting speed (m/min)<br>
            T0 — base tool life (min)<br>
            n  — Taylor exponent<br>
            f0, d0 — feed (mm/rev) and depth (mm)<br>
            x, y   — feed and depth exponents<br>
            % change in V, f, d</span>
    </div>
    <div class="info-col">
      <strong>Outputs</strong>
      <span>C or C_ext — calibrated Taylor constant<br>
            V1 — new cutting speed<br>
            T1 — new tool life at changed conditions<br>
            % change in tool life<br>
            Bar chart: base vs new life</span>
    </div>
  </div>
</div>""", unsafe_allow_html=True)

    st.markdown('<div class="formula-box">Standard: V·T^n = C (speed change) | Extended: V·T^n·f^x·d^y = C_ext</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-title">Base Conditions</div>', unsafe_allow_html=True)
        V0 = st.number_input("Base Speed V0 (m/min)", value=28.0, format="%.4f", key="V0")
        T0 = st.number_input("Base Tool Life T0 (min)", value=60.0, format="%.4f", key="T0")
        n3 = st.number_input("Taylor exponent n", value=0.14, format="%.5f", key="n3")

    with col2:
        st.markdown('<div class="section-title">Extended Parameters (optional)</div>', unsafe_allow_html=True)
        use_ext = st.checkbox("Use extended equation (feed + depth of cut)")
        f0  = st.number_input("Base Feed f0 (mm/rev)", value=0.3, format="%.4f", key="f0", disabled=not use_ext)
        d0  = st.number_input("Base Depth d0 (mm)", value=2.6, format="%.4f", key="d0", disabled=not use_ext)
        x3  = st.number_input("Feed exponent x", value=0.78, format="%.4f", key="x3", disabled=not use_ext)
        y3  = st.number_input("Depth exponent y", value=0.28, format="%.4f", key="y3", disabled=not use_ext)

    st.markdown('<div class="section-title">Percentage Changes</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1: dV  = st.number_input("Change in Speed (%)",  value=25.0, format="%.2f", key="dV")
    with c2: df3 = st.number_input("Change in Feed (%)",   value=0.0,  format="%.2f", key="df3", disabled=not use_ext)
    with c3: dd3 = st.number_input("Change in Depth (%)",  value=0.0,  format="%.2f", key="dd3", disabled=not use_ext)

    c1, _ = st.columns([1, 5])
    with c1:
        calc3 = st.button("Calculate", key="btn3")

    if calc3:
        try:
            if any(v <= 0 for v in [V0, T0, n3]):
                st.markdown('<div class="error-box">Base values must be positive.</div>', unsafe_allow_html=True)
            else:
                x, y, f_u, d_u, df_u, dd_u = (x3, y3, f0, d0, df3, dd3) if use_ext else (0.0, 0.0, 1.0, 1.0, 0.0, 0.0)
                T1, C_ext, V1, f1, d1 = extended_taylor(V0, T0, n3, f_u, d_u, x, y, dV, df_u, dd_u)
                pct = (T1 - T0) / T0 * 100

                if use_ext:
                    res = (f"C_ext = V0·T0^n·f0^x·d0^y = {V0}·{T0}^{n3}·{f_u}^{x}·{d_u}^{y} = {C_ext:.5f}\n\n"
                           f"New: V1={V1:.4f} ({dV:+.1f}%)  f1={f1:.4f} ({df_u:+.1f}%)  d1={d1:.4f} ({dd_u:+.1f}%)\n\n"
                           f"New tool life T1 = {T1:.4f} min\nLife change    : {pct:+.2f}%")
                else:
                    C_base = taylor_constant(V0, T0, n3)
                    res = (f"C = V0·T0^n = {V0}·{T0}^{n3} = {C_base:.5f}\n\n"
                           f"New speed V1 = {V0}·(1+{dV}/100) = {V1:.4f} m/min\n\n"
                           f"New tool life T1 = (C/V1)^(1/n) = ({C_base:.5f}/{V1:.4f})^(1/{n3})\n"
                           f"               = {T1:.4f} min\n\nLife change : {pct:+.2f}%")

                st.markdown(f'<div class="result-box">{res}</div>', unsafe_allow_html=True)
                log_result("3 — Parameter Variation",
                           {"V0": V0, "T0": T0, "n": n3, "dV%": dV},
                           {"V1": round(V1,4), "T1": round(T1,4), "life_change_%": round(pct,2)},
                           f"Changing speed by {dV}% changes tool life from {T0} to {T1:.4f} min ({pct:+.2f}%).")

                fig = make_bar_plot(["Base  T0", "New  T1"], [T0, T1], ["#2c7be5","#e8820c"],
                                    "Tool Life (min)", "Tool Life: Before vs After Parameter Change")
                st.pyplot(fig)

        except Exception as e:
            st.markdown(f'<div class="error-box">Calculation error: {e}</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
#  MODULE 4 — Find Constants from Data
# ═══════════════════════════════════════════════════════════

elif module.startswith("4"):
    st.markdown("### Module 4 — Find n and C from Experimental Data")

    st.markdown("""
<div class="module-info-card">
  <h4>What this module does</h4>
  <p>Given multiple experimental pairs of cutting speed (V) and tool life (T) measured in a
     machining test, this module determines Taylor's constants n and C by fitting the equation
     in log-log space. The slope of the fitted line equals −n and the intercept equals log(C).
     This is how Taylor's constants are established from real cutting experiments in the lab.</p>
  <div class="info-grid">
    <div class="info-col">
      <strong>Inputs</strong>
      <span>V1, V2, ... — measured cutting speeds (m/min)<br>
            T1, T2, ... — corresponding tool lives (min)<br>
            Minimum 2 data points required</span>
    </div>
    <div class="info-col">
      <strong>Outputs</strong>
      <span>n — Taylor exponent (slope = −n)<br>
            C — Taylor constant (intercept)<br>
            R² — goodness of fit (1.0 = perfect)<br>
            Data table with fitted values<br>
            log-log scatter + fitted curve</span>
    </div>
  </div>
</div>""", unsafe_allow_html=True)

    st.markdown('<div class="formula-box">log(V) = log(C) − n · log(T)     (Linear fit in log-log space)</div>', unsafe_allow_html=True)

    st.caption("Textbook example: V = [52, 50, 49, 46, 42] m/min,  T = [3, 4, 4.9, 10.5, 30] min")
    col1, col2 = st.columns(2)
    with col1:
        speeds_in = st.text_input("Cutting Speeds V (m/min) — comma separated", value="52, 50, 49, 46, 42", key="s4")
    with col2:
        lives_in  = st.text_input("Tool Lives T (min) — comma separated", value="3, 4, 4.9, 10.5, 30", key="l4")

    c1, _ = st.columns([1, 5])
    with c1:
        calc4 = st.button("Calculate", key="btn4")

    if calc4:
        try:
            speeds = [float(v.strip()) for v in speeds_in.split(",")]
            lives  = [float(t.strip()) for t in lives_in.split(",")]

            if len(speeds) != len(lives):
                st.markdown('<div class="error-box">Number of speeds must equal number of tool lives.</div>', unsafe_allow_html=True)
            elif len(speeds) < 2:
                st.markdown('<div class="error-box">At least 2 data points are required.</div>', unsafe_allow_html=True)
            elif any(v <= 0 for v in speeds) or any(t <= 0 for t in lives):
                st.markdown('<div class="error-box">All values must be positive.</div>', unsafe_allow_html=True)
            else:
                n4, C4, r2 = find_n_and_C(speeds, lives)
                rows = "".join(
                    f"<tr><td>{i+1}</td><td>{speeds[i]}</td><td>{lives[i]}</td>"
                    f"<td>{cutting_speed_from_C(lives[i], C4, n4):.3f}</td></tr>"
                    for i in range(len(speeds))
                )
                st.markdown(f"""
<table class="data-table">
  <tr><th>#</th><th>V measured</th><th>T measured</th><th>V fitted</th></tr>
  {rows}
</table>""", unsafe_allow_html=True)

                res = (f"Regression result:\n  n  = {n4:.5f}\n  C  = {C4:.4f}\n  R\u00b2 = {r2:.6f}\n\n"
                       f"Taylor equation: V * T^{n4:.5f} = {C4:.4f}")
                st.markdown(f'<div class="result-box">{res}</div>', unsafe_allow_html=True)
                log_result("4 — Find Constants", {"speeds": speeds, "lives": lives},
                           {"n": round(n4,5), "C": round(C4,4), "R2": round(r2,6)},
                           f"Fitted Taylor constants: n={n4:.5f}, C={C4:.4f} (R²={r2:.4f}).")

                fig = make_loglog_plot(speeds, lives, n4, C4, "Experimental Data — log(V) vs log(T)")
                st.pyplot(fig)

        except ValueError:
            st.markdown('<div class="error-box">Invalid input — ensure all values are numbers separated by commas.</div>', unsafe_allow_html=True)
        except Exception as e:
            st.markdown(f'<div class="error-box">Calculation error: {e}</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
#  MODULE 5 — Graphical Solver
# ═══════════════════════════════════════════════════════════

elif module.startswith("5"):
    st.markdown("### Module 5 — Graphical Solver")

    st.markdown("""
<div class="module-info-card">
  <h4>What this module does</h4>
  <p>Produces a dual-panel graphical solution to Taylor's equation from experimental data.
     The left panel shows the classic log(V) vs log(T) on log-log axes with the fitted curve.
     The right panel shows the same data in linear log-space — a true straight line whose
     slope = −n and intercept = log(C). A prediction line is drawn at the user-specified
     speed to read off tool life directly from the graph, exactly as done in a lab solution.</p>
  <div class="info-grid">
    <div class="info-col">
      <strong>Inputs</strong>
      <span>V1...Vn — cutting speed data points (m/min)<br>
            T1...Tn — tool life data points (min)<br>
            V_predict — speed at which to predict tool life</span>
    </div>
    <div class="info-col">
      <strong>Outputs</strong>
      <span>n — from slope = −n of log-log line<br>
            C — from intercept = log(C)<br>
            R² — quality of fit<br>
            T_predicted — at user-specified speed<br>
            Two-panel plot (log-log + linear log)</span>
    </div>
  </div>
</div>""", unsafe_allow_html=True)

    st.markdown('<div class="formula-box">Plot log(V) vs log(T)  |  Slope = -n  |  Intercept = log(C)  |  Read T at given V</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        g_speeds = st.text_input("Cutting Speeds V (m/min)", value="52, 50, 49, 46, 42", key="gs5")
    with col2:
        g_lives  = st.text_input("Tool Lives T (min)", value="3, 4, 4.9, 10.5, 30", key="gl5")
    V_pred = st.number_input("Predict tool life at speed V =", value=35.0, format="%.4f", key="Vp5")

    c1, _ = st.columns([1, 5])
    with c1:
        calc5 = st.button("Plot & Solve", key="btn5")

    if calc5:
        try:
            s5 = [float(v.strip()) for v in g_speeds.split(",")]
            l5 = [float(t.strip()) for t in g_lives.split(",")]

            if len(s5) != len(l5) or len(s5) < 2:
                st.markdown('<div class="error-box">Need equal and at least 2 data points.</div>', unsafe_allow_html=True)
            else:
                n5, C5, r2_5 = find_n_and_C(s5, l5)
                T_pred = tool_life_from_C(V_pred, C5, n5)
                log_T5 = np.log10(l5)
                log_V5 = np.log10(s5)
                coeffs5 = np.polyfit(log_T5, log_V5, 1)
                slope5 = coeffs5[0]
                intercept5 = coeffs5[1]

                res = (f"Log\u2081\u2080 linear fit: log(V) = {intercept5:.5f} + ({slope5:.5f})\u00b7log(T)\n"
                       f"  Slope       = {slope5:.5f}   =>   n = {-slope5:.5f}\n"
                       f"  Intercept   = {intercept5:.5f}   =>   C = 10^{intercept5:.5f} = {10**intercept5:.4f}\n"
                       f"  R\u00b2          = {r2_5:.6f}\n\n"
                       f"Predicted tool life at V = {V_pred} m/min:\n"
                       f"  T = (C/V)^(1/n) = ({C5:.4f}/{V_pred})^(1/{n5:.5f}) = {T_pred:.4f} min")
                st.markdown(f'<div class="result-box">{res}</div>', unsafe_allow_html=True)
                log_result("5 — Graphical Solver",
                           {"speeds": s5, "lives": l5, "V_predict": V_pred},
                           {"n": round(n5,5), "C": round(C5,4), "R2": round(r2_5,6), "T_predicted": round(T_pred,4)},
                           f"Graphical solution: n={n5:.5f}, C={C5:.4f}. At V={V_pred}, T_predicted={T_pred:.4f} min.")

                apply_style()
                fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.5))

                T_rng = np.linspace(min(l5)*0.5, max(l5)*1.8, 400)
                V_fit = [cutting_speed_from_C(t, C5, n5) for t in T_rng]
                ax1.scatter(l5, s5, color="#2c7be5", s=60, zorder=5, label="Data",
                            edgecolors="#0d1f35", linewidths=0.5)
                ax1.plot(T_rng, V_fit, color="#e8820c", lw=2, label="Fitted curve")
                ax1.axvline(T_pred, color="#3cb371", ls="--", lw=1.2, label=f"T={T_pred:.2f} min")
                ax1.axhline(V_pred, color="#3cb371", ls="--", lw=1.2)
                ax1.set_xscale("log"); ax1.set_yscale("log")
                ax1.set_xlabel("T (min)"); ax1.set_ylabel("V (m/min)")
                ax1.set_title("log(V) vs log(T)", fontweight="bold")
                ax1.legend(fontsize=8)
                ax1.xaxis.set_major_formatter(ticker.ScalarFormatter())
                ax1.yaxis.set_major_formatter(ticker.ScalarFormatter())
                ax1.grid(True, which="both", ls="--", lw=0.6, color="#d0dce8")

                lT_rng = np.linspace(min(log_T5)-0.2, max(log_T5)+0.2, 200)
                lV_fit = np.polyval(coeffs5, lT_rng)
                ax2.scatter(log_T5, log_V5, color="#2c7be5", s=60, zorder=5, label="Data",
                            edgecolors="#0d1f35", linewidths=0.5)
                ax2.plot(lT_rng, lV_fit, color="#e8820c", lw=2, label=f"slope={slope5:.4f}")
                ax2.set_xlabel("log\u2081\u2080(T)"); ax2.set_ylabel("log\u2081\u2080(V)")
                ax2.set_title(f"Linear Log Space  |  n = {n5:.5f}", fontweight="bold")
                ax2.legend(fontsize=8)
                ax2.grid(True, ls="--", lw=0.6, color="#d0dce8")
                fig.tight_layout()
                st.pyplot(fig)

        except ValueError:
            st.markdown('<div class="error-box">Invalid input — ensure all entries are numeric.</div>', unsafe_allow_html=True)
        except Exception as e:
            st.markdown(f'<div class="error-box">Calculation error: {e}</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
#  MODULE 6 — Extended Taylor Equation
# ═══════════════════════════════════════════════════════════

elif module.startswith("6"):
    st.markdown("### Module 6 — Extended Taylor Equation")

    st.markdown("""
<div class="module-info-card">
  <h4>What this module does</h4>
  <p>Solves the extended form of Taylor's equation that accounts for all three primary
     machining parameters: cutting speed V, feed rate f, and depth of cut d. The extended
     constant C_ext is calibrated from a known reference condition (often from a tool
     manufacturer or prior test), and then the tool life is computed for any new set
     of operating parameters. This is the most realistic model used in production machining.</p>
  <div class="info-grid">
    <div class="info-col">
      <strong>Inputs</strong>
      <span>V_ref, T_ref — reference speed and life<br>
            f_ref, d_ref — reference feed and depth<br>
            n, x, y — Taylor + extended exponents<br>
            V_new, f_new, d_new — new conditions</span>
    </div>
    <div class="info-col">
      <strong>Outputs</strong>
      <span>C_ext — extended Taylor constant<br>
            T_new — tool life at new conditions<br>
            % life change from reference<br>
            Step-by-step substitution<br>
            Bar chart: reference vs new life</span>
    </div>
  </div>
</div>""", unsafe_allow_html=True)

    st.markdown('<div class="formula-box">V · T^n · f^x · d^y = C_ext     =>     T_new = ( C_ext / (V · f^x · d^y) )^(1/n)</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-title">Reference Condition</div>', unsafe_allow_html=True)
        Vref = st.number_input("V_ref (m/min)", value=28.0, format="%.4f", key="Vr6")
        Tref = st.number_input("T_ref (min)", value=60.0, format="%.4f", key="Tr6")
        fref = st.number_input("f_ref (mm/rev)", value=0.3, format="%.4f", key="fr6")
        dref = st.number_input("d_ref (mm)", value=2.6, format="%.4f", key="dr6")

    with col2:
        st.markdown('<div class="section-title">Exponents</div>', unsafe_allow_html=True)
        n6 = st.number_input("Taylor exponent n", value=0.14, format="%.5f", key="n6")
        x6 = st.number_input("Feed exponent x", value=0.78, format="%.5f", key="x6")
        y6 = st.number_input("Depth exponent y", value=0.28, format="%.5f", key="y6")

        st.markdown('<div class="section-title">New Conditions</div>', unsafe_allow_html=True)
        Vnew = st.number_input("V_new (m/min)", value=35.0, format="%.4f", key="Vn6")
        fnew = st.number_input("f_new (mm/rev)", value=0.375, format="%.4f", key="fn6")
        dnew = st.number_input("d_new (mm)", value=3.25, format="%.4f", key="dn6")

    c1, _ = st.columns([1, 5])
    with c1:
        calc6 = st.button("Calculate", key="btn6")

    if calc6:
        try:
            if any(v <= 0 for v in [Vref, Tref, fref, dref, n6, x6, y6, Vnew, fnew, dnew]):
                st.markdown('<div class="error-box">All values must be positive.</div>', unsafe_allow_html=True)
            else:
                C_ext = Vref * (Tref**n6) * (fref**x6) * (dref**y6)
                T_new = (C_ext / (Vnew * (fnew**x6) * (dnew**y6))) ** (1.0/n6)
                pct6  = (T_new - Tref) / Tref * 100

                res = (f"C_ext = V_ref\u00b7T_ref^n\u00b7f_ref^x\u00b7d_ref^y\n"
                       f"      = {Vref}\u00b7{Tref}^{n6}\u00b7{fref}^{x6}\u00b7{dref}^{y6}\n"
                       f"      = {C_ext:.6f}\n\n"
                       f"T_new = (C_ext / (V\u00b7f^x\u00b7d^y))^(1/n)\n"
                       f"      = ({C_ext:.4f} / ({Vnew}\u00b7{fnew}^{x6}\u00b7{dnew}^{y6}))^(1/{n6})\n"
                       f"      = {T_new:.4f} min\n\nLife change : {pct6:+.2f}%")
                st.markdown(f'<div class="result-box">{res}</div>', unsafe_allow_html=True)
                log_result("6 — Extended Taylor",
                           {"V_ref": Vref, "T_ref": Tref, "f_ref": fref, "d_ref": dref,
                            "n": n6, "x": x6, "y": y6, "V_new": Vnew, "f_new": fnew, "d_new": dnew},
                           {"C_ext": round(C_ext,5), "T_new": round(T_new,4), "change_%": round(pct6,2)},
                           f"Extended Taylor: C_ext={C_ext:.4f}. New tool life T_new={T_new:.4f} min ({pct6:+.2f}% from reference).")

                fig = make_bar_plot(["Reference T_ref", "New T_new"], [Tref, T_new],
                                    ["#2c7be5","#e8820c"], "Tool Life (min)",
                                    "Tool Life: Reference vs New Conditions")
                st.pyplot(fig)

        except Exception as e:
            st.markdown(f'<div class="error-box">Calculation error: {e}</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
#  MODULE 7 — Conclusion & Summary
# ═══════════════════════════════════════════════════════════

elif module.startswith("7"):
    st.markdown("### Module 7 — Conclusion & Session Summary")

    st.markdown("""
<div class="module-info-card">
  <h4>What this page does</h4>
  <p>This page consolidates every calculation performed during this session into a complete
     engineering summary report. For each logged calculation, the module used, all input
     parameters, computed outputs, and a plain-English conclusion are shown together. A combined
     bar chart visualises all tool life values computed across modules, and a final set of
     engineering design principles drawn from Taylor's theory is presented.</p>
  <div class="info-grid">
    <div class="info-col">
      <strong>Inputs shown</strong>
      <span>All parameters entered in Modules 1 through 6<br>
            during this session</span>
    </div>
    <div class="info-col">
      <strong>Outputs shown</strong>
      <span>All computed results and conclusions per module<br>
            Summary bar chart of all tool life values<br>
            Key engineering principles from Taylor's model</span>
    </div>
  </div>
</div>""", unsafe_allow_html=True)

    log = st.session_state.calc_log

    if not log:
        st.markdown("""
<div class="empty-state">
  No calculations recorded yet.<br>
  Use Modules 1 through 6 and click Calculate — all results will appear here automatically.
</div>""", unsafe_allow_html=True)

    else:
        # Header banner
        st.markdown(f"""
<div class="concl-header">
  <h2>Session Calculation Report</h2>
  <p style="font-size:0.88rem;color:#a0c4e8;margin:0;">
    Total calculations logged: <strong style="color:#7ec8ff;">{len(log)}</strong>
  </p>
</div>""", unsafe_allow_html=True)

        # Per-entry display
        for i, entry in enumerate(log, 1):
            inp_html = "<br>".join(
                f"<strong>{k}</strong>&nbsp;=&nbsp;{v}" for k, v in entry["inputs"].items()
            )
            out_html = "<br>".join(
                f"<strong>{k}</strong>&nbsp;=&nbsp;{v}" for k, v in entry["outputs"].items()
            )
            st.markdown(f"""
<div class="log-entry">
  <div class="le-header">
    [{i}] &nbsp; {entry['module']}
    <span class="le-time">Logged at {entry['time']}</span>
  </div>
  <div class="log-kv">
    <div class="log-kv-col">
      <strong>Inputs</strong>
      <span style="font-size:0.82rem;line-height:1.75;">{inp_html}</span>
    </div>
    <div class="log-kv-col">
      <strong>Outputs</strong>
      <span style="font-size:0.82rem;line-height:1.75;">{out_html}</span>
    </div>
  </div>
  <div class="concl-text">{entry['conclusion']}</div>
</div>""", unsafe_allow_html=True)

        st.markdown("---")

        # Aggregate statistics
        st.markdown("#### Aggregate Analysis")

        all_T, all_n = [], []
        for entry in log:
            for k, v in entry["outputs"].items():
                if isinstance(v, float) and k.upper().startswith("T") and 0 < v < 1e6:
                    all_T.append((entry["module"], k, v))
            for k, v in entry["inputs"].items():
                if k in ("n", "n_A", "n_B") and isinstance(v, float):
                    all_n.append(v)

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Calculations", len(log))
        if all_T:
            best  = max(all_T, key=lambda x: x[2])
            worst = min(all_T, key=lambda x: x[2])
            col2.metric("Longest Tool Life Computed", f"{best[2]:.4f} min",  f"from {best[0][:20]}")
            col3.metric("Shortest Tool Life Computed", f"{worst[2]:.4f} min", f"from {worst[0][:20]}")

        if all_n:
            st.markdown(f"""
<div class="info-box">
  <strong>Taylor Exponent Observed:</strong> n ranged from {min(all_n):.5f} to {max(all_n):.5f}
  across all calculations. Higher n means tool life is less sensitive to speed —
  the V-T curve is flatter. Lower n means a steep penalty: even a small speed
  increase sharply reduces tool life.
</div>""", unsafe_allow_html=True)

        # Summary bar chart of all tool lives
        if len(all_T) >= 2:
            st.markdown("#### All Computed Tool Lives — Combined Chart")
            apply_style()
            fig_s, ax_s = plt.subplots(figsize=(max(7, len(all_T)*1.1), 3.8))
            labels_s = [f"[{i+1}] {t[1]}\n({t[0][:16]})" for i, t in enumerate(all_T)]
            vals_s   = [t[2] for t in all_T]
            cols_s   = ["#2c7be5" if i % 2 == 0 else "#e8820c" for i in range(len(vals_s))]
            bars_s   = ax_s.bar(labels_s, vals_s, color=cols_s, edgecolor="#c0cede", lw=0.8)
            for bar, val in zip(bars_s, vals_s):
                ax_s.text(bar.get_x()+bar.get_width()/2, bar.get_height()+max(vals_s)*0.015,
                          f"{val:.2f}", ha="center", va="bottom", fontsize=8.5, color="#1a2e42")
            ax_s.set_ylabel("Tool Life (min)", fontsize=10)
            ax_s.set_title("All Computed Tool Life Values — Session Overview", fontsize=11, fontweight="bold")
            ax_s.set_ylim(0, max(vals_s)*1.3)
            ax_s.grid(axis="y", ls="--", lw=0.6, color="#d0dce8")
            ax_s.tick_params(axis="x", labelsize=7.5)
            fig_s.tight_layout()
            st.pyplot(fig_s)

        # Final written conclusion
        st.markdown("---")
        st.markdown("#### Plain-English Conclusions — Per Calculation")
        concl_lines = "\n\n".join(f"[{i}]  {e['conclusion']}" for i, e in enumerate(log, 1))
        st.markdown(f'<div class="result-box">{concl_lines}</div>', unsafe_allow_html=True)

        # Engineering principles
        st.markdown("---")
        st.markdown("#### Key Engineering Principles (Taylor's Model)")
        st.markdown("""
<div class="info-box">
  <strong>(1) Exponent n and sensitivity:</strong> A higher n (e.g., 0.4–0.5, typical for ceramics) means
  tool life falls slowly as speed rises — these tools tolerate aggressive speeds. A lower n
  (e.g., 0.1–0.15, typical for HSS) means a steep penalty — even a 25% speed increase can
  halve or quarter tool life.<br><br>
  <strong>(2) Speed dominates over feed and depth:</strong> In the extended equation V·T^n·f^x·d^y = C,
  speed exponent (1/n) is typically much larger than x or y. Reducing speed is the most powerful
  lever for extending tool life.<br><br>
  <strong>(3) Crossover speed determines tool selection:</strong> If two tools cross over at speed V_c,
  use the tool with the higher C below V_c and the other above it. Never apply a single tool
  recommendation across the full speed range without checking the crossover.<br><br>
  <strong>(4) Log-log linearity is the signature of Taylor's model:</strong> If experimental V-T data
  plots as a straight line on log-log axes, Taylor's equation is valid. Curvature indicates other
  mechanisms (built-up edge, thermal softening) are acting and the model needs extension.
</div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  Footer
# ─────────────────────────────────────────────
st.markdown("---")
st.caption(
    "Taylor Tool Life Solver  |  V · T^n = C  |  "
    "For academic and laboratory use  |  Maintain consistent units throughout each session."
)

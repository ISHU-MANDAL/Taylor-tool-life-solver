"""
Taylor's Tool Life Equation Solver
=====================================
A professional engineering calculator for machining tool life analysis.
Based on Taylor's Tool Life Equation: V * T^n = C
"""

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from io import BytesIO

# ─────────────────────────────────────────────
#  Page configuration
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Taylor Tool Life Solver",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
#  Global stylesheet
# ─────────────────────────────────────────────
st.markdown("""
<style>
    /* Main background */
    .stApp { background-color: #f4f6f9; }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #1e2a38;
    }
    section[data-testid="stSidebar"] * {
        color: #d0dce8 !important;
    }
    section[data-testid="stSidebar"] .stRadio label {
        font-size: 0.95rem;
        padding: 4px 0;
    }

    /* Cards */
    .calc-card {
        background: #ffffff;
        border: 1px solid #dce3ec;
        border-radius: 6px;
        padding: 24px 28px;
        margin-bottom: 18px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    }

    /* Section headers */
    .section-title {
        font-size: 1.05rem;
        font-weight: 600;
        color: #1e2a38;
        border-bottom: 2px solid #2c7be5;
        padding-bottom: 6px;
        margin-bottom: 16px;
    }

    /* Result box */
    .result-box {
        background: #eef4ff;
        border-left: 4px solid #2c7be5;
        border-radius: 4px;
        padding: 14px 18px;
        margin-top: 14px;
        font-family: 'Courier New', monospace;
        font-size: 0.95rem;
        color: #1a2b3c;
        white-space: pre-wrap;
    }

    /* Error box */
    .error-box {
        background: #fff0f0;
        border-left: 4px solid #d9534f;
        border-radius: 4px;
        padding: 12px 16px;
        margin-top: 12px;
        color: #a02020;
        font-size: 0.9rem;
    }

    /* Info box */
    .info-box {
        background: #f0f7ee;
        border-left: 4px solid #4caf50;
        border-radius: 4px;
        padding: 12px 16px;
        margin-top: 10px;
        font-size: 0.88rem;
        color: #2d5a27;
    }

    /* Formula display */
    .formula-box {
        background: #f8f9fb;
        border: 1px dashed #bbc8d8;
        border-radius: 4px;
        padding: 10px 14px;
        font-family: 'Courier New', monospace;
        font-size: 0.92rem;
        color: #3a4a5c;
        margin-bottom: 16px;
    }

    /* Units label */
    .unit-hint {
        font-size: 0.78rem;
        color: #7a8fa8;
        margin-top: -10px;
        margin-bottom: 8px;
    }

    /* Page title */
    .page-title {
        font-size: 1.7rem;
        font-weight: 700;
        color: #1e2a38;
        margin-bottom: 2px;
    }
    .page-subtitle {
        font-size: 0.93rem;
        color: #556677;
        margin-bottom: 24px;
    }

    /* Divider */
    hr { border-color: #dce3ec; }

    /* Button styling */
    .stButton > button {
        background-color: #2c7be5;
        color: white;
        border: none;
        border-radius: 4px;
        padding: 8px 22px;
        font-size: 0.9rem;
        font-weight: 500;
    }
    .stButton > button:hover {
        background-color: #1a63c4;
    }

    /* Input label */
    .stNumberInput label, .stTextInput label, .stSelectbox label {
        font-size: 0.88rem;
        color: #3a4a5c;
        font-weight: 500;
    }

    /* Table */
    .data-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.9rem;
        margin-top: 8px;
    }
    .data-table th {
        background: #2c7be5;
        color: white;
        padding: 8px 12px;
        text-align: center;
    }
    .data-table td {
        padding: 7px 12px;
        border-bottom: 1px solid #e4ecf4;
        text-align: center;
    }
    .data-table tr:nth-child(even) td { background: #f4f8ff; }
</style>
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
    """
    Fit Taylor's equation to (V, T) data using log-log linear regression.
    log(V) = log(C) - n * log(T)
    Returns (n, C, r_squared)
    """
    log_T = np.log(speeds)   # x-axis  (confusingly named, follows log(V) = f(log T))
    log_V = np.log(lives)
    # We regress log(V) on log(T): log(V) = a + b*log(T)
    # where b = -n and a = log(C)
    log_T_arr = np.log(np.array(lives))
    log_V_arr = np.log(np.array(speeds))
    coeffs = np.polyfit(log_T_arr, log_V_arr, 1)
    b, a = coeffs          # b = slope = -n, a = intercept = log(C)
    n = -b
    C = np.exp(a)
    # R-squared
    y_hat = np.polyval(coeffs, log_T_arr)
    ss_res = np.sum((log_V_arr - y_hat) ** 2)
    ss_tot = np.sum((log_V_arr - np.mean(log_V_arr)) ** 2)
    r2 = 1 - ss_res / ss_tot if ss_tot != 0 else 1.0
    return n, C, r2


def extended_taylor(V0, T0, n, f0, d0, x, y, z, delta_V, delta_f, delta_d):
    """
    Extended Taylor's equation: V * T^n * f^x * d^y = C_ext
    (or simplified single-parameter version when x=y=0)
    New tool life after parameter changes.
    """
    C_ext = V0 * (T0 ** n) * (f0 ** x) * (d0 ** y)
    V1 = V0 * (1 + delta_V / 100)
    f1 = f0 * (1 + delta_f / 100)
    d1 = d0 * (1 + delta_d / 100)
    # T1^n = C_ext / (V1 * f1^x * d1^y)
    T1 = (C_ext / (V1 * (f1 ** x) * (d1 ** y))) ** (1.0 / n)
    return T1, C_ext, V1, f1, d1


def compare_tools_crossover(n_A, C_A, n_B, C_B):
    """
    Find crossover speed where T_A = T_B.
    T_A = (C_A/V)^(1/n_A)  T_B = (C_B/V)^(1/n_B)
    Solved numerically.
    """
    from scipy.optimize import brentq
    def f(V):
        if V <= 0:
            return 1
        try:
            T_A = tool_life_from_C(V, C_A, n_A)
            T_B = tool_life_from_C(V, C_B, n_B)
            return T_A - T_B
        except Exception:
            return 0
    # Scan for sign change
    V_vals = np.linspace(1, max(C_A, C_B) * 2, 5000)
    signs = [np.sign(f(v)) for v in V_vals]
    crossover_V = None
    for i in range(len(signs) - 1):
        if signs[i] != signs[i + 1] and signs[i] != 0:
            try:
                crossover_V = brentq(f, V_vals[i], V_vals[i + 1])
                break
            except Exception:
                pass
    return crossover_V


# ─────────────────────────────────────────────
#  Plotting helpers
# ─────────────────────────────────────────────

def make_loglog_plot(speeds, lives, n=None, C=None, title="log(V) vs log(T)"):
    fig, ax = plt.subplots(figsize=(6.5, 4.2))
    ax.scatter(lives, speeds, color="#2c7be5", s=60, zorder=5, label="Data points")
    if n is not None and C is not None:
        T_fit = np.linspace(min(lives) * 0.5, max(lives) * 1.5, 300)
        V_fit = [cutting_speed_from_C(t, C, n) for t in T_fit]
        ax.plot(T_fit, V_fit, color="#d9534f", linewidth=1.6,
                label=f"Fit: n={n:.4f}, C={C:.3f}")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Tool Life T (min)", fontsize=10)
    ax.set_ylabel("Cutting Speed V (m/min)", fontsize=10)
    ax.set_title(title, fontsize=11, fontweight="bold", color="#1e2a38")
    ax.legend(fontsize=9)
    ax.grid(True, which="both", linestyle="--", linewidth=0.5, color="#c8d6e8")
    ax.xaxis.set_major_formatter(ticker.ScalarFormatter())
    ax.yaxis.set_major_formatter(ticker.ScalarFormatter())
    fig.tight_layout()
    return fig


def make_comparison_plot(n_A, C_A, n_B, C_B, crossover=None):
    V_max = max(C_A, C_B) * 1.2
    V_vals = np.linspace(1, V_max, 500)
    T_A = [tool_life_from_C(v, C_A, n_A) for v in V_vals]
    T_B = [tool_life_from_C(v, C_B, n_B) for v in V_vals]
    fig, ax = plt.subplots(figsize=(6.5, 4.2))
    ax.plot(V_vals, T_A, color="#2c7be5", linewidth=1.8, label="Tool A")
    ax.plot(V_vals, T_B, color="#d9534f", linewidth=1.8, label="Tool B")
    if crossover:
        ax.axvline(crossover, color="#4caf50", linestyle="--",
                   linewidth=1.2, label=f"Crossover V={crossover:.2f}")
    ax.set_xlabel("Cutting Speed V (m/s or m/min)", fontsize=10)
    ax.set_ylabel("Tool Life T (s or min)", fontsize=10)
    ax.set_title("Tool A vs Tool B — Life Comparison", fontsize=11,
                 fontweight="bold", color="#1e2a38")
    ax.legend(fontsize=9)
    ax.grid(True, linestyle="--", linewidth=0.5, color="#c8d6e8")
    fig.tight_layout()
    return fig


def fig_to_bytes(fig):
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=140)
    buf.seek(0)
    return buf


# ─────────────────────────────────────────────
#  Sidebar navigation
# ─────────────────────────────────────────────

with st.sidebar:
    st.markdown("## Taylor Tool Life Solver")
    st.markdown("*Engineering Calculator*")
    st.markdown("---")
    module = st.radio(
        "Select Module",
        options=[
            "1. Tool Comparison (A vs B)",
            "2. Tool Life Equation Solver",
            "3. Parameter Variation",
            "4. Find Constants from Data",
            "5. Graphical Solver",
            "6. Extended Taylor Equation",
        ],
    )
    st.markdown("---")
    st.markdown("""
**Reference Equations**

`VT^n = C`

`V · T^n · f^x · d^y = C`

`n = -slope (log-log)`

`C = e^intercept`
""")
    st.markdown("---")
    st.caption("Units must be consistent throughout each calculation.")


# ─────────────────────────────────────────────
#  Page header
# ─────────────────────────────────────────────

st.markdown('<div class="page-title">Taylor Tool Life Equation Solver</div>', unsafe_allow_html=True)
st.markdown('<div class="page-subtitle">A professional engineering calculator for machining and tool life analysis</div>', unsafe_allow_html=True)
st.markdown("---")


# ═══════════════════════════════════════════════════════════
#  MODULE 1 — Tool Comparison
# ═══════════════════════════════════════════════════════════

if module.startswith("1"):
    st.markdown("### Module 1 — Tool Comparison (A vs B)")
    st.markdown('<div class="formula-box">Tool A: V · T^n_A = C_A &nbsp;&nbsp;|&nbsp;&nbsp; Tool B: V · T^n_B = C_B</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="section-title">Tool A Parameters</div>', unsafe_allow_html=True)
        nA = st.number_input("Exponent n_A", value=0.22, format="%.4f", key="nA")
        CA = st.number_input("Constant C_A", value=42.5, format="%.4f", key="CA",
                             help="Obtained from V*T^n = C_A")

    with col2:
        st.markdown('<div class="section-title">Tool B Parameters</div>', unsafe_allow_html=True)
        nB = st.number_input("Exponent n_B", value=0.45, format="%.4f", key="nB")
        CB = st.number_input("Constant C_B", value=88.6, format="%.4f", key="CB")

    st.markdown('<div class="section-title">Evaluation Speed</div>', unsafe_allow_html=True)
    V_eval = st.number_input("Cutting Speed V (m/s)", value=1.0, format="%.4f", key="V_eval",
                              help="Speed at which to compare tool lives")

    c1, c2 = st.columns([1, 4])
    with c1:
        calc = st.button("Calculate", key="btn1")
    with c2:
        reset = st.button("Reset", key="rst1")

    if calc:
        try:
            if nA <= 0 or nB <= 0 or CA <= 0 or CB <= 0 or V_eval <= 0:
                st.markdown('<div class="error-box">All values must be positive and non-zero.</div>', unsafe_allow_html=True)
            else:
                T_A = tool_life_from_C(V_eval, CA, nA)
                T_B = tool_life_from_C(V_eval, CB, nB)
                winner = "Tool A" if T_A > T_B else ("Tool B" if T_B > T_A else "Both tools are equal")

                result_text = (
                    f"At V = {V_eval} m/s:\n"
                    f"  Tool A life  T_A = ({CA}/{V_eval})^(1/{nA}) = {T_A:.4f} s\n"
                    f"  Tool B life  T_B = ({CB}/{V_eval})^(1/{nB}) = {T_B:.4f} s\n\n"
                    f"  Difference   : {abs(T_A - T_B):.4f} s\n"
                    f"  Better tool  : {winner}"
                )
                st.markdown(f'<div class="result-box">{result_text}</div>', unsafe_allow_html=True)

                # Crossover analysis
                try:
                    from scipy.optimize import brentq
                    crossover = compare_tools_crossover(nA, CA, nB, CB)
                    if crossover:
                        cross_text = f"Crossover speed where T_A = T_B: V = {crossover:.4f} m/s"
                        st.markdown(f'<div class="info-box">{cross_text}</div>', unsafe_allow_html=True)
                except ImportError:
                    crossover = None

                # Plot
                fig = make_comparison_plot(nA, CA, nB, CB, crossover)
                st.pyplot(fig)

        except Exception as e:
            st.markdown(f'<div class="error-box">Calculation error: {e}</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
#  MODULE 2 — Tool Life Equation Solver
# ═══════════════════════════════════════════════════════════

elif module.startswith("2"):
    st.markdown("### Module 2 — Tool Life Equation Solver")
    st.markdown('<div class="formula-box">V · T^n = C &nbsp;&nbsp;— Solve for any one unknown given the other three</div>', unsafe_allow_html=True)

    solve_for = st.selectbox("Solve for", ["Tool Life T", "Cutting Speed V", "Constant C"])

    st.markdown('<div class="section-title">Known Values</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        n_val = st.number_input("Taylor exponent n", value=0.28, format="%.5f", key="n2")

    if solve_for == "Tool Life T":
        with col1:
            V_in = st.number_input("Cutting Speed V (m/min)", value=28.0, format="%.4f", key="V2")
        with col2:
            C_in = st.number_input("Constant C", value=None, format="%.4f", key="C2",
                                    placeholder="Enter C")

    elif solve_for == "Cutting Speed V":
        with col1:
            T_in = st.number_input("Tool Life T (min)", value=60.0, format="%.4f", key="T2v")
        with col2:
            C_in = st.number_input("Constant C", value=None, format="%.4f", key="C2v",
                                    placeholder="Enter C")

    else:  # Solve for C
        with col1:
            V_in = st.number_input("Cutting Speed V (m/min)", value=28.0, format="%.4f", key="V2c")
        with col2:
            T_in = st.number_input("Tool Life T (min)", value=60.0, format="%.4f", key="T2c")

    c1, c2 = st.columns([1, 4])
    with c1:
        calc2 = st.button("Calculate", key="btn2")

    if calc2:
        try:
            if n_val <= 0:
                st.markdown('<div class="error-box">Exponent n must be positive.</div>', unsafe_allow_html=True)
            elif solve_for == "Tool Life T":
                if C_in is None or C_in <= 0 or V_in <= 0:
                    st.markdown('<div class="error-box">V and C must be positive.</div>', unsafe_allow_html=True)
                else:
                    T_out = tool_life_from_C(V_in, C_in, n_val)
                    res = (
                        f"Formula : T = (C / V)^(1/n)\n"
                        f"        = ({C_in} / {V_in})^(1/{n_val})\n"
                        f"        = {T_out:.4f} min"
                    )
                    st.markdown(f'<div class="result-box">{res}</div>', unsafe_allow_html=True)

            elif solve_for == "Cutting Speed V":
                if C_in is None or C_in <= 0 or T_in <= 0:
                    st.markdown('<div class="error-box">T and C must be positive.</div>', unsafe_allow_html=True)
                else:
                    V_out = cutting_speed_from_C(T_in, C_in, n_val)
                    res = (
                        f"Formula : V = C / T^n\n"
                        f"        = {C_in} / {T_in}^{n_val}\n"
                        f"        = {V_out:.4f} m/min"
                    )
                    st.markdown(f'<div class="result-box">{res}</div>', unsafe_allow_html=True)

            else:
                if V_in <= 0 or T_in <= 0:
                    st.markdown('<div class="error-box">V and T must be positive.</div>', unsafe_allow_html=True)
                else:
                    C_out = taylor_constant(V_in, T_in, n_val)
                    res = (
                        f"Formula : C = V * T^n\n"
                        f"        = {V_in} * {T_in}^{n_val}\n"
                        f"        = {C_out:.4f}"
                    )
                    st.markdown(f'<div class="result-box">{res}</div>', unsafe_allow_html=True)

        except Exception as e:
            st.markdown(f'<div class="error-box">Calculation error: {e}</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
#  MODULE 3 — Parameter Variation (25% increase)
# ═══════════════════════════════════════════════════════════

elif module.startswith("3"):
    st.markdown("### Module 3 — Parameter Variation Analysis")
    st.markdown('<div class="formula-box">Extended: V · T^n · f^x · d^y = C_ext &nbsp;&nbsp;(or standard: V · T^n = C with speed change only)</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="section-title">Base Operating Conditions</div>', unsafe_allow_html=True)
        V0 = st.number_input("Base Cutting Speed V0 (m/min)", value=28.0, format="%.4f", key="V0")
        T0 = st.number_input("Base Tool Life T0 (min)", value=60.0, format="%.4f", key="T0")
        n3 = st.number_input("Taylor exponent n", value=0.14, format="%.5f", key="n3")

    with col2:
        st.markdown('<div class="section-title">Extended Equation Parameters (optional)</div>', unsafe_allow_html=True)
        use_extended = st.checkbox("Use extended equation (with feed and depth of cut)")
        f0 = st.number_input("Base Feed f0 (mm/rev)", value=0.3, format="%.4f", key="f0",
                              disabled=not use_extended)
        d0 = st.number_input("Base Depth of Cut d0 (mm)", value=2.6, format="%.4f", key="d0",
                              disabled=not use_extended)
        x_exp = st.number_input("Feed exponent x", value=0.78, format="%.4f", key="xexp",
                                 disabled=not use_extended)
        y_exp = st.number_input("Depth exponent y", value=0.28, format="%.4f", key="yexp",
                                 disabled=not use_extended)

    st.markdown('<div class="section-title">Percentage Changes</div>', unsafe_allow_html=True)
    col3, col4, col5 = st.columns(3)
    with col3:
        dV = st.number_input("Change in Speed (%)", value=25.0, format="%.2f", key="dV")
    with col4:
        df = st.number_input("Change in Feed (%)", value=0.0, format="%.2f", key="df",
                              disabled=not use_extended)
    with col5:
        dd = st.number_input("Change in Depth (%)", value=0.0, format="%.2f", key="dd",
                              disabled=not use_extended)

    c1, c2 = st.columns([1, 4])
    with c1:
        calc3 = st.button("Calculate", key="btn3")

    if calc3:
        try:
            if V0 <= 0 or T0 <= 0 or n3 <= 0:
                st.markdown('<div class="error-box">Base values must be positive.</div>', unsafe_allow_html=True)
            else:
                if use_extended:
                    x, y = x_exp, y_exp
                    f_use, d_use = f0, d0
                    df_use, dd_use = df, dd
                else:
                    x, y = 0.0, 0.0
                    f_use, d_use = 1.0, 1.0
                    df_use, dd_use = 0.0, 0.0

                T1, C_ext, V1, f1, d1 = extended_taylor(
                    V0, T0, n3, f_use, d_use, x, y, 0,
                    dV, df_use, dd_use
                )

                pct_change = (T1 - T0) / T0 * 100

                if use_extended:
                    res = (
                        f"Base constant C_ext = V0 * T0^n * f0^x * d0^y\n"
                        f"                    = {V0} * {T0}^{n3} * {f_use}^{x} * {d_use}^{y}\n"
                        f"                    = {C_ext:.5f}\n\n"
                        f"New conditions:\n"
                        f"  V1 = {V1:.4f} m/min  ({dV:+.1f}%)\n"
                        f"  f1 = {f1:.4f} mm/rev  ({df_use:+.1f}%)\n"
                        f"  d1 = {d1:.4f} mm     ({dd_use:+.1f}%)\n\n"
                        f"New tool life T1 = {T1:.4f} min\n"
                        f"Change in life   : {pct_change:+.2f}%"
                    )
                else:
                    C_base = taylor_constant(V0, T0, n3)
                    res = (
                        f"Base constant C = V0 * T0^n\n"
                        f"               = {V0} * {T0}^{n3}\n"
                        f"               = {C_base:.5f}\n\n"
                        f"New speed V1   = {V1:.4f} m/min  ({dV:+.1f}%)\n\n"
                        f"New tool life T1 = (C/V1)^(1/n)\n"
                        f"               = ({C_base:.5f}/{V1:.4f})^(1/{n3})\n"
                        f"               = {T1:.4f} min\n\n"
                        f"Change in life : {pct_change:+.2f}%"
                    )

                st.markdown(f'<div class="result-box">{res}</div>', unsafe_allow_html=True)

                # Bar chart comparison
                fig, ax = plt.subplots(figsize=(5, 3.2))
                bars = ax.bar(["Base T0", "New T1"], [T0, T1],
                              color=["#2c7be5", "#d9534f"], width=0.4)
                ax.set_ylabel("Tool Life (min)", fontsize=10)
                ax.set_title("Tool Life Comparison", fontsize=11, fontweight="bold", color="#1e2a38")
                for bar, val in zip(bars, [T0, T1]):
                    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                            f"{val:.2f}", ha="center", va="bottom", fontsize=10)
                ax.grid(axis="y", linestyle="--", linewidth=0.5, color="#c8d6e8")
                ax.set_ylim(0, max(T0, T1) * 1.25)
                fig.tight_layout()
                st.pyplot(fig)

        except Exception as e:
            st.markdown(f'<div class="error-box">Calculation error: {e}</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
#  MODULE 4 — Find Constants from Data
# ═══════════════════════════════════════════════════════════

elif module.startswith("4"):
    st.markdown("### Module 4 — Find n and C from Experimental Data")
    st.markdown('<div class="formula-box">log(V) = log(C) − n · log(T) &nbsp;&nbsp;=> Fit a straight line in log-log space</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-title">Enter Cutting Speed and Tool Life Pairs</div>', unsafe_allow_html=True)
    st.caption("Enter at least 2 data points. Example from textbook: V = [52, 50, 49, 46, 42], T = [3, 4, 4.9, 10.5, 30]")

    col1, col2 = st.columns(2)
    with col1:
        speeds_input = st.text_input(
            "Cutting Speeds V (m/min) — comma separated",
            value="52, 50, 49, 46, 42",
            key="speeds_in"
        )
    with col2:
        lives_input = st.text_input(
            "Tool Lives T (min) — comma separated",
            value="3, 4, 4.9, 10.5, 30",
            key="lives_in"
        )

    c1, c2 = st.columns([1, 4])
    with c1:
        calc4 = st.button("Calculate", key="btn4")

    if calc4:
        try:
            speeds = [float(v.strip()) for v in speeds_input.split(",")]
            lives = [float(t.strip()) for t in lives_input.split(",")]

            if len(speeds) != len(lives):
                st.markdown('<div class="error-box">Number of speed values must equal number of tool life values.</div>', unsafe_allow_html=True)
            elif len(speeds) < 2:
                st.markdown('<div class="error-box">At least 2 data points are required.</div>', unsafe_allow_html=True)
            elif any(v <= 0 for v in speeds) or any(t <= 0 for t in lives):
                st.markdown('<div class="error-box">All values must be positive.</div>', unsafe_allow_html=True)
            else:
                n_fit, C_fit, r2 = find_n_and_C(speeds, lives)

                # Data table
                rows = "".join(
                    f"<tr><td>{i+1}</td><td>{speeds[i]}</td><td>{lives[i]}</td>"
                    f"<td>{cutting_speed_from_C(lives[i], C_fit, n_fit):.3f}</td></tr>"
                    for i in range(len(speeds))
                )
                table_html = f"""
                <table class="data-table">
                  <tr>
                    <th>#</th>
                    <th>V (m/min)</th>
                    <th>T (min)</th>
                    <th>V_fitted (m/min)</th>
                  </tr>
                  {rows}
                </table>
                """
                st.markdown(table_html, unsafe_allow_html=True)

                res = (
                    f"Fitted Taylor constants:\n"
                    f"  n = {n_fit:.5f}\n"
                    f"  C = {C_fit:.4f}\n"
                    f"  R² = {r2:.6f}\n\n"
                    f"Taylor equation: V * T^{n_fit:.5f} = {C_fit:.4f}"
                )
                st.markdown(f'<div class="result-box">{res}</div>', unsafe_allow_html=True)

                # Log-log plot
                fig = make_loglog_plot(speeds, lives, n_fit, C_fit,
                                       title="Experimental Data — log(V) vs log(T)")
                st.pyplot(fig)

        except ValueError:
            st.markdown('<div class="error-box">Invalid input. Ensure all values are numbers separated by commas.</div>', unsafe_allow_html=True)
        except Exception as e:
            st.markdown(f'<div class="error-box">Calculation error: {e}</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
#  MODULE 5 — Graphical Solver
# ═══════════════════════════════════════════════════════════

elif module.startswith("5"):
    st.markdown("### Module 5 — Graphical Solver (log-log plot)")
    st.markdown('<div class="formula-box">Plot log(V) vs log(T). Slope = -n. Intercept = log(C).</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-title">Data Input</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        g_speeds = st.text_input("Cutting Speeds V (m/min)", value="52, 50, 49, 46, 42", key="g_speeds")
    with col2:
        g_lives = st.text_input("Tool Lives T (min)", value="3, 4, 4.9, 10.5, 30", key="g_lives")

    st.markdown('<div class="section-title">Predict Tool Life at a Specific Speed</div>', unsafe_allow_html=True)
    V_predict = st.number_input("Predict tool life at V =", value=35.0, format="%.4f", key="V_predict")

    c1, c2 = st.columns([1, 4])
    with c1:
        calc5 = st.button("Plot & Solve", key="btn5")

    if calc5:
        try:
            speeds5 = [float(v.strip()) for v in g_speeds.split(",")]
            lives5 = [float(t.strip()) for t in g_lives.split(",")]

            if len(speeds5) != len(lives5) or len(speeds5) < 2:
                st.markdown('<div class="error-box">Need equal and at least 2 data points.</div>', unsafe_allow_html=True)
            else:
                n5, C5, r2_5 = find_n_and_C(speeds5, lives5)
                T_pred = tool_life_from_C(V_predict, C5, n5)

                log_T = np.log10(lives5)
                log_V = np.log10(speeds5)
                coeffs = np.polyfit(log_T, log_V, 1)
                slope = coeffs[0]   # = -n
                intercept = coeffs[1]  # = log10(C)

                res = (
                    f"Log-log linear fit:\n"
                    f"  log(V) = {intercept:.5f} + ({slope:.5f}) * log(T)\n"
                    f"  Slope      = {slope:.5f}  =>  n = {-slope:.5f}\n"
                    f"  Intercept  = {intercept:.5f}  =>  C = 10^{intercept:.5f} = {10**intercept:.4f}\n\n"
                    f"  R^2 = {r2_5:.6f}\n\n"
                    f"Tool life at V = {V_predict} m/min:\n"
                    f"  T = (C/V)^(1/n) = ({C5:.4f}/{V_predict})^(1/{n5:.5f})\n"
                    f"  T = {T_pred:.4f} min"
                )
                st.markdown(f'<div class="result-box">{res}</div>', unsafe_allow_html=True)

                # Enhanced plot: both log-log and linear-scale
                fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.5))

                # Log-log plot
                T_range = np.linspace(min(lives5) * 0.5, max(lives5) * 1.8, 400)
                V_fit = [cutting_speed_from_C(t, C5, n5) for t in T_range]
                ax1.scatter(lives5, speeds5, color="#2c7be5", s=60, zorder=5, label="Data")
                ax1.plot(T_range, V_fit, color="#d9534f", lw=1.6, label="Fitted line")
                ax1.axvline(T_pred, color="#4caf50", linestyle=":", lw=1.2,
                            label=f"T={T_pred:.2f} at V={V_predict}")
                ax1.axhline(V_predict, color="#4caf50", linestyle=":", lw=1.2)
                ax1.set_xscale("log"); ax1.set_yscale("log")
                ax1.set_xlabel("T (min)"); ax1.set_ylabel("V (m/min)")
                ax1.set_title("log(V) vs log(T)", fontweight="bold", color="#1e2a38")
                ax1.legend(fontsize=8)
                ax1.grid(True, which="both", ls="--", lw=0.5, color="#c8d6e8")
                ax1.xaxis.set_major_formatter(ticker.ScalarFormatter())
                ax1.yaxis.set_major_formatter(ticker.ScalarFormatter())

                # Linear log scale axes
                ax2.scatter(log_T, log_V, color="#2c7be5", s=60, zorder=5, label="Data")
                lT_range = np.linspace(min(log_T) - 0.2, max(log_T) + 0.2, 200)
                lV_fit = np.polyval(coeffs, lT_range)
                ax2.plot(lT_range, lV_fit, color="#d9534f", lw=1.6, label="Fit")
                ax2.set_xlabel("log(T)"); ax2.set_ylabel("log(V)")
                ax2.set_title(f"Linear log space  |  slope={slope:.4f}", fontweight="bold", color="#1e2a38")
                ax2.legend(fontsize=8)
                ax2.grid(True, ls="--", lw=0.5, color="#c8d6e8")

                fig.tight_layout()
                st.pyplot(fig)

        except ValueError:
            st.markdown('<div class="error-box">Invalid data. Check that all entries are numeric.</div>', unsafe_allow_html=True)
        except Exception as e:
            st.markdown(f'<div class="error-box">Calculation error: {e}</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
#  MODULE 6 — Extended Taylor Equation
# ═══════════════════════════════════════════════════════════

elif module.startswith("6"):
    st.markdown("### Module 6 — Extended Taylor Equation")
    st.markdown('<div class="formula-box">V · T^n · f^x · d^y = C_ext</div>', unsafe_allow_html=True)
    st.markdown("Solve for tool life T given a reference condition and a new set of parameters.")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="section-title">Reference / Calibration Condition</div>', unsafe_allow_html=True)
        V_ref = st.number_input("Reference Speed V_ref (m/min)", value=28.0, format="%.4f", key="Vref6")
        T_ref = st.number_input("Reference Tool Life T_ref (min)", value=60.0, format="%.4f", key="Tref6")
        f_ref = st.number_input("Reference Feed f_ref (mm/rev)", value=0.3, format="%.4f", key="fref6")
        d_ref = st.number_input("Reference Depth d_ref (mm)", value=2.6, format="%.4f", key="dref6")

    with col2:
        st.markdown('<div class="section-title">Equation Exponents</div>', unsafe_allow_html=True)
        n6 = st.number_input("Taylor exponent n", value=0.14, format="%.5f", key="n6")
        x6 = st.number_input("Feed exponent x", value=0.78, format="%.5f", key="x6")
        y6 = st.number_input("Depth exponent y", value=0.28, format="%.5f", key="y6")

        st.markdown('<div class="section-title">New Operating Conditions</div>', unsafe_allow_html=True)
        V_new = st.number_input("New Speed V (m/min)", value=35.0, format="%.4f", key="Vnew6")
        f_new = st.number_input("New Feed f (mm/rev)", value=0.375, format="%.4f", key="fnew6")
        d_new = st.number_input("New Depth d (mm)", value=3.25, format="%.4f", key="dnew6")

    c1, c2 = st.columns([1, 4])
    with c1:
        calc6 = st.button("Calculate", key="btn6")

    if calc6:
        try:
            if any(v <= 0 for v in [V_ref, T_ref, f_ref, d_ref, n6, x6, y6, V_new, f_new, d_new]):
                st.markdown('<div class="error-box">All values must be positive.</div>', unsafe_allow_html=True)
            else:
                C_ext = V_ref * (T_ref ** n6) * (f_ref ** x6) * (d_ref ** y6)
                # Solve: T_new = (C_ext / (V_new * f_new^x * d_new^y))^(1/n)
                T_new = (C_ext / (V_new * (f_new ** x6) * (d_new ** y6))) ** (1.0 / n6)
                pct = (T_new - T_ref) / T_ref * 100

                res = (
                    f"Extended constant C_ext = V_ref * T_ref^n * f_ref^x * d_ref^y\n"
                    f"  = {V_ref} * {T_ref}^{n6} * {f_ref}^{x6} * {d_ref}^{y6}\n"
                    f"  = {C_ext:.6f}\n\n"
                    f"New tool life T_new = (C_ext / (V * f^x * d^y))^(1/n)\n"
                    f"  = ({C_ext:.4f} / ({V_new} * {f_new}^{x6} * {d_new}^{y6}))^(1/{n6})\n"
                    f"  = {T_new:.4f} min\n\n"
                    f"Change in life : {pct:+.2f}%"
                )
                st.markdown(f'<div class="result-box">{res}</div>', unsafe_allow_html=True)

        except Exception as e:
            st.markdown(f'<div class="error-box">Calculation error: {e}</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  Footer
# ─────────────────────────────────────────────
st.markdown("---")
st.caption(
    "Taylor Tool Life Solver — For academic and laboratory use. "
    "Ensure consistent units across all inputs. "
    "Taylor's equation: V·T^n = C"
)

import json
from pathlib import Path

import pandas as pd
import streamlit as st


def render_html(html: str) -> None:
    """Render an HTML block via st.markdown safely.

    Streamlit's Markdown parser treats any line indented 4+ spaces as a
    fenced code block (standard Markdown behavior). Since our HTML is
    built from nested, indented f-strings/triple-quoted blocks, that
    indentation would otherwise get rendered as literal code instead of
    live HTML. Stripping leading/trailing whitespace per line avoids it.
    """
    st.markdown(
        "\n".join(line.strip() for line in html.strip().split("\n")),
        unsafe_allow_html=True,
    )


# ============================================================
# CONFIGURATION
# ============================================================

# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

RUNS_DIR = PROJECT_ROOT / "runs"

st.set_page_config(
    page_title="Presales AI Orchestrator",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# DESIGN TOKENS + GLOBAL STYLES
# ============================================================
# Aesthetic: a mission-control console for a multi-agent DAG.
# Deep-space navy surfaces, a signal-cyan accent for anything
# "live", and a monospace display face for IDs/durations so the
# page reads like flight telemetry rather than a generic admin
# panel. The signature element is the vertical "signal rail"
# that runs the DAG section — a pulsing node per layer, wired
# into a single continuous line, standing in for the arrows a
# typical DAG diagram would use.

st.markdown(
    """
    <style>

    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&family=Inter:wght@400;500;600;700;800&display=swap');

    :root{
        --bg-void: #0B1120;
        --bg-panel: #121A2C;
        --bg-panel-raised: #182238;
        --border-steel: #223049;
        --border-steel-soft: #1A2438;
        --text-primary: #E7ECF5;
        --text-secondary: #7C8BA8;
        --text-tertiary: #4E5C78;
        --accent-signal: #22D3EE;
        --accent-signal-dim: rgba(34, 211, 238, 0.12);
        --status-success: #34D399;
        --status-success-dim: rgba(52, 211, 153, 0.10);
        --status-warning: #FBBF24;
        --status-warning-dim: rgba(251, 191, 36, 0.10);
        --status-danger: #F87171;
        --status-danger-dim: rgba(248, 113, 113, 0.10);
        --status-pending: #52627A;
        --status-pending-dim: rgba(82, 98, 122, 0.10);
        --font-display: 'JetBrains Mono', ui-monospace, monospace;
        --font-body: 'Inter', -apple-system, sans-serif;
    }

    /* ---------- App shell ---------- */

    .stApp{
        background: var(--bg-void);
        font-family: var(--font-body);
    }

    .block-container{
        max-width: 1440px;
        padding-top: 1.6rem;
        padding-bottom: 3rem;
    }

    [data-testid="stSidebar"]{
        background: var(--bg-panel);
        border-right: 1px solid var(--border-steel);
    }

    [data-testid="stSidebar"] *{
        color: var(--text-primary);
    }

    [data-testid="stSidebar"] hr{
        border-color: var(--border-steel);
    }

    h1, h2, h3, h4, h5, h6, p, span, label, div{
        color: var(--text-primary);
    }

    /* Selectbox / multiselect chrome */
    [data-baseweb="select"] > div{
        background: var(--bg-panel-raised) !important;
        border-color: var(--border-steel) !important;
        font-family: var(--font-display);
        font-size: 13px;
    }
    [data-baseweb="popover"] li{
        font-family: var(--font-display);
        font-size: 13px;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"]{
        gap: 4px;
        border-bottom: 1px solid var(--border-steel);
    }
    .stTabs [data-baseweb="tab"]{
        font-family: var(--font-display);
        font-size: 12px;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        color: var(--text-secondary);
        padding: 10px 4px;
    }
    .stTabs [aria-selected="true"]{
        color: var(--accent-signal) !important;
        border-bottom-color: var(--accent-signal) !important;
    }

    /* Expander */
    [data-testid="stExpander"]{
        background: var(--bg-panel);
        border: 1px solid var(--border-steel);
        border-radius: 10px;
    }
    [data-testid="stExpander"] summary{
        font-family: var(--font-display);
        font-size: 13px;
    }

    /* Dataframe */
    [data-testid="stDataFrame"]{
        border: 1px solid var(--border-steel);
        border-radius: 10px;
        overflow: hidden;
    }

    /* Alerts */
    [data-testid="stAlert"]{
        background: var(--bg-panel-raised);
        border: 1px solid var(--border-steel);
        border-radius: 10px;
    }

    code{
        font-family: var(--font-display) !important;
        background: var(--bg-panel-raised) !important;
        color: var(--accent-signal) !important;
        border: 1px solid var(--border-steel);
    }

    /* ---------- Console header ---------- */

    .console-header{
        background: var(--bg-panel);
        border: 1px solid var(--border-steel);
        border-radius: 14px;
        padding: 20px 26px;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        flex-wrap: wrap;
        gap: 14px;
    }

    .console-title-block{
        display: flex;
        flex-direction: column;
        gap: 4px;
    }

    .console-eyebrow{
        font-family: var(--font-display);
        font-size: 11px;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        color: var(--text-tertiary);
    }

    .console-title{
        font-family: var(--font-body);
        font-weight: 800;
        font-size: 24px;
        letter-spacing: -0.01em;
    }

    .console-meta{
        font-family: var(--font-display);
        font-size: 13px;
        color: var(--text-secondary);
    }

    .console-meta b{
        color: var(--text-primary);
        font-weight: 600;
    }

    .led-status{
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 8px 16px;
        border-radius: 999px;
        border: 1px solid var(--border-steel);
        background: var(--bg-panel-raised);
        font-family: var(--font-display);
        font-size: 12px;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }

    .led-dot{
        width: 9px;
        height: 9px;
        border-radius: 50%;
        flex-shrink: 0;
    }

    .led-dot.pulse{
        animation: pulse-ring 1.6s ease-in-out infinite;
    }

    @keyframes pulse-ring{
        0%   { box-shadow: 0 0 0 0 currentColor; opacity: 1; }
        70%  { box-shadow: 0 0 0 6px transparent; opacity: 0.7; }
        100% { box-shadow: 0 0 0 0 transparent; opacity: 1; }
    }

    /* ---------- KPI strip ---------- */

    .kpi-strip{
        display: grid;
        grid-template-columns: repeat(5, 1fr);
        gap: 12px;
        margin-bottom: 22px;
    }

    .kpi-cell{
        background: var(--bg-panel);
        border: 1px solid var(--border-steel);
        border-radius: 12px;
        padding: 16px 18px;
    }

    .kpi-label{
        font-family: var(--font-display);
        font-size: 10.5px;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: var(--text-tertiary);
        margin-bottom: 10px;
    }

    .kpi-value{
        font-family: var(--font-display);
        font-size: 26px;
        font-weight: 700;
        color: var(--text-primary);
        display: flex;
        align-items: baseline;
        gap: 8px;
    }

    .kpi-value small{
        font-size: 13px;
        color: var(--text-tertiary);
        font-weight: 500;
    }

    /* ---------- Section label ---------- */

    .rail-section-title{
        font-family: var(--font-display);
        font-size: 12px;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: var(--text-secondary);
        margin: 28px 0 14px 0;
        display: flex;
        align-items: center;
        gap: 10px;
    }

    .rail-section-title::before{
        content: "";
        width: 3px;
        height: 14px;
        background: var(--accent-signal);
        border-radius: 2px;
    }

    /* ---------- Signal rail DAG ---------- */

    .dag-frame{
        background: var(--bg-panel);
        border: 1px solid var(--border-steel);
        border-radius: 14px;
        padding: 26px 26px 10px 26px;
    }

    .orchestrator-row{
        display: flex;
        justify-content: center;
        margin-bottom: 22px;
    }

    .orchestrator-node{
        border: 1px solid var(--accent-signal);
        background: var(--accent-signal-dim);
        border-radius: 10px;
        padding: 12px 26px;
        text-align: center;
    }

    .orchestrator-node .o-name{
        font-family: var(--font-display);
        font-weight: 700;
        font-size: 14px;
        color: var(--accent-signal);
        letter-spacing: 0.03em;
    }

    .orchestrator-node .o-sub{
        font-family: var(--font-display);
        font-size: 10.5px;
        color: var(--text-secondary);
        letter-spacing: 0.06em;
        text-transform: uppercase;
        margin-top: 3px;
    }

    .rail{
        position: relative;
        padding-left: 30px;
    }

    .rail::before{
        content: "";
        position: absolute;
        left: 9px;
        top: 6px;
        bottom: 6px;
        width: 2px;
        background: linear-gradient(to bottom, var(--border-steel), var(--border-steel) 100%);
    }

    .layer-row{
        position: relative;
        margin-bottom: 18px;
    }

    .rail-node{
        position: absolute;
        left: -30px;
        top: 18px;
        width: 20px;
        height: 20px;
        border-radius: 50%;
        border: 2px solid var(--border-steel);
        background: var(--bg-panel);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 2;
    }

    .rail-node-dot{
        width: 8px;
        height: 8px;
        border-radius: 50%;
    }

    .layer-panel{
        background: var(--bg-panel-raised);
        border: 1px solid var(--border-steel-soft);
        border-radius: 12px;
        padding: 16px 18px;
    }

    .layer-panel.is-current{
        border-color: var(--accent-signal);
        box-shadow: 0 0 0 1px var(--accent-signal), 0 0 24px -8px var(--accent-signal);
    }

    .layer-heading{
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 14px;
    }

    .layer-heading-label{
        font-family: var(--font-display);
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 0.08em;
        color: var(--text-secondary);
    }

    .layer-current-tag{
        font-family: var(--font-display);
        font-size: 10px;
        letter-spacing: 0.1em;
        color: var(--accent-signal);
        border: 1px solid var(--accent-signal);
        border-radius: 999px;
        padding: 2px 8px;
    }

    .agent-grid{
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
    }

    .agent-card{
        flex: 1 1 200px;
        max-width: 240px;
        background: var(--bg-panel);
        border-radius: 10px;
        padding: 13px 14px;
        border-left: 3px solid var(--status-pending);
    }

    .agent-card.st-completed{ border-left-color: var(--status-success); }
    .agent-card.st-running{ border-left-color: var(--accent-signal); background: var(--accent-signal-dim); }
    .agent-card.st-blocked{ border-left-color: var(--status-warning); }
    .agent-card.st-failed{ border-left-color: var(--status-danger); }
    .agent-card.st-pending{ border-left-color: var(--status-pending); opacity: 0.72; }

    .agent-card .a-id{
        font-family: var(--font-display);
        font-weight: 700;
        font-size: 13px;
        color: var(--text-primary);
    }

    .agent-card .a-type{
        font-family: var(--font-body);
        font-size: 12px;
        color: var(--text-secondary);
        margin-top: 2px;
    }

    .agent-card .a-footer{
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-top: 12px;
    }

    .status-chip{
        font-family: var(--font-display);
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 0.06em;
        padding: 3px 8px;
        border-radius: 5px;
    }

    .chip-completed{ color: var(--status-success); background: var(--status-success-dim); }
    .chip-running{ color: var(--accent-signal); background: var(--accent-signal-dim); }
    .chip-blocked{ color: var(--status-warning); background: var(--status-warning-dim); }
    .chip-failed{ color: var(--status-danger); background: var(--status-danger-dim); }
    .chip-pending{ color: var(--status-pending); background: var(--status-pending-dim); }

    .a-duration{
        font-family: var(--font-display);
        font-size: 11px;
        color: var(--text-tertiary);
    }

    /* ---------- Legend ---------- */

    .legend-row{
        display: flex;
        align-items: center;
        gap: 8px;
        font-family: var(--font-display);
        font-size: 12.5px;
        color: var(--text-secondary);
        padding: 4px 0;
    }

    .legend-dot{
        width: 8px;
        height: 8px;
        border-radius: 50%;
        flex-shrink: 0;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# STATUS CONFIG
# ============================================================

STATUS_CONFIG = {
    "completed": {"label": "COMPLETED", "color": "var(--status-success)", "class": "completed", "pulse": False},
    "running":   {"label": "RUNNING",   "color": "var(--accent-signal)",  "class": "running",   "pulse": True},
    "blocked":   {"label": "BLOCKED",   "color": "var(--status-warning)", "class": "blocked",   "pulse": False},
    "failed":    {"label": "FAILED",    "color": "var(--status-danger)",  "class": "failed",    "pulse": False},
    "pending":   {"label": "PENDING",   "color": "var(--status-pending)", "class": "pending",   "pulse": False},
}


def get_status_config(status):
    return STATUS_CONFIG.get(status, STATUS_CONFIG["pending"])


# ============================================================
# DATA LOADING
# ============================================================

def get_runs():
    if not RUNS_DIR.exists():
        return []

    runs=[]
    for run_dir in  RUNS_DIR.iterdir():
        if not run_dir.is_dir():
            continue
        execution_file = run_dir / "execution.json"

        if not execution_file.exists():
            continue

        runs.append(run_dir)
    return sorted(
        runs,
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )


def load_run(run_dir):
    execution_file = run_dir / "execution.json"
    if not execution_file.exists():
        return None
    try:
        with open(execution_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as exc:
        st.error(f"Failed to load execution.json: {exc}")
        return None


runs = get_runs()

if not runs:
    st.warning("No workflow executions found in `runs/`.")
    st.stop()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.markdown(
        "<div class='console-eyebrow' style='margin-bottom:2px;'>WORKFLOW MONITOR</div>"
        "<div style='font-family:var(--font-display); font-weight:700; font-size:17px; "
        "margin-bottom:18px;'>◈ Mission Control</div>",
        unsafe_allow_html=True,
    )

    selected_run = st.selectbox(
        "EXECUTION RUN",
        runs,
        format_func=lambda p: p.name,
    )

    st.divider()

    st.markdown(
        "<div class='console-eyebrow' style='margin-bottom:10px;'>STATUS LEGEND</div>",
        unsafe_allow_html=True,
    )

    legend_html = ""
    for key, cfg in STATUS_CONFIG.items():
        legend_html += (
            f"<div class='legend-row'>"
            f"<span class='legend-dot' style='background:{cfg['color']};'></span>"
            f"{cfg['label']}</div>"
        )
    st.markdown(legend_html, unsafe_allow_html=True)


execution = load_run(selected_run)

if execution is None:
    st.error("Unable to load selected workflow.")
    st.stop()


# ============================================================
# BASIC DATA
# ============================================================

workflow_id = execution.get("workflow_id", "Unknown")
workflow_status = execution.get("status", "unknown")
current_layer = execution.get("current_layer")
duration = execution.get("duration_seconds")
nodes = execution.get("nodes", {})
layers = execution.get("layers", {})


# ============================================================
# HEADER
# ============================================================

overall_cfg = get_status_config(workflow_status)
pulse_class = "pulse" if overall_cfg["pulse"] else ""

render_html(
    f"""
    <div class="console-header">
        <div class="console-title-block">
            <div class="console-eyebrow">DYNAMIC DAG EXECUTION MONITOR</div>
            <div class="console-title">◈ Presales Multi-Agent Orchestrator</div>
            <div class="console-meta">RUN <b>{workflow_id}</b></div>
        </div>
        <div class="led-status" style="color:{overall_cfg['color']};">
            <span class="led-dot {pulse_class}" style="background:{overall_cfg['color']}; color:{overall_cfg['color']};"></span>
            {overall_cfg['label']}
        </div>
    </div>
    """
)


# ============================================================
# KPI CALCULATIONS
# ============================================================

counts = {"completed": 0, "running": 0, "failed": 0, "blocked": 0, "pending": 0}
for node in nodes.values():
    status = node.get("status", "pending")
    counts[status] = counts.get(status, 0) + 1


kpi_html = f"""
<div class="kpi-strip">
    <div class="kpi-cell">
        <div class="kpi-label">Total Agents</div>
        <div class="kpi-value">{len(nodes)}</div>
    </div>
    <div class="kpi-cell">
        <div class="kpi-label">Completed</div>
        <div class="kpi-value" style="color:var(--status-success);">{counts['completed']}</div>
    </div>
    <div class="kpi-cell">
        <div class="kpi-label">Running</div>
        <div class="kpi-value" style="color:var(--accent-signal);">{counts['running']}</div>
    </div>
    <div class="kpi-cell">
        <div class="kpi-label">Failed / Blocked</div>
        <div class="kpi-value">
            <span style="color:var(--status-danger);">{counts['failed']}</span>
            <small>/</small>
            <span style="color:var(--status-warning);">{counts['blocked']}</span>
        </div>
    </div>
    <div class="kpi-cell">
        <div class="kpi-label">Current Layer</div>
        <div class="kpi-value">{current_layer if current_layer is not None else "—"}</div>
    </div>
</div>
"""
render_html(kpi_html)


# ============================================================
# DAG VISUALIZATION — signal rail
# ============================================================

st.markdown("<div class='rail-section-title'>EXECUTION DAG</div>", unsafe_allow_html=True)

sorted_layers = sorted(layers.items(), key=lambda item: int(item[0]))

rail_rows_html = ""

for layer_number, node_ids in sorted_layers:
    try:
        layer_number_int = int(layer_number)
    except Exception:
        layer_number_int = layer_number

    is_current = current_layer == layer_number_int or current_layer == str(layer_number)

    # Determine the rail-node color: worst status present in the layer wins,
    # falling back to "completed" green if everything in it is done.
    layer_statuses = [nodes.get(nid, {}).get("status", "pending") for nid in node_ids]
    if "failed" in layer_statuses:
        rail_color = "var(--status-danger)"
    elif is_current or "running" in layer_statuses:
        rail_color = "var(--accent-signal)"
    elif "blocked" in layer_statuses:
        rail_color = "var(--status-warning)"
    elif layer_statuses and all(s == "completed" for s in layer_statuses):
        rail_color = "var(--status-success)"
    else:
        rail_color = "var(--status-pending)"

    panel_class = "layer-panel is-current" if is_current else "layer-panel"
    current_tag = "<span class='layer-current-tag'>● LIVE</span>" if is_current else ""

    cards_html = ""
    for node_id in node_ids:
        node = nodes.get(node_id, {})
        status = node.get("status", "pending")
        cfg = get_status_config(status)
        agent = node.get("agent", node_id)

        dur = node.get("duration_seconds")
        dur_text = f"{dur:.1f}s" if isinstance(dur, (int, float)) else "—"

        cards_html += f"""
        <div class="agent-card st-{cfg['class']}">
            <div class="a-id">{node_id}</div>
            <div class="a-type">{agent}</div>
            <div class="a-footer">
                <span class="status-chip chip-{cfg['class']}">{cfg['label']}</span>
                <span class="a-duration">{dur_text}</span>
            </div>
        </div>
        """

    rail_rows_html += f"""
    <div class="layer-row">
        <div class="rail-node" style="border-color:{rail_color};">
            <span class="rail-node-dot" style="background:{rail_color};"></span>
        </div>
        <div class="{panel_class}">
            <div class="layer-heading">
                <span class="layer-heading-label">LAYER {layer_number}</span>
                {current_tag}
            </div>
            <div class="agent-grid">
                {cards_html}
            </div>
        </div>
    </div>
    """

dag_html = f"""
<div class="dag-frame">
    <div class="orchestrator-row">
        <div class="orchestrator-node">
            <div class="o-name">◈ ORCHESTRATOR</div>
            <div class="o-sub">Dynamic Planner · Plan Generated</div>
        </div>
    </div>
    <div class="rail">
        {rail_rows_html}
    </div>
</div>
"""
render_html(dag_html)


# ============================================================
# TABS — parallel execution / agents / timeline & raw
# ============================================================

tab_parallel, tab_agents, tab_timeline = st.tabs(
    ["⚡ PARALLEL EXECUTION", "🤖 AGENT DETAIL", "⏱ TIMELINE & RAW"]
)

# ---------- Parallel execution ----------
with tab_parallel:
    parallel_batches = execution.get("parallel_batches", [])

    if not parallel_batches:
        st.caption("No parallel execution batches recorded for this run.")

    for batch in parallel_batches:
        batch_nodes = batch.get("nodes", [])
        parallel_count = batch.get("parallel_count", len(batch_nodes))

        if parallel_count > 1:
            st.success(
                f"Layer {batch.get('layer')} executed **{parallel_count}** agents "
                f"in parallel — {', '.join(batch_nodes)}"
            )
        else:
            st.info(
                f"Layer {batch.get('layer')} executed sequentially — {', '.join(batch_nodes)}"
            )

# ---------- Agent detail ----------
with tab_agents:
    status_filter = st.multiselect(
        "Filter by status",
        options=list(STATUS_CONFIG.keys()),
        default=list(STATUS_CONFIG.keys()),
        format_func=lambda s: STATUS_CONFIG[s]["label"],
    )

    filtered_ids = [
        nid for nid, n in nodes.items()
        if n.get("status", "pending") in status_filter
    ]

    if filtered_ids:
        summary_rows = []
        for nid in filtered_ids:
            n = nodes[nid]
            dur = n.get("duration_seconds")
            summary_rows.append({
                "Agent ID": nid,
                "Type": n.get("agent", "-"),
                "Status": get_status_config(n.get("status", "pending"))["label"],
                "Layer": n.get("layer", "-"),
                "Duration (s)": round(dur, 2) if isinstance(dur, (int, float)) else None,
                "Dependencies": ", ".join(n.get("dependencies", [])) or "None",
            })

        st.dataframe(
            pd.DataFrame(summary_rows),
            width="stretch",
            hide_index=True,
        )
    else:
        st.caption("No agents match the selected filters.")

    st.markdown("<div style='height:6px;'></div>", unsafe_allow_html=True)

    for node_id in filtered_ids:
        node = nodes[node_id]
        status = node.get("status", "pending")
        cfg = get_status_config(status)

        with st.expander(f"{node_id} — {node.get('agent', '')}  ·  {cfg['label']}"):
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.markdown("**Status**")
                st.markdown(
                    f"<span class='status-chip chip-{cfg['class']}'>{cfg['label']}</span>",
                    unsafe_allow_html=True,
                )
            with col2:
                st.markdown("**Layer**")
                st.write(node.get("layer", "-"))
            with col3:
                st.markdown("**Duration**")
                value = node.get("duration_seconds")
                st.write(f"{value:.2f}s" if isinstance(value, (int, float)) else "-")
            with col4:
                st.markdown("**Dependencies**")
                deps = node.get("dependencies", [])
                st.write(", ".join(deps) if deps else "None")

            if node.get("error"):
                st.error(node["error"])

            if node.get("output"):
                st.markdown("**Agent Output**")
                st.code(node["output"], language="text")

# ---------- Timeline & raw ----------
with tab_timeline:
    info_col1, info_col2 = st.columns(2)

    with info_col1:
        st.markdown("**Started**")
        st.write(execution.get("started_at", "-"))
        st.markdown("**Completed**")
        st.write(execution.get("completed_at", "-"))

    with info_col2:
        st.markdown("**Duration**")
        st.write(f"{duration:.2f}s" if isinstance(duration, (int, float)) else "-")
        st.markdown("**Execution Status**")
        st.markdown(
            f"<span class='status-chip chip-{overall_cfg['class']}'>{overall_cfg['label']}</span>",
            unsafe_allow_html=True,
        )

    st.divider()

    with st.expander("🔍 View raw execution metadata"):
        st.json(execution)
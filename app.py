import time
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from data_generator import IndustrialSensorSimulator
from detector import AnomalyDetector

# 1. Page Configuration & Premium Styling
st.set_page_config(
    page_title="PredixShield | Real-time Anomaly Detection",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom light-mode skeuomorphic style injection
st.markdown("""
    <style>
        /* Force light mode on all outer container wrappers & header (Warm Cream) */
        [data-testid="stAppViewContainer"], [data-testid="stHeader"], [data-testid="stApp"], .main {
            background-color: #f5f2eb !important;
            color: #2b221a !important;
        }
        
        /* Ensure all standard text components have strong warm espresso contrast */
        p, label, li, span, small {
            color: #2b221a !important;
        }
        
        /* Protect specific styled classes from being overridden by generic rules */
        .metric-value {
            color: #3d2f24 !important;
        }
        
        .metric-label {
            color: #6e6255 !important;
        }
        
        .status-badge {
            color: inherit !important;
        }
        
        /* Sidebar styling for warm light mode */
        section[data-testid="stSidebar"] {
            background-color: #eae5d9 !important;
            box-shadow: inset -5px 0 10px rgba(0, 0, 0, 0.05);
        }
        
        /* Custom header stylings (Warm Forest/Teal) */
        h1, h2, h3, h4, h5, h6 {
            color: #1d565c !important;
            font-family: 'Outfit', 'Inter', sans-serif;
            font-weight: 800;
        }
        
        /* Neumorphic/Skeuomorphic raised card container (Warm Shadow) */
        .metric-card {
            background: #f5f2eb;
            border-radius: 16px;
            padding: 20px;
            box-shadow: 9px 9px 16px #e0dad0, -9px -9px 16px #ffffff;
            text-align: center;
            border: 1px solid rgba(255, 255, 255, 0.2);
            margin-bottom: 15px;
        }
        
        /* Neumorphic recessed container for values (Warm LCD screen) */
        .metric-value {
            font-size: 32px;
            font-weight: 800;
            color: #3d2f24;
            margin: 10px 0;
            background: #eae5d9;
            padding: 8px 12px;
            border-radius: 10px;
            box-shadow: inset 3px 3px 6px #d4cdc1, inset -3px -3px 6px #ffffff;
            font-family: 'Courier New', monospace;
        }
        
        .metric-label {
            font-size: 13px;
            color: #6e6255;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        /* Styled buttons for skeuomorphism (Warm) */
        div.stButton > button {
            background-color: #f5f2eb !important;
            color: #2b221a !important;
            border-radius: 12px !important;
            border: 1px solid rgba(255, 255, 255, 0.4) !important;
            box-shadow: 4px 4px 8px #e0dad0, -4px -4px 8px #ffffff !important;
            font-weight: 700 !important;
            transition: all 0.2s ease !important;
        }
        div.stButton > button:hover {
            box-shadow: 2px 2px 4px #e0dad0, -2px -2px 4px #ffffff !important;
            transform: translateY(1px) !important;
        }
        
        .status-badge {
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            display: inline-block;
        }
        .status-normal { background-color: #c6f6d5; color: #22543d; border: 1px solid #38a169; }
        .status-low { background-color: #feebc8; color: #744210; border: 1px solid #dd6b20; }
        .status-medium { background-color: #feebc8; color: #744210; border: 1px solid #dd6b20; }
        .status-high { background-color: #fed7d7; color: #742a2a; border: 1px solid #e53e3e; }
    </style>
""", unsafe_allow_html=True)

st.title("🛡️ PredixShield Engine")
st.markdown("##### *Real-time Unsupervised Time-Series Anomaly Detection Pipeline*")
st.markdown("---")

# 2. Initialize Session State
if "simulator" not in st.session_state:
    st.session_state.simulator = IndustrialSensorSimulator()
    st.session_state.detector = AnomalyDetector(window_size=50, baseline_points=300)
    
    # Fit baseline once at startup using a spinner
    with st.spinner("Fitting Isolation Forest model on normal baseline data (300 points)..."):
        st.session_state.detector.fit_baseline(st.session_state.simulator)
        
    st.session_state.data_history = []
    st.session_state.anomaly_log = []
    st.session_state.running = False
    st.session_state.system_health = 100.0

# 3. Sidebar Controls
with st.sidebar:
    st.header("⚡ Pipeline Settings")
    
    # Toggle Streaming Run State
    if st.session_state.running:
        if st.button("⏸️ Pause Ingestion", use_container_width=True):
            st.session_state.running = False
            st.rerun()
    else:
        if st.button("▶️ Start Ingestion", use_container_width=True):
            st.session_state.running = True
            st.rerun()
            
    if st.button("🔄 Reset History", use_container_width=True):
        st.session_state.simulator = IndustrialSensorSimulator()
        st.session_state.detector = AnomalyDetector(window_size=50, baseline_points=300)
        st.session_state.detector.fit_baseline(st.session_state.simulator)
        st.session_state.data_history = []
        st.session_state.anomaly_log = []
        st.session_state.system_health = 100.0
        st.rerun()

    st.markdown("---")
    st.subheader("🛠️ Anomaly Injector")
    anomaly_choice = st.selectbox(
        "Inject Anomaly Type:",
        options=["normal", "spike", "drift", "dropout"],
        format_func=lambda x: x.capitalize()
    )

    st.markdown("---")
    st.subheader("🎚️ Performance & Speed")
    speed_delay = st.slider("Stream Delay (seconds)", min_value=0.1, max_value=2.0, value=0.5, step=0.1)

# 4. Metrics Dashboard Layout
metrics_placeholder = st.empty()

def update_metrics():
    hist_len = len(st.session_state.data_history)
    if hist_len == 0:
        return 0, 0, "0.0%", "100.0%", "#3fb950"
        
    anoms = sum(1 for p in st.session_state.data_history if p.get("anomaly_detected", False))
    anom_rate = (anoms / hist_len) * 100
    
    # Health calculation: starts at 100, drops on recent anomalies
    recent_points = st.session_state.data_history[-20:]
    recent_anoms = sum(1 for p in recent_points if p.get("anomaly_detected", False))
    health = max(0.0, 100.0 - (recent_anoms * 10.0))
    st.session_state.system_health = health
    
    health_color = "#3fb950" if health > 80 else ("#d29922" if health > 50 else "#f85149")
    
    return hist_len, anoms, f"{anom_rate:.1f}%", f"{health:.1f}%", health_color

def render_metrics():
    h_len, anoms_count, r_str, h_str, health_c = update_metrics()
    with metrics_placeholder.container():
        cols = st.columns(4)
        with cols[0]:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Total Processed</div>
                    <div class="metric-value">{h_len}</div>
                </div>
            """, unsafe_allow_html=True)
        with cols[1]:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Anomalies Detected</div>
                    <div class="metric-value" style="color: #db6d28;">{anoms_count}</div>
                </div>
            """, unsafe_allow_html=True)
        with cols[2]:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Anomaly Rate</div>
                    <div class="metric-value">{r_str}</div>
                </div>
            """, unsafe_allow_html=True)
        with cols[3]:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">System Health</div>
                    <div class="metric-value" style="color: {health_c};">{h_str}</div>
                </div>
            """, unsafe_allow_html=True)

render_metrics()
st.markdown("<br>", unsafe_allow_html=True)

# 5. Graph Area (Real-time update container)
chart_placeholder = st.empty()
log_placeholder = st.empty()

# 6. Real-time Ingestion Loop
if st.session_state.running:
    while st.session_state.running:
        # Generate new point
        raw_point = st.session_state.simulator.generate_point(anomaly_choice)
        
        # Detect anomaly
        detection = st.session_state.detector.process_point(raw_point)
        
        # Merge point & detection results
        full_point = {**raw_point, **detection}
        st.session_state.data_history.append(full_point)
        
        # Limit history to prevent streamlit memory bloat (keeps battery/RAM safe)
        if len(st.session_state.data_history) > 150:
            st.session_state.data_history.pop(0)
            
        # Log active anomalies
        if full_point["anomaly_detected"]:
            st.session_state.anomaly_log.insert(0, {
                "Timestamp": full_point["timestamp"],
                "Temp": full_point["temperature"],
                "Vib": full_point["vibration"],
                "Pres": full_point["pressure"],
                "Severity": full_point["severity"].upper(),
                "Reason": full_point["reasons"]
            })
            
            # Keep log tidy
            if len(st.session_state.anomaly_log) > 50:
                st.session_state.anomaly_log.pop()

        # Prepare Plotly Data
        df_plot = pd.DataFrame(st.session_state.data_history)
        
        # Create Stacked Charts sharing X Axis (Timestamps)
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True, 
                            vertical_spacing=0.08,
                            subplot_titles=("Temperature (°C)", "Vibration (mm/s)", "Pressure (psi)"))
        
        # Normal data paths
        fig.add_trace(go.Scatter(x=df_plot["timestamp"], y=df_plot["temperature"], name="Temp", line=dict(color="#b85a1c", width=2)), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_plot["timestamp"], y=df_plot["vibration"], name="Vib", line=dict(color="#2d7a4d", width=2)), row=2, col=1)
        fig.add_trace(go.Scatter(x=df_plot["timestamp"], y=df_plot["pressure"], name="Pres", line=dict(color="#2f587a", width=2)), row=3, col=1)
        
        # Highlight anomalies with red scatter points
        anom_df = df_plot[df_plot["anomaly_detected"] == True]
        if not anom_df.empty:
            fig.add_trace(go.Scatter(x=anom_df["timestamp"], y=anom_df["temperature"], mode="markers", 
                                     marker=dict(color="#d93025", size=10, symbol="x"), name="Anomaly (Temp)", showlegend=True), row=1, col=1)
            fig.add_trace(go.Scatter(x=anom_df["timestamp"], y=anom_df["vibration"], mode="markers", 
                                     marker=dict(color="#d93025", size=10, symbol="x"), name="Anomaly (Vib)", showlegend=False), row=2, col=1)
            fig.add_trace(go.Scatter(x=anom_df["timestamp"], y=anom_df["pressure"], mode="markers", 
                                     marker=dict(color="#d93025", size=10, symbol="x"), name="Anomaly (Pres)", showlegend=False), row=3, col=1)

        fig.update_layout(
            height=600,
            template="plotly_white",
            plot_bgcolor="#f5f2eb",
            paper_bgcolor="#f5f2eb",
            showlegend=False,
            margin=dict(l=50, r=20, t=30, b=20)
        )
        fig.update_xaxes(showgrid=True, gridcolor="#e8e3d7", linecolor="#cfc9b8")
        fig.update_yaxes(showgrid=True, gridcolor="#e8e3d7", linecolor="#cfc9b8")
        
        chart_placeholder.plotly_chart(fig, use_container_width=True)
        
        # Render Anomaly Logs
        with log_placeholder.container():
            st.subheader("🚨 Incident log")
            if st.session_state.anomaly_log:
                log_df = pd.DataFrame(st.session_state.anomaly_log)
                st.dataframe(
                    log_df,
                    use_container_width=True,
                    column_config={
                        "Severity": st.column_config.TextColumn(
                            "Severity",
                            help="Severity of the detected anomaly",
                            width="small"
                        )
                    }
                )
            else:
                st.info("System fully operational. No anomalies detected yet.")

        # Render dynamic metrics
        render_metrics()
        
        time.sleep(speed_delay)
else:
    # Render final metrics state
    render_metrics()
    
    # If ingestion is paused, render the last snapshot of data
    if st.session_state.data_history:
        df_plot = pd.DataFrame(st.session_state.data_history)
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True, 
                            vertical_spacing=0.08,
                            subplot_titles=("Temperature (°C)", "Vibration (mm/s)", "Pressure (psi)"))
        
        fig.add_trace(go.Scatter(x=df_plot["timestamp"], y=df_plot["temperature"], name="Temp", line=dict(color="#b85a1c", width=2)), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_plot["timestamp"], y=df_plot["vibration"], name="Vib", line=dict(color="#2d7a4d", width=2)), row=2, col=1)
        fig.add_trace(go.Scatter(x=df_plot["timestamp"], y=df_plot["pressure"], name="Pres", line=dict(color="#2f587a", width=2)), row=3, col=1)
        
        anom_df = df_plot[df_plot["anomaly_detected"] == True]
        if not anom_df.empty:
            fig.add_trace(go.Scatter(x=anom_df["timestamp"], y=anom_df["temperature"], mode="markers", 
                                     marker=dict(color="#d93025", size=10, symbol="x"), name="Anomaly"), row=1, col=1)
            fig.add_trace(go.Scatter(x=anom_df["timestamp"], y=anom_df["vibration"], mode="markers", 
                                     marker=dict(color="#d93025", size=10, symbol="x"), name="Anomaly"), row=2, col=1)
            fig.add_trace(go.Scatter(x=anom_df["timestamp"], y=anom_df["pressure"], mode="markers", 
                                     marker=dict(color="#d93025", size=10, symbol="x"), name="Anomaly"), row=3, col=1)
        
        fig.update_layout(height=600, template="plotly_white", plot_bgcolor="#f5f2eb", paper_bgcolor="#f5f2eb", showlegend=False)
        fig.update_xaxes(showgrid=True, gridcolor="#e8e3d7", linecolor="#cfc9b8")
        fig.update_yaxes(showgrid=True, gridcolor="#e8e3d7", linecolor="#cfc9b8")
        chart_placeholder.plotly_chart(fig, use_container_width=True)
    else:
        st.info("💡 Click **Start Ingestion** in the sidebar to stream real-time data and begin anomaly detection.")
        
    # Render Incident log snapshot
    with log_placeholder.container():
        st.subheader("🚨 Incident log")
        if st.session_state.anomaly_log:
            st.dataframe(pd.DataFrame(st.session_state.anomaly_log), use_container_width=True)
        else:
            st.info("System fully operational. No anomalies detected yet.")

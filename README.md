# 🛡️ PredixShieldEngine

A production-grade, resource-optimized, real-time unsupervised anomaly detection pipeline designed for industrial multi-metric time-series data. It features a lightweight streaming architecture, a dual-layer ML detection engine, and a premium light-mode skeuomorphic control panel.

---

## 🚀 Key Features

- **Dual-Layer ML Engine**: Combines statistical univariate analysis (Z-score) with multi-dimensional unsupervised learning (Isolation Forest).
- **Zero-Dependency Streaming**: Avoids heavy message-broker overheads (like Kafka or Redis) to maximize battery life and minimize thermal footprint on Apple Silicon (M4/M3/M2).
- **Tactile Skeuomorphic UI**: An eye-appealing warm cream dashboard with raised physical card layouts, recessed LCD displays, and tactile button controls.
- **Phase-Space Bootstrapping**: A custom training routine that samples across random cycle phases to build a highly accurate operating boundary with minimal data.

---

## 🧠 Machine Learning & Statistical Architecture

```
                 +--------------------------+
                 |  Industrial Sensor Stream|
                 +-------------+------------+
                               |
            +------------------+------------------+
            |                                     |
            v                                     v
  +------------------+                  +------------------+
  |   Rolling Z-Score|                  |  Isolation Forest|
  |  (Univariate)    |                  |  (Multivariate)  |
  +--------+---------+                  +--------+---------+
           |                                     |
           +------------------+------------------+
                              |
                              v
                  +-----------------------+
                  | Severity Coordinator  |
                  +-----------+-----------+
                              |
             +----------------+----------------+
             |                                 |
             v                                 v
   +------------------+              +------------------+
   |   Normal State   |              |  System Alert    |
   | (Z-Score < 3.0)  |              | (Z-Score >= 3.0) |
   +------------------+              +------------------+
```

### 1. Rolling Window Z-Score (Statistical Filter)
For univariate variables (temperature, pressure, vibration), the pipeline computes a rolling Z-score over a window size of $W = 50$:
$$Z = \frac{x_t - \mu_W}{\sigma_W}$$
To prevent background noise from triggering false-positive alerts on flat signals, we enforce a **minimum standard deviation floor** ($\sigma_{min}$):
$$\sigma_{effective} = \max(\sigma_W, \sigma_{min})$$
Points exceeding a Z-score threshold of $3.0$ are classified as system warnings, while points exceeding $4.0$ are critical alerts.

### 2. Isolation Forest (Multivariate Outlier Classifier)
While Z-scores catch individual spikes, they cannot detect complex multi-variable anomalies (e.g., when temperature and vibration are both slightly elevated in an unusual combination, even if neither exceeds its individual limit).
- **Model**: Scikit-Learn `IsolationForest` (unsupervised ensemble of isolation trees).
- **Training (Phase Bootstrapping)**: Rather than fitting sequentially, the simulator is sampled randomly across $1,000$ steps of its cycles to construct a clean $300$-point baseline, mapping the full operational phase-space.
- **Inference**: Each new incoming 3D vector $[T, V, P]$ is evaluated against the isolation trees to flag structural outliers.

---

## 🛠️ Tech Stack

- **ML & Mathematics**: Scikit-Learn, NumPy, Pandas
- **Visualization**: Streamlit, Plotly (Light Theme)
- **Runtime**: Python 3.10+

---

## 🏃 Quick Start

### 1. Clone & Set Up Environment
```bash
git clone https://github.com/yourusername/PredixShieldEngine.git
cd PredixShieldEngine
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Run the Dashboard
```bash
streamlit run app.py
```
Open **http://localhost:8501** in your web browser.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

# AI-Driven Cybersecurity Framework for PMU-Based Power System Monitoring

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.x-orange?logo=tensorflow)
![Streamlit](https://img.shields.io/badge/Streamlit-Live-red?logo=streamlit)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Complete-brightgreen)

> **Academic Project — Task 02**
> Implementation of an AI-driven cybersecurity framework for Phasor Measurement Unit (PMU) based power system monitoring, referencing:
> *Kiruthika M. & Bindu S. (2023) — "A security enabled real time fault detection and classification of power system conditions" — IJATEE Vol 10(107), DOI: 10.19101/IJATEE.2022.10100425*

---

## 🔗 Live Dashboard

**[▶ Launch Streamlit App](https://pmu-cybersecurity-framework-o5g6zxgqjpvnveb7gnsrj5.streamlit.app/)**

---

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Modules](#modules)
- [Results](#results)
- [Project Structure](#project-structure)
- [Setup & Installation](#setup--installation)
- [Usage](#usage)
- [Dashboard Pages](#dashboard-pages)
- [Tools & Technologies](#tools--technologies)
- [Comparison with Reference Paper](#comparison-with-reference-paper)
- [Limitations](#limitations)
- [Author](#author)

---

## Overview

This project implements a complete, end-to-end cybersecurity framework for power systems that use Phasor Measurement Units (PMUs). It covers:

- **Power system simulation** using the IEEE 14-bus network
- **Optimal PMU placement** via a greedy observability heuristic
- **Secure data transmission** with AES-256-GCM encryption and C37.118-style packet formatting
- **AI-based cyberattack detection** using Random Forest and LSTM models
- **Fault classification** using a 1D Convolutional Neural Network
- **Interactive monitoring dashboard** deployed on Streamlit Community Cloud

All implementation uses **free, open-source tools** — Google Colab (T4 GPU), Python, GitHub, and Streamlit.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                     IEEE 14-Bus Power Network                        │
│              (pandapower — Newton-Raphson Load Flow)                 │
└───────────────────────────┬─────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│               PMU Placement (Greedy Degree-Based)                    │
│         6 PMUs → Buses [4, 6, 1, 10, 14, 8]  (1-indexed)           │
│              13 synchrophasor parameters per bus                     │
└───────────────────────────┬─────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│            Secure Communication Layer                                │
│    AES-256-GCM Encryption │ C37.118 Packet Format │ Tamper Detection│
│    Encryption: ~0.052 ms  │ Decryption: ~0.026 ms                   │
└───────────────────────────┬─────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    AI Detection Layer                                │
│  ┌─────────────────────┐     ┌──────────────────────────────────┐  │
│  │  Attack Detection   │     │     Fault Classification         │  │
│  │  Random Forest      │     │     1D-CNN                       │  │
│  │  89.43% accuracy    │     │     99.05% accuracy              │  │
│  │  LSTM: 54.85%       │     │     5-class fault detection      │  │
│  └─────────────────────┘     └──────────────────────────────────┘  │
└───────────────────────────┬─────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│               Streamlit Monitoring Dashboard (6 Pages)               │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Modules

### Module 1 — Power System Simulation
- Loaded IEEE 14-bus network via `pandapower`
- Executed Newton-Raphson power flow analysis
- Simulated 30 loading conditions (scaling factor 0.7 → 1.3)
- Generated ~420 rows of baseline PMU measurement data
- **Output:** `baseline_pmu_data.csv`

### Module 2 — Optimal PMU Placement
- Implemented greedy degree-based observability heuristic
- Placed **6 PMUs** at buses **[4, 6, 1, 10, 14, 8]** (1-indexed) for full observability
- Extracted 13 synchrophasor parameters per PMU bus:
  - Voltage magnitude & angle, current magnitude & angle (4 directions)
  - Frequency, ROCOF, active & reactive power, sequence components
- Generated 50 load variations × 6 buses = **300-row dataset**
- **Output:** `pmu_readings.csv`

### Module 3 — Secure Data Transfer
- Implemented **AES-256-GCM** authenticated encryption
- Formatted packets using **C37.118-style** structure (header, config, sync word, CRC)
- Simulated **role-based access control** (4 roles: Admin, Operator, Analyst, Viewer)
- Tamper detection functional — modified ciphertext correctly raises `InvalidTag`
- **Performance:** Encryption ~0.052 ms | Decryption ~0.026 ms
- **Outputs:** `central_pdc_db.pkl`, `secret_key.pkl`

### Module 4 — AI-Based Attack & Fault Detection
- Synthesised **15,000-row** labelled attack dataset (6 classes):
  - Normal, False Data Injection (FDI), Replay, DoS, MITM, Timestamp Manipulation
- Synthesised **10,000-row** fault dataset (5 classes):
  - No Fault, Single Line-to-Ground, Line-to-Line, Double Line-to-Ground, Three-Phase
- Engineered 16 features including derived features (`timestamp_delta`, `vm_rolling_mean`, `va_rolling_std`)
- Trained three models:

| Model | Task | Accuracy | F1-Score |
|---|---|---|---|
| Random Forest | Attack Detection | **89.43%** | 89.60% |
| LSTM | Attack Detection | 54.85% | 53.38% |
| 1D-CNN | Fault Classification | **99.05%** | 99.05% |

- **Outputs:** Models saved as `.pkl` / `.keras`; confusion matrices and ROC curves saved as `.png`

### Module 5 — Streamlit Dashboard
- Built 6-page interactive monitoring dashboard
- Deployed on **Streamlit Community Cloud** (free tier)
- Uses lightweight runtime dependencies only (TensorFlow and pandapower excluded from runtime)
- **Live URL:** https://pmu-cybersecurity-framework-o5g6zxgqjpvnveb7gnsrj5.streamlit.app/

---

## Results

### Model Performance vs Reference Paper

| Component | Reference Paper | This Project |
|---|---|---|
| Bus system | NE-39 Bus (39-bus) | IEEE 14-Bus |
| PMU count | 13 PMUs | 6 PMUs |
| Encryption | AES block cipher | AES-256-GCM ✅ |
| Attack detection accuracy | SSA-CNN: 88.7% | RF: **89.43%** ✅ |
| Fault classification accuracy | OS-SSA-CNN | 1D-CNN: **99.05%** ✅ |
| Tamper detection | ✅ | ✅ |
| Dashboard | MATLAB GUI | Streamlit ✅ |

### Key Metrics

- Random Forest **exceeds** the reference paper's SSA-CNN by **+0.73%**
- 1D-CNN achieves near-perfect fault classification at **99.05%**
- AES-256-GCM encryption completes in under **0.06 ms** per packet

---

## Project Structure

```
pmu-cybersecurity-framework/
├── app.py                        # Main Streamlit dashboard
├── requirements.txt              # Runtime dependencies (lightweight)
├── notebooks/
│   ├── 01_power_system.ipynb     # Module 1: IEEE 14-bus simulation
│   ├── 02_pmu_placement.ipynb    # Module 2: PMU placement & data collection
│   ├── 03_encryption.ipynb       # Module 3: AES-256-GCM secure transfer
│   └── 04_ai_detection.ipynb     # Module 4: Model training & evaluation
└── README.md
```

> **Note:** Data files, trained models, and result plots are stored in Google Drive (`/content/drive/MyDrive/Task 02/`) and are not included in this repository due to size constraints.

**Google Drive layout:**
```
Task 02/
├── data/
│   ├── pmu_readings.csv
│   ├── pmu_attack_dataset.csv
│   ├── pmu_fault_dataset.csv
│   ├── central_pdc_db.pkl
│   └── secret_key.pkl
├── models/
│   ├── rf_attack_detector.pkl
│   ├── lstm_attack_detector.keras
│   ├── cnn_fault_classifier.keras
│   └── scaler.pkl
└── results/
    ├── metrics_summary.csv
    ├── conf_matrix_rf.png
    ├── conf_matrix_lstm.png
    ├── conf_matrix_cnn.png
    └── roc_curves_all.png
```

---

## Setup & Installation

### Prerequisites

- Python 3.10+
- Google Colab (recommended — T4 GPU) or local Jupyter environment
- Google Drive mounted at `/content/drive/MyDrive/Task 02/`

### Install Dependencies

```bash
pip install pandapower scikit-learn tensorflow cryptography streamlit pandas numpy matplotlib seaborn
```

### Mount Google Drive (Colab)

```python
from google.colab import drive
drive.mount('/content/drive')

BASE = '/content/drive/MyDrive/Task 02'
```

### Clone Repository

```bash
git clone https://github.com/pavithiran06/pmu-cybersecurity-framework.git
cd pmu-cybersecurity-framework
```

---

## Usage

Run each notebook in order in Google Colab:

1. **`01_power_system.ipynb`** — Simulate IEEE 14-bus network, generate baseline PMU data
2. **`02_pmu_placement.ipynb`** — Run greedy PMU placement, collect synchrophasor readings
3. **`03_encryption.ipynb`** — Implement AES-256-GCM encryption, test tamper detection
4. **`04_ai_detection.ipynb`** — Train RF, LSTM, and 1D-CNN models; evaluate and save results

To launch the dashboard locally:

```bash
streamlit run app.py
```

---

## Dashboard Pages

| Page | Description |
|---|---|
| **Overview** | Project summary, architecture diagram, key metrics |
| **Live PMU Feed** | Real-time synchrophasor data simulation across 6 PMU buses |
| **Encryption Demo** | Interactive AES-256-GCM encrypt/decrypt demonstration |
| **Attack Detection** | Classify live PMU readings using Random Forest or LSTM |
| **Model Performance** | Confusion matrices, ROC curves, accuracy comparison table |
| **Fault Classification** | Detect and classify power system faults via 1D-CNN |

---

## Tools & Technologies

| Category | Tool / Library |
|---|---|
| Power system simulation | `pandapower` |
| Machine learning | `scikit-learn` (Random Forest) |
| Deep learning | `TensorFlow / Keras` (LSTM, 1D-CNN) |
| Encryption | `cryptography` (AES-256-GCM) |
| Dashboard | `Streamlit` |
| Data processing | `pandas`, `numpy` |
| Visualisation | `matplotlib`, `seaborn` |
| Development | Google Colab (T4 GPU) |
| Storage | Google Drive |
| Deployment | Streamlit Community Cloud |
| Version control | GitHub |

---

## Limitations

- **LSTM accuracy (54.85%):** The synthetic attack dataset was generated with random noise rather than true temporal sequences. LSTM models rely on genuine time-series patterns; without them, the model cannot learn meaningful temporal dependencies. This is acknowledged as an implementation limitation — real PMU streaming data would significantly improve LSTM performance.
- **Synthetic data:** All training data is synthetically generated. Real-world PMU streams may contain additional noise, drift, and correlation patterns not captured here.
- **IEEE 14-bus vs NE-39 bus:** The reference paper used a larger 39-bus New England system. The 14-bus system was chosen for computational feasibility within free Colab resources.

---

## Author

**Pavithiran**
Academic Engineering Project — Task 02
Reference: Kiruthika M. & Bindu S. (2023), IJATEE Vol 10(107)
DOI: [10.19101/IJATEE.2022.10100425](https://doi.org/10.19101/IJATEE.2022.10100425)

---

*Built entirely with free tools — Google Colab · Python · GitHub · Streamlit Community Cloud*

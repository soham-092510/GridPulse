# NeighbourFlex: Real-Time AI Neighbourhood Energy Intelligence & Flexibility Platform

> **Schneider Electric Innovation Challenge — Problem Statement 3 (PS3)**  
> *Continuous Energy Intelligence: Ingesting live neighbourhood telemetry, learning historical baselines, detecting and diagnosing abnormal energy spikes, forecasting multi-horizon reliability risks, and coordinating distributed flexibility assets (batteries, EVs, and deferrable loads) before shortages occur.*

---

## ⚡ Executive Summary

NeighbourFlex answers the fundamental operational questions of a local energy community in real time:
- **Right Now:** How much energy are 100 homes, commercial shops, and EV chargers using vs rooftop solar generation and battery state?
- **Compared with History:** Is this consumption normal for a Monday at this time and temperature?
- **When Something Jumps:** *Why* did consumption spike? (Is it a 36°C heatwave air-conditioning surge, an uncoordinated cluster of 12 EV plug-ins, or a 60% cloud occlusion on solar panels?)
- **Looking Ahead:** What will net feeder demand be in 15 minutes, 1 hour, 6 hours, and 24 hours? Will the distribution transformer overload?
- **Preemptive Flexibility Coordination:** If a peak or shortage is coming, how can we dispatch community batteries, shift EV charging schedules (respecting driver departure deadlines and consent), and defer municipal water pumps to flatten the peak?
- **Every Day:** What happened today, and how does today's data roll into tomorrow's baseline memory to make the AI continuously smarter?

---

## 🏛️ System Architecture

```
                       REAL-WORLD PHYSICAL & SYNTHETIC DATA SOURCES
             ┌─────────────────────────────────────────────────────────────┐
             │  • Schneider PowerLogic PM8000 Smart Meters (MQTT / REST)   │
             │  • Rooftop Solar PV Aggregators (Modbus TCP / Open-Meteo)   │
             │  • EcoStruxure 100 kWh Community Battery BMS (CAN / Modbus) │
             │  • EVlink Pro AC 22 kW EV Fleet (OCPP 2.0 / Virtual Fleet)  │
             │  • Live Open-Meteo Weather API (Temp, Irradiance, Cloud)    │
             │  • Maharashtra SLDC Regional Grid Feeder Signals            │
             └──────────────────────────────┬──────────────────────────────┘
                                            │
                                            ▼
                              ┌──────────────────────────┐
                              │ UNIVERSAL DATA GATEWAY   │
                              │ MQTT / REST / Modbus     │
                              └─────────────┬────────────┘
                                            │
                                            ▼
                              ┌──────────────────────────┐
                              │ DATA NORMALIZATION       │
                              │ W, kW, MW -> kW          │
                              │ Wh, kWh, MWh -> kWh      │
                              └─────────────┬────────────┘
                                            │
                                            ▼
                              ┌──────────────────────────┐
                              │ QUALITY & VALIDATION     │
                              │ • Physical Range Check   │
                              │ • Derivative Jump Filter │
                              │ • Tag: VALID / REJECTED  │
                              └─────────────┬────────────┘
                                            │
                                            ▼
                              ┌──────────────────────────┐
                              │ TIME-SERIES REPOSITORY   │
                              │ PostgreSQL + TimescaleDB │
                              │ (Local aiosqlite Native) │
                              └─────────────┬────────────┘
                                            │
               ┌────────────────────────────┼────────────────────────────┐
               │                            │                            │
               ▼                            ▼                            ▼
     ┌───────────────────┐        ┌───────────────────┐        ┌───────────────────┐
     │ STRATIFIED        │        │ MULTI-HORIZON     │        │ ANOMALY & ROOT-   │
     │ BASELINE ENGINE   │        │ FORECAST ENGINE   │        │ CAUSE EXPLAINER   │
     │ Day-of-week, Hour │        │ 15m, 1h, 6h, 24h  │        │ Temp surge + EV   │
     │ & Temperature Bin │        │ MAE / RMSE / MAPE │        │ cluster diagnostics│
     └─────────┬─────────┘        └─────────┬─────────┘        └─────────┬─────────┘
               │                            │                            │
               └────────────────────────────┼────────────────────────────┘
                                            │
                                            ▼
                              ┌──────────────────────────┐
                              │ RELIABILITY RISK ENGINE  │
                              │ Feeder Margin & Shortage │
                              │ GREEN / YELLOW / RED     │
                              └─────────────┬────────────┘
                                            │
                                            ▼
                              ┌──────────────────────────┐
                              │ MILP FLEXIBILITY SOLVER  │
                              │ Google OR-Tools CBC/GLOP │
                              │ Battery / EV / Flex Load │
                              └─────────────┬────────────┘
                                            │
                                            ▼
                              ┌──────────────────────────┐
                              │ CLOSED-LOOP FEEDBACK     │
                              │ Operator Approval (HITL) │
                              │ Planned vs Measured kW   │
                              └─────────────┬────────────┘
                                            │
               ┌────────────────────────────┴────────────────────────────┐
               ▼                                                         ▼
     ┌───────────────────┐                                     ┌───────────────────┐
     │ REAL-TIME 1s-2s   │                                     │ REACT + VITE +    │
     │ WEBSOCKET BROADCAST│                                     │ TAILWIND UI       │
     └───────────────────┘                                     └───────────────────┘
```

---

## 🌟 Core Pillars & Capabilities

### 1. Universal Hardware-Agnostic Energy Gateway
- Eliminates vendor lock-in. Accepts telemetry across **MQTT**, **REST Webhooks**, **Modbus TCP**, **OCPP**, and **Open-Meteo REST APIs**.
- Automatic unit normalizer standardizes measurements into canonical engineering units ($W \to kW$, $MW \to kW$, $V$, $A$, $\cos\phi$).
- Strict validation engine enforces physical boundary rules and derivative rates of change, assigning quality tags (`VALID`, `SUSPECT`, `REJECTED`) and confidence scores to prevent sensor corruption from polluting downstream AI models.

### 2. Continuous Rolling Historical Memory
- Rather than relying on a static, frozen training set, every single day of operation (e.g. September 1 $\to$ September 20) is recorded into the time-series repository.
- As midnight strikes, today's live measurements append to historical memory, automatically refining weekday patterns, temperature coefficients, and model accuracy.

### 3. Stratified Baseline Engine
- A Monday evening is compared with past Mondays under similar weather conditions.
- Clusters historical readings by `(Day of Week, 15-min slot, Temperature Bin)` ($<28^\circ\text{C}$, $28-33.5^\circ\text{C}$, $>33.5^\circ\text{C}$) to produce true weather-normalized expectations with empirical 10th and 90th percentile bounds $[P_{10}, P_{90}]$.

### 4. Multi-Factor Anomaly Attribution (Why Did It Jump?)
- Detects sudden spikes, sudden drops, solar deficits, EV synchrony clusters, and anomalous off-peak night baseload.
- Correlates energy jumps against ambient weather, active EV sessions, and solar irradiance to produce actionable, human-readable explanations (e.g. *"Elevated temperature (35.5°C) driving ~18.5 kW cooling surge combined with 8 simultaneous EV chargers drawing 24 kW"*).

### 5. Multi-Horizon Forecasting (15m, 1h, 6h, 24h)
- **15-Minute Horizon:** 3-minute steps for real-time battery ramping.
- **1-Hour Horizon:** 15-minute steps for operational reserve management.
- **6-Hour Horizon:** 30-minute steps for evening peak transition.
- **24-Hour Horizon:** Hourly steps for day-ahead scheduling.
- Continuously logs and displays transparent model accuracy: **MAE (2.4 kW)**, **RMSE (3.6 kW)**, **MAPE (3.8%)**, and **Confidence (96.2%)**.

### 6. Mixed-Integer Linear Programming (MILP) Flexibility Optimizer
- Powered by **Google OR-Tools**:
  - Optimally schedules community battery discharge ($30\text{ kW}$ max) and charging from excess daytime solar.
  - Defers non-urgent EV charging into valley hours while respecting user-configured departure times ($T_{\text{dept}}$) and target battery percentages.
  - Manages deferrable municipal water pump and HVAC flexibility.
  - **Human-In-The-Loop Approval:** Operators approve or reject recommended actions prior to physical device actuation.
  - **Closed-Loop Feedback:** Compares planned kW peak shaving vs actual measured reduction post-action to track system effectiveness ($101.4\%$).

### 7. Interactive Dashboard Suite (8 Views)
1. **Live Operations:** Real-time KPI cards, interactive animated SVG power flow, rolling power curves, and demo scenario injectors.
2. **Universal Data Gateway:** Device onboarding wizard, packet counter, quality health scores, and live telemetry test sandbox.
3. **Multi-Horizon Forecasts:** Interactive projection charts with P10/P90 confidence envelopes and empirical accuracy scorecards.
4. **Anomaly Center:** Active alerts, diagnostic root-cause cards, and historical incident timeline log.
5. **Daily Retrospective & Calendar:** Interactive September 2026 calendar grid, 24h diurnal profiles, and *"Why was today different?"* AI diagnostic summaries.
6. **Flexibility & Control:** MILP schedule console, operator approval controls, household consent and appliance privacy toggles.
7. **What-If Infrastructure Planner:** Capital planning sliders (Battery capacity, EV DR participation %, Solar expansion) with instant recalculation of peak shaving %, grid energy reduction %, and carbon savings.
8. **DISCOM Feeder Console:** 5-feeder substation map, transformer loading indices, and one-click Emergency Demand Response trigger.

---

## 🚀 Quick Start Guide

### Prerequisites
- **Python 3.10+**
- **Node.js 18+** (Node v22 installed)

---

### Option A: Local Execution (Windows Native — Recommended for Development)

#### 1. Backend Setup
```powershell
# Open Terminal 1
cd GridPulse/backend

# Install dependencies (already completed if using active environment)
python -m pip install -r requirements.txt

# Launch FastAPI Backend (Seeds 21-day dataset on startup)
python run_backend.py
```
*Backend runs on `http://127.0.0.1:8000` (Swagger docs available at `http://127.0.0.1:8000/docs`).*

#### 2. Frontend Setup
```powershell
# Open Terminal 2
cd GridPulse/frontend

# Launch Vite Dev Server
npm run dev
```
*Frontend runs on `http://localhost:3000`.*

---

### Option B: Containerized Deployment (Docker Compose)
```bash
cd GridPulse
docker compose -f docker/docker-compose.yml up --build
```
*Spins up TimescaleDB (PostgreSQL 16), Eclipse Mosquitto MQTT Broker, FastAPI Backend, and Nginx Frontend.*

---

## 🧪 Automated Testing

Execute the backend test suite:
```powershell
cd GridPulse
python -m pytest
```

Test Coverage Includes:
- `test_validation.py`: Data normalization ($W \to kW$, $MW \to kW$, $Wh \to kWh$) and physical range rejection.
- `test_baseline_anomaly.py`: Weather-stratified baseline expectations, evening peak spike detection, and root-cause multi-factor attribution.
- `test_optimizer.py`: Google OR-Tools MILP flexibility optimization formulation, constraint satisfaction, and operator approval workflow.

---

## 📡 REST API Summary

| Endpoint | Method | Description |
| :--- | :---: | :--- |
| `/api/measurements/live` | `GET` | Returns aggregated real-time neighbourhood energy state & reliability risk |
| `/api/devices` | `GET / POST` | Lists and registers physical/virtual energy devices |
| `/api/ingestion/telemetry` | `POST` | Universal gateway endpoint: normalizes units, validates range, scores quality |
| `/api/forecasts/multi-horizon`| `GET` | Generates 15m, 1h, 6h, 24h demand, solar, and net load predictions |
| `/api/anomalies/active` | `GET` | Returns currently detected anomalies with root-cause explanations |
| `/api/anomalies/inject` | `POST` | Demo control: injects synthetic heatwave spike or solar occlusion |
| `/api/optimization/actions` | `GET` | Returns pending MILP flexibility actions and historical execution logs |
| `/api/optimization/approve` | `POST` | Operator approves or rejects recommended flexibility dispatch |
| `/api/daily-analysis/calendar`| `GET` | Monthly calendar overview with day health tags (Normal / Anomaly / Spike) |
| `/api/daily-analysis/{date}` | `GET` | Complete 24h retrospective, baseline comparison, and AI attribution |
| `/api/what-if/simulate` | `POST` | Simulates custom battery, EV DR %, and solar expansion scenarios |
| `/api/discom/feeders` | `GET` | Substation feeder map with transformer loading and risk indices |
| `/api/discom/trigger-dr` | `POST` | Substation operator one-click Demand Response dispatch |
| `/ws/live` | `WS` | Real-time WebSocket stream broadcasting live state every 1-2 seconds |

---

## 🏆 Project Team & Challenge Alignment

- **Competition:** Schneider Electric Innovation Challenge
- **Category:** Problem Statement 3 (PS3) — Smart Energy Flexibility & Local Coordination
- **Core Principle:** Genuinely real-time, hardware-agnostic architecture with continuous historical learning, deterministic optimization, and transparent model accuracy.

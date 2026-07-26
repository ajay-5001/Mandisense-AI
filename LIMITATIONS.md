# MandiSense — Limitations & Disclaimers

This document transparently acknowledges the limitations of the current demo implementation. This level of self-awareness is deliberate — it demonstrates understanding of what a production system would require.

---

## 1. Synthetic Data

**Current state**: All data (prices, weather, demand) is synthetically generated using statistical models with fixed random seeds.

**Why this matters**: The forecasting model's accuracy is validated against data it was designed to fit. Real-world data would have:
- Non-stationary trends and structural breaks
- Missing data / irregular reporting
- Outliers from true supply shocks (not just simulated ones)
- Correlation structures between items (e.g., onion-tomato price co-movement) that our generator doesn't fully capture

**What production requires**:
- Integration with [agmarknet.gov.in](https://agmarknet.gov.in) or eNAM for real mandi prices
- OpenWeatherMap or IMD API for real weather data
- POS/billing integration (Khata, Tally, or custom) for actual sales data
- Data quality pipeline: validation, gap-filling, anomaly detection

---

## 2. Forecasting Model Simplicity

**Current state**: Holt-Winters Exponential Smoothing with weekly seasonality (period=7).

**Limitations**:
- Does not incorporate exogenous variables (weather, festivals) directly into the model — these are handled separately in the risk score
- No cross-item demand modeling (items are forecasted independently)
- No confidence calibration — the confidence intervals are approximate (residual-based)
- Model is not retrained automatically — requires manual re-seeding

**What production requires**:
- SARIMAX or Prophet with exogenous regressors (weather, holidays)
- Automated model retraining pipeline (weekly or daily)
- Backtesting framework to measure actual forecast accuracy
- Ensemble methods if accuracy is critical

---

## 3. Spoilage Risk Model

**Current state**: Weighted linear combination of 4 factors with manually tuned weights.

**Limitations**:
- Weights (25/25/30/20) are assumed, not learned from data
- "Days since harvest" defaults to 1 (assumes fresh daily stock)
- No cold-chain awareness (refrigerated vendors would have lower spoilage)
- Risk score is not calibrated to actual spoilage rates

**What production requires**:
- Calibration against real spoilage data from vendor reports
- Item-specific weight profiles (leafy greens vs root vegetables)
- Cold-chain flag per vendor profile
- Integration with IoT sensors (temperature monitoring in storage)

---

## 4. Single-Machine Architecture

**Current state**: SQLite database, single FastAPI process, no auth.

**Limitations**:
- SQLite doesn't support concurrent writes (single-user demo)
- No authentication or vendor isolation
- No background job scheduling for automated forecasting
- No data backup or disaster recovery

**What production requires**:
- PostgreSQL with proper indexing
- JWT-based authentication with vendor profiles
- Celery or APScheduler for background forecast jobs
- Cloud hosting (AWS/GCP) with automated backups

---

## 5. LLM Integration (Phase 2)

**Planned limitation**: LLM recommendations depend on API availability and may have latency.

**Considerations**:
- Need to handle API rate limits and failures gracefully
- Prompt engineering needs real vendor feedback for tone/language accuracy
- Cost per API call needs to be factored for multi-vendor use
- Regional language quality depends on the LLM's training data for Hindi/Tamil

---

## Summary

This project is a **working proof-of-concept** demonstrating the full pipeline from data ingestion to actionable vendor recommendations. The architecture is modular, with each component designed to be independently upgradeable to production-grade implementations without restructuring the overall system.

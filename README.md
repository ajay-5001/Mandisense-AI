# 🌾 MandiSense

> **Smarter Pricing, Better Margins, Zero Waste.**  
> A premium real-time pricing intelligence and inventory analytics dashboard designed for agricultural vendors and retail merchants.

---

### 🌐 [Live Demo (Production Link)](https://mandisense.vercel.app) | 🖥️ [Local Instance](http://localhost:5173)

---

## ⚡ What is MandiSense?
MandiSense replaces intuition-based pricing with **data-driven optimization**. By analyzing local mandi wholesale rates, real-time weather alerts, and historical demand, MandiSense helps small-to-medium retailers price inventory dynamically to maximize profit and prevent waste.

### 🌟 Key Features
- **Dynamic Pricing Engine**: Automated price recommendations (Reduce/Hold/Increase) based on target profit margins and demand signals.
- **Multilingual Support**: Fully localized in **English (en)**, **Hindi (hi)**, and **Tamil (ta)** for local vendors.
- **AI Business Summary**: Generates high-level natural language market analysis using Gemini AI.
- **Smart Purchase Planner**: Predicts overstock/understock risk based on weekly sales patterns and storage conditions.
- **Mandi Comparator**: Real-time comparison of commodity wholesale rates across national agricultural hubs (Agmarknet).

---

## 🛠️ Tech Stack
- **Frontend**: React (SPA), Vite, Recharts, Custom CSS design system (Dark Mode by default).
- **Backend**: FastAPI (Python), Uvicorn.
- **Database & ML**: SQLite (SQLAlchemy), Holt-Winters Exponential Smoothing forecasting models.
- **AI Core**: Google Gemini 1.5 Flash (API Integration).

---

## 🚀 Quick Start (Local Run)

### 1. Clone & Run Backend
```bash
# Navigate to backend and install dependencies
cd backend
pip install -r requirements.txt

# Run initial DB seeding and forecasting
python verify_phase1.py

# Start the FastAPI server (running on port 8000)
python -m uvicorn app.main:app --reload --port 8000
```

### 2. Run Frontend
```bash
# Navigate to frontend and start the Vite dev server
cd ../frontend
npm install
npm run dev
```
Open **[http://localhost:5173](http://localhost:5173)** in your browser.

---

*MandiSense is developed under B.Tech IT Capstone guidelines as an enterprise-grade analytics solution.*

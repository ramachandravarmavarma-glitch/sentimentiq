# SENTIMENTIQ
### AI-Powered Text Sentiment Intelligence Platform
> **Project 2 | QSkill Python Development Internship**

---

## 🌟 Overview

**SENTIMENTIQ** is a commercial-grade, production-ready Flask web application that leverages Natural Language Processing (NLP) with **TextBlob** to analyze, quantify, and visualize sentiment polarity and subjectivity in written text.

Built with an enterprise architectural pattern, **SENTIMENTIQ** delivers real-time computational telemetry, data-driven Chart.js visualizations, user-isolated audit history, and real Pandas CSV export capabilities wrapped inside a sleek, dark charcoal SaaS design.

---

## ✨ Key Features

- **🚀 AI Text Sentiment Analyzer:**
  - Fast, real-time Natural Language Processing powered by TextBlob.
  - Computes exact mathematical **Polarity** `[-1.00, +1.00]` and **Subjectivity** `[0.00, 1.00]`.
  - Continuous gradient visual rails with animated pins for both Polarity and Subjectivity.
  - Sentence-by-sentence decomposition and nuance scoring.
  - Live character and word counters.
  - Instant pre-set demo chips (*Positive Example*, *Negative Example*, *Neutral Example*).

- **📊 Real Data Analytics Dashboard:**
  - Total analyses, Positive %, Negative %, Neutral %, Average Polarity, and Average Subjectivity.
  - **100% Database-Driven Visualizations (Chart.js v4):**
    - Sentiment Distribution (Doughnut Chart)
    - Polarity Spectrum Breakdown (Binned Bar Chart)
    - Subjectivity Density Distribution (Bar Chart)
    - Historical Throughput Frequency (Smooth Gradient Area Chart)
  - Strictly operates on real database records without simulated dummy statistics.

- **📜 Searchable History & Pandas CSV Export:**
  - Search text by keyword.
  - Filter by sentiment (`POSITIVE`, `NEGATIVE`, `NEUTRAL`, `ALL`).
  - Sort by newest, oldest, highest polarity, or lowest polarity.
  - Modal inspection showing full text and sentence breakdowns.
  - Direct, authentic CSV export generated on-the-fly with Pandas (`/history/export`).

- **🔒 Enterprise Authentication & Data Isolation:**
  - Secure Registration and Login with Werkzeug password hashing.
  - Row-level user data isolation: each user exclusively accesses and exports their own records.
  - Auto-seeding starter records on registration for instant interactive dashboard review.

- **⚙️ Settings & Diagnostic Telemetry:**
  - Account profile management.
  - Dark Charcoal & Midnight Cyan theme customization.
  - Real-time SQLite engine telemetry (active database size in KB, engine version, total system records).

- **📚 In-App Documentation:**
  - Comprehensive guide covering Sentiment Analysis theory, TextBlob mechanics, classification thresholds, database schema, and operational runbooks.

---

## 📐 Documented Classification Thresholds

SentimentIQ classifies text using rigorous, clearly documented mathematical thresholds:

| Sentiment | Polarity Condition | Description |
| :--- | :--- | :--- |
| **POSITIVE** | `Polarity > +0.10` | Statements expressing satisfaction, optimism, approval, or joy. |
| **NEGATIVE** | `Polarity < -0.10` | Statements expressing distress, failure, disappointment, or criticism. |
| **NEUTRAL** | `-0.10 <= Polarity <= +0.10` | Factual, informative, or emotionally balanced statements. |

### Subjectivity Nuance Spectrum:
- `0.00 - 0.20`: Highly Objective (Pure facts, data points, or unopinionated reporting)
- `0.21 - 0.40`: Moderately Objective
- `0.41 - 0.60`: Balanced (Mix of facts and interpretation)
- `0.61 - 0.80`: Moderately Subjective
- `0.81 - 1.00`: Highly Subjective (Personal feeling, judgment, or intense bias)

---

## 🛠️ Technology Stack

### Backend
- **Python 3.12+**
- **Flask 3.1+** (Application Factory, Blueprints)
- **Flask-SQLAlchemy 3.1+ & SQLAlchemy 2.0+**
- **SQLite 3**
- **TextBlob 0.20+** (NLP Polarity & Subjectivity engine)
- **Pandas 2.2+** (Tabular data formatting & CSV export)
- **Werkzeug 3.1+** (Security & Password Hashing)
- **Pytest 8.0+** (Automated Test Suite)

### Frontend
- **HTML5 & Vanilla CSS3** (Custom Glassmorphism, CSS Custom Properties, Smooth Transitions)
- **Bootstrap 5.3.3** (Responsive Grid & Base Components)
- **Chart.js 4.4+** (Dark-themed Data Visualizations)
- **Lucide Icons**
- **Google Fonts:** Outfit (Headings), Plus Jakarta Sans (UI Body), JetBrains Mono (Metrics)

---

## 📁 Project Structure

```
sentimentiq/
│
├── app.py                      # Flask application factory (create_app)
├── config.py                   # Configuration classes (Development, Testing, Production)
├── requirements.txt            # Python dependencies
├── .env.example                # Example environment variables
├── README.md                   # Complete documentation and setup guide
│
├── database/
│   ├── __init__.py             # Database package exports
│   ├── database.py             # SQLAlchemy instance and init_db helper
│   └── models.py               # User and SentimentResult SQLAlchemy models
│
├── routes/
│   ├── __init__.py             # Blueprints export
│   ├── main.py                 # Landing page, settings, documentation
│   ├── auth.py                 # Registration, login, logout, @login_required
│   ├── sentiment.py            # Dashboard view and /api/analyze endpoint
│   ├── history.py              # History filtering, search, view, delete, Pandas CSV export
│   └── analytics.py            # Real metrics calculation & Chart.js API
│
├── services/
│   ├── __init__.py             # Service package exports
│   └── sentiment_service.py    # TextBlob analysis logic & threshold evaluation
│
├── templates/
│   ├── base.html               # Master layout with responsive sidebar and topbar
│   ├── landing.html            # Public promotional landing page
│   ├── login.html              # Secure user authentication
│   ├── register.html           # User account creation
│   ├── dashboard.html          # Overview KPI cards and recent activity
│   ├── analyze.html            # Text analyzer workspace with dynamic gauges
│   ├── history.html            # Searchable audit table with CSV export
│   ├── analytics.html          # Real Chart.js statistical dashboards
│   ├── settings.html           # Profile, themes, preferences & DB telemetry
│   └── documentation.html      # Comprehensive in-app technical reference
│
├── static/
│   ├── css/
│   │   └── style.css           # Custom dark SaaS design tokens & glass cards
│   └── js/
│       ├── main.js             # Toast notifications, drawer toggle, alert timers
│       ├── sentiment.js        # Live counters, presets, AJAX analyzer controller
│       └── charts.js           # Real database Chart.js rendering engine
│
└── tests/
    ├── __init__.py             # Tests package
    ├── test_sentiment.py       # Unit tests for SentimentService
    └── test_routes.py          # Integration tests for routes, auth, CSV, and isolation
```

---

## 🚀 Setup & Installation

### Step 1: Clone or Navigate to the Project Directory
```powershell
cd C:\Users\ramac\Desktop\sentimentiq
```

### Step 2: Create a Virtual Environment
```powershell
python -m venv .venv
```

### Step 3: Activate the Virtual Environment
**On Windows PowerShell:**
```powershell
.venv\Scripts\activate
```
*(On Linux/macOS: `source .venv/bin/activate`)*

### Step 4: Install Dependencies
```powershell
pip install -r requirements.txt
```

### Step 5: (Optional) Set Environment Variables
Copy `.env.example` to `.env`:
```powershell
Copy-Item .env.example .env
```

### Step 6: Run the Application
```powershell
python app.py
```

### Step 7: Open in Your Browser
Open: **[http://127.0.0.1:5000](http://127.0.0.1:5000)**

---

## 🧪 Running Automated Tests

Run the complete pytest test suite:
```powershell
python -m pytest tests/ -v
```

All 13 unit and route integration tests validate:
- Positive, negative, and neutral sentiment classification
- Threshold boundary compliance
- Empty and invalid input handling
- User registration, login, and session persistence
- Text analysis API persistence to SQLite
- Real Pandas CSV export output format
- Analytics aggregation metrics
- Multi-tenant data isolation between different users

---

## 🔧 Troubleshooting

- **Database file not found:** The application automatically creates the `database/` directory and `sentimentiq.db` file upon initial startup.
- **Port 5000 already in use:** Specify a custom port in `app.py` or run `flask run --port=5001`.
- **TextBlob NLTK warnings:** SentimentIQ uses TextBlob's built-in `PatternAnalyzer`, which requires no manual NLTK corpus downloads.

---

## 📜 Internship Attribution
- **Internship:** QSkill Python Development Internship
- **Project:** Project 2 — SENTIMENTIQ (AI-Powered Text Sentiment Intelligence)
- **Status:** Complete & Production-Ready

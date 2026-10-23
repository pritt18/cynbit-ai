# Revio Intelligence

Aspect-based sentiment analysis, crisis detection, and automated review response system.

### Overview

Most review aggregation platforms only track star ratings and high-level positive/negative sentiment. That misses two critical things:
1. Mixed feedback gets flattened (e.g. *"the app UI is great, but billing charged me twice and support took 3 days"* gets scored as neutral, hiding real issues).
2. High-risk escalations (outage reports, data leak allegations, chargeback threats) get buried in review queues until brand damage has already happened.

This project implements a multi-tier pipeline to break reviews down into operational aspects, score urgency, and draft tone-appropriate responses with safety guardrails.

---

### Features

- **Contrastive Clause Splitting:** Breaks compound sentences on transition words (`but`, `however`, `although`) so positive and negative clauses don't cancel each other out.
- **Aspect-Based Sentiment (ABSA):** Maps feedback to 5 core business areas: Support, Billing, Reliability/Infrastructure, Features, and UI/UX.
- **Crisis & Urgency Scorer (0-100):** Evaluates rating weight, negative sentiment intensity, and high-risk regex triggers (security, legal, churn, chargeback).
- **Human-in-the-Loop Guardrails:** Urgent or high-risk reviews (score >= 65) are flagged for human review before any reply can be published.
- **Brand-Aligned Response Drafting:** Synthesizes context-specific replies across four tones (Empathetic, Professional, Warm, Executive Escalation).
- **Interactive UI & REST API:** Built with Streamlit for live testing/batch analysis and FastAPI for backend integration.

---

### Project Structure

```
cynbit-ai/
├── src/
│   ├── engine.py           # Core ABSA and crisis scoring logic
│   ├── generator.py        # Response drafting & guardrails
│   ├── api.py              # FastAPI endpoints (/analyze, /batch-analyze, /generate-response)
│   ├── app.py              # Streamlit demo dashboard
│   └── pipeline.py         # CLI for batch CSV processing
├── notebooks/
│   └── cynbit_revio_poc.ipynb  # Interactive walkthrough notebook
├── data/
│   ├── sample_reviews.csv      # Test reviews across G2, Trustpilot, App Store, Google
│   └── analyzed_reviews.csv    # Processed pipeline output
├── tests/
│   └── test_engine.py          # Pytest suite (8 unit & integration tests)
├── reports/
│   ├── 01_AI_OPPORTUNITY_REPORT.md
│   └── 02_TECHNICAL_APPROACH_REPORT.md
└── requirements.txt
```

---

### Setup & Usage

#### 1. Install Dependencies
```bash
git clone https://github.com/pritt18/cynbit-ai.git
cd cynbit-ai
pip install -r requirements.txt
```

#### 2. Run Tests
```bash
pytest tests/test_engine.py -v
```

#### 3. Run Streamlit Dashboard
```bash
streamlit run src/app.py
```
Opens at `http://localhost:8501` with tabs for single review inspection, batch CSV analysis, and escalation routing.

#### 4. Run FastAPI Backend
```bash
uvicorn src.api:app --reload --port 8000
```
Interactive docs available at `http://localhost:8000/docs`.

#### 5. Batch CLI Pipeline
```bash
python src/pipeline.py --input data/sample_reviews.csv --output data/analyzed_reviews.csv
```

---

### API Endpoints

- `GET /health` - Health check
- `POST /api/v1/analyze` - Analyze single review text for aspects, urgency score, and churn risk
- `POST /api/v1/batch-analyze` - Process list of reviews with aggregate statistics
- `POST /api/v1/generate-response` - Generate context-aware reply with safety flags

---

### Author
Pritam Gangurde ([@pritt18](https://github.com/pritt18))

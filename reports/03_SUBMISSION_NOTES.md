# Project Documentation & Execution Notes

**Repository:** [github.com/pritt18/cynbit-ai](https://github.com/pritt18/cynbit-ai)  
**Author:** Pritam Gangurde  

---

### Links for Submission

- **Primary Repository:**  
  `https://github.com/pritt18/cynbit-ai`

- **Interactive Walkthrough (Notebook):**  
  `https://github.com/pritt18/cynbit-ai/blob/main/notebooks/cynbit_revio_poc.ipynb`

- **Opportunity & Strategic Report:**  
  `https://github.com/pritt18/cynbit-ai/blob/main/reports/01_AI_OPPORTUNITY_REPORT.md`

- **Technical Approach & Architecture Report:**  
  `https://github.com/pritt18/cynbit-ai/blob/main/reports/02_TECHNICAL_APPROACH_REPORT.md`

- **Processed Dataset Output:**  
  `https://github.com/pritt18/cynbit-ai/blob/main/data/analyzed_reviews.csv`

---

### Execution Notes (Copy-Paste Text)

```text
Built an aspect-based sentiment and automated crisis detection engine for customer reviews. Most review tools just give a 1-5 star score or basic positive/negative tag, which doesn't tell teams where the problem actually is (billing vs support vs bugs) and often misses urgent escalations like data leak claims or chargeback threats.

Architecture & Implementation:
- Clause Splitting & Aspect Mining: Reviews are split into clauses (handling contrastive words like 'but' or 'however') so that mixed feedback like "great UI but horrible support" gets mapped accurately to individual departments (DevOps, Billing, Support, Product).
- Urgency & Crisis Scoring: Custom 0-100 heuristic scoring based on rating weight, sentiment polarity, and regex triggers for legal, security, or churn risks. Critical reviews trigger an SLA warning and require human approval before any reply goes out.
- Response Generation & Guardrails: Drafts tone-matched responses (Empathetic, Professional, Escalation) with built-in guardrails so it doesn't make unapproved financial or legal commitments.
- Tech Stack: Python 3.11, FastAPI for the REST endpoints, and Streamlit for the live demo dashboard. Includes 8 unit tests covering aspect extraction, edge cases, and API routes.

Quick Run:
- Tests: pytest tests/test_engine.py -v
- Web UI: streamlit run src/app.py
- API: uvicorn src.api:app --reload --port 8000
```

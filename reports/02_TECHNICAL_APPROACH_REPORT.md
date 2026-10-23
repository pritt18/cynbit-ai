# Technical Approach Report: Revio Intelligence

**Author:** Pritam Gangurde  
**System:** Multi-Tier Review Intelligence & Escalation Architecture  
**Date:** October 2026  

---

### 1. Architecture Overview

Revio Intelligence is designed as an asynchronous microservice that sits between omnichannel review sources (webhooks, API pollers) and internal communication tools (Slack, CRM, support ticketing).

```
[Review Ingestion]
Google / Trustpilot / G2 / App Store
       │
       ▼
[Preprocessing & Normalization]
Tokenization & Contrastive Clause Splitting (", but", "however")
       │
       ▼
[Intelligence Core]
├── Aspect-Based Sentiment Analysis (ABSA) -> Department Tagging
├── Urgency & Crisis Scorer (0 - 100)
└── Churn Risk Classification (Low / Medium / High)
       │
       ▼
[Response & Action Routing]
├── Urgency < 65: Automated brand-aligned reply draft
└── Urgency >= 65: Human-in-the-loop review queue + Slack/PagerDuty alert
```

---

### 2. Model & Algorithmic Strategy

Instead of routing every single review to an expensive, high-latency LLM API call (which costs money and takes 500-1500ms per request), the architecture uses a hybrid approach:

1. **Fast Rule-Based / Lexicon ABSA (Tier 1):**
   - Runs locally in `< 5ms` with zero GPU requirements.
   - Accurately parses sentences, extracts contrastive clauses, and maps keywords to five core business domains:
     - Customer Support (`support`, `ticket`, `helpdesk`, `response time`)
     - Pricing & Billing (`price`, `billing`, `refund`, `chargeback`, `fee`)
     - Reliability & Uptime (`outage`, `crash`, `down`, `server`, `leak`, `bug`)
     - Product Features (`features`, `dashboard`, `tool`, `automation`, `api`)
     - Ease of Use (`clean`, `intuitive`, `confusing`, `hard to navigate`)
   - Provides a direct drop-in interface for fine-tuned transformer models (`DeBERTa-v3-small` / ONNX runtime) when scale demands it.

2. **Heuristic Urgency Engine (Tier 2):**
   - Calculates a risk score between 0 and 100 using rating weight, negative sentiment intensity, and high-risk regex triggers:
     - Data leaks, security vulnerabilities (+40 weight)
     - Legal threats, chargebacks, fraud allegations (+45 weight)
     - Immediate churn / contract cancellation threats (+35 weight)
     - Multi-hour server outages (+30 weight)
   - Triggers an automatic SLA categorization:
     - Tier 1: Urgent (< 1 hour) - Escalated to leadership
     - Tier 2: High (< 4 hours) - Escalated to senior support / ops
     - Tier 3: Standard (< 24 hours) - Normal queue
     - Tier 4: Routine - Auto-replied or batched

3. **Response Drafting with Safety Guardrails (Tier 3):**
   - Synthesizes responses based on selected brand voice (Empathetic, Professional, Warm, or Executive Escalation).
   - If a review has an urgency score $\ge 65$ or contains legal/security triggers, the engine **locks auto-publishing** and sets `human_review_required = True`.
   - Ensures the company does not inadvertently admit legal liability or make unauthorized refund promises publicly.

---

### 3. Handling Mixed Reviews (Contrastive Clauses)

A major failure point of off-the-shelf sentiment models is compound sentences:
> *"The app UI is clean and easy to use, **but** pricing is very expensive and customer support took days to answer."*

If analyzed as a single string:
- Positive tokens (`clean`, `easy`) cancel out negative tokens (`expensive`, `took days`).
- The review gets classified as "Neutral", and the product team never learns that customer support or billing has issues.

Our preprocessor splits text into clauses using contrastive markers (`", but "`, `"; "`, `" however, "`, `" although "`). Each clause is scored independently and assigned to its corresponding department:
- Clause 1: *"The app UI is clean and easy to use"* -> UI/UX (Positive)
- Clause 2: *"pricing is very expensive"* -> Billing (Negative)
- Clause 3: *"customer support took days to answer"* -> Support (Negative)

---

### 4. Cloud Deployment Architecture

- **Service Framework:** FastAPI running behind Uvicorn / Gunicorn.
- **Containerization:** Standard Docker image (`python:3.11-slim`), stateless design for horizontal scaling on AWS ECS Fargate or Azure Container Apps.
- **Message Broker:** Redis / Celery for handling high-volume spikes of webhook reviews.
- **Database:** PostgreSQL for storing reviews, aspect breakdowns, and review resolution logs.
- **Monitoring:** Prometheus metrics tracking latency, aspect sentiment distribution, and number of daily high-urgency escalations.

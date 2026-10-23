"""
Unit and Integration Tests for Revio-Intelligence Engine.
Author: Pritam Gangurde (pritt18)
"""

import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.engine import RevioIntelligenceEngine
from src.generator import BrandResponseGenerator
from src.api import app


@pytest.fixture
def engine():
    return RevioIntelligenceEngine()


@pytest.fixture
def generator():
    return BrandResponseGenerator()


@pytest.fixture
def api_client():
    return TestClient(app)


def test_positive_review_sentiment(engine):
    text = "Cynbit delivered exceptional AI agent software! Fast, reliable, and high ROI. Amazing work."
    analysis = engine.analyze_review(text, rating=5, author="John Doe", platform="Clutch")
    assert analysis.overall_sentiment == "Positive"
    assert analysis.sentiment_score > 0.3
    assert analysis.is_crisis is False
    assert analysis.churn_risk == "Low"


def test_crisis_outage_detection(engine):
    text = "Severe outage during prime hours! Your server was down for 5 hours and we lost data. We are terminating our contract."
    analysis = engine.analyze_review(text, rating=1, author="Marcus", platform="Trustpilot")
    assert analysis.overall_sentiment == "Negative"
    assert analysis.is_crisis is True
    assert analysis.urgency_score >= 70
    assert analysis.churn_risk == "High"
    assert any("Outage" in t or "Churn" in t for t in analysis.crisis_tags)


def test_aspect_based_sentiment(engine):
    text = "The UI dashboard is clean and easy to navigate, but pricing is very expensive and customer support took days to answer."
    aspects = engine.extract_aspect_sentiments(text)
    aspect_map = {a.aspect: a.sentiment for a in aspects}

    # Should detect Ease of Use as Positive, and Pricing & Billing as Negative
    assert "Ease of Use & UX" in aspect_map or "Product Quality & Features" in aspect_map
    assert "Pricing & Billing" in aspect_map
    assert aspect_map["Pricing & Billing"] == "Negative"


def test_brand_response_generation(engine, generator):
    text = "Great platform! Revio streamlined all our customer feedback smoothly."
    analysis = engine.analyze_review(text, rating=5, author="Sarah Jenkins", platform="G2")
    response = generator.generate(analysis)

    assert "Sarah Jenkins" in response.response_text
    assert response.human_review_required is False
    assert response.tone == "Warm & Enthusiastic"


def test_crisis_guardrail_enforcement(engine, generator):
    text = "Security breach! Our database credentials were leaked online. We will sue."
    analysis = engine.analyze_review(text, rating=1, author="Deepak", platform="Google Reviews")
    response = generator.generate(analysis)

    # Human review must be mandated for security/legal threats
    assert response.human_review_required is True
    assert response.tone == "Executive Priority Escalation"
    assert "priority@cynbit.in" in response.response_text


def test_api_health(api_client):
    res = api_client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"


def test_api_analyze_endpoint(api_client):
    payload = {
        "review_text": "TenantEase rent payment is smooth, but maintenance tickets are bugged.",
        "review_id": "TEST-101",
        "rating": 3,
        "author": "Alice",
        "platform": "App Store"
    }
    res = api_client.post("/api/v1/analyze", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["review_id"] == "TEST-101"
    assert "aspects" in data
    assert data["urgency_score"] >= 0


def test_api_generate_response_endpoint(api_client):
    payload = {
        "review_text": "Outstanding work by Cynbit team on our custom LLM integration!",
        "review_id": "TEST-102",
        "rating": 5,
        "author": "Bob",
        "platform": "Clutch"
    }
    res = api_client.post("/api/v1/generate-response", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "Bob" in data["response_text"]
    assert data["human_review_required"] is False

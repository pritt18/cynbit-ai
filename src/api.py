"""
Revio-Intelligence REST API: Production-grade FastAPI endpoints.
Built for Cynbit Technologies - AI Opportunity Proof of Concept.
Author: Pritam Gangurde (pritt18)
"""

import sys
from pathlib import Path
from typing import List, Optional, Dict, Any
from dataclasses import asdict
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.engine import RevioIntelligenceEngine, ReviewAnalysis, AspectSentimentResult
from src.generator import BrandResponseGenerator, GeneratedResponse

# Initialize FastAPI App
app = FastAPI(
    title="Cynbit Revio-Intelligence API",
    description="Aspect-Based Sentiment Mining, Churn/Crisis Early Warning & Autonomous Response Engine",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for cross-origin frontend support
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize singletons
engine = RevioIntelligenceEngine()
generator = BrandResponseGenerator()


# Pydantic Schemas
class SingleReviewRequest(BaseModel):
    review_text: str = Field(..., min_length=3, description="Customer review text")
    review_id: Optional[str] = Field(default="REV-001", description="Unique identifier for the review")
    rating: Optional[int] = Field(default=None, ge=1, le=5, description="Star rating from 1 to 5")
    author: Optional[str] = Field(default="Anonymous", description="Author or reviewer name")
    platform: Optional[str] = Field(default="Google Reviews", description="Source channel (e.g., G2, Trustpilot)")


class AspectResponseModel(BaseModel):
    aspect: str
    sentiment: str
    score: float
    department: str
    relevant_snippets: List[str]
    confidence: float


class ReviewAnalysisResponse(BaseModel):
    review_id: str
    raw_text: str
    author: Optional[str]
    platform: Optional[str]
    overall_sentiment: str
    sentiment_score: float
    rating: Optional[int]
    aspects: List[AspectResponseModel]
    urgency_score: int
    is_crisis: bool
    crisis_tags: List[str]
    churn_risk: str
    sla_recommendation: str
    root_cause_summary: str
    action_item: str


class BatchReviewRequest(BaseModel):
    reviews: List[SingleReviewRequest]


class BatchReviewResponse(BaseModel):
    total_reviews: int
    positive_count: int
    negative_count: int
    neutral_count: int
    crisis_count: int
    high_churn_risk_count: int
    results: List[ReviewAnalysisResponse]


class GenerateResponseRequest(BaseModel):
    review_text: str = Field(..., min_length=3)
    review_id: Optional[str] = "REV-001"
    rating: Optional[int] = None
    author: Optional[str] = "Anonymous"
    platform: Optional[str] = "Google Reviews"
    preferred_tone: Optional[str] = None
    sign_off_name: Optional[str] = "The Cynbit Customer Experience Team"


class GenerateResponseOutput(BaseModel):
    review_id: str
    response_text: str
    tone: str
    human_review_required: bool
    escalation_reason: Optional[str]
    internal_slack_ticket: str
    confidence_score: float


@app.get("/", tags=["System"])
def root_info():
    """System metadata and API service health."""
    return {
        "service": "Cynbit Revio-Intelligence API",
        "status": "online",
        "version": "1.0.0",
        "author": "Pritam Gangurde",
        "endpoints": {
            "docs": "/docs",
            "single_analysis": "/api/v1/analyze",
            "batch_analysis": "/api/v1/batch-analyze",
            "generate_response": "/api/v1/generate-response"
        }
    }


@app.get("/health", tags=["System"])
def health_check():
    """Health check probe."""
    return {"status": "healthy", "engine": "RevioIntelligenceEngine v1.0"}


@app.post("/api/v1/analyze", response_model=ReviewAnalysisResponse, tags=["Intelligence"])
def analyze_single_review(payload: SingleReviewRequest):
    """
    Performs Aspect-Based Sentiment Analysis, Crisis Detection, and Churn Risk Scoring
    on an individual customer review.
    """
    try:
        analysis = engine.analyze_review(
            text=payload.review_text,
            review_id=payload.review_id or "REV-001",
            rating=payload.rating,
            author=payload.author,
            platform=payload.platform
        )
        return ReviewAnalysisResponse(**asdict(analysis))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@app.post("/api/v1/batch-analyze", response_model=BatchReviewResponse, tags=["Intelligence"])
def analyze_batch_reviews(payload: BatchReviewRequest):
    """
    Processes a batch of reviews and returns aggregate analytics alongside itemized insights.
    """
    try:
        results: List[ReviewAnalysisResponse] = []
        pos = neg = neu = crisis = high_churn = 0

        for r in payload.reviews:
            analysis = engine.analyze_review(
                text=r.review_text,
                review_id=r.review_id or f"REV-BATCH-{len(results)+1}",
                rating=r.rating,
                author=r.author,
                platform=r.platform
            )
            item = ReviewAnalysisResponse(**asdict(analysis))
            results.append(item)

            if item.overall_sentiment == "Positive":
                pos += 1
            elif item.overall_sentiment == "Negative":
                neg += 1
            else:
                neu += 1

            if item.is_crisis:
                crisis += 1
            if item.churn_risk == "High":
                high_churn += 1

        return BatchReviewResponse(
            total_reviews=len(results),
            positive_count=pos,
            negative_count=neg,
            neutral_count=neu,
            crisis_count=crisis,
            high_churn_risk_count=high_churn,
            results=results
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@app.post("/api/v1/generate-response", response_model=GenerateResponseOutput, tags=["Generation"])
def generate_brand_response(payload: GenerateResponseRequest):
    """
    Synthesizes a brand-aligned, empathetic public reply with safety and escalation guardrails.
    """
    try:
        analysis = engine.analyze_review(
            text=payload.review_text,
            review_id=payload.review_id or "REV-001",
            rating=payload.rating,
            author=payload.author,
            platform=payload.platform
        )
        resp = generator.generate(
            analysis=analysis,
            preferred_tone=payload.preferred_tone,
            sign_off_name=payload.sign_off_name or "The Cynbit Customer Experience Team"
        )
        return GenerateResponseOutput(**asdict(resp))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

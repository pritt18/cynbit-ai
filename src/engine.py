"""
Revio Intelligence Engine: Core NLP, ABSA, and Crisis Detection Engine.
Aspect-Based Sentiment Mining, Urgency Scoring, and Churn Risk Modeling.
"""

import re
import math
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

# Aspect Definitions with associated lexicons and context patterns
ASPECT_TAXONOMY: Dict[str, Dict[str, Any]] = {
    "Customer Support": {
        "keywords": [
            "support", "agent", "ticket", "service", "representative", "helpdesk",
            "reply", "response time", "unreachable", "communication", "onboarding",
            "assisted", "assistance", "staff", "team"
        ],
        "department": "Customer Success & Ops"
    },
    "Pricing & Billing": {
        "keywords": [
            "price", "pricing", "cost", "expensive", "bill", "billing", "fee",
            "charge", "double-charged", "refund", "chargeback", "payment", "money",
            "roi", "worth", "expensive", "affordable"
        ],
        "department": "Finance & Billing"
    },
    "System Reliability & Performance": {
        "keywords": [
            "outage", "downtime", "crash", "bug", "bugs", "latency", "slow",
            "server", "down", "uptime", "glitch", "load", "hanging", "error",
            "security", "leak", "credentials", "unreachable", "failed"
        ],
        "department": "Core Infrastructure & DevOps"
    },
    "Product Quality & Features": {
        "keywords": [
            "feature", "features", "ui", "ux", "dashboard", "tool", "workflow",
            "automation", "agent", "model", "capabilities", "functionality",
            "integration", "webhook", "api", "app", "mobile"
        ],
        "department": "Product & Engineering"
    },
    "Ease of Use & UX": {
        "keywords": [
            "easy", "intuitive", "smooth", "seamless", "clean", "simple",
            "complicated", "confusing", "hard", "clunky", "navigation",
            "interface", "design"
        ],
        "department": "Design & Product UX"
    }
}

# Critical Crisis & Escalation Triggers
CRISIS_TRIGGERS: List[Dict[str, Any]] = [
    {"pattern": r"\b(security|leak|leaked|breach|vulnerability|credentials)\b", "weight": 40, "tag": "Security Threat"},
    {"pattern": r"\b(scam|fraud|lawsuit|legal|sue|court|regulator|police)\b", "weight": 45, "tag": "Legal / Fraud Risk"},
    {"pattern": r"\b(chargeback|double-charged|dispute|refund)\b", "weight": 35, "tag": "Billing Dispute"},
    {"pattern": r"\b(terminate|cancel contract|churn|switching to|leaving)\b", "weight": 35, "tag": "High Churn Risk"},
    {"pattern": r"\b(outage|unreachable|down for \d+|lost data|corrupted)\b", "weight": 30, "tag": "Severe Outage / Data Loss"},
    {"pattern": r"\b(unacceptable|horrible|worst|disaster|furious|terrible)\b", "weight": 20, "tag": "Severe Dissatisfaction"}
]

# Lexicons for lightweight, zero-dependency high-speed sentiment scoring
POSITIVE_WORDS = {
    "great", "excellent", "outstanding", "seamless", "fast", "love", "best",
    "top-notch", "reliable", "helpful", "good", "amazing", "smooth", "high roi",
    "valuable", "friendly", "superb", "perfect", "easy", "clean", "effective",
    "impressive", "world-class", "innovative", "saving", "streamlined", "instantaneous"
}

NEGATIVE_WORDS = {
    "bad", "terrible", "worst", "unacceptable", "slow", "bug", "bugs", "glitch",
    "outage", "downtime", "delayed", "expensive", "scam", "fraud", "failed",
    "leak", "broken", "useless", "annoying", "poor", "crash", "horrible",
    "disaster", "furious", "double-charged", "unreachable", "robotic", "looping",
    "delayed", "frustrating", "waste", "confusing", "clunky"
}

INTENSIFIERS = {
    "very": 1.5, "extremely": 2.0, "completely": 1.8, "totally": 1.8,
    "super": 1.5, "hugely": 1.7, "absolutely": 1.9, "exceptionally": 1.8
}

NEGATIONS = {"not", "never", "no", "neither", "barely", "hardly", "didn't", "cannot", "can't", "doesn't", "isn't"}


@dataclass
class AspectSentimentResult:
    aspect: str
    sentiment: str  # Positive, Neutral, Negative
    score: float    # -1.0 to 1.0
    department: str
    relevant_snippets: List[str]
    confidence: float


@dataclass
class ReviewAnalysis:
    review_id: str
    raw_text: str
    author: Optional[str]
    platform: Optional[str]
    overall_sentiment: str
    sentiment_score: float
    rating: Optional[int]
    aspects: List[AspectSentimentResult]
    urgency_score: int          # 0 - 100
    is_crisis: bool
    crisis_tags: List[str]
    churn_risk: str             # High, Medium, Low
    sla_recommendation: str
    root_cause_summary: str
    action_item: str


class RevioIntelligenceEngine:
    """
    Advanced Sentiment & Crisis Intelligence Engine designed for multi-tenant SaaS platforms.
    Deconstructs reviews into Aspect-Based Sentiments, detects operational risks,
    and calculates urgency metrics.
    """

    def __init__(self):
        self.taxonomy = ASPECT_TAXONOMY
        self.crisis_triggers = CRISIS_TRIGGERS

    def _split_into_sentences(self, text: str) -> List[str]:
        """
        Split text into individual sentences and contrastive clauses for fine-grained aspect analysis.
        Separates clauses joined by ', but', ';', 'however', 'although', etc.
        """
        raw_chunks = re.split(r'(?<=[.!?])\s+', text.strip())
        clauses: List[str] = []
        for chunk in raw_chunks:
            sub_clauses = re.split(
                r'\s*(?:,\s*but\s+|;\s*|\s+however,?\s*|\s+although\s+|\s+whereas\s+|\s+yet\s+)\s*',
                chunk,
                flags=re.IGNORECASE
            )
            for sc in sub_clauses:
                if len(sc.strip()) > 3:
                    clauses.append(sc.strip())
        return clauses

    def _score_text_sentiment(self, text: str) -> float:
        """
        Calculates valence score between -1.0 and +1.0 using tokenized n-gram analysis
        with negation and intensifier support.
        """
        words = re.findall(r"\b[\w'-]+\b", text.lower())
        if not words:
            return 0.0

        score = 0.0
        multiplier = 1.0
        negated = False

        for i, word in enumerate(words):
            if word in NEGATIONS:
                negated = True
                continue

            current_multiplier = multiplier
            if i > 0 and words[i - 1] in INTENSIFIERS:
                current_multiplier *= INTENSIFIERS[words[i - 1]]

            word_val = 0.0
            if word in POSITIVE_WORDS:
                word_val = 1.0
            elif word in NEGATIVE_WORDS:
                word_val = -1.2  # Negative words weighted slightly higher for risk detection

            if negated:
                word_val = -word_val * 0.8
                negated = False

            score += word_val * current_multiplier

        # Normalize score between -1.0 and +1.0 using hyperbolic tangent
        norm_score = math.tanh(score / 3.0)
        return round(norm_score, 3)

    def extract_aspect_sentiments(self, text: str) -> List[AspectSentimentResult]:
        """
        Performs Aspect-Based Sentiment Analysis (ABSA).
        Maps sentence-level contexts to operational business aspects.
        """
        sentences = self._split_into_sentences(text)
        aspect_results: List[AspectSentimentResult] = []

        for aspect_name, meta in self.taxonomy.items():
            keywords = meta["keywords"]
            department = meta["department"]
            relevant_snippets: List[str] = []
            snippet_scores: List[float] = []

            for sentence in sentences:
                sentence_lower = sentence.lower()
                # Check for keyword occurrence
                if any(re.search(rf"\b{re.escape(k)}\b", sentence_lower) for k in keywords):
                    sent_score = self._score_text_sentiment(sentence)
                    relevant_snippets.append(sentence)
                    snippet_scores.append(sent_score)

            if snippet_scores:
                avg_score = sum(snippet_scores) / len(snippet_scores)
                avg_score = max(-1.0, min(1.0, round(avg_score, 3)))
                
                if avg_score > 0.15:
                    label = "Positive"
                elif avg_score < -0.15:
                    label = "Negative"
                else:
                    label = "Neutral"

                # Confidence based on snippet support and score margin
                confidence = round(min(0.98, 0.65 + (len(snippet_scores) * 0.1) + abs(avg_score) * 0.2), 2)

                aspect_results.append(
                    AspectSentimentResult(
                        aspect=aspect_name,
                        sentiment=label,
                        score=avg_score,
                        department=department,
                        relevant_snippets=relevant_snippets,
                        confidence=confidence
                    )
                )

        return aspect_results

    def compute_urgency_and_crisis(
        self, text: str, rating: Optional[int], overall_sentiment_score: float
    ) -> Dict[str, Any]:
        """
        Evaluates crisis potential, urgency level (0-100), and SLA escalation pathway.
        """
        urgency = 0
        detected_tags: List[str] = []

        # 1. Rating contribution
        if rating is not None:
            if rating == 1:
                urgency += 40
            elif rating == 2:
                urgency += 25
            elif rating == 3:
                urgency += 10
            elif rating >= 4:
                urgency += 0

        # 2. Sentiment negativity contribution
        if overall_sentiment_score < -0.5:
            urgency += 25
        elif overall_sentiment_score < -0.1:
            urgency += 15

        # 3. Crisis regex trigger evaluation
        text_lower = text.lower()
        for trigger in self.crisis_triggers:
            if re.search(trigger["pattern"], text_lower):
                urgency += trigger["weight"]
                if trigger["tag"] not in detected_tags:
                    detected_tags.append(trigger["tag"])

        urgency = max(0, min(100, int(urgency)))
        is_crisis = urgency >= 65 or len(detected_tags) >= 2 or any("Security" in t or "Legal" in t for t in detected_tags)

        # Churn Risk Calculation
        if urgency >= 70 or any("Churn" in t or "Dispute" in t for t in detected_tags):
            churn_risk = "High"
        elif urgency >= 40 or overall_sentiment_score < -0.2:
            churn_risk = "Medium"
        else:
            churn_risk = "Low"

        # SLA Determination
        if urgency >= 80 or any("Security" in t or "Legal" in t for t in detected_tags):
            sla = "Tier-1 Critical: < 1 Hour (Executive & Legal Escalation)"
        elif urgency >= 55:
            sla = "Tier-2 High: < 4 Hours (Senior Support Lead)"
        elif urgency >= 30:
            sla = "Tier-3 Normal: < 24 Hours (Standard Agent Workflow)"
        else:
            sla = "Tier-4 Automated: Instant / Automated Brand Response"

        return {
            "urgency_score": urgency,
            "is_crisis": is_crisis,
            "crisis_tags": detected_tags,
            "churn_risk": churn_risk,
            "sla": sla
        }

    def analyze_review(
        self,
        text: str,
        review_id: str = "REV-LIVE",
        rating: Optional[int] = None,
        author: Optional[str] = "Anonymous",
        platform: Optional[str] = "Direct Web"
    ) -> ReviewAnalysis:
        """
        Executes end-to-end multi-dimensional intelligence on a single review.
        """
        # Overall sentiment
        overall_score = self._score_text_sentiment(text)
        if overall_score > 0.15:
            overall_label = "Positive"
        elif overall_score < -0.15:
            overall_label = "Negative"
        else:
            overall_label = "Neutral"

        # Aspect extraction
        aspects = self.extract_aspect_sentiments(text)

        # Urgency & Crisis
        risk_metrics = self.compute_urgency_and_crisis(text, rating, overall_score)

        # Root Cause Analysis
        negative_aspects = [a.aspect for a in aspects if a.sentiment == "Negative"]
        positive_aspects = [a.aspect for a in aspects if a.sentiment == "Positive"]

        if risk_metrics["is_crisis"]:
            root_cause = f"CRITICAL INCIDENT: Triggered by {', '.join(risk_metrics['crisis_tags'])}."
            action_item = f"Immediate incident dispatch to {', '.join(set([a.department for a in aspects])) or 'Operations'} team."
        elif negative_aspects:
            root_cause = f"Customer dissatisfaction primarily focused on: {', '.join(negative_aspects)}."
            action_item = f"Notify {', '.join(set([a.department for a in aspects if a.sentiment == 'Negative']))} to review root cause ticket."
        elif positive_aspects:
            root_cause = f"High satisfaction across {', '.join(positive_aspects)}."
            action_item = "Acknowledge review, reinforce brand advocacy, and invite for case study or testimonial."
        else:
            root_cause = "General brand sentiment with no specific departmental breakdown."
            action_item = "Send standard automated brand-aligned courtesy response."

        return ReviewAnalysis(
            review_id=review_id,
            raw_text=text,
            author=author,
            platform=platform,
            overall_sentiment=overall_label,
            sentiment_score=overall_score,
            rating=rating,
            aspects=aspects,
            urgency_score=risk_metrics["urgency_score"],
            is_crisis=risk_metrics["is_crisis"],
            crisis_tags=risk_metrics["crisis_tags"],
            churn_risk=risk_metrics["churn_risk"],
            sla_recommendation=risk_metrics["sla"],
            root_cause_summary=root_cause,
            action_item=action_item
        )


if __name__ == "__main__":
    engine = RevioIntelligenceEngine()
    sample = "TenantEase has a clean UI, but the maintenance ticket notification failed during an urgent leak. Support took 3 days!"
    result = engine.analyze_review(sample, rating=2, author="Priya S.", platform="Google Reviews")
    print(f"Sentiment: {result.overall_sentiment} ({result.sentiment_score})")
    print(f"Urgency: {result.urgency_score}/100, Crisis: {result.is_crisis}")
    print("Aspects detected:")
    for a in result.aspects:
        print(f" - {a.aspect}: {a.sentiment} ({a.score}) -> Dept: {a.department}")

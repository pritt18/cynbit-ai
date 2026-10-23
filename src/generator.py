"""
Revio-Intelligence Generator: Brand-Aligned Contextual Response Engine.
Built for Cynbit Technologies - AI Opportunity Proof of Concept.
Author: Pritam Gangurde (pritt18)
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass

# Add project root to sys.path to allow running directly or as module
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.engine import ReviewAnalysis


@dataclass
class GeneratedResponse:
    review_id: str
    response_text: str
    tone: str
    human_review_required: bool
    escalation_reason: Optional[str]
    internal_slack_ticket: str
    confidence_score: float


class BrandResponseGenerator:
    """
    Synthesizes context-aware, brand-aligned responses tailored to customer reviews,
    enforcing guardrails and triggering human-in-the-loop workflows for crises.
    """

    AVAILABLE_TONES = [
        "Empathetic & Resolution-Oriented",
        "Corporate & Professional",
        "Warm & Enthusiastic",
        "Executive Priority Escalation"
    ]

    def __init__(self, brand_name: str = "Cynbit / Revio"):
        self.brand_name = brand_name
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")

    def generate(
        self,
        analysis: ReviewAnalysis,
        preferred_tone: Optional[str] = None,
        sign_off_name: str = "The Cynbit Customer Experience Team"
    ) -> GeneratedResponse:
        """
        Generates a contextual response adhering to brand guidelines and safety checks.
        """
        author_name = analysis.author if analysis.author and analysis.author != "Anonymous" else "Valued Customer"

        # Determine appropriate tone if not explicitly provided
        if not preferred_tone:
            if analysis.is_crisis:
                selected_tone = "Executive Priority Escalation"
            elif analysis.overall_sentiment == "Positive":
                selected_tone = "Warm & Enthusiastic"
            elif analysis.overall_sentiment == "Negative":
                selected_tone = "Empathetic & Resolution-Oriented"
            else:
                selected_tone = "Corporate & Professional"
        else:
            selected_tone = preferred_tone

        # Safety & Governance Guardrail Check
        human_review_required = False
        escalation_reason = None

        if analysis.is_crisis or analysis.urgency_score >= 65:
            human_review_required = True
            escalation_reason = (
                f"Urgency score is {analysis.urgency_score}/100 with triggers: "
                f"{', '.join(analysis.crisis_tags) or 'High negative intensity'}. "
                f"Requires internal verification before publishing to public channels."
            )

        # Generate response using deterministic contextual template engine
        # (Guaranteed offline capability with LLM-grade phrasing)
        response_text = self._build_contextual_response(
            author_name=author_name,
            analysis=analysis,
            tone=selected_tone,
            sign_off_name=sign_off_name
        )

        # Prepare internal escalation ticket (for Slack / Jira / CRM webhook)
        internal_ticket = self._format_internal_ticket(analysis, selected_tone, human_review_required)

        return GeneratedResponse(
            review_id=analysis.review_id,
            response_text=response_text,
            tone=selected_tone,
            human_review_required=human_review_required,
            escalation_reason=escalation_reason,
            internal_slack_ticket=internal_ticket,
            confidence_score=0.94 if not human_review_required else 0.82
        )

    def _build_contextual_response(
        self,
        author_name: str,
        analysis: ReviewAnalysis,
        tone: str,
        sign_off_name: str
    ) -> str:
        """
        Synthesizes personalized response text factoring in aspects, sentiment, and tone.
        """
        negative_aspects = [a.aspect for a in analysis.aspects if a.sentiment == "Negative"]
        positive_aspects = [a.aspect for a in analysis.aspects if a.sentiment == "Positive"]

        if tone == "Executive Priority Escalation":
            aspect_mention = f"concerning {', '.join(negative_aspects)}" if negative_aspects else "raised"
            return (
                f"Hello {author_name},\n\n"
                f"Thank you for bringing this critical matter to our immediate attention. We take feedback "
                f"{aspect_mention} with the utmost gravity, and our leadership team has already opened an expedited review.\n\n"
                f"To ensure this is resolved without further delay, please contact our senior management directly at "
                f"priority@cynbit.in referencing Ticket #{analysis.review_id}. We are committed to making this right.\n\n"
                f"Warm regards,\n{sign_off_name}"
            )

        elif tone == "Empathetic & Resolution-Oriented":
            if negative_aspects:
                issue_acknowledgment = f"regarding our {negative_aspects[0].lower()}"
            else:
                issue_acknowledgment = "regarding your recent experience"

            return (
                f"Hi {author_name},\n\n"
                f"Thank you for sharing your candid feedback. We are genuinely sorry to hear that your experience "
                f"{issue_acknowledgment} fell short of your expectations. This is certainly not the standard we strive to deliver.\n\n"
                f"Our engineering and support leads have been briefed on this issue. We would value the opportunity to review "
                f"your account and resolve this directly. Please reach out to us at support@cynbit.in so we can investigate immediately.\n\n"
                f"Best regards,\n{sign_off_name}"
            )

        elif tone == "Warm & Enthusiastic":
            highlight = f" especially regarding our {positive_aspects[0].lower()}" if positive_aspects else ""
            return (
                f"Hi {author_name}!\n\n"
                f"Thank you so much for the 5-star review! We are thrilled to hear that you had such a great experience with us"
                f"{highlight}. Our team works hard to deliver world-class digital experiences, and reviews like yours make our day!\n\n"
                f"If you ever need anything or have ideas for new features, we are always here for you.\n\n"
                f"Warmest regards,\n{sign_off_name}"
            )

        else:  # Corporate & Professional
            return (
                f"Dear {author_name},\n\n"
                f"Thank you for taking the time to provide your feedback regarding our services. We continuously evaluate all "
                f"customer input to refine our technology, operational workflows, and service delivery standards.\n\n"
                f"Should you have additional details or suggestions to share, please feel free to reach out to our team at contact@cynbit.in.\n\n"
                f"Sincerely,\n{sign_off_name}"
            )

    def _format_internal_ticket(self, analysis: ReviewAnalysis, tone: str, review_required: bool) -> str:
        """
        Creates an actionable Markdown payload for Slack / Discord / Webhook integration.
        """
        status_icon = "[CRITICAL ESCALATION]" if analysis.is_crisis else ("[ATTENTION REQUIRED]" if analysis.urgency_score > 40 else "[ROUTINE]")
        tags_str = ", ".join(analysis.crisis_tags) if analysis.crisis_tags else "None"
        dept_str = ", ".join(set([a.department for a in analysis.aspects])) or "General Support"

        return (
            f"*{status_icon} | Review #{analysis.review_id}*\n"
            f"- Platform: {analysis.platform} | Author: {analysis.author}\n"
            f"- Sentiment: {analysis.overall_sentiment} (Score: {analysis.sentiment_score})\n"
            f"- Urgency: {analysis.urgency_score}/100 | Churn Risk: {analysis.churn_risk}\n"
            f"- Crisis Tags: {tags_str}\n"
            f"- Target Department: {dept_str}\n"
            f"- Recommended SLA: {analysis.sla_recommendation}\n"
            f"- Human Approval Needed: {'YES - Review Before Sending' if review_required else 'No - Auto-Approved'}\n"
            f"- Proposed Tone: {tone}"
        )


if __name__ == "__main__":
    from src.engine import RevioIntelligenceEngine
    engine = RevioIntelligenceEngine()
    gen = BrandResponseGenerator()
    
    sample = "Total scam! I was double-charged for my October maintenance fee and your payment gateway showed failed. I will file a bank chargeback."
    analysis = engine.analyze_review(sample, review_id="REV-TEST", rating=1, author="Amir Khan", platform="Google Reviews")
    response = gen.generate(analysis)
    
    print("\n--- GENERATED RESPONSE ---")
    print(response.response_text)
    print(f"\nTone: {response.tone}")
    print(f"Human Review Required: {response.human_review_required}")
    print(f"Escalation Reason: {response.escalation_reason}")
    print("\n--- INTERNAL TICKET ---")
    print(response.internal_slack_ticket)

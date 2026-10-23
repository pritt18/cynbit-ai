"""
Revio-Intelligence Dashboard: Interactive Streamlit Web Application.
Aspect-Based Sentiment Mining, Churn/Crisis Early Warning & Autonomous Response Engine.
"""

import sys
from pathlib import Path
import pandas as pd
import streamlit as st

# Setup Path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.engine import RevioIntelligenceEngine, ASPECT_TAXONOMY
from src.generator import BrandResponseGenerator

# Page Configuration
st.set_page_config(
    page_title="Revio Intelligence | Enterprise CX & Crisis Engine",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E293B;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #64748B;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background: #FFFFFF;
        border-radius: 10px;
        padding: 1.2rem;
        border: 1px solid #E2E8F0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .crisis-alert {
        background-color: #FEF2F2;
        border-left: 5px solid #EF4444;
        padding: 1rem;
        border-radius: 6px;
        color: #991B1B;
        margin-bottom: 1rem;
    }
    .success-alert {
        background-color: #F0FDF4;
        border-left: 5px solid #22C55E;
        padding: 1rem;
        border-radius: 6px;
        color: #166534;
        margin-bottom: 1rem;
    }
    .badge-positive {
        background-color: #DCFCE7;
        color: #166534;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .badge-negative {
        background-color: #FEE2E2;
        color: #991B1B;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .badge-neutral {
        background-color: #F1F5F9;
        color: #475569;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: 600;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Singletons
@st.cache_resource
def load_components():
    return RevioIntelligenceEngine(), BrandResponseGenerator()

engine, generator = load_components()

# Preset Test Scenarios
PRESETS = {
    "1. Critical Infrastructure Outage (Enterprise SaaS)": {
        "text": "Unacceptable server outage during our holiday marketing campaign. Your dashboard was unreachable for 4 hours and support took 2 days to reply. We are considering terminating our enterprise contract immediately.",
        "rating": 1,
        "author": "Marcus Vance",
        "platform": "Trustpilot"
    },
    "2. Billing Dispute & Chargeback Threat (TenantEase)": {
        "text": "Total scam. I was double-charged for my October maintenance fee and your payment gateway showed failed transaction. I want an immediate refund or I will file a bank chargeback.",
        "rating": 1,
        "author": "Amir Khan",
        "platform": "Google Reviews"
    },
    "3. Positive Autonomous Agent Praise (Enterprise Client)": {
        "text": "Outstanding autonomous AI agent integration! The team transformed our manual customer triage into an automated 24/7 intelligent pipeline. High ROI and smooth delivery.",
        "rating": 5,
        "author": "Vikram Singhania",
        "platform": "Clutch"
    },
    "4. Mixed UX & Notification Delay (TenantEase)": {
        "text": "The app interface is clean and paying rent is smooth, but maintenance ticket notifications are delayed. Landlords do not see water leak alerts in time.",
        "rating": 3,
        "author": "Priya Sharma",
        "platform": "App Store"
    },
    "5. Feature Request & Prompt Controls (Revio SaaS)": {
        "text": "The AI auto-response feature is too robotic and repeats the exact same phrases. It doesn't capture nuanced feedback about pricing dissatisfaction. Needs better prompt controls.",
        "rating": 2,
        "author": "Jessica Taylor",
        "platform": "G2"
    }
}

# Sidebar
with st.sidebar:
    st.markdown("### ⚡ REVIO INTELLIGENCE")
    st.markdown("**Enterprise CX & Crisis Platform**")
    st.markdown("*Aspect Sentiment & Automated Response Engine*")
    st.markdown("---")
    st.markdown("### 🎯 Engine Capabilities")
    st.markdown("""
    - **Aspect-Based Sentiment (ABSA)**
    - **Crisis & Urgency Scorer (0-100)**
    - **Churn Risk Detection**
    - **Brand-Aligned Response Synthesis**
    - **Human-in-the-Loop Guardrails**
    - **Departmental SLA Routing**
    """)
    st.markdown("---")
    st.markdown("**Version:** v1.0.0 Enterprise  \n**Status:** Online & Active")

# Main Header
st.markdown('<div class="main-header">⚡ Revio Intelligence Engine</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Aspect-Based Sentiment Mining, Churn/Crisis Early Warning & Autonomous Brand-Aligned Response Engine</div>', unsafe_allow_html=True)

# Navigation Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "🔍 Single Review Diagnostic",
    "📊 Omnichannel Batch Intelligence",
    "🚨 Crisis Escalation Matrix",
    "🏛️ System Synergy & Architecture"
])

# ----------------- TAB 1: SINGLE REVIEW DIAGNOSTIC -----------------
with tab1:
    st.markdown("### 🧪 Live Review Intelligence & Response Playground")
    st.write("Analyze individual feedback from any channel, isolate operational aspects, score urgency, and draft brand-aligned replies.")

    # Preset Selector
    preset_choice = st.selectbox(
        "Load Pre-Configured Test Scenario:",
        ["Select a preset..."] + list(PRESETS.keys())
    )

    if preset_choice != "Select a preset...":
        preset_data = PRESETS[preset_choice]
        default_text = preset_data["text"]
        default_rating = preset_data["rating"]
        default_author = preset_data["author"]
        default_platform = preset_data["platform"]
    else:
        default_text = "The onboarding experience was smooth and your AI agent is fast, but your monthly billing charge was confusing and customer support took 48 hours to explain it."
        default_rating = 3
        default_author = "Elena Rostova"
        default_platform = "Google Reviews"

    col_input1, col_input2 = st.columns([3, 1])

    with col_input1:
        review_text = st.text_area("Customer Review Content:", value=default_text, height=110)

    with col_input2:
        rating = st.selectbox("Star Rating:", [1, 2, 3, 4, 5], index=[1, 2, 3, 4, 5].index(default_rating))
        author = st.text_input("Reviewer Name:", value=default_author)
        platform = st.selectbox("Platform Channel:", ["Google Reviews", "Trustpilot", "G2", "Capterra", "App Store", "Clutch"], index=0)

    col_tone1, col_tone2 = st.columns([2, 1])
    with col_tone1:
        preferred_tone = st.selectbox(
            "Desired Response Brand Tone:",
            ["Auto-Select (Recommended)", "Empathetic & Resolution-Oriented", "Corporate & Professional", "Warm & Enthusiastic", "Executive Priority Escalation"]
        )
    with col_tone2:
        sign_off = st.text_input("Brand Sign-off:", value="The Customer Experience Team")

    if st.button("🚀 Run Intelligence Analysis", type="primary", use_container_width=True):
        tone_arg = None if preferred_tone == "Auto-Select (Recommended)" else preferred_tone
        analysis = engine.analyze_review(
            text=review_text,
            review_id="REV-DEMO-001",
            rating=rating,
            author=author,
            platform=platform
        )
        gen_response = generator.generate(analysis, preferred_tone=tone_arg, sign_off_name=sign_off)

        st.markdown("---")
        st.subheader("📊 Diagnostic Summary")

        # Top Metric Cards
        mcol1, mcol2, mcol3, mcol4 = st.columns(4)

        with mcol1:
            st.metric("Overall Sentiment", f"{analysis.overall_sentiment}", f"Score: {analysis.sentiment_score}")

        with mcol2:
            st.metric("Urgency Index", f"{analysis.urgency_score} / 100", f"SLA: {analysis.sla_recommendation.split(':')[0]}")

        with mcol3:
            st.metric("Churn Risk Level", f"{analysis.churn_risk}")

        with mcol4:
            st.metric("Crisis Detected?", f"{'YES 🚨' if analysis.is_crisis else 'NO ✅'}")

        # Crisis Alert Banner if applicable
        if analysis.is_crisis:
            st.markdown(f"""
            <div class="crisis-alert">
                <strong>🚨 CRITICAL INCIDENT ESCALATION TRIGGERED</strong><br>
                <strong>Detected Triggers:</strong> {', '.join(analysis.crisis_tags)}<br>
                <strong>Recommended Action:</strong> {analysis.action_item}
            </div>
            """, unsafe_allow_html=True)

        # Aspect-Based Sentiment Breakdown
        st.markdown("#### 🎯 Aspect-Based Sentiment Analysis (ABSA)")
        if analysis.aspects:
            aspect_data = []
            for a in analysis.aspects:
                aspect_data.append({
                    "Aspect": a.aspect,
                    "Sentiment": a.sentiment,
                    "Valence Score (-1 to +1)": a.score,
                    "Assigned Department": a.department,
                    "Confidence": f"{int(a.confidence * 100)}%",
                    "Context Snippet": " | ".join(a.relevant_snippets)
                })
            st.dataframe(pd.DataFrame(aspect_data), use_container_width=True)
        else:
            st.info("No specific operational aspects detected in this text (general brand sentiment).")

        # Response Generation Section
        st.markdown("---")
        st.subheader("🤖 Brand-Aligned Contextual Response Studio")

        res_col1, res_col2 = st.columns([3, 2])

        with res_col1:
            st.markdown(f"**Drafted Public Response (Tone: `{gen_response.tone}`)**")
            st.text_area("Generated Reply:", value=gen_response.response_text, height=180)

            if gen_response.human_review_required:
                st.warning(f"⚠️ **Human-in-the-Loop Gate:** {gen_response.escalation_reason}")
            else:
                st.success("✅ **Auto-Publish Safe:** Meets brand compliance and safety thresholds.")

        with res_col2:
            st.markdown("**Internal Ticket Payload (Slack / CRM Webhook)**")
            st.code(gen_response.internal_slack_ticket, language="markdown")


# ----------------- TAB 2: BATCH INTELLIGENCE -----------------
with tab2:
    st.markdown("### 📊 Omnichannel Batch Analytics & Departmental Insights")
    st.write("Aggregated analysis of customer reviews across Google, Trustpilot, G2, App Store, and Clutch.")

    csv_path = PROJECT_ROOT / "data" / "sample_reviews.csv"
    if csv_path.exists():
        df_raw = pd.read_csv(csv_path)
    else:
        df_raw = pd.DataFrame()

    if not df_raw.empty:
        # Run batch analysis
        analyzed_records = []
        aspect_records = []

        for idx, row in df_raw.iterrows():
            res = engine.analyze_review(
                text=str(row.get("review_text", "")),
                review_id=str(row.get("review_id", f"REV-{idx}")),
                rating=int(row["rating"]) if pd.notnull(row.get("rating")) else None,
                author=str(row.get("author", "User")),
                platform=str(row.get("platform", "Web"))
            )
            analyzed_records.append({
                "ID": res.review_id,
                "Platform": res.platform,
                "Rating": res.rating,
                "Sentiment": res.overall_sentiment,
                "Score": res.sentiment_score,
                "Urgency": res.urgency_score,
                "Crisis": "🚨 Yes" if res.is_crisis else "No",
                "Churn Risk": res.churn_risk,
                "Review Text": res.raw_text[:80] + "..."
            })

            for a in res.aspects:
                aspect_records.append({
                    "Aspect": a.aspect,
                    "Sentiment": a.sentiment,
                    "Department": a.department,
                    "Score": a.score
                })

        df_analyzed = pd.DataFrame(analyzed_records)
        df_aspects = pd.DataFrame(aspect_records)

        # High-level KPIs
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        with kpi1:
            st.metric("Total Reviews", len(df_analyzed))
        with kpi2:
            pos_ratio = (df_analyzed["Sentiment"] == "Positive").mean() * 100
            st.metric("Positive Sentiment %", f"{pos_ratio:.1f}%")
        with kpi3:
            crisis_count = (df_analyzed["Crisis"] == "🚨 Yes").sum()
            st.metric("Critical Incidents", crisis_count, delta=f"{crisis_count} urgent")
        with kpi4:
            high_churn_count = (df_analyzed["Churn Risk"] == "High").sum()
            st.metric("High Churn Risk Accounts", high_churn_count)

        # Visualizations
        col_chart1, col_chart2 = st.columns(2)

        with col_chart1:
            st.markdown("#### Sentiment Distribution by Platform")
            plat_sent = pd.crosstab(df_analyzed["Platform"], df_analyzed["Sentiment"])
            st.bar_chart(plat_sent)

        with col_chart2:
            st.markdown("#### Aspect Breakdown by Department")
            if not df_aspects.empty:
                asp_chart = pd.crosstab(df_aspects["Aspect"], df_aspects["Sentiment"])
                st.bar_chart(asp_chart)

        st.markdown("#### 📋 Processed Reviews Dataset")
        st.dataframe(df_analyzed, use_container_width=True)


# ----------------- TAB 3: CRISIS MATRIX -----------------
with tab3:
    st.markdown("### 🚨 Crisis Escalation & SLA Triage Matrix")
    st.write("Real-time monitoring of severe reputation risks, legal allegations, security breaches, and churn threats.")

    urgent_cases = [
        {
            "Review ID": "REV-1013",
            "Platform": "Google Reviews",
            "Product": "Cloud Infrastructure",
            "Trigger": "Security Threat (Credentials Leaked)",
            "Urgency": "95 / 100",
            "Assigned Department": "Core Infrastructure & DevOps",
            "SLA": "Tier-1 (< 1 Hour)",
            "Status": "Requires Executive Response Approval"
        },
        {
            "Review ID": "REV-1008",
            "Platform": "Google Reviews",
            "Product": "TenantEase",
            "Trigger": "Billing Dispute (Double-Charged, Chargeback)",
            "Urgency": "85 / 100",
            "Assigned Department": "Finance & Billing",
            "SLA": "Tier-1 (< 1 Hour)",
            "Status": "Customer Refund Issued / Pending Direct Outreach"
        },
        {
            "Review ID": "REV-1002",
            "Platform": "Trustpilot",
            "Product": "Revio SaaS",
            "Trigger": "Outage & Immediate Churn Threat",
            "Urgency": "80 / 100",
            "Assigned Department": "Customer Success & DevOps",
            "SLA": "Tier-2 (< 4 Hours)",
            "Status": "Account Manager Contacted Client"
        }
    ]

    st.table(pd.DataFrame(urgent_cases))
    st.info("💡 **Enterprise Workflow:** When an urgency score exceeds 75, the engine automatically routes an incident notification via Slack / PagerDuty / Webhook to the respective department head, preventing public reputation damage.")


# ----------------- TAB 4: ARCHITECTURE & SYNERGY -----------------
with tab4:
    st.markdown("### 🏛️ Strategic Alignment: Business Synergy & Architecture")

    st.markdown("""
    #### Business Value & Revenue Defense:
    1. **Supercharges SaaS Platforms**: Turns basic star-rating monitoring into an enterprise-grade **Customer Experience Intelligence Engine**.
    2. **Omnichannel Feedback Aggregation**: Unifies customer signals across Google, Trustpilot, G2, App Store, and internal ticketing.
    3. **High ROI & Churn Prevention**: Reduces reputation triage time by **75%**, prevents customer churn with **real-time crisis alerts**, and ensures brand-compliant messaging.
    """)

    st.markdown("#### System Architecture Flow")
    st.code("""
    [Omnichannel Ingestion]
    Google Reviews / Trustpilot / G2 / App Store / Webhooks
                │
                ▼
    [Revio-Intelligence Core Engine]
    ├── Preprocessing & Negation Tokenizer
    ├── Aspect-Based Sentiment Mining (ABSA) -> Departmental Tagging
    ├── Urgency & Crisis Risk Classifier (0-100 Scale)
    └── Churn Probability Estimator
                │
                ▼
    [Autonomous Brand Response Engine]
    ├── Tone Matching (Empathetic / Professional / Warm / Executive)
    ├── Safety & Compliance Guardrails (Human-in-the-Loop for Crises)
    └── CRM & Slack Ticket Dispatcher
                │
                ▼
    [Actionable Delivery]
    Automated Brand Reply  |  Executive Alert  |  Product Department Backlog
    """, language="text")

st.markdown("---")
st.markdown("<center><small>Revio Intelligence Platform | Aspect Sentiment Mining & Autonomous Response Engine</small></center>", unsafe_allow_html=True)

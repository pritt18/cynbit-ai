"""
Revio-Intelligence Pipeline: CLI / Batch execution pipeline.
Aspect-Based Sentiment Mining & Autonomous Response Generation.
"""

import sys
import argparse
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.engine import RevioIntelligenceEngine
from src.generator import BrandResponseGenerator


def run_batch_pipeline(input_csv: str, output_csv: str):
    """
    Reads customer reviews from CSV, processes each through the Revio-Intelligence
    Engine, synthesizes recommended brand responses, and writes an enriched dataset.
    """
    print(f"[+] Loading reviews from: {input_csv}")
    df = pd.read_csv(input_csv)
    print(f"[+] Found {len(df)} records to process.")

    engine = RevioIntelligenceEngine()
    generator = BrandResponseGenerator()

    results = []

    for idx, row in df.iterrows():
        review_id = str(row.get("review_id", f"REV-{idx+1}"))
        text = str(row.get("review_text", ""))
        rating = int(row["rating"]) if pd.notnull(row.get("rating")) else None
        author = str(row.get("author", "Anonymous"))
        platform = str(row.get("platform", "Web"))

        # Run engine analysis
        analysis = engine.analyze_review(
            text=text,
            review_id=review_id,
            rating=rating,
            author=author,
            platform=platform
        )

        # Run response generator
        response = generator.generate(analysis)

        # Format aspects as readable string
        aspect_summary = "; ".join([f"{a.aspect}: {a.sentiment} ({a.department})" for a in analysis.aspects])

        results.append({
            "review_id": review_id,
            "platform": platform,
            "author": author,
            "rating": rating,
            "review_text": text,
            "overall_sentiment": analysis.overall_sentiment,
            "sentiment_score": analysis.sentiment_score,
            "aspects_breakdown": aspect_summary,
            "urgency_score": analysis.urgency_score,
            "is_crisis": analysis.is_crisis,
            "crisis_tags": ", ".join(analysis.crisis_tags),
            "churn_risk": analysis.churn_risk,
            "sla_recommendation": analysis.sla_recommendation,
            "action_item": analysis.action_item,
            "suggested_response": response.response_text,
            "human_review_required": response.human_review_required
        })

    out_df = pd.DataFrame(results)
    out_path = Path(output_csv)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_df.to_csv(out_path, index=False)

    print(f"\n[+] Processing complete! Enriched dataset saved to: {output_csv}")
    print(f"[+] Summary Stats:")
    print(f"    - Total Processed: {len(out_df)}")
    print(f"    - Positive Sentiment: {(out_df['overall_sentiment'] == 'Positive').sum()}")
    print(f"    - Negative Sentiment: {(out_df['overall_sentiment'] == 'Negative').sum()}")
    print(f"    - Neutral Sentiment:  {(out_df['overall_sentiment'] == 'Neutral').sum()}")
    print(f"    - Critical Crises:    {out_df['is_crisis'].sum()}")
    print(f"    - High Churn Risks:   {(out_df['churn_risk'] == 'High').sum()}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Revio-Intelligence Batch CLI")
    parser.add_argument("--input", default=str(PROJECT_ROOT / "data" / "sample_reviews.csv"), help="Input CSV path")
    parser.add_argument("--output", default=str(PROJECT_ROOT / "data" / "analyzed_reviews.csv"), help="Output CSV path")
    args = parser.parse_args()

    run_batch_pipeline(args.input, args.output)

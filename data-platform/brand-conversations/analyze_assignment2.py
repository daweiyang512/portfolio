from __future__ import annotations
import argparse
import json
from pathlib import Path
import pandas as pd

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
OUT = HERE / "outputs"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    parser = argparse.ArgumentParser(description="Rebuild descriptive Assignment 2 summaries")
    parser.add_argument("--source", type=Path, default=BASE / "data" / "Assignment2_Data_2025.csv")
    parser.add_argument("--labels", type=Path, default=BASE / "data" / "tweets_with_topic_classification.csv")
    args = parser.parse_args()
    source = args.source
    labels_path = args.labels
    if source.suffix.lower() == ".csv":
        source_df = pd.read_csv(source)
    elif source.suffix.lower() in {".xlsx", ".xls"}:
        source_df = pd.read_excel(source)
    else:
        raise ValueError("Source must be a CSV or Excel workbook")
    labels = pd.read_csv(labels_path)
    if "id" not in source_df or "id" not in labels or "topic_label" not in labels:
        raise ValueError("Expected id in both files and topic_label in the classification file")
    source_df["created_at"] = pd.to_datetime(source_df["created_at"], utc=True, errors="raise")
    labels["created_at"] = pd.to_datetime(labels["created_at"], utc=True, errors="raise")
    match_key = ["created_at", "text"]
    if source_df.duplicated(match_key).any() or labels.duplicated(match_key).any():
        raise ValueError("Timestamp + full text is not a unique post key")
    d = source_df.merge(labels[match_key + ["topic_label"]], on=match_key, validate="one_to_one")
    if len(d) != len(source_df) or len(d) != len(labels):
        raise ValueError("Source and topic labels do not match one-to-one by timestamp + full text")
    d["month"] = d["created_at"].dt.strftime("%Y-%m")
    d["engagement_total"] = d[["like", "reply", "retweet"]].fillna(0).sum(axis=1)

    topic = d.groupby(["brand", "topic_label"], dropna=False).size().rename("posts").reset_index()
    topic["brand_total"] = topic.groupby("brand")["posts"].transform("sum")
    topic["within_brand_share"] = topic["posts"] / topic["brand_total"]
    topic.to_csv(OUT / "brand_topic_summary.csv", index=False)

    engagement = d.groupby(["brand", "topic_label"], dropna=False).agg(
        posts=("id", "size"), mean_likes=("like", "mean"), median_likes=("like", "median"),
        mean_replies=("reply", "mean"), median_replies=("reply", "median"),
        mean_retweets=("retweet", "mean"), median_retweets=("retweet", "median"),
        mean_total_engagement=("engagement_total", "mean"), median_total_engagement=("engagement_total", "median"),
    ).reset_index()
    engagement.to_csv(OUT / "engagement_by_brand_and_topic.csv", index=False)
    monthly = d.groupby(["month", "brand", "topic_label"], dropna=False).size().rename("posts").reset_index()
    monthly.to_csv(OUT / "monthly_topic_counts.csv", index=False)

    report = {
        "analysis": "Current reproducible descriptive analysis of Assignment 2 social posts",
        "source": source.name, "label_source": labels_path.name,
        "records": int(len(d)), "id_field_unique_values": int(d.id.nunique()), "record_match_key": "UTC created_at + exact full text", "brands": {str(k): int(v) for k, v in d.brand.value_counts().items()},
        "date_range_utc": {"start": d.created_at.min().isoformat(), "end": d.created_at.max().isoformat()},
        "topic_label_counts": {str(k): int(v) for k, v in d.topic_label.value_counts().items()},
        "label_provenance": "Existing labels are treated as input; this script does not recreate the original labeling model or rubric.",
        "outputs": ["brand_topic_summary.csv", "engagement_by_brand_and_topic.csv", "monthly_topic_counts.csv"],
        "limitations": ["Small observational sample of 324 posts across four brand accounts.", "Engagement reflects observed counts and is not normalized for exposure or account size.", "Topic labels are imported and their original generation method is not established here.", "Descriptive differences do not establish causal effects or represent all customers."]
    }
    (OUT / "analysis_summary.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()

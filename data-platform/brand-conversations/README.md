# Brand conversations and engagement — Data Platform Assignment 2

This is a current portfolio reconstruction from the main 324-row assignment dataset and its supplied topic labels. It validates the source-to-label link, then creates descriptive summaries by brand, topic, and month. It does not claim to reproduce the original group workflow or the label-generating model.

## Run

Install the packages in the repository's `requirements.txt`. Keep authorized files in the ignored local folder `data-platform/data/`, then run from the repository root:

```powershell
python data-platform/brand-conversations/analyze_assignment2.py --source "data-platform/data/Assignment2_Data_2025.csv" --labels "data-platform/data/tweets_with_topic_classification.csv"
```

The source may also be supplied as a CSV. The script writes only aggregate tables and an analysis summary next to itself.

## Checks and outputs

- Confirm required source and label columns exist.
- Parse timestamps as UTC; reject duplicate timestamp/text keys.
- Validate a one-to-one join using UTC timestamp + exact full text. The supplied numeric `id` field has only six distinct values across the 324 posts and is not used as a join key.
- Calculate post counts and within-brand topic shares, likes/replies/retweets by brand and topic, and monthly topic counts.
- Record row counts, brand distribution, date range, label counts, and limitations in `outputs/analysis_summary.json`.

## Data boundary and limitations

The main assignment brief describes a few hundred rows and the main CSV contains 324 posts. The separate 38-row update dataset is not part of this reconstruction. The full post text is not included in the public repository. Existing labels are treated as inputs because their generating model/rubric is not reproduced. Engagement counts are not exposure-adjusted, and descriptive differences do not establish causal effects.

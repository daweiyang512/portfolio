# Assignment 2 social-post analysis — current reconstruction

This reproducible analysis validates the 324-row source-to-label record link, then summarizes existing topic labels and engagement by brand, topic, and month. It is a current portfolio analysis; it does not claim to recreate the original assignment steps.

## Run

Run from the repository root with Python 3.10+, `pandas`, and `openpyxl` installed. Put authorized source files in `data-marketing-management-lab/data/` (ignored by Git), or pass `--source` and `--labels` paths. For example: `python data-marketing-management-lab/assignment-2/analyze_assignment2.py --source "data-marketing-management-lab/data/Assignment2_Data_2025.xlsx" --labels "data-marketing-management-lab/data/tweets_with_topic_classification.csv"`. Generated aggregate summaries go to `data-marketing-management-lab/assignment-2/outputs/`.

## What it demonstrates

- Input validation: exact one-to-one matching by UTC timestamp + full text. The supplied post `id` field has only six unique values for 324 records, so it is not used as a join key.
- Reproducible transformations: UTC timestamps, month grouping, and a transparent total-engagement field (likes + replies + retweets).
- Descriptive analysis: within-brand topic shares, engagement summaries by brand/topic, and monthly topic counts.

## Scope limits

The 324 posts cover four brand accounts over roughly four months. Existing topic labels are treated as given because their original rubric/model is not available in this deliverable. The large numeric post IDs appear to have lost precision and are not reliable unique identifiers. Engagement counts are not exposure-adjusted, and the analysis is descriptive rather than causal.

# Data Marketing Management Lab | Portfolio Cases

Two current, reproducible portfolio analyses: e-commerce churn classification and social-post marketing analysis. These are current reconstructions and do not claim to recreate the historical course workflow.

## Case studies

- [E-commerce churn](churn/README.md): stratified holdout, leakage-aware preprocessing, majority baseline, regularized logistic regression and threshold sensitivity.
- [Assignment 2 social posts](assignment-2/README.md): source-to-label integrity check, topic shares and engagement summaries.
- [Portfolio website](index.html): recruiter-facing overview and case pages.

## Data boundary

Raw customer records and social-post text are not included. Do not add them unless their publication rights are verified. For a local rerun, provide authorized source files as command-line inputs. Public aggregate outputs are provided for review.

## Run

Install dependencies from `data-marketing-management-lab/requirements.txt`. For a local rerun, place authorized source files in `data-marketing-management-lab/data/` (that folder is ignored by Git), or pass their paths explicitly:

```powershell
python data-marketing-management-lab/churn/run_rebuild.py --source "data-marketing-management-lab/data/Project Dataset.xlsx"
python data-marketing-management-lab/assignment-2/analyze_assignment2.py --source "data-marketing-management-lab/data/Assignment2_Data_2025.xlsx" --labels "data-marketing-management-lab/data/tweets_with_topic_classification.csv"
```

The Assignment 2 labels are treated as input; this package does not claim to recreate the original label-generation method. The supplied numeric post IDs are not used because they are not unique in the provided data.

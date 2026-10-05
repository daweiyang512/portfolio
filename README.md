# Dawei Yang | Portfolio

This repository presents a master's thesis case, two master's-course cases, and an independent residential market-analysis case. Each case has its own page and evidence.

| Work | Portfolio case | Public evidence |
| --- | --- | --- |
| Master's Thesis · Marketing Management | Framing, time pressure, and sustainable consumption decisions | Five-page case brief, public thesis copy, selected original Python excerpts, aggregate model outputs. |
| Data Marketing Management Lab | E-commerce churn risk | A stratified held-out evaluation, majority-class baseline, regularized logistic regression, and a visible precision/recall trade-off. |
| Data Platform | Brand conversations and engagement | A 324-post record-link check and descriptive summaries by brand, topic, and month. |
| Independent market analysis | Coastal villa market positioning | Regional and local listing evidence, exploratory price-structure screening, seasonal rental scenarios, and an explicit comparison-universe sensitivity note. The subject address is withheld; other comparable addresses are retained. |

Open the [portfolio homepage](index.html), then choose a case. The site is static and can be read without GitHub knowledge. Code and aggregate outputs are optional technical evidence.

The thesis case reports 2,107 valid choice observations and 2,197 valid reaction-time observations from 101 participants. The raw participant-level survey export and row-level records are not included. The full thesis copy uses a public cover without the identifying student number or email.

## Data and scope

Raw customer records, full tweet text, and row-level churn predictions are not included. The Data Platform reconstruction uses the main 324-row assignment dataset and supplied topic labels. The separate 38-row update dataset is not merged into that analysis. The original group slide's “7000+ tweets” phrase is not used as the analyzed sample size because the supplied assignment brief and main data file support a 324-row sample.

## Run a reconstruction locally

Install the packages in `requirements.txt`, then provide authorized source files locally. The `.gitignore` excludes local `data/` folders and spreadsheet files.

For churn, provide the course workbook with the `Original dataset` sheet:

```powershell
python data-marketing-management-lab/churn/run_rebuild.py --source "data-marketing-management-lab/data/dataset of marketing management lab.xlsx"
```

For Data Platform, provide the main assignment source workbook and the existing topic-label CSV:

```powershell
python data-platform/brand-conversations/analyze_assignment2.py --source "data-platform/data/Assignment2_Data_2025.csv" --labels "data-platform/data/tweets_with_topic_classification.csv"
```

The scripts write aggregate outputs next to their code. The churn script does not export row-level predictions.

## Limits

The churn result is one held-out split, not a production validation or proof of retention impact. The Data Platform analysis treats supplied topic labels as inputs and reports descriptive associations; it does not reproduce the original labeling model or establish causal effects.

The thesis case distinguishes constructed trial rows from valid model observations. Its framing and time-pressure results are reported with uncertainty, and its entropy extension is exploratory. The source notebook's attention-check flag logic requires revalidation; attention-based robustness claims are not presented as validated evidence.

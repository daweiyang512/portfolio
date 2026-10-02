# E-commerce churn risk — current reconstruction

This is a fresh, reproducible analysis of the supplied `Project Dataset.xlsx` / `E Comm` sheet. It demonstrates the current workflow and makes no claim about the historical steps used to produce the older files elsewhere in this folder.

## Run

From the repository root, run `python data-marketing-management-lab/churn/run_rebuild.py --source "data-marketing-management-lab/data/Project Dataset.xlsx"` with Python 3.10+ and `pandas`, `numpy`, and `openpyxl` installed. The source workbook is intentionally not copied into this deliverable. The script writes held-out predictions, model coefficients, and an evaluation report under `data-marketing-management-lab/churn/outputs/`.

## Method

- Target: `Churn` (0/1). `CustomerID` is excluded as an identifier; any derived `Churnclass` column is also excluded.
- A fixed seed creates a stratified 80/20 train/test split.
- Missing-value rules, category levels, and scaling parameters are fitted using training data only.
- A majority-class baseline is compared with L2-regularized logistic regression.
- The untouched test split is evaluated at a declared 0.5 probability threshold with accuracy, precision, recall, F1, ROC AUC, average precision, and a confusion matrix. A separate threshold table shows the precision/recall trade-off without choosing a threshold on the test set.

## Interpretation limits

This is one reproducible holdout, not a validated production model. The results are specific to this dataset and split. Coefficients show conditional associations, not causes; no retention campaign impact is measured. Check the dataset's publication rights and remove or mask identifiers before publishing any source data.


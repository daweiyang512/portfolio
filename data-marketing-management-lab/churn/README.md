# E-commerce churn risk — current reconstruction

This is a reproducible analysis of `dataset of marketing management lab.xlsx` / `Original dataset`. It demonstrates the current method and does not claim to recreate the historical steps behind earlier course files.

## Run

From the repository root, install the packages in `requirements.txt` and run:

```powershell
python data-marketing-management-lab/churn/run_rebuild.py --source "data-marketing-management-lab/data/dataset of marketing management lab.xlsx"
```

Keep the source workbook in the ignored local `data-marketing-management-lab/data/` folder. The script writes only an evaluation report, model coefficients, and threshold sensitivity. It does not export row-level predictions.

## Method

- Target: `Churn` (0/1). `CustomerID`, the derived `Churnclass` field, and prior `Pred:Churnclass` / `Pred:Conf.Churnclass` outputs are excluded.
- Fixed seed, stratified 80/20 train/test split.
- Missing-value imputation, one-hot encoding, and scaling are fitted on training data only.
- Compare a majority-class baseline with L2-regularized logistic regression.
- Evaluate the untouched test split at a declared 0.5 threshold; report precision, recall, F1, ROC AUC, average precision, and the confusion matrix.
- A threshold table shows the precision/recall trade-off without selecting a threshold on the test set.

## Limits

This is one holdout on one dataset, not production validation. Results do not establish business impact. Coefficients are associations in the fitted model, not causal effects. Do not publish the source workbook or row-level predictions without authorization.

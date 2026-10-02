# Data Marketing Management Lab

## Portfolio case

**E-commerce churn risk.** A current reconstruction of a personal course project using the 5,630-row `Original dataset` sheet in `dataset of marketing management lab.xlsx`. The public analysis compares a majority-class baseline with regularized logistic regression on one stratified 80/20 holdout.

## Case pages and evidence

- [Course page](index.html)
- [Churn case](churn.html)
- [Rebuild script and method notes](churn/README.md)
- [Evaluation summary](churn/outputs/evaluation.json)
- [Threshold sensitivity](churn/outputs/threshold_sensitivity.csv)

The source workbook is not included. The `.gitignore` excludes the local `data/` folder and spreadsheet files. The reconstruction excludes customer identifiers, the derived `Churnclass` field, and prior prediction/confidence columns from model inputs.

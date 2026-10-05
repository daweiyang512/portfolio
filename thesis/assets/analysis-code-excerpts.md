# Selected original analysis code excerpts

Extracted from the submitted thesis analysis notebook. These excerpts show the actual transformations and model pattern; they depend on earlier notebook variables and are not presented as a standalone reproduction script. Raw participant records and cell outputs are omitted.


## Notebook cell 9

```python
# CELL 3 — STEP 1：wide → decision-level long（不删；只重构）
ID_COL = "_recordId"
FRAME_COL = "Frame"
PRESSURE_COL = "TimePressure"
COND_COL = "Condition"
LANG_COL = "Q_Language"

if ID_COL not in df_wide.columns:
    raise ValueError("Missing _recordId in df_wide")

def decision_cols_for_trial(t: int):
    return [f"{t}_QID27", f"{t}_QID31", f"{t}_QID28", f"{t}_QID32",
            f"{t}_QID43", f"{t}_QID44", f"{t}_QID45", f"{t}_QID46"]

def rt_col_for_trial(t: int):
    return f"{t}_QID34_PAGE_SUBMIT"

rows = []
for t in range(1, T_MAX + 1):
    dcols = [c for c in decision_cols_for_trial(t) if c in df_wide.columns]
    if not dcols:
        continue

    decision_raw = df_wide[dcols].bfill(axis=1).iloc[:, 0]
    decision_src = df_wide[dcols].notna().idxmax(axis=1)

    rtcol = rt_col_for_trial(t)
    rt = pd.to_numeric(df_wide[rtcol], errors="coerce") if rtcol in df_wide.columns else np.nan

    tmp = pd.DataFrame({
        "participant": df_wide[ID_COL].astype(str),
        "trial": t,
        "decision_raw": pd.to_numeric(decision_raw, errors="coerce"),
        "decision_src": decision_src.astype(str),
        "RT": rt,
        "product": product_by_trial.get(t, np.nan),
    })

    if FRAME_COL in df_wide.columns:
        tmp["frame"] = df_wide[FRAME_COL].astype(str)
    if PRESSURE_COL in df_wide.columns:
        tmp["time_pressure"] = df_wide[PRESSURE_COL].astype(str)
    if COND_COL in df_wide.columns:
        tmp["condition"] = df_wide[COND_COL]
    if LANG_COL in df_wide.columns:
        tmp["language"] = df_wide[LANG_COL].astype(str)

    for c in ["progress", "finished", "duration", "status"]:
        if c in df_wide.columns:
            tmp[c] = df_wide[c].values

    rows.append(tmp)

df_long = pd.concat(rows, ignore_index=True)

# eco_choice：默认 1=Eco, 2=Standard（如相反自己互换）
df_long["eco_choice"] = np.where(df_long["decision_raw"] == 1, 1,
                          np.where(df_long["decision_raw"] == 2, 0, np.nan))

df_long.shape, df_long.head(5)
```


## Notebook cell 35

```python
def logit_cluster(formula, data, cluster_col="participant", disp=0):
    d = data.dropna().copy().reset_index(drop=True)
    res = smf.logit(formula, data=d).fit(
        disp=disp,
        cov_type="cluster",
        cov_kwds={"groups": d[cluster_col]}
    )
    return res, d

def or_ci_table(res):
    """
    statsmodels Logit + cluster robust 的 coef/SE/CI 转成 OR/CI
    """
    params = res.params
    bse = res.bse
    z = params / bse
    p = res.pvalues

    ci = res.conf_int()
    ci.columns = ["ci_low", "ci_high"]

    out = pd.DataFrame({
        "coef": params,
        "se": bse,
        "z": z,
        "p": p,
        "OR": np.exp(params),
        "OR_ci_low": np.exp(ci["ci_low"]),
        "OR_ci_high": np.exp(ci["ci_high"]),
    })
    return out

def save_table(df, path):
    df.to_csv(path, index=True)
    print("Saved table:", path)
```


## Notebook cell 49

```python
def entropy_binary(x):
    p = np.nanmean(x)
    if np.isnan(p) or p == 0 or p == 1:
        return 0.0
    return -(p*np.log(p) + (1-p)*np.log(1-p))

participant_entropy = (
    df_analysis
    .groupby("participant")["eco_choice"]
    .apply(entropy_binary)
    .reset_index()
    .rename(columns={"eco_choice": "entropy"})
)

# 标准化（你本聊天后续用的是 entropy_z）
participant_entropy["entropy_z"] = (
    (participant_entropy["entropy"] - participant_entropy["entropy"].mean())
    / participant_entropy["entropy"].std(ddof=0)
)

# 带上 language（本聊天里你也用 participant->language 映射）
lang_map = df_analysis.groupby("participant")["language"].first().reset_index()
participant_entropy = participant_entropy.merge(lang_map, on="participant", how="left")

participant_entropy.head()
```


## Notebook cell 56

```python
import pandas as pd
import numpy as np
import statsmodels.formula.api as smf

# 1) 只取必要列（避免别的列的缺失触发隐式删行）
d6 = df[["eco_choice","frame","participant"]].copy()

# 2) 类型与清洗（不改变含义，只保证可拟合）
d6["eco_choice"] = pd.to_numeric(d6["eco_choice"], errors="coerce")
d6["frame"] = d6["frame"].astype(str).str.strip()
d6["participant"] = d6["participant"].astype(str)

# 3) 明确 reference（Gain baseline）
d6["frame"] = pd.Categorical(d6["frame"], categories=["Gain","Loss"])

# 4) 显式 dropna —— 关键：保证 y/X/groups 同长度
d6 = d6.dropna(subset=["eco_choice","frame","participant"]).copy()

print("STEP6A-final N used:", len(d6))
print(d6["frame"].value_counts())

# 5) cluster logit
m6a_final = smf.logit(
    "eco_choice ~ frame",
    data=d6
).fit(
    disp=0,
    cov_type="cluster",
    cov_kwds={"groups": d6["participant"]}
)

print(m6a_final.summary())
```

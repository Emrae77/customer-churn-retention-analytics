"""Keep one customer per row, preserve meaningful source categories and nulls.

This Python reference path makes the dashboard previews reproducible on macOS,
Linux and Windows. The equivalent SQL Server workflow lives in sql/.
"""

import hashlib
import json
from pathlib import Path
from urllib.request import Request, urlopen

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW_COLUMNS = [
    "customerID", "gender", "SeniorCitizen", "Partner", "Dependents", "tenure",
    "PhoneService", "MultipleLines", "InternetService", "OnlineSecurity",
    "OnlineBackup", "DeviceProtection", "TechSupport", "StreamingTV",
    "StreamingMovies", "Contract", "PaperlessBilling", "PaymentMethod",
    "MonthlyCharges", "TotalCharges", "Churn",
]
TENURE_BANDS = ["0 months", "1–12 months", "13–24 months", "25–48 months", "49–72 months"]
CONTRACTS = ["Month-to-month", "One year", "Two year"]
INTERNET_TYPES = ["DSL", "Fiber optic", "No"]
PAYMENTS = ["Electronic check", "Mailed check", "Bank transfer (automatic)", "Credit card (automatic)"]
ALLOWED = {
    "gender": {"Female", "Male"},
    "SeniorCitizen": {"0", "1"},
    "Partner": {"Yes", "No"}, "Dependents": {"Yes", "No"},
    "PhoneService": {"Yes", "No"},
    "MultipleLines": {"Yes", "No", "No phone service"},
    "InternetService": set(INTERNET_TYPES),
    "Contract": set(CONTRACTS), "PaperlessBilling": {"Yes", "No"},
    "PaymentMethod": set(PAYMENTS), "Churn": {"Yes", "No"},
}
for _name in ["OnlineSecurity", "OnlineBackup", "DeviceProtection", "TechSupport", "StreamingTV", "StreamingMovies"]:
    ALLOWED[_name] = {"Yes", "No", "No internet service"}


def source_info():
    return json.loads((ROOT / "data/source.json").read_text(encoding="utf-8"))


def verify_source(path):
    meta = source_info()
    digest = hashlib.sha256(Path(path).read_bytes()).hexdigest()
    if digest != meta["sha256"]:
        raise ValueError("Source checksum mismatch. Use the pinned IBM CSV; do not mix dataset versions.")
    return digest


def ensure_source():
    target = ROOT / "data/raw/Telco-Customer-Churn.csv"
    if not target.exists():
        target.parent.mkdir(parents=True, exist_ok=True)
        request = Request(source_info()["download_url"], headers={"User-Agent": "TelcoAnalyticsPortfolio/1.0"})
        with urlopen(request, timeout=45) as response:
            payload = response.read()
        if hashlib.sha256(payload).hexdigest() != source_info()["sha256"]:
            raise ValueError("Downloaded source failed its SHA-256 check.")
        temporary = target.with_suffix(".download")
        temporary.write_bytes(payload)
        temporary.replace(target)
    verify_source(target)
    return target


def clean_customers(raw):
    if list(raw.columns) != RAW_COLUMNS:
        raise ValueError("Expected the classic IBM 21-column schema in its original order.")
    df = raw.copy()
    for column in RAW_COLUMNS:
        df[column] = df[column].astype("string").str.strip()
    if df["customerID"].isna().any() or df["customerID"].eq("").any():
        raise ValueError("Missing customer identifiers.")
    if df["customerID"].duplicated().any():
        raise ValueError("Duplicate customer identifiers; resolve before counting customers.")
    for column, allowed in ALLOWED.items():
        if df[column].isna().any() or not df[column].isin(allowed).all():
            raise ValueError("Unexpected value in {}".format(column))
    for column in ["tenure", "MonthlyCharges", "TotalCharges"]:
        raw_values = df[column]
        missing = raw_values.isna() | raw_values.eq("")
        numeric = pd.to_numeric(raw_values.mask(missing), errors="coerce")
        if (numeric.isna() & ~missing).any():
            raise ValueError("Non-numeric value in {}".format(column))
        if column != "TotalCharges" and missing.any():
            raise ValueError("Missing required value in {}".format(column))
        if numeric.dropna().lt(0).any():
            raise ValueError("Negative value in {}".format(column))
        df[column] = numeric.astype("Float64")
    if ((df["tenure"] % 1 != 0) | (df["tenure"] > 72)).any():
        raise ValueError("Tenure must be an integer from 0 through 72 for this sample.")
    df["tenure"] = df["tenure"].astype("int64")
    df["SeniorCitizen"] = df["SeniorCitizen"].astype("int64")
    df["ChurnFlag"] = df["Churn"].map({"Yes": 1, "No": 0}).astype("int64")
    df["TotalChargesMissing"] = df["TotalCharges"].isna().astype("int64")
    df["TenureBandSort"] = pd.cut(df["tenure"], [-1, 0, 12, 24, 48, 72], labels=False).astype("int64")
    df["TenureBand"] = df["TenureBandSort"].map(dict(enumerate(TENURE_BANDS)))
    return df[RAW_COLUMNS + ["ChurnFlag", "TenureBand", "TenureBandSort", "TotalChargesMissing"]]


def load_customers(path):
    raw = pd.read_csv(path, dtype=str, keep_default_na=False)
    return raw, clean_customers(raw)


def segment_summary(df, dimension, order=None):
    rows = []
    labels = order if order is not None else sorted(df[dimension].unique())
    for segment in labels:
        part = df.loc[df[dimension] == segment]
        total = len(part)
        churned = int(part["ChurnFlag"].sum())
        rows.append({"segment": segment, "customers": total, "churned": churned,
                     "not_churned": total - churned,
                     "churn_rate_pct": round(100 * churned / total, 6) if total else None,
                     "avg_monthly_charges": round(float(part["MonthlyCharges"].mean()), 6) if total else None})
    return rows


def analyze(raw, df):
    n = len(df)
    yes = int(df["ChurnFlag"].sum())
    checks = {
        "raw_rows": len(raw), "raw_columns": len(raw.columns), "clean_rows": n,
        "unique_customers": int(df["customerID"].nunique()),
        "duplicate_customer_ids": int(df["customerID"].duplicated().sum()),
        "rows_removed": len(raw) - n,
        "total_charges_missing": int(df["TotalChargesMissing"].sum()),
        "missing_total_charges_at_tenure_zero": int(((df["TotalChargesMissing"] == 1) & (df["tenure"] == 0)).sum()),
        "unexpected_churn_labels": int((~raw["Churn"].str.strip().isin(["Yes", "No"])).sum()),
        "invalid_numeric_values": 0,
    }
    overall = {"customers": n, "churned": yes, "not_churned": n - yes,
               "churn_rate_pct": round(100 * yes / n, 6),
               "not_churned_share_pct": round(100 * (n - yes) / n, 6),
               "avg_monthly_charges": round(float(df["MonthlyCharges"].mean()), 6)}
    segments = {
        "contract": segment_summary(df, "Contract", CONTRACTS),
        "tenure": segment_summary(df, "TenureBand", TENURE_BANDS),
        "internet_service": segment_summary(df, "InternetService", INTERNET_TYPES),
        "payment_method": segment_summary(df, "PaymentMethod", PAYMENTS),
        "tech_support_internet_only": segment_summary(df.loc[df["InternetService"] != "No"], "TechSupport", ["No", "Yes"]),
    }
    intersection = []
    for contract in CONTRACTS:
        for record in segment_summary(df.loc[df["Contract"] == contract], "TenureBand", TENURE_BANDS):
            intersection.append({"contract": contract, **record})
    return {"source": source_info(), "scope": "Static customer snapshot; churn rate is the observed share labelled Yes.",
            "overall": overall, "data_quality": checks, "segments": segments,
            "contract_by_tenure": intersection}

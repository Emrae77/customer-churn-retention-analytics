"""Download the pinned sample, prepare data, compute metrics and render images."""

import json
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd

from scripts.prepare_data import ROOT, analyze, ensure_source, load_customers


def main():
    path = ensure_source()
    raw, customers = load_customers(path)
    if len(customers) != 7043:
        raise ValueError("Pinned source should contain 7,043 customers.")
    report = analyze(raw, customers)
    for relative in ["data/processed", "reports", "images"]:
        (ROOT / relative).mkdir(parents=True, exist_ok=True)
    customers.to_csv(ROOT / "data/processed/telco_customers.csv", index=False, float_format="%.2f", na_rep="")
    (ROOT / "reports/metrics.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    for name, rows in report["segments"].items():
        pd.DataFrame(rows).to_csv(ROOT / ("reports/{}.csv".format(name)), index=False)
    pd.DataFrame(report["contract_by_tenure"]).to_csv(ROOT / "reports/contract_by_tenure.csv", index=False)
    from scripts.render_dashboards import render_all
    render_all(report)
    print("Prepared {:,} customers; {:,} churned; {:.2f}% observed churn.".format(
        report["overall"]["customers"], report["overall"]["churned"], report["overall"]["churn_rate_pct"]))
    print("Preserved {} missing TotalCharges values; removed {} rows.".format(
        report["data_quality"]["total_charges_missing"], report["data_quality"]["rows_removed"]))
    print("Created reports/metrics.json, summary CSVs and three original dashboard PNGs.")


if __name__ == "__main__":
    main()

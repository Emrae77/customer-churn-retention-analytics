# Local data

Run `python scripts/build_project.py` from the project root.

- `raw/Telco-Customer-Churn.csv`: exact checksum-verified IBM sample, downloaded on first run.
- `processed/telco_customers.csv`: prepared data with all 7,043 customers, 21 original fields and four documented derived fields.
- `source.json`: pinned source URL, SHA-256 and dataset version.

Raw and processed CSVs are ignored by Git. Do not substitute a different Telco dataset into the pinned filename. See [data source and preparation](../docs/DATA_SOURCE.md).

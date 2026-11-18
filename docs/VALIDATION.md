# Validation and testing

## Run the reference checks

```bash
python scripts/build_project.py
python -m unittest discover -s tests -v
```

The automated Python checks cover:

- The exact source file's SHA-256 checksum.
- The 7,043-customer population and 1,869/5,174 outcome reconciliation.
- Retention of all 11 missing TotalCharges rows and preservation of missing numeric values.
- Contract counts and within-group rate denominators.
- Reconciliation of each complete grouping to the overall customer and churn totals.
- Tenure-band boundaries, including 0, 12, 24, 48 and 72 months.
- Preservation of `No internet service` and the internet-only support comparison population.
- Rejection of duplicate IDs, invalid categories and invalid required numeric values.
- Empty groups returning an unavailable rate rather than a misleading 0%.

## Execution boundary

The Python reference data preparation and dashboard rendering were run while preparing this package. SQL Server scripts and Power BI measures are supplied for native execution; a SQL Server instance and Power BI Desktop were not available for a live validation run. A passing Python test does not prove that a SQL Server connection, DAX expression or Power BI report works in a particular installation.

The GitHub Actions workflow runs the Python reference path only. Its first run downloads the pinned IBM source and therefore requires network access.

## SQL Server acceptance checks

After loading the raw table and running the scripts in `sql/`, compare the resulting views to `reports/metrics.json` and the aggregate CSVs. Require 7,043 prepared rows, 7,043 distinct keys, 1,869 churned customers, 5,174 not-churned customers and 11 nullable TotalCharges values. Contract totals must be 3,875 / 1,473 / 1,695 and churn counts 1,655 / 166 / 48. Run the supplied SQL validation queries before connecting Power BI.

## Power BI acceptance checks

| Case | Expected behaviour |
| --- | --- |
| No filters | 7,043 total; 1,869 churned; 26.54% churn |
| Contract = Month-to-month | 3,875 total; 1,655 churned; 42.71% |
| Contract = Two year | 1,695 total; 48 churned; 2.83% |
| Tenure = 1–12 months | 2,175 total; 1,037 churned; 47.68% |
| Tenure = 0 months | 11 total; 0 churned; 11 missing TotalCharges |
| No customers selected | Rate is blank/unavailable, not an invented 0% |
| Clear filters | Original totals return |

Check that a slicer filters both numerator and denominator, tenure sorts numerically, and each chart tooltip includes its customer count. The same customer can appear in several charts; the visual layout must not imply the groups are additive.

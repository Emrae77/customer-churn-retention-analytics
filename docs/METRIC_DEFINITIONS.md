# Metric definitions

The grain is one row per customer. A filtered dashboard must use the same filtered customer population in each numerator and denominator. A rate is recomputed from counts, never obtained by averaging segment percentages.

| Metric | Definition | Unfiltered reference |
| --- | --- | ---: |
| Total customers | Distinct customerID; equals row count after uniqueness validation | 7,043 |
| Churned customers | Customers whose Churn = Yes | 1,869 |
| Not-churned customers | Customers whose Churn = No | 5,174 |
| Churn rate | Churned customers / total customers | 26.536987% |
| Not-churned share | Not-churned customers / total customers | 73.463013% |
| Average monthly charge | Mean MonthlyCharges for the selected customers | 64.761692 source units |
| Missing TotalCharges | Customers whose numeric TotalCharges is missing | 11 |
| Churn contribution of a segment | Churned customers in segment / all churned customers | Month-to-month: 88.550027% |

Display rates with one or two decimal places, but retain the unrounded values for calculations. DAX rate measures return fractions and should be formatted as percentages; SQL/report CSV `churn_rate_pct` values already use a 0–100 scale.

## Two different percentages

Month-to-month customers have **1,655 / 3,875 = 42.71%** churn within that contract group. They account for **1,655 / 1,869 = 88.55%** of all customers labelled churned. The first describes the group's rate; the second describes its share of the recorded departures.

For two-year contracts, **48 / 1,695 = 2.83%** is the within-group churn rate. The gap from month-to-month contracts is approximately **39.88 percentage points**. It is a descriptive comparison between different customers. It is not an estimated treatment effect of changing someone's contract.

## Limits of the terminology

`Not-churned share` means the share labelled No in this snapshot. It is not a longitudinal retention rate with an opening cohort, additions and departures tracked over time. There are no dates in this CSV from which to derive a monthly trend or retention curve.

Contract, tenure, internet and payment views overlap. Do not add their churn counts together. For support-service comparisons, the exported `tech_support_internet_only.csv` includes internet subscribers only: 5,517 customers. Customers with `InternetService = No` are excluded from that particular comparison, not from overall churn reporting.

TotalCharges missing values must remain NULL/blank. An all-missing group does not have a measured charge total of zero. MonthlyCharges associated with churned customers is not a confirmed amount of lost, avoidable or recoverable revenue.

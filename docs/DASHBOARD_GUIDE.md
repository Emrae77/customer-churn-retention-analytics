# Dashboard guide

## What you are looking at

The three figures tell one story: establish the size of recorded churn, inspect customer-group differences, and check the data behind the calculations. They are original static images generated from the pinned IBM sample by the Python reference workflow. They are not screenshots exported from a Power BI file, and the images do not have interactive filters.

Power Query, DAX, a theme and build instructions are supplied in [powerbi/](../powerbi/) for a native report implementation. The original `.pbix` file is unavailable. The SQL Server and Power BI paths require validation in their respective applications; the rendered figures follow the Python reference calculations.

The source is a customer snapshot. The word “health” describes the overview of its recorded customer outcomes; it does not imply a live health score or an operational alerting system.

## Page 1: Customer health

Open [customer-health.png](../images/customer-health.png).

Read the population first. There are **7,043 customers**, of whom **1,869 have `Churn=Yes`** and **5,174 have `Churn=No`**. The overall observed churn share is:

```text
1,869 / 7,043 × 100 = 26.54%, rounded to two decimal places
```

This answers how many customers in the sample carry the supplied churn label. It does not establish a churn trend, a forecast or the current status of a live customer base.

### Contract comparisons

| Contract | Customers | Churned | Churn share within the group |
| --- | ---: | ---: | ---: |
| Month-to-month | 3,875 | 1,655 | 42.71% |
| One year | 1,473 | 166 | 11.27% |
| Two year | 1,695 | 48 | 2.83% |

A rate uses the group itself as its denominator. The month-to-month figure is `1,655 / 3,875`, not `1,655 / 7,043`. Its share of all churned customers is another measure with a different denominator: `1,655 / 1,869`, or 88.6% when rounded to one decimal place. That is the figure in the page's bottom callout. The dashed line marks the overall 26.54% churn share as a reference, not an approved business target.

The comparison shows both a high recorded churn share and a large number of churned records in the month-to-month group. A sensible explanation is: “This is a substantial concentration to investigate.” The data does not justify: “Moving everyone to a longer contract will produce the same low churn share.” Customers choosing different contracts may also differ in tenure, preferences and circumstances.

### Tenure comparisons

Tenure is the number of months recorded for a customer. The reference workflow uses five ordered groups:

| Tenure | Customers | Churned | Observed churn share |
| --- | ---: | ---: | ---: |
| 0 months | 11 | 0 | 0.00% |
| 1–12 months | 2,175 | 1,037 | 47.68% |
| 13–24 months | 1,024 | 294 | 28.71% |
| 25–48 months | 1,594 | 325 | 20.39% |
| 49–72 months | 2,239 | 213 | 9.51% |

These are different customer groups. The chart is not following the same customers through time, so its shape must not be described as a month-by-month improvement or a survival curve. The zero-month group has only 11 records; its observed zero churn count is not evidence that newly joined customers are certain to remain.

## Page 2: Segment performance

Open [segment-performance.png](../images/segment-performance.png).

This page examines the broad finding through service, payment and contract-tenure comparisons. Read a label, its customer count and its within-group rate together. The comparisons below describe the same underlying customers in several ways, so their counts cannot be added across dimensions.

### Internet service

Fibre-optic customers have **1,297 churned records among 3,096 customers**, or **41.89%**. DSL shows **459 of 2,421**, or **18.96%**. Customers with no internet service show **113 of 1,526**, or **7.40%**.

This is a service-group association. It does not measure network quality, outage frequency or satisfaction. A manager would need additional evidence to connect the pattern to a specific service problem. The source value `No` in `InternetService` means no internet service, rather than a missing response.

### Payment method

Electronic-check customers have **1,071 churned records among 2,365 customers**, or **45.29%**. The other payment groups have different rates and customer mixes. This suggests a question about billing experience; it does not establish that changing a customer's payment method would change their likelihood of leaving.

Use this comparison to request payment-failure records, billing complaints and customer feedback. Those fields are not present in the sample.

### Contract and tenure together

The contract-by-tenure view divides each contract group into the same five tenure bands used on the first page. Each cell's denominator is the number of customers in that particular combination.

This view helps answer whether a broad contract pattern looks different when customers with more similar recorded tenure are compared. Pay attention to small cells. A cell containing very few people can have a striking percentage without supplying strong evidence of a general pattern. An empty cell has no rate; it should remain unavailable rather than being displayed as a measured zero.

Even with two dimensions, the analysis is descriptive. Unobserved customer differences can remain, and no experiment has assigned customers to contract types.

### Additional summary: TechSupport population

The supporting output `reports/tech_support_internet_only.csv` contains an additional comparison that is not pictured on the dashboard page. It is limited to **internet subscribers**. Customers whose source label is `No internet service` are outside that comparison's population. Within the eligible population, compare the `Yes` and `No` groups using their own customer counts.

This restriction makes the question clearer: how does recorded churn differ between internet customers with and without the support service? It still does not demonstrate the causal benefit of purchasing support. Uptake may be related to contract, tenure or other customer characteristics.

## Page 3: Data quality

Open [data-quality.png](../images/data-quality.png).

The preparation preserves the customer grain: one row represents one customer. It checks the classic 21-column schema, required identifiers, duplicate IDs, expected category values and numeric validity. The source has **7,043 unique customer IDs**, and the prepared dataset retains **7,043 rows**.

The key issue is `TotalCharges`. Eleven source cells contain whitespace rather than a numeric amount. After trimming, those become missing values. All 11 records have zero tenure and `Churn=No`; none are removed.

This choice has two practical effects. Churn calculations continue to use the full customer population, and calculations using cumulative charges retain an explicit gap. There are **7,032 known values out of 7,043** for that field. An all-missing group, such as the zero-month group, does not have a measured total of zero.

The quality checks cover the rules implemented in this repository. They do not prove that a source record matches an external billing system or that every possible data issue has been found. No composite quality grade is needed to understand the actual checks and the remaining missingness.

## Definitions to keep consistent

| Term | Meaning in this project |
| --- | --- |
| Customers | Rows with unique customer IDs in the displayed population. |
| Churned | Customers whose supplied `Churn` label is `Yes`. |
| Not churned | Customers whose label is `No`; not confirmation of current active status. |
| Churn share | Churned customers divided by all customers in the same scope. |
| Tenure band | A defined grouping of recorded months; not a calendar period. |
| Percentage-point difference | Subtraction of two percentage values; different from relative percentage change. |
| Missing `TotalCharges` | Unknown cumulative charge amounts, preserved as null rather than imputed zero. |

The CSV has no explicit currency field. If a future report applies a currency symbol to charge amounts, document that display assumption. Summed `MonthlyCharges` for churned customers is not an audited lost-revenue measure or an estimate of what a retention campaign could recover.

## A two-minute demonstration

Spend the first 45 seconds on Customer health. Explain the 7,043-customer denominator, 26.54% observed churn share and the month-to-month concentration. Show that the bar labels include counts, not just percentages.

Use the next 45 seconds on Segment performance. Choose one service or payment comparison, then show contract and tenure together. Explain why the overlapping groups cannot be added and which additional operational evidence would help investigate the pattern.

Use the final 30 seconds on Data quality. Point to the 11 missing charge values and explain why the customer rows remain in the analysis. End with a specific next question, such as reviewing first-bill experience among early-tenure customers, rather than promising a retention improvement.

## Reproduce and review the figures

From the repository root, with the Python environment active:

```bash
python scripts/build_project.py
python -m unittest discover -s tests -v
```

The build verifies the pinned source and writes the prepared CSV, summary files and three images. To check a finding, inspect `reports/metrics.json` and the relevant segment CSV, then follow the calculation in `scripts/prepare_data.py`. Confirm the group count before interpreting the rate.

If building the native Power BI report, compare its card totals and filtered measures with these reference outputs. Test denominator behavior, empty selections, the zero-month band and the internet-only support scope. Save and review the resulting `.pbix` separately before describing a figure as a Power BI export.

See [the business case](BUSINESS_CASE.md) for the proposed operational questions and [source metadata](../data/source.json) for the exact dataset used.

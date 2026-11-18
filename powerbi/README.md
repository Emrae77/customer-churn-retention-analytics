# Build the Power BI report

This folder contains the Power Query import code, DAX measure definitions and a
report theme needed to recreate the analysis in Power BI. **Power BI Desktop is
not available in the preparation environment, so no `.pbix` has been created or
validated here.** The SQL Server scripts, M queries and DAX have been reviewed
as source, but still need native execution in your installation. Repository
preview images are calculated and rendered with Python; they are **not exports
from Power BI**. Any supplied reference images are design references, not proof
of a completed interactive report.

## 1. Load one customer table

Choose **one** route. Both produce the same 21 source fields plus `ChurnFlag`,
`TenureBand`, `TenureBandSort` and `TotalChargesMissing`.

### Route A: cleaned CSV

Run `python scripts/build_project.py` at the repository root first. In Power BI
Desktop, create a blank query, open its Advanced Editor, and paste
`import_cleaned_csv.pq`. Replace `CleanedCsvPath` with the full local path to
`data/processed/telco_customers.csv`. Name the query **Customers** and apply it.
The query expects the cleaned 25-column output, not the raw 21-column download.
It preserves blank total charges as null and sets numeric types explicitly.

### Route B: SQL Server

Complete the steps in [`../sql/README.md`](../sql/README.md), including validation.
Create a blank query, paste `connect_sql_view.pq`, and edit the server and
database names. Authenticate through Power BI's data-source prompt and name the
query **Customers**. Use Import mode for this small portfolio dataset. The query
reads `dbo.vw_TelcoCustomers`; it does not perform a database load or update.

Do not load both copies and append them. There should be **one row per customer**
and 7,043 rows. No relationships or date table are required for this single-table
snapshot analysis. The dataset does not provide an observation timeline from
which to construct monthly churn trends or retention cohorts.

## 2. Set up the model and measures

- Keep `customerID` as text. Set its default summarization to **Don't summarize**.
- Keep `SeniorCitizen`, `tenure`, and the three numeric flags/sort fields as whole
  numbers; treat senior status as a category rather than an amount to sum.
- Use fixed decimal types for `MonthlyCharges` and `TotalCharges`. Display
  charges with two decimal places; avoid a currency symbol unless you explicitly
  state the unit and source assumption.
- Select `TenureBand` and use **Sort by column → TenureBandSort**. The order is
  `0 months`, `1–12 months`, `13–24 months`, `25–48 months`, `49–72 months`.
- Create each definition from `measures.dax` separately with **New measure**.
  The file is a catalog of seven measures, not a single DAX query to execute.
- Format `ChurnRate` and `NotChurnedShare` as percentages with two decimal
  places, customer counts as whole numbers, and average charges to two decimals.
- Import `theme.json` through the report theme controls. Use teal for
  not-churned/status-neutral context and orange for churn or higher-priority
  review. Set status colors explicitly in visuals; palette order alone does not
  guarantee which label receives a color.

### Why these measures respect filters

`TotalCustomers` counts customer rows under the current filters. `Churned` and
`NotChurned` intersect that context with a status through `KEEPFILTERS`; they do
not replace an existing selection on `ChurnFlag`. The strict `== 0` comparison
prevents a blank/unknown flag from being treated as a known not-churned customer.
`DIVIDE` leaves a rate blank when its denominator is zero, avoiding a misleading
zero-percent rate for an empty population. See the Microsoft references below.

Consequently, selecting only churned customers makes the selected population's
churn rate 100%. That is expected filter behavior. The Overview should use
segment slicers, not a hidden churn-only page filter. If you add a status slicer,
make its effect obvious. The rate is always the share within the current
population, not a ratio using an unrelated all-customer denominator.

## 3. Suggested report pages

### Overview — Where should we look first?

| Visual | Fields/measures | Interpretation |
| --- | --- | --- |
| KPI cards | `TotalCustomers`, `Churned`, `ChurnRate`, `NotChurnedShare` | Size and churn status of the selected population. |
| Horizontal bars | Axis: `Contract`; value: `ChurnRate`; tooltips: `TotalCustomers`, `Churned` | Compare contract groups while keeping denominators visible. |
| Horizontal bars | Axis: `InternetService`; value: `ChurnRate`; tooltips: counts | Investigate service-group associations. |
| Column chart | Axis: `TenureBand` sorted by its sort column; value: `ChurnRate` | Compare tenure groups, retaining the zero-month group. |
| Slicers | `Contract`, `InternetService`, `TenureBand` | Make the selected customer population explicit. |

Use a 16:9 canvas, a navy title, ample white space and consistent percentage
scales. Show a short subtitle stating that this is an IBM sample customer
snapshot. A chart's category ranking is not an estimate of an intervention's
effect, nor a causal explanation for churn.

### Segment review — Which combination needs follow-up?

Add a matrix with `Contract` and `InternetService`, displaying `TotalCustomers`,
`Churned` and `ChurnRate`. Add a payment-method chart and a separate support or
security comparison. Keep `No internet service` and `No phone service` distinct
from `No`: they describe service applicability, not the same customer choice.
Always expose segment counts so small groups are not mistaken for strong
evidence. Use the result to propose a targeted review or experiment, not to
declare that a contract or payment method caused customers to leave.

### Data quality — What did cleaning preserve?

Show `TotalCustomers` and `MissingTotalCharges` cards. Add a table containing
`customerID`, `tenure`, `MonthlyCharges`, `TotalCharges`, and
`TotalChargesMissing`, filtered to the missing flag equal to 1. It should display
11 customers, all with zero tenure in the pinned sample. Leave `TotalCharges`
blank; do not replace it with zero or remove these customers from the model.

## 4. Validate the native report

These are checks to perform in Power BI after creating the model. They are not
claims that Desktop execution has already taken place.

| Check | Expected result |
| --- | --- |
| No filters | Total 7,043; churned 1,869; not churned 5,174. |
| No filters, rate cards | Churn rate 26.54%; not-churned share 73.46% (rounded). |
| No filters, charges | Average monthly charges approximately 64.76; 11 missing total charges. |
| Select `Churn = Yes` or `ChurnFlag = 1` | Total 1,869; churned 1,869; not churned 0; churn rate 100%. |
| Select `Churn = No` or `ChurnFlag = 0` | Total 5,174; churned 0; not churned 5,174; churn rate 0%. |
| Select `TenureBand = 0 months` | Total 11; missing total charges 11. |
| Contract or internet slicer | Counts and rates reconcile with the corresponding SQL/CSV segment output. |
| Empty population | Count measures show 0; percentage and average-charge measures remain blank. |
| Clear all filters | Return to the unfiltered anchors above. |

Also check visual interactions: selecting one bar should affect the intended
cards and tables, and clearing it should restore the original totals. Confirm
that a page-level filter or bookmark has not silently changed the denominator.
Save the `.pbix` only after those checks. A later published report URL is a
separate deliverable from the repository or its static preview images.

## 5. What the report means

This is descriptive customer churn and retention-opportunity analysis, not a
machine-learning prediction project. `NotChurnedShare` measures the sample's
current status complement; call it **not-churned share**, not a measured
long-term retention rate. The data does not establish why an individual left,
whether a proposed offer would retain them, or the financial return from an
action. Monthly charges and cumulative charges should not be presented as
verified lost revenue or customer lifetime value.

The management question is practical: which sufficiently large segments have
an elevated observed churn share, what else should we investigate about those
customers, and what controlled action could we test next?

## Microsoft primary references

- [Csv.Document](https://learn.microsoft.com/en-us/powerquery-m/csv-document)
- [Sql.Database](https://learn.microsoft.com/en-us/powerquery-m/sql-database)
- [COUNTROWS](https://learn.microsoft.com/en-us/dax/countrows-function-dax)
- [CALCULATE](https://learn.microsoft.com/en-us/dax/calculate-function-dax)
- [KEEPFILTERS](https://learn.microsoft.com/en-us/dax/keepfilters-function-dax)
- [DIVIDE](https://learn.microsoft.com/en-us/dax/divide-function-dax)
- [DAX operators, including strict equality](https://learn.microsoft.com/en-us/dax/dax-operator-reference)
- [Report themes](https://learn.microsoft.com/en-us/power-bi/create-reports/desktop-report-themes)

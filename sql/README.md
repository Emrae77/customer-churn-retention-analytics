# SQL Server workflow

These scripts target **SQL Server 2017 or later**, using `TRIM`, `TRY_CONVERT`
and `CREATE OR ALTER VIEW`. They have been reviewed statically; **they have not
been executed against SQL Server in this delivery environment**. The separate
Python analysis provides the computed reference outputs.

## Run order

1. Run `python scripts/build_project.py` from the repository root to obtain and
   verify the pinned original CSV. The raw file is
   `data/raw/Telco-Customer-Churn.csv`.
2. In SQL Server Management Studio, choose a dedicated project database. Run
   `01_create_raw_table.sql` in that database. The script creates
   `dbo.TelcoChurnRaw` only if absent; it does not erase an existing table.
3. Load the CSV with the client-side loader below. An alternative import tool
   must retain all 21 fields as text and preserve the whitespace-only charges.
4. Run `02_profile_raw.sql`, then `03_create_clean_view.sql`,
   `04_segment_analysis.sql`, and `05_validate.sql` in order.
5. Connect Power BI to `dbo.vw_TelcoCustomers` and rename the loaded table
   `Customers`. Use the customer-level view for slicers and DAX; the separate
   segment view is a SQL review aid.

`GO` is a batch separator understood by SSMS/sqlcmd; it is not a SQL statement
to send directly through a generic Python cursor. The scripts use the database
selected by the connection and do not create or choose a database for you.

## Load from your computer

Install `pyodbc` in your project environment and install a suitable Microsoft
ODBC Driver for SQL Server on your machine. Python packages alone do not install
that system driver. Supply a connection string through the environment:

```bash
python -m pip install pyodbc
python sql/load_sql_server.py --dry-run
```

Set `TELCO_SQL_CONNECTION_STRING` using your local credential mechanism. For a
Windows integrated-authentication connection, a template is:

```powershell
$env:TELCO_SQL_CONNECTION_STRING = "Driver={ODBC Driver 18 for SQL Server};Server=YOUR_SERVER;Database=TelcoAnalytics;Trusted_Connection=yes;Encrypt=yes;TrustServerCertificate=no;"
```

The server and certificate configuration must match your installation. Use an
authentication method supported by your server; do not put passwords in source
files or commit connection strings. The loader does not read `.env` automatically.

Then, from the repository root:

```bash
python sql/load_sql_server.py --csv data/raw/Telco-Customer-Churn.csv
```

The loader uses parameterized inserts, verifies the header and row count, and
commits one transaction. It refuses a nonempty raw table, so rerunning it cannot
silently double the dataset. It does not download data, create the table, or
delete existing data. `--dry-run` validates only the local CSV, without SQL
Server, an ODBC driver or `pyodbc`.

## Cleaning contract

The cleaned view keeps **all 7,043 customers**. The 21 original column names and
their order are followed by `ChurnFlag`, `TenureBand`, `TenureBandSort`, and
`TotalChargesMissing`, matching `data/processed/telco_customers.csv`.

| Field | Rule |
| --- | --- |
| Categorical text | Trim surrounding spaces; retain categories such as `No internet service` and `No phone service`. Empty text becomes NULL. |
| `SeniorCitizen`, `tenure` | Convert trimmed nonblank text to integers with `TRY_CONVERT`. |
| `MonthlyCharges`, `TotalCharges` | Convert to `decimal(12,2)`; blank text becomes NULL before conversion. |
| `ChurnFlag` | Exactly `Yes` → 1 and `No` → 0. Unknown or missing labels become NULL and fail validation. |
| `TotalChargesMissing` | 1 only when the original charge text is NULL or blank after trimming; otherwise 0. |
| `TenureBand` / sort | `0 months` / 0, `1–12 months` / 1, `13–24 months` / 2, `25–48 months` / 3, `49–72 months` / 4. Unsupported tenure remains NULL and fails validation. |

The 11 blank `TotalCharges` values are retained as NULL, not filled with zero or
inferred from monthly charges. A nonblank invalid numeric also becomes NULL via
`TRY_CONVERT`, but the validation script distinguishes that failure from the
11 expected missing values. There is no `ELSE 0` conversion for unknown churn.

## Expected validation and metric interpretation

The pinned source should yield 7,043 unique customers, 1,869 churned and 5,174
not churned; 11 missing cumulative charges occur at tenure zero. The validation
script checks these source-specific anchors, category vocabularies, required
numeric fields, and segment reconciliation. It prints PASS/FAIL rows and raises
an error if any check fails. Do not adapt those expected counts to make a failed
load appear successful without first understanding the difference.

`ChurnRate` is churned customers divided by all customers in that segment.
`NotChurnedShare` is the snapshot's not-churned share. The latter does **not**
measure repeat retention over time. `AverageMonthlyCharges` averages the monthly
charge field in the selected population; it is not revenue lost to churn.

The segment view repeats the population once per dimension. Counts can be
reconciled within Contract or within TenureBand, but must not be added across
different dimensions. Segment patterns are descriptive associations. They do
not establish which action would prevent churn or how much an intervention
would earn.

## Primary technical references

- [Microsoft: TRIM](https://learn.microsoft.com/en-us/sql/t-sql/functions/trim-transact-sql)
- [Microsoft: TRY_CONVERT](https://learn.microsoft.com/en-us/sql/t-sql/functions/try-convert-transact-sql)
- [Microsoft: CREATE VIEW](https://learn.microsoft.com/en-us/sql/t-sql/statements/create-view-transact-sql)
- [Microsoft: ODBC Driver for SQL Server](https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server)

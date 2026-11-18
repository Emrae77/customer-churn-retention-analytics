"""Load the original IBM CSV as text into an empty dbo.TelcoChurnRaw table.

The SQL connection string comes only from TELCO_SQL_CONNECTION_STRING.
Requires pyodbc and a working SQL Server ODBC driver for an actual load.
--dry-run validates the file without either dependency or a database connection.
"""

import argparse
import csv
import os
from pathlib import Path


COLUMNS = (
    "customerID", "gender", "SeniorCitizen", "Partner", "Dependents", "tenure",
    "PhoneService", "MultipleLines", "InternetService", "OnlineSecurity",
    "OnlineBackup", "DeviceProtection", "TechSupport", "StreamingTV",
    "StreamingMovies", "Contract", "PaperlessBilling", "PaymentMethod",
    "MonthlyCharges", "TotalCharges", "Churn",
)


def read_rows(path, expected_rows):
    """Keep cell text, including the source's whitespace-only total charges."""
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.reader(handle)
        if tuple(next(reader, ())) != COLUMNS:
            raise ValueError("CSV header does not match the original 21-column schema.")
        rows = []
        for line_number, row in enumerate(reader, start=2):
            if len(row) != len(COLUMNS):
                raise ValueError("Wrong field count on CSV line {}.".format(line_number))
            if any(len(cell) > 255 for cell in row):
                raise ValueError("Cell exceeds nvarchar(255) on line {}.".format(line_number))
            rows.append(tuple(row))
    if len(rows) != expected_rows:
        raise ValueError("Expected {} rows; found {}.".format(expected_rows, len(rows)))
    return rows


def load_rows(rows, connection_string):
    import pyodbc

    column_sql = ", ".join("[{}]".format(name) for name in COLUMNS)
    markers = ", ".join("?" for _ in COLUMNS)
    insert_sql = "INSERT INTO dbo.TelcoChurnRaw ({}) VALUES ({})".format(
        column_sql, markers
    )
    connection = pyodbc.connect(connection_string, autocommit=False)
    try:
        cursor = connection.cursor()
        cursor.execute("SET XACT_ABORT ON;")
        # Lock the table during the initial count and insert, preventing this
        # script from appending a second copy while another load is running.
        cursor.execute(
            "SELECT COUNT_BIG(*) FROM dbo.TelcoChurnRaw WITH (TABLOCKX, HOLDLOCK)"
        )
        if cursor.fetchone()[0] != 0:
            raise ValueError("Raw table is not empty; refusing to append duplicate data.")
        cursor.fast_executemany = True
        cursor.executemany(insert_sql, rows)
        cursor.execute("SELECT COUNT_BIG(*) FROM dbo.TelcoChurnRaw")
        if cursor.fetchone()[0] != len(rows):
            raise RuntimeError("Loaded row count does not match the CSV; rolling back.")
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--csv", type=Path, default=Path("data/raw/Telco-Customer-Churn.csv")
    )
    parser.add_argument("--expected-rows", type=int, default=7043)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    rows = read_rows(args.csv, args.expected_rows)
    if args.dry_run:
        print("CSV validated: {} rows, {} original fields.".format(len(rows), len(COLUMNS)))
        return
    connection_string = os.getenv("TELCO_SQL_CONNECTION_STRING")
    if not connection_string:
        parser.error("Set TELCO_SQL_CONNECTION_STRING before running a database load.")
    load_rows(rows, connection_string)
    print("Committed {} text rows to dbo.TelcoChurnRaw.".format(len(rows)))


if __name__ == "__main__":
    main()

/*
Run in your chosen SQL Server database (SQL Server 2017 or later).
Every source field is text at ingestion. No row is dropped by this script.
Existing data is left untouched; the loader refuses a nonempty raw table.
*/
SET NOCOUNT ON;
SET XACT_ABORT ON;

IF OBJECT_ID(N'dbo.TelcoChurnRaw', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.TelcoChurnRaw
    (
        [customerID]       nvarchar(255) NULL,
        [gender]           nvarchar(255) NULL,
        [SeniorCitizen]    nvarchar(255) NULL,
        [Partner]          nvarchar(255) NULL,
        [Dependents]       nvarchar(255) NULL,
        [tenure]           nvarchar(255) NULL,
        [PhoneService]     nvarchar(255) NULL,
        [MultipleLines]    nvarchar(255) NULL,
        [InternetService]  nvarchar(255) NULL,
        [OnlineSecurity]   nvarchar(255) NULL,
        [OnlineBackup]     nvarchar(255) NULL,
        [DeviceProtection] nvarchar(255) NULL,
        [TechSupport]      nvarchar(255) NULL,
        [StreamingTV]      nvarchar(255) NULL,
        [StreamingMovies]  nvarchar(255) NULL,
        [Contract]         nvarchar(255) NULL,
        [PaperlessBilling] nvarchar(255) NULL,
        [PaymentMethod]    nvarchar(255) NULL,
        [MonthlyCharges]   nvarchar(255) NULL,
        [TotalCharges]     nvarchar(255) NULL,
        [Churn]            nvarchar(255) NULL
    );
END;

SELECT DB_NAME() AS DatabaseName, COUNT_BIG(*) AS RawRows
FROM dbo.TelcoChurnRaw;

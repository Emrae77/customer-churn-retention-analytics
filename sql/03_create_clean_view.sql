/*
Read-only cleaning layer: 21 original fields plus 4 derived fields.
TRIM removes surrounding ordinary spaces; NULLIF prevents blank numeric text
from being interpreted as zero. TRY_CONVERT exposes invalid values as NULL.
No WHERE, DISTINCT, join or imputation removes or manufactures customer rows.
*/
SET ANSI_NULLS ON;
GO
SET QUOTED_IDENTIFIER ON;
GO
CREATE OR ALTER VIEW dbo.vw_TelcoCustomers
AS
WITH Cleaned AS
(
    SELECT
        NULLIF(TRIM(customerID), N'') AS customerID,
        NULLIF(TRIM(gender), N'') AS gender,
        TRY_CONVERT(int, NULLIF(TRIM(SeniorCitizen), N'')) AS SeniorCitizen,
        NULLIF(TRIM(Partner), N'') AS Partner,
        NULLIF(TRIM(Dependents), N'') AS Dependents,
        TRY_CONVERT(int, NULLIF(TRIM(tenure), N'')) AS tenure,
        NULLIF(TRIM(PhoneService), N'') AS PhoneService,
        NULLIF(TRIM(MultipleLines), N'') AS MultipleLines,
        NULLIF(TRIM(InternetService), N'') AS InternetService,
        NULLIF(TRIM(OnlineSecurity), N'') AS OnlineSecurity,
        NULLIF(TRIM(OnlineBackup), N'') AS OnlineBackup,
        NULLIF(TRIM(DeviceProtection), N'') AS DeviceProtection,
        NULLIF(TRIM(TechSupport), N'') AS TechSupport,
        NULLIF(TRIM(StreamingTV), N'') AS StreamingTV,
        NULLIF(TRIM(StreamingMovies), N'') AS StreamingMovies,
        NULLIF(TRIM(Contract), N'') AS Contract,
        NULLIF(TRIM(PaperlessBilling), N'') AS PaperlessBilling,
        NULLIF(TRIM(PaymentMethod), N'') AS PaymentMethod,
        TRY_CONVERT(decimal(12,2), NULLIF(TRIM(MonthlyCharges), N''))
            AS MonthlyCharges,
        TRY_CONVERT(decimal(12,2), NULLIF(TRIM(TotalCharges), N''))
            AS TotalCharges,
        NULLIF(TRIM(Churn), N'') AS Churn,
        CASE WHEN NULLIF(TRIM(TotalCharges), N'') IS NULL THEN 1 ELSE 0 END
            AS TotalChargesMissing
    FROM dbo.TelcoChurnRaw
)
SELECT
    customerID, gender, SeniorCitizen, Partner, Dependents, tenure,
    PhoneService, MultipleLines, InternetService, OnlineSecurity, OnlineBackup,
    DeviceProtection, TechSupport, StreamingTV, StreamingMovies, Contract,
    PaperlessBilling, PaymentMethod, MonthlyCharges, TotalCharges, Churn,
    CASE Churn COLLATE Latin1_General_100_BIN2
        WHEN N'Yes' THEN 1
        WHEN N'No' THEN 0
        ELSE NULL
    END AS ChurnFlag,
    CASE
        WHEN tenure = 0 THEN N'0 months'
        WHEN tenure BETWEEN 1 AND 12 THEN N'1–12 months'
        WHEN tenure BETWEEN 13 AND 24 THEN N'13–24 months'
        WHEN tenure BETWEEN 25 AND 48 THEN N'25–48 months'
        WHEN tenure BETWEEN 49 AND 72 THEN N'49–72 months'
        ELSE NULL
    END AS TenureBand,
    CASE
        WHEN tenure = 0 THEN 0
        WHEN tenure BETWEEN 1 AND 12 THEN 1
        WHEN tenure BETWEEN 13 AND 24 THEN 2
        WHEN tenure BETWEEN 25 AND 48 THEN 3
        WHEN tenure BETWEEN 49 AND 72 THEN 4
        ELSE NULL
    END AS TenureBandSort,
    TotalChargesMissing
FROM Cleaned;
GO

SELECT TOP (10) * FROM dbo.vw_TelcoCustomers ORDER BY customerID;

/* Read-only source profiling. Run after loading the original 21-column CSV. */
SET NOCOUNT ON;

SELECT
    COUNT_BIG(*) AS RawRows,
    COUNT(DISTINCT NULLIF(TRIM(customerID), N'')) AS DistinctCustomerIDs,
    SUM(CASE WHEN NULLIF(TRIM(customerID), N'') IS NULL THEN 1 ELSE 0 END)
        AS MissingCustomerIDs,
    SUM(CASE WHEN NULLIF(TRIM(TotalCharges), N'') IS NULL THEN 1 ELSE 0 END)
        AS BlankTotalCharges,
    SUM(CASE WHEN NULLIF(TRIM(TotalCharges), N'') IS NOT NULL
                  AND TRY_CONVERT(decimal(12,2), TRIM(TotalCharges)) IS NULL
             THEN 1 ELSE 0 END) AS NonblankTotalChargesConversionFailures
FROM dbo.TelcoChurnRaw;

-- Expected: no duplicate IDs. Do not silently deduplicate the source.
SELECT TRIM(customerID) AS customerID, COUNT_BIG(*) AS Occurrences
FROM dbo.TelcoChurnRaw
GROUP BY TRIM(customerID)
HAVING COUNT_BIG(*) > 1;

-- Preserve and inspect all categorical levels, including service-not-applicable.
SELECT v.FieldName, v.FieldValue, COUNT_BIG(*) AS Customers
FROM dbo.TelcoChurnRaw AS r
CROSS APPLY (VALUES
    (N'gender', TRIM(r.gender)),
    (N'SeniorCitizen', TRIM(r.SeniorCitizen)),
    (N'Partner', TRIM(r.Partner)),
    (N'Dependents', TRIM(r.Dependents)),
    (N'PhoneService', TRIM(r.PhoneService)),
    (N'MultipleLines', TRIM(r.MultipleLines)),
    (N'InternetService', TRIM(r.InternetService)),
    (N'OnlineSecurity', TRIM(r.OnlineSecurity)),
    (N'OnlineBackup', TRIM(r.OnlineBackup)),
    (N'DeviceProtection', TRIM(r.DeviceProtection)),
    (N'TechSupport', TRIM(r.TechSupport)),
    (N'StreamingTV', TRIM(r.StreamingTV)),
    (N'StreamingMovies', TRIM(r.StreamingMovies)),
    (N'Contract', TRIM(r.Contract)),
    (N'PaperlessBilling', TRIM(r.PaperlessBilling)),
    (N'PaymentMethod', TRIM(r.PaymentMethod)),
    (N'Churn', TRIM(r.Churn))
) AS v(FieldName, FieldValue)
GROUP BY v.FieldName, v.FieldValue
ORDER BY v.FieldName, Customers DESC, v.FieldValue;

-- Examine the 11 missing cumulative charges alongside their original tenure.
SELECT customerID, tenure, MonthlyCharges, TotalCharges, Churn
FROM dbo.TelcoChurnRaw
WHERE NULLIF(TRIM(TotalCharges), N'') IS NULL
ORDER BY customerID;

/*
Dataset-specific release checks for the pinned classic IBM 7,043-row file.
Run after 03 and 04. Review the results; any failed check raises an error.
This script only reads application data. It does not repair invalid values.
*/
SET NOCOUNT ON;

DECLARE @CategoryIssues TABLE
(
    customerID nvarchar(255),
    FieldName nvarchar(50),
    RawValue nvarchar(255)
);

WITH Expected AS
(
    SELECT FieldName, FieldValue
    FROM (VALUES
        (N'gender', N'Female'), (N'gender', N'Male'),
        (N'SeniorCitizen', N'0'), (N'SeniorCitizen', N'1'),
        (N'Partner', N'Yes'), (N'Partner', N'No'),
        (N'Dependents', N'Yes'), (N'Dependents', N'No'),
        (N'PhoneService', N'Yes'), (N'PhoneService', N'No'),
        (N'MultipleLines', N'Yes'), (N'MultipleLines', N'No'),
        (N'MultipleLines', N'No phone service'),
        (N'InternetService', N'DSL'), (N'InternetService', N'Fiber optic'),
        (N'InternetService', N'No'),
        (N'OnlineSecurity', N'Yes'), (N'OnlineSecurity', N'No'),
        (N'OnlineSecurity', N'No internet service'),
        (N'OnlineBackup', N'Yes'), (N'OnlineBackup', N'No'),
        (N'OnlineBackup', N'No internet service'),
        (N'DeviceProtection', N'Yes'), (N'DeviceProtection', N'No'),
        (N'DeviceProtection', N'No internet service'),
        (N'TechSupport', N'Yes'), (N'TechSupport', N'No'),
        (N'TechSupport', N'No internet service'),
        (N'StreamingTV', N'Yes'), (N'StreamingTV', N'No'),
        (N'StreamingTV', N'No internet service'),
        (N'StreamingMovies', N'Yes'), (N'StreamingMovies', N'No'),
        (N'StreamingMovies', N'No internet service'),
        (N'Contract', N'Month-to-month'), (N'Contract', N'One year'),
        (N'Contract', N'Two year'),
        (N'PaperlessBilling', N'Yes'), (N'PaperlessBilling', N'No'),
        (N'PaymentMethod', N'Electronic check'),
        (N'PaymentMethod', N'Mailed check'),
        (N'PaymentMethod', N'Bank transfer (automatic)'),
        (N'PaymentMethod', N'Credit card (automatic)'),
        (N'Churn', N'Yes'), (N'Churn', N'No')
    ) AS e(FieldName, FieldValue)
)
INSERT INTO @CategoryIssues (customerID, FieldName, RawValue)
SELECT r.customerID, v.FieldName, v.FieldValue
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
WHERE NOT EXISTS
(
    SELECT 1 FROM Expected AS e
    WHERE e.FieldName = v.FieldName
      AND e.FieldValue COLLATE Latin1_General_100_BIN2
          = v.FieldValue COLLATE Latin1_General_100_BIN2
);

DECLARE @Checks TABLE
(
    CheckName nvarchar(100), Actual bigint, Expected bigint
);

INSERT INTO @Checks (CheckName, Actual, Expected)
VALUES
    (N'Raw customer rows', (SELECT COUNT_BIG(*) FROM dbo.TelcoChurnRaw), 7043),
    (N'Cleaned customer rows',
        (SELECT COUNT_BIG(*) FROM dbo.vw_TelcoCustomers), 7043),
    (N'Unique nonblank customer IDs',
        (SELECT COUNT(DISTINCT customerID) FROM dbo.vw_TelcoCustomers), 7043),
    (N'Churned customers',
        (SELECT COUNT_BIG(*) FROM dbo.vw_TelcoCustomers WHERE ChurnFlag = 1), 1869),
    (N'Not-churned customers',
        (SELECT COUNT_BIG(*) FROM dbo.vw_TelcoCustomers WHERE ChurnFlag = 0), 5174),
    (N'Unknown churn labels',
        (SELECT COUNT_BIG(*) FROM dbo.vw_TelcoCustomers WHERE ChurnFlag IS NULL), 0),
    (N'Missing total-charge flags',
        (SELECT SUM(TotalChargesMissing) FROM dbo.vw_TelcoCustomers), 11),
    (N'NULL total-charge values',
        (SELECT COUNT_BIG(*) FROM dbo.vw_TelcoCustomers WHERE TotalCharges IS NULL), 11),
    (N'Missing total charges with zero tenure',
        (SELECT COUNT_BIG(*) FROM dbo.vw_TelcoCustomers
         WHERE TotalChargesMissing = 1 AND tenure = 0), 11),
    (N'Invalid or missing required numerics',
        (SELECT COUNT_BIG(*) FROM dbo.vw_TelcoCustomers
         WHERE SeniorCitizen IS NULL OR SeniorCitizen NOT IN (0, 1)
            OR tenure IS NULL OR tenure NOT BETWEEN 0 AND 72
            OR MonthlyCharges IS NULL OR MonthlyCharges < 0), 0),
    (N'Failed nonblank total-charge conversions or negative charges',
        (SELECT COUNT_BIG(*) FROM dbo.vw_TelcoCustomers
         WHERE (TotalChargesMissing = 0 AND TotalCharges IS NULL)
            OR TotalCharges < 0), 0),
    (N'Missing tenure bands',
        (SELECT COUNT_BIG(*) FROM dbo.vw_TelcoCustomers
         WHERE TenureBand IS NULL OR TenureBandSort IS NULL), 0),
    (N'Unexpected or missing category values',
        (SELECT COUNT_BIG(*) FROM @CategoryIssues), 0),
    (N'Contract segment customer reconciliation',
        (SELECT SUM(TotalCustomers) FROM dbo.vw_TelcoSegmentKPIs
         WHERE Dimension = N'Contract'), 7043),
    (N'Contract segment churn reconciliation',
        (SELECT SUM(Churned) FROM dbo.vw_TelcoSegmentKPIs
         WHERE Dimension = N'Contract'), 1869);

SELECT CheckName, Actual, Expected,
       CASE WHEN Actual = Expected THEN N'PASS' ELSE N'FAIL' END AS Result
FROM @Checks
ORDER BY CheckName;

SELECT * FROM @CategoryIssues ORDER BY FieldName, customerID;

IF EXISTS (SELECT 1 FROM @Checks WHERE Actual IS NULL OR Actual <> Expected)
    THROW 51001, 'Validation failed. Review the result sets before reporting.', 1;

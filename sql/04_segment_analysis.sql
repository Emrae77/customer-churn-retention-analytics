/*
Rates are proportions (0 to 1); format as percentages in the report.
Each dimension repeats the customer population. Do not add counts across
different dimensions. This view describes associations, not churn causes.
*/
SET ANSI_NULLS ON;
GO
SET QUOTED_IDENTIFIER ON;
GO
CREATE OR ALTER VIEW dbo.vw_TelcoSegmentKPIs
AS
SELECT
    s.Dimension,
    s.Segment,
    s.SegmentSort,
    COUNT_BIG(*) AS TotalCustomers,
    SUM(CASE WHEN c.ChurnFlag = 1 THEN 1 ELSE 0 END) AS Churned,
    SUM(CASE WHEN c.ChurnFlag = 0 THEN 1 ELSE 0 END) AS NotChurned,
    SUM(CASE WHEN c.ChurnFlag IS NULL THEN 1 ELSE 0 END) AS UnknownChurnCustomers,
    CAST(1.0 * SUM(CASE WHEN c.ChurnFlag = 1 THEN 1 ELSE 0 END)
         / NULLIF(COUNT_BIG(*), 0) AS decimal(9,6)) AS ChurnRate,
    CAST(1.0 * SUM(CASE WHEN c.ChurnFlag = 0 THEN 1 ELSE 0 END)
         / NULLIF(COUNT_BIG(*), 0) AS decimal(9,6)) AS NotChurnedShare,
    AVG(c.MonthlyCharges) AS AverageMonthlyCharges,
    SUM(c.TotalChargesMissing) AS MissingTotalCharges
FROM dbo.vw_TelcoCustomers AS c
CROSS APPLY (VALUES
    (N'Contract', c.Contract, 0),
    (N'InternetService', c.InternetService, 0),
    (N'PaymentMethod', c.PaymentMethod, 0),
    (N'TenureBand', c.TenureBand, c.TenureBandSort),
    (N'TechSupport', c.TechSupport, 0),
    (N'OnlineSecurity', c.OnlineSecurity, 0),
    (N'PaperlessBilling', c.PaperlessBilling, 0)
) AS s(Dimension, Segment, SegmentSort)
GROUP BY s.Dimension, s.Segment, s.SegmentSort;
GO

-- Overall snapshot. NotChurnedShare is a status share, not a longitudinal
-- retention rate: this dataset has no customer-level observation timeline.
SELECT
    COUNT_BIG(*) AS TotalCustomers,
    SUM(CASE WHEN ChurnFlag = 1 THEN 1 ELSE 0 END) AS Churned,
    SUM(CASE WHEN ChurnFlag = 0 THEN 1 ELSE 0 END) AS NotChurned,
    CAST(1.0 * SUM(CASE WHEN ChurnFlag = 1 THEN 1 ELSE 0 END)
         / NULLIF(COUNT_BIG(*), 0) AS decimal(9,6)) AS ChurnRate,
    CAST(1.0 * SUM(CASE WHEN ChurnFlag = 0 THEN 1 ELSE 0 END)
         / NULLIF(COUNT_BIG(*), 0) AS decimal(9,6)) AS NotChurnedShare,
    AVG(MonthlyCharges) AS AverageMonthlyCharges,
    SUM(TotalChargesMissing) AS MissingTotalCharges
FROM dbo.vw_TelcoCustomers;

SELECT *
FROM dbo.vw_TelcoSegmentKPIs
ORDER BY Dimension, SegmentSort, ChurnRate DESC, Segment;

-- A joint slice can check whether a broad pattern persists within contracts.
-- Always show denominators; small groups are not strong policy evidence.
SELECT
    Contract, InternetService,
    COUNT_BIG(*) AS TotalCustomers,
    SUM(CASE WHEN ChurnFlag = 1 THEN 1 ELSE 0 END) AS Churned,
    CAST(1.0 * SUM(CASE WHEN ChurnFlag = 1 THEN 1 ELSE 0 END)
         / NULLIF(COUNT_BIG(*), 0) AS decimal(9,6)) AS ChurnRate
FROM dbo.vw_TelcoCustomers
GROUP BY Contract, InternetService
ORDER BY Contract, ChurnRate DESC;

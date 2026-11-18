// Alternative to CSV import, after running sql/01 through sql/05 successfully.
// Use one source only for the Customers table. Credentials stay in Power BI.
let
    ServerName = "YOUR_SERVER",
    DatabaseName = "TelcoAnalytics",
    Source = Sql.Database(
        ServerName,
        DatabaseName,
        [CreateNavigationProperties = false]
    ),
    Customers = Source{[Schema = "dbo", Item = "vw_TelcoCustomers"]}[Data],
    Typed = Table.TransformColumnTypes(
        Customers,
        {
            {"SeniorCitizen", Int64.Type}, {"tenure", Int64.Type},
            {"MonthlyCharges", Currency.Type}, {"TotalCharges", Currency.Type},
            {"ChurnFlag", Int64.Type}, {"TenureBandSort", Int64.Type},
            {"TotalChargesMissing", Int64.Type}
        }
    )
in
    Typed

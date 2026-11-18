// Power Query: create one blank query, paste in Advanced Editor, name Customers.
// Edit only this path to your generated 25-column cleaned CSV.
let
    CleanedCsvPath = "C:\Projects\customer-churn-retention-analytics\data\processed\telco_customers.csv",
    Source = Csv.Document(
        File.Contents(CleanedCsvPath),
        [Delimiter = ",", Columns = 25, Encoding = 65001,
         QuoteStyle = QuoteStyle.Csv, ExtraValues = ExtraValues.Error]
    ),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    ExpectedColumns = {
        "customerID", "gender", "SeniorCitizen", "Partner", "Dependents", "tenure",
        "PhoneService", "MultipleLines", "InternetService", "OnlineSecurity",
        "OnlineBackup", "DeviceProtection", "TechSupport", "StreamingTV",
        "StreamingMovies", "Contract", "PaperlessBilling", "PaymentMethod",
        "MonthlyCharges", "TotalCharges", "Churn", "ChurnFlag", "TenureBand",
        "TenureBandSort", "TotalChargesMissing"
    },
    CheckedHeaders =
        if Table.ColumnNames(Headers) = ExpectedColumns then Headers
        else error "Expected the generated 25-column cleaned customer CSV.",
    NullCharges = Table.TransformColumns(
        CheckedHeaders,
        {{"TotalCharges",
          each if _ = null or Text.Trim(_) = "" then null else _,
          type nullable text}}
    ),
    Typed = Table.TransformColumnTypes(
        NullCharges,
        {
            {"customerID", type text}, {"gender", type text},
            {"SeniorCitizen", Int64.Type}, {"Partner", type text},
            {"Dependents", type text}, {"tenure", Int64.Type},
            {"PhoneService", type text}, {"MultipleLines", type text},
            {"InternetService", type text}, {"OnlineSecurity", type text},
            {"OnlineBackup", type text}, {"DeviceProtection", type text},
            {"TechSupport", type text}, {"StreamingTV", type text},
            {"StreamingMovies", type text}, {"Contract", type text},
            {"PaperlessBilling", type text}, {"PaymentMethod", type text},
            {"MonthlyCharges", Currency.Type}, {"TotalCharges", Currency.Type},
            {"Churn", type text}, {"ChurnFlag", Int64.Type},
            {"TenureBand", type text}, {"TenureBandSort", Int64.Type},
            {"TotalChargesMissing", Int64.Type}
        },
        "en-US"
    )
in
    Typed

"""Checks for denominators, missing-value handling and fixed source results."""

import unittest

import pandas as pd

from scripts.prepare_data import (
    ROOT, TENURE_BANDS, analyze, clean_customers, load_customers,
    segment_summary, verify_source,
)


class TelcoAnalysisTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.path = ROOT / "data/raw/Telco-Customer-Churn.csv"
        if not cls.path.exists():
            raise RuntimeError("Run python scripts/build_project.py before running tests.")
        cls.raw, cls.clean = load_customers(cls.path)
        cls.report = analyze(cls.raw, cls.clean)

    def test_fixed_source_checksum(self):
        self.assertEqual(verify_source(self.path), "16320c9c1ec72448db59aa0a26a0b95401046bef5d02fd3aeb906448e3055e91")

    def test_population_and_outcome_reconcile(self):
        summary = self.report["overall"]
        self.assertEqual(summary["customers"], 7043)
        self.assertEqual(summary["churned"], 1869)
        self.assertEqual(summary["not_churned"], 5174)
        self.assertEqual(summary["churned"] + summary["not_churned"], summary["customers"])
        self.assertAlmostEqual(summary["churn_rate_pct"], 100 * 1869 / 7043, places=5)

    def test_missing_charges_do_not_drop_customers(self):
        missing = self.clean.loc[self.clean["TotalChargesMissing"] == 1]
        self.assertEqual(len(missing), 11)
        self.assertTrue(missing["TotalCharges"].isna().all())
        self.assertTrue(missing["tenure"].eq(0).all())
        self.assertEqual(len(self.raw), len(self.clean))
        self.assertTrue(pd.isna(missing["TotalCharges"].sum(min_count=1)))

    def test_contract_counts_and_denominators(self):
        rows = self.report["segments"]["contract"]
        self.assertEqual([(r["customers"], r["churned"]) for r in rows], [(3875, 1655), (1473, 166), (1695, 48)])
        self.assertAlmostEqual(rows[0]["churn_rate_pct"], 100 * 1655 / 3875, places=5)
        self.assertAlmostEqual(rows[2]["churn_rate_pct"], 100 * 48 / 1695, places=5)

    def test_groupings_reconcile_to_population(self):
        for key in ["contract", "tenure", "internet_service", "payment_method"]:
            rows = self.report["segments"][key]
            self.assertEqual(sum(r["customers"] for r in rows), 7043, key)
            self.assertEqual(sum(r["churned"] for r in rows), 1869, key)

    def test_tenure_cutoffs(self):
        data = self.raw.iloc[:10].copy()
        data["tenure"] = ["0", "1", "12", "13", "24", "25", "48", "49", "71", "72"]
        clean = clean_customers(data)
        self.assertEqual(clean["TenureBandSort"].tolist(), [0, 1, 1, 2, 2, 3, 3, 4, 4, 4])
        self.assertEqual(clean["TenureBand"].iloc[0], TENURE_BANDS[0])

    def test_service_absence_is_not_missing(self):
        no_internet = self.clean.loc[self.clean["InternetService"] == "No"]
        self.assertEqual(len(no_internet), 1526)
        self.assertTrue(no_internet["TechSupport"].eq("No internet service").all())
        supported = self.report["segments"]["tech_support_internet_only"]
        self.assertEqual(sum(r["customers"] for r in supported), 5517)
        self.assertEqual(sum(r["churned"] for r in supported), 1756)

    def test_duplicate_ids_are_rejected(self):
        data = pd.concat([self.raw.iloc[:3], self.raw.iloc[:1]], ignore_index=True)
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            clean_customers(data)

    def test_invalid_labels_and_numbers_are_rejected(self):
        for field, value in [("Churn", "Maybe"), ("Contract", "unknown"), ("TotalCharges", "not a number"), ("MonthlyCharges", "")]:
            with self.subTest(field=field):
                data = self.raw.iloc[:3].copy()
                data.loc[data.index[0], field] = value
                with self.assertRaises(ValueError):
                    clean_customers(data)

    def test_empty_segment_is_not_zero_churn(self):
        rows = segment_summary(self.clean.iloc[:0], "Contract", ["Two year"])
        self.assertEqual(rows[0]["customers"], 0)
        self.assertIsNone(rows[0]["churn_rate_pct"])


if __name__ == "__main__":
    unittest.main()

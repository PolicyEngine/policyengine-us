"""The standalone oracle must reject source and assumption drift without PE."""

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace


BUILDER = (
    Path(__file__).resolve().parents[2]
    / "tools/taxsim/generate_federal_tax_history_reference.py"
)
SPEC = importlib.util.spec_from_file_location("federal_tax_history_reference", BUILDER)
builder = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(builder)


class FederalTaxHistoryReferenceTest(unittest.TestCase):
    def test_every_year_from_2017_through_2026_is_required(self):
        builder.validate_years(range(2017, 2027))
        self.assertEqual(tuple(builder.YEARS), tuple(range(2017, 2027)))

    def test_a_missing_intermediate_year_is_rejected(self):
        with self.assertRaisesRegex(RuntimeError, "every year"):
            builder.validate_years([2017, 2018, *range(2020, 2027)])

    def test_shifted_year_endpoints_are_rejected(self):
        with self.assertRaisesRegex(RuntimeError, "every year"):
            builder.validate_years(range(2016, 2026))

    def test_duplicate_or_out_of_order_years_are_rejected(self):
        with self.assertRaisesRegex(RuntimeError, "every year"):
            builder.validate_years([2017, 2018, 2018, *range(2020, 2027)])
        with self.assertRaisesRegex(RuntimeError, "every year"):
            builder.validate_years(reversed(range(2017, 2027)))

    def test_original_reference_projection_preserves_its_four_years(self):
        reference = {
            "cases": ["synthetic"],
            "years": {str(year): {"value": year} for year in range(2017, 2027)},
        }
        projected = builder.original_reference_subset(reference)
        self.assertEqual(list(projected["years"]), ["2017", "2018", "2021", "2026"])
        self.assertEqual(len(reference["years"]), 10)
        self.assertEqual(projected["years"]["2021"], {"value": 2021})

    def test_wrong_version_is_rejected(self):
        with self.assertRaisesRegex(RuntimeError, "6.9.1"):
            builder.validate_version("0.0.0")

    def test_modified_oracle_source_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "source.py").write_text("changed\n")
            with self.assertRaisesRegex(RuntimeError, "source.py"):
                builder.verify_source_hashes(root, {"source.py": "incorrect"})

    def test_income_tax_bucket_drift_is_rejected(self):
        policy = SimpleNamespace(soi_iitax=[True])
        with self.assertRaisesRegex(RuntimeError, "soi_iitax"):
            builder.validate_policy_assumptions(policy)

    def test_unequal_fica_shares_are_rejected(self):
        policy = SimpleNamespace(
            soi_iitax=[False],
            FICA_ss_trt_employer=[0.062],
            FICA_ss_trt_employee=[0.061],
            FICA_mc_trt_employer=[0.0145],
            FICA_mc_trt_employee=[0.0145],
        )
        with self.assertRaisesRegex(RuntimeError, "FICA_ss"):
            builder.validate_policy_assumptions(policy)

    def test_json_output_does_not_overwrite_an_existing_file(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "reference.json"
            builder.write_reference(output, {"source": "first"})
            with self.assertRaises(FileExistsError):
                builder.write_reference(output, {"source": "second"})
            self.assertEqual(json.loads(output.read_text()), {"source": "first"})

    def test_output_rejects_a_yaml_path(self):
        with self.assertRaisesRegex(ValueError, "JSON"):
            builder.write_reference(Path("nonexistent-reference.yaml"), {})


if __name__ == "__main__":
    unittest.main()

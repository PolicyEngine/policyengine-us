"""Generate 60 independent federal tax reference cases, every year 2017-2026.

Run this file directly in an isolated environment containing Tax-Calculator 6.9.1.
It imports no PolicyEngine runtime and writes only to an explicit new JSON file.
Tax-Calculator's exact mode preserves statutory steps; it does not reproduce
every IRS tax-table or filing-rounding convention. The 2020-2021 credits represent
annual entitlement rather than a filing balance net of advance payments.
"""

import argparse
import hashlib
import importlib.metadata
import json
import platform
from pathlib import Path


TAXCALC_VERSION = "6.9.1"
YEARS = tuple(range(2017, 2027))
ORIGINAL_YEARS = (2017, 2018, 2021, 2026)
LEGACY_REFERENCE_SHA256 = (
    "4c224c18070c060a58cf7000deb75bef08ae0e3cf52466aeab212cc22f002c9f"
)
TAXCALC_SOURCE_HASHES = {
    "records.py": "6ca49df37ea153403ed00dfc8afae7e24ed7b832ecbcff63a72397a61c35f697",
    "calculator.py": "e869a26948b5c9f4ecfa717280b48ac003cc0fa9e7bd7f64ec4ca6231b742715",
    "calcfunctions.py": "bfee8b802307cc7c613a0e74943b3a8a0316448950ac7794d5c4dea06fc33ff8",
    "policy_current_law.json": (
        "80f97af457e05f30d94667cf4c0089a950efcced6f300f04912471035b50d2cc"
    ),
    "records_variables.json": (
        "a123615110212c5c3679b04e7d5813a6eff8356b37d1a89b59f3b5ddd5b72f15"
    ),
}
CASES = [
    {"id": "single_wages", "status": "SINGLE", "wages": [40_000], "children": []},
    {
        "id": "parent_eitc",
        "status": "HEAD_OF_HOUSEHOLD",
        "wages": [20_000],
        "children": [8],
    },
    {
        "id": "joint_children",
        "status": "JOINT",
        "wages": [40_000, 0],
        "children": [8, 12],
    },
    {
        "id": "joint_ctc_phaseout",
        "status": "JOINT",
        "wages": [120_001, 0],
        "children": [8, 12],
    },
    {
        "id": "single_exemption_phaseout",
        "status": "SINGLE",
        "wages": [300_001],
        "children": [],
    },
    {
        "id": "joint_two_earners",
        "status": "JOINT",
        "wages": [35_000, 35_000],
        "children": [8, 12],
    },
]
MARS = {"SINGLE": 1, "JOINT": 2, "HEAD_OF_HOUSEHOLD": 4}
FIELDS = {
    "adjusted_gross_income": "c00100",
    "standard_deduction": "standard",
    "exemptions": "c04600",
    "taxable_income": "c04800",
    "income_tax_before_credits": "c05800",
    "eitc": "eitc",
    "income_tax": "iitax",
}


def sha256(data: bytes) -> str:
    """Return a lowercase digest of source or serialized reference bytes."""
    return hashlib.sha256(data).hexdigest()


def validate_version(actual: str) -> None:
    """Reject another oracle version before performing calculations."""
    if actual != TAXCALC_VERSION:
        raise RuntimeError(f"Requires Tax-Calculator {TAXCALC_VERSION}; found {actual}")


def validate_years(years) -> None:
    """Reject gaps, duplicates, reordering, or changed coverage endpoints."""
    if tuple(years) != tuple(range(2017, 2027)):
        raise RuntimeError("Reference requires every year 2017 through 2026 in order")


def original_reference_subset(reference: dict) -> dict:
    """Retain the original 24-case reference for its unchanged-byte check."""
    return {
        **{key: value for key, value in reference.items() if key != "provenance"},
        "years": {str(year): reference["years"][str(year)] for year in ORIGINAL_YEARS},
    }


def verify_source_hashes(root: Path, expected: dict[str, str]) -> dict[str, str]:
    """Reject modifications to the pinned oracle's relevant source files."""
    observed = {}
    for name, digest in expected.items():
        observed[name] = sha256((root / name).read_bytes())
        if observed[name] != digest:
            raise RuntimeError(
                f"Tax-Calculator source differs from the reference: {name}"
            )
    return observed


def validate_policy_assumptions(policy) -> None:
    """Check the income-tax bucket and equal FICA shares used by this mapping."""
    if list(policy.soi_iitax) != [False]:
        raise RuntimeError("Reference requires soi_iitax=False")
    for component in ("FICA_ss", "FICA_mc"):
        employer = list(getattr(policy, f"{component}_trt_employer"))
        employee = list(getattr(policy, f"{component}_trt_employee"))
        if employer != employee:
            raise RuntimeError(
                f"Reference requires equal {component} employer/employee rates"
            )


def record_inputs(year: int) -> list[dict]:
    """Describe each synthetic filing unit in Tax-Calculator input variables."""
    rows = []
    for index, case in enumerate(CASES):
        adults, children = len(case["wages"]), len(case["children"])
        rows.append(
            {
                "RECID": index + 1,
                "MARS": MARS[case["status"]],
                "FLPDYR": year,
                "XTOT": adults + children,
                "e00200": sum(case["wages"]),
                "e00200p": case["wages"][0],
                "e00200s": case["wages"][-1] if adults == 2 else 0,
                "n24": children,
                "EIC": children,
                "nu18": children,
                "n21": adults,
                "age_head": 35,
                "age_spouse": 33 if adults == 2 else 0,
            }
        )
    return rows


def generate_reference() -> dict:
    """Run the pinned external oracle for every specified case and year."""
    validate_years(YEARS)
    version = importlib.metadata.version("taxcalc")
    validate_version(version)
    distribution = importlib.metadata.distribution("taxcalc")
    sources = verify_source_hashes(
        Path(distribution.locate_file("taxcalc")), TAXCALC_SOURCE_HASHES
    )

    import pandas as pd
    from taxcalc import Calculator, Policy, Records

    output = {
        "taxcalc_version": version,
        "exact_calculations": True,
        "start_year_equals_policy_year": True,
        "no_aging_or_microdata": True,
        "full_credit_takeup": True,
        "employee_payroll_mapping": "ptax_was / 2 + ptax_amc; wages-only records",
        "cases": CASES,
        "years": {},
    }
    inputs = {}
    for year in YEARS:
        rows = record_inputs(year)
        inputs[str(year)] = rows
        records = Records(
            data=pd.DataFrame(rows),
            start_year=year,
            gfactors=None,
            weights=None,
            adjust_ratios=None,
            exact_calculations=True,
        )
        records.credit_claim_urn[:] = 0
        if not all(value == 1 for value in records.exact):
            raise RuntimeError("Tax-Calculator did not enable exact statutory steps")
        policy = Policy()
        policy.set_year(year)
        validate_policy_assumptions(policy)
        calc = Calculator(policy=policy, records=records)
        if calc.current_year != year or records.current_year != year:
            raise RuntimeError("Reference policy and record years must match")
        if not all(value == 0 for value in calc.array("credit_claim_urn")):
            raise RuntimeError("Reference requires full eligible-credit receipt")
        calc.calc_all()
        result = {}
        for index, case in enumerate(CASES):
            result[case["id"]] = {
                name: float(calc.array(source)[index])
                for name, source in FIELDS.items()
            }
            # Ordinary wage FICA includes both halves; Additional Medicare
            # is employee-only. There are no self-employment or state taxes.
            result[case["id"]]["employee_payroll_tax"] = float(
                calc.array("ptax_was")[index] / 2 + calc.array("ptax_amc")[index]
            )
        output["years"][str(year)] = result

    legacy_digest = sha256(
        (json.dumps(original_reference_subset(output), indent=2) + "\n").encode()
    )
    if legacy_digest != LEGACY_REFERENCE_SHA256:
        raise RuntimeError(
            "Oracle inputs/results differ from the archived reference; "
            f"expected {LEGACY_REFERENCE_SHA256}, found {legacy_digest}"
        )
    output["provenance"] = {
        "generator_source_sha256": sha256(Path(__file__).read_bytes()),
        "taxcalc_source_sha256": sources,
        "legacy_reference_sha256": legacy_digest,
        "legacy_reference_years": list(ORIGINAL_YEARS),
        "reference_years": list(YEARS),
        "contiguous_years": True,
        "reference_without_provenance_sha256": sha256(
            (json.dumps(output, indent=2) + "\n").encode()
        ),
        "versions": {
            "python": platform.python_version(),
            **{
                name: importlib.metadata.version(name)
                for name in ("taxcalc", "pandas", "numpy", "numba")
            },
        },
        "taxcalc_record_inputs_by_year": inputs,
        "soi_iitax": False,
        "credit_claim_urn": 0,
        "record_arguments": {
            "gfactors": None,
            "weights": None,
            "adjust_ratios": None,
            "exact_calculations": True,
        },
        "scope": (
            "Wages-only hypothetical filing units; annual credit entitlements; "
            "unsmoothed statutory steps and rate schedules, not every IRS "
            "tax-table or filing-rounding convention. No survey records."
        ),
    }
    return output


def write_reference(output: Path, reference: dict) -> None:
    """Write a new explicit JSON artifact without replacing existing files."""
    if output.suffix.lower() != ".json":
        raise ValueError("Reference output must use a .json extension (JSON only)")
    with output.open("x") as handle:
        handle.write(json.dumps(reference, indent=2) + "\n")


def main() -> None:
    """Expose the standalone generator without modifying committed YAML tests."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    if args.output.suffix.lower() != ".json":
        parser.error("--output must use a .json extension")
    if args.output.exists():
        parser.error("--output must name a new file")
    try:
        reference = generate_reference()
        write_reference(args.output, reference)
    except (RuntimeError, OSError, importlib.metadata.PackageNotFoundError) as error:
        parser.exit(1, f"{error}\n")
    print(
        json.dumps(
            {
                "taxcalc_version": TAXCALC_VERSION,
                "cases": len(CASES) * len(YEARS),
                "years": list(YEARS),
                "sha256": sha256(args.output.read_bytes()),
                "legacy_reference_sha256": LEGACY_REFERENCE_SHA256,
            }
        )
    )


if __name__ == "__main__":
    main()

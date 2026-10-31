"""Audit stored sources before scoring Social Security benefit reforms.

This reads HDF metadata, not calculated simulation outputs.  A receipt applies
only to the exact bytes it hashes.  It is deliberately a separate scoring
preflight: household situations may still supply final benefit overrides.
"""

import argparse
from collections import Counter
from collections.abc import Iterable
from hashlib import sha256
import json
from pathlib import Path

import pandas as pd


CERTIFIED_ARTIFACT = (
    "hf://datasets/policyengine/populace-us/populace_us_2024.h5"
    "@populace-us-2024-spm-20260909"
)
CERTIFIED_YEAR = 2024
CERTIFIED_SHA256 = "6496cc4393d4d3c6574f76eca231de5898c803b9067645591fd5c4d3e65aee84"
COMPONENTS = (
    "social_security_retirement",
    "social_security_disability",
    "social_security_survivors",
    "social_security_dependents",
)
CALCULATED_BENEFIT_LEAVES = frozenset(
    {
        "social_security",
        "social_security_across_the_board_factor",
        "social_security_payable_factor",
    }
    | {
        f"{component}_{suffix}"
        for component in COMPONENTS
        for suffix in (
            "base",
            "joint_cola_factor",
            "pia_ratio_factor",
            "payable_factor",
        )
    }
)
CALCULATED_TAX_LEAVES = frozenset(
    (
        "employee_social_security_tax",
        "employer_social_security_tax",
        "self_employment_social_security_tax",
        "employer_total_social_security_tax",
        "net_investment_income_tax",
        "niit",
        "oasdi_payroll_tax_revenue",
        "oasdi_benefit_taxation_revenue",
        "oasdi_niit_revenue",
        "oasdi_income",
        "oasdi_cost",
        "oasdi_modeled_balance",
    )
)


def _is_calculated_tax_leaf(name: str) -> bool:
    # Include later NIIT and TOB revenue variants without rejecting source
    # inputs such as net investment income or a supplied NIIT income basis.
    # The S.770 section 8 and owners' draw tax and OASDI transfer leaves feed
    # the OASDI accounting outputs; their classification hooks remain inputs.
    return (
        name in CALCULATED_TAX_LEAVES
        or name.startswith("tob_revenue_")
        or name.startswith("net_investment_income_tax_")
        or name.startswith("niit_liability")
        or name.startswith("niit_revenue")
        or name.endswith("_niit_revenue")
        or (
            name.startswith(("s770_", "owners_draw_"))
            and name.endswith(("_tax", "_revenue_oasdi"))
        )
    )


def _file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def preflight_social_security_dataset(
    file_path: str | Path,
    *,
    artifact: str = CERTIFIED_ARTIFACT,
    expected_year: int = CERTIFIED_YEAR,
    expected_sha256: str = CERTIFIED_SHA256,
    projection_end_year: int = 2035,
    intentional_final_overrides: Iterable[str] = (),
) -> dict:
    """Validate a single-year stored H5 artifact and return a JSON receipt.

    Alternative artifacts must supply their own artifact URI, base year and
    expected SHA256.  Each component may be stored under its original name
    (which the PE-US constructor migrates) or its pure ``_reported`` name.
    Storing both is rejected because that preserves a final public override.

    Projection must use ``extend_single_year_dataset`` through the recorded
    end year.  Its rows are independent annual cross-sections: integer-age
    retirement eligibility is inferred afresh as ``year - age + 62``, subject
    to a one-year birthday ambiguity.  This receipt does not turn projected
    rows into a longitudinal entitlement or income history.
    """
    path = Path(file_path)
    if not artifact or not expected_sha256:
        raise ValueError("An artifact identity and expected SHA256 are required.")
    if artifact == CERTIFIED_ARTIFACT and (
        expected_year != CERTIFIED_YEAR or expected_sha256.lower() != CERTIFIED_SHA256
    ):
        raise ValueError(
            "The certified artifact's year and SHA256 pins cannot be changed; "
            "identify an alternative artifact for an alternative audit."
        )
    if projection_end_year < expected_year:
        raise ValueError("The projection end year precedes the base year.")
    actual_sha256 = _file_sha256(path)
    if actual_sha256 != expected_sha256.lower():
        raise ValueError(
            f"Dataset SHA256 mismatch: expected {expected_sha256}, got {actual_sha256}."
        )

    columns_by_entity = {}
    row_counts = {}
    entities = ("person", "household", "tax_unit", "spm_unit", "family", "marital_unit")
    with pd.HDFStore(path, mode="r") as store:
        keys = set(store.keys())
        if "/_time_period" not in keys:
            raise ValueError("Dataset must store its base year in _time_period.")
        stored_years = store["_time_period"].tolist()
        if stored_years != [expected_year]:
            raise ValueError(
                f"Dataset base year mismatch: expected {expected_year}, "
                f"got {stored_years}."
            )
        unknown = keys - {"/_time_period"} - {f"/{entity}" for entity in entities}
        if unknown:
            raise ValueError(f"Unexpected stored H5 keys: {sorted(unknown)}.")
        for entity in entities:
            key = f"/{entity}"
            if key not in keys:
                if entity in ("person", "household", "tax_unit"):
                    raise ValueError(f"Dataset is missing required entity {entity}.")
                continue
            storer = store.get_storer(key)
            if storer.is_table:
                columns = list(storer.non_index_axes[0][1])
                row_counts[entity] = int(storer.nrows)
            else:
                # Fixed-format H5 stores column labels separately; slicing an
                # empty frame reads the labels without materializing rows.
                columns = list(store.select(key, start=0, stop=0).columns)
                row_counts[entity] = int(storer.shape[0])
            columns_by_entity[entity] = sorted(columns)

    all_columns = [
        column for columns in columns_by_entity.values() for column in columns
    ]
    duplicate_columns = sorted(
        name for name, count in Counter(all_columns).items() if count > 1
    )
    if duplicate_columns:
        raise ValueError(f"Columns appear more than once: {duplicate_columns}.")
    stored_columns = set(all_columns)
    bypasses = sorted(
        name
        for name in stored_columns
        if name in CALCULATED_BENEFIT_LEAVES or _is_calculated_tax_leaf(name)
    )
    if bypasses:
        raise ValueError(
            f"Stored calculated outputs bypass reform formulas: {bypasses}."
        )

    source_mapping = {}
    person_columns = set(columns_by_entity["person"])
    for public_name in COMPONENTS:
        source_name = f"{public_name}_reported"
        candidates = person_columns & {public_name, source_name}
        if len(candidates) != 1:
            raise ValueError(
                f"Store exactly one Person source for {public_name}: "
                f"{public_name} or {source_name}; found {sorted(candidates)}."
            )
        stored_name = next(iter(candidates))
        source_mapping[stored_name] = source_name

    overrides = sorted(set(intentional_final_overrides))
    forbidden_overrides = sorted(
        name
        for name in overrides
        if name in CALCULATED_BENEFIT_LEAVES
        or name in COMPONENTS
        or _is_calculated_tax_leaf(name)
    )
    if forbidden_overrides:
        raise ValueError(
            "Population scoring cannot use final benefit or tax overrides: "
            f"{forbidden_overrides}."
        )

    return {
        "artifact": artifact,
        "sha256": actual_sha256,
        "base_year": expected_year,
        "stored_h5_keys": sorted(keys),
        "stored_columns": sorted(stored_columns),
        "stored_column_count": len(stored_columns),
        "columns_by_entity": columns_by_entity,
        "row_counts": row_counts,
        "source_mapping": source_mapping,
        "intentional_final_overrides": overrides,
        "projection": {
            "method": "extend_single_year_dataset",
            "end_year": projection_end_year,
            "population": "independent annual cross-sections",
            "retirement_eligibility_proxy": "payment_year - age + 62",
            "integer_age_uncertainty_years": 1,
            "carry_inferred_history_across_years": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file_path", type=Path)
    parser.add_argument("--artifact", default=CERTIFIED_ARTIFACT)
    parser.add_argument("--year", type=int, default=CERTIFIED_YEAR)
    parser.add_argument("--sha256", default=CERTIFIED_SHA256)
    parser.add_argument("--projection-end-year", type=int, default=2035)
    args = parser.parse_args()
    receipt = preflight_social_security_dataset(
        args.file_path,
        artifact=args.artifact,
        expected_year=args.year,
        expected_sha256=args.sha256,
        projection_end_year=args.projection_end_year,
    )
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

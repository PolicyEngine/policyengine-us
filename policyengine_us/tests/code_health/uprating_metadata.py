"""
Test that parameters with annual updates have proper uprating metadata.

This test detects parameters that have been manually updated for 3+ consecutive years
with inflation-like growth rates (0-10%) but are missing uprating metadata.
"""

from policyengine_us.model_api import REPO
from policyengine_us.tools.detect_missing_uprating import (
    detect_missing_uprating,
)
from policyengine_us.tools.uprating_config import EXCLUSIONS


def test_parameters_with_annual_updates_have_uprating_metadata():
    """
    Detect parameters that have been updated annually for 3+ consecutive years
    with growth rates consistent with inflation (0-10%/year), but lack uprating metadata.

    This catches cases where:
    - Parameters are being manually updated every year
    - Growth rates suggest inflation adjustment (not policy changes)
    - Missing automation via 'uprating:' metadata

    Exclusions are configured in: policyengine_us/tools/uprating_config.py
    """
    parameters_dir = REPO / "parameters"

    findings_by_file = detect_missing_uprating(parameters_dir, verbose=False)

    if not findings_by_file:
        # All good!
        return

    # Build detailed error message
    errors = []
    total_params = sum(len(findings) for findings in findings_by_file.values())

    errors.append(
        f"\nFound {total_params} parameters in {len(findings_by_file)} files "
        "with annual updates but missing uprating metadata.\n"
    )

    # Sort by number of years (highest priority first)
    sorted_files = sorted(
        findings_by_file.items(),
        key=lambda x: max(len(f["years"]) for f in x[1]),
        reverse=True,
    )

    for rel_path, file_findings in sorted_files[:10]:  # Show top 10
        max_years = max(len(f["years"]) for f in file_findings)
        min_year = min(min(f["years"]) for f in file_findings if f["years"])
        max_year = max(max(f["years"]) for f in file_findings if f["years"])

        growth_rates = [
            f.get("avg_growth")
            for f in file_findings
            if f.get("avg_growth") is not None
        ]
        avg_growth = (
            sum(growth_rates) / len(growth_rates) if growth_rates else None
        )

        years_str = f"{min_year}-{max_year} ({max_years} years)"
        growth_str = (
            f", avg growth: {avg_growth:.2%}/year" if avg_growth else ""
        )

        errors.append(f"\n  • {rel_path}")
        errors.append(f"    {years_str}{growth_str}")
        if len(file_findings) > 1:
            errors.append(
                f"    {len(file_findings)} parameters in this file"
            )

    if len(findings_by_file) > 10:
        errors.append(
            f"\n  ... and {len(findings_by_file) - 10} more files"
        )

    errors.append(
        "\n\nTo fix: Add 'uprating:' metadata to these parameters or exclude them "
        "if they are uprating source data.\n"
    )

    assert False, "".join(errors)

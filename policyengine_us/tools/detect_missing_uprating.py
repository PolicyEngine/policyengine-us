#!/usr/bin/env python3
"""
Detects parameters that should have uprating metadata but don't.

Logic: If a parameter has been updated annually for 3+ consecutive years,
it should have automated uprating.
"""

import yaml
from pathlib import Path
from datetime import date


def load_yaml_safe(file_path):
    """Load YAML file safely."""
    try:
        with open(file_path, "r") as f:
            return yaml.safe_load(f)
    except Exception:
        # Silently skip files that can't be loaded
        return None


def check_time_series(
    data,
    current_year=2025,
    debug_file=None,
    min_growth_rate=None,
    max_growth_rate=None,
):
    """
    Check if parameter has values for 3+ consecutive recent years with growth rates consistent with inflation.

    Args:
        data: Dictionary to check
        current_year: Current year for filtering
        debug_file: Enable debug output
        min_growth_rate: Minimum YoY growth rate (default from config)
        max_growth_rate: Maximum YoY growth rate (default from config)

    Returns (has_pattern, years_found, has_uprating_metadata, avg_growth_rate)
    """
    if not isinstance(data, dict):
        return False, [], False, None

    # Import config defaults if not provided
    if min_growth_rate is None or max_growth_rate is None:
        from policyengine_us.tools.uprating_config import (
            MIN_GROWTH_RATE,
            MAX_GROWTH_RATE,
        )

        if min_growth_rate is None:
            min_growth_rate = MIN_GROWTH_RATE
        if max_growth_rate is None:
            max_growth_rate = MAX_GROWTH_RATE

    # Check if this level has uprating metadata
    has_uprating = (
        "uprating" in data
        or "metadata" in data
        and isinstance(data.get("metadata"), dict)
        and "uprating" in data.get("metadata", {})
    )

    # Look for year-based keys (int, string, or date objects)
    year_keys = []
    date_keys_found = 0
    for key in data.keys():
        year = None
        # Try date object (YAML parses "2013-01-01" as datetime.date)
        if isinstance(key, date):
            year = key.year
            date_keys_found += 1
        # Try integer key
        elif isinstance(key, int):
            year = key
        # Try string key (might be "2013" or "2013-01-01")
        elif isinstance(key, str):
            # Extract year from date format or plain year
            if "-" in key:
                # Date format like "2013-01-01"
                try:
                    year = int(key.split("-")[0])
                except (ValueError, TypeError, IndexError):
                    pass
            elif key.isdigit():
                # Plain year format like "2013"
                try:
                    year = int(key)
                except (ValueError, TypeError):
                    pass

        if year and 2000 <= year <= current_year:
            year_keys.append(year)

    if debug_file and date_keys_found > 0:
        print(
            f"DEBUG check_time_series: found {date_keys_found} date keys, {len(year_keys)} valid years"
        )

    if len(year_keys) >= 3:
        year_keys.sort()

        # Check for consecutive years in recent history
        # Look for 3+ consecutive years
        for i in range(len(year_keys) - 2):
            if (
                year_keys[i + 1] == year_keys[i] + 1
                and year_keys[i + 2] == year_keys[i] + 2
            ):
                # Found 3 consecutive years
                # Get values for these years
                vals = []
                years_with_vals = []
                for target_year in year_keys[i : i + 3]:
                    for key, value in data.items():
                        key_year = None
                        if isinstance(key, date):
                            key_year = key.year
                        elif isinstance(key, int):
                            key_year = key
                        elif isinstance(key, str) and key.isdigit():
                            key_year = int(key)
                        elif isinstance(key, str) and "-" in key:
                            try:
                                key_year = int(key.split("-")[0])
                            except:
                                pass

                        if key_year == target_year:
                            vals.append(value)
                            years_with_vals.append(target_year)
                            break

                if (
                    len(vals) >= 3 and len(set(str(v) for v in vals)) > 1
                ):  # At least 2 different values
                    # Calculate year-over-year growth rates
                    try:
                        growth_rates = []
                        for j in range(len(vals) - 1):
                            val1 = float(vals[j])
                            val2 = float(vals[j + 1])
                            if val1 > 0:  # Avoid division by zero
                                growth_rate = (val2 - val1) / val1
                                growth_rates.append(growth_rate)

                        if growth_rates:
                            avg_growth = sum(growth_rates) / len(growth_rates)

                            # Check if growth rates are within inflation range
                            all_within_range = all(
                                min_growth_rate <= gr <= max_growth_rate
                                for gr in growth_rates
                            )

                            if all_within_range:
                                return (
                                    True,
                                    year_keys,
                                    has_uprating,
                                    avg_growth,
                                )
                    except (ValueError, TypeError, ZeroDivisionError):
                        # If we can't calculate growth rates, skip this parameter
                        pass

    return False, year_keys, has_uprating, None


def scan_parameter_file(file_path, current_year=2025, verbose=False):
    """Scan a parameter file for missing uprating metadata."""
    data = load_yaml_safe(file_path)
    if not data:
        return []

    findings = []
    debug = verbose  # Enable detailed debugging

    def recurse(obj, path="", parent_has_uprating=False):
        """Recursively check all levels of the parameter tree."""
        if not isinstance(obj, dict):
            return

        has_pattern, years, has_uprating, avg_growth = check_time_series(
            obj, current_year, debug_file=debug
        )

        if debug and has_pattern:
            print(
                f"DEBUG: {path or 'ROOT'} - pattern={has_pattern}, years={len(years)}, has_uprating={has_uprating}, parent={parent_has_uprating}, avg_growth={avg_growth:.2%}"
                if avg_growth
                else f"DEBUG: {path or 'ROOT'} - pattern={has_pattern}, years={len(years)}, has_uprating={has_uprating}, parent={parent_has_uprating}"
            )

        # Check if parent or current level has uprating
        has_any_uprating = has_uprating or parent_has_uprating

        if has_pattern and not has_any_uprating:
            findings.append(
                {
                    "path": path,
                    "years": years,
                    "file": str(file_path),
                    "avg_growth": avg_growth,
                }
            )
            if verbose:
                growth_str = (
                    f" (avg growth: {avg_growth:.2%})" if avg_growth else ""
                )
                print(
                    f"Found: {file_path} @ {path} - {len(years)} years{growth_str}"
                )

        # Recurse into nested structures
        for key, value in obj.items():
            # Skip metadata keys
            if key in [
                "metadata",
                "uprating",
                "description",
                "unit",
                "reference",
            ]:
                continue
            # Don't recurse into date keys (they hold values, not structure)
            if isinstance(key, date):
                continue
            # Don't recurse into large integer keys that represent years
            if isinstance(key, int) and key >= 1900:
                continue
            # Recurse into dict values
            if isinstance(value, dict):
                new_path = f"{path}.{key}" if path else str(key)
                recurse(value, new_path, has_any_uprating)

    recurse(data)
    return findings


def detect_missing_uprating(parameters_dir, verbose=False, exclusions=None):
    """
    Detect parameters with annual updates but missing uprating metadata.

    Args:
        parameters_dir: Path to parameters directory
        verbose: Enable verbose output
        exclusions: List of file patterns to exclude (default from config)

    Returns:
        Dictionary mapping file paths to list of findings
    """
    if exclusions is None:
        from policyengine_us.tools.uprating_config import EXCLUSIONS

        exclusions = EXCLUSIONS

    all_findings = []

    # Scan all YAML files
    for yaml_file in Path(parameters_dir).rglob("*.yaml"):
        # Check exclusions
        rel_path = str(yaml_file).replace(str(parameters_dir) + "/", "")
        if any(excl in rel_path for excl in exclusions):
            if verbose:
                print(f"Skipping excluded: {rel_path}")
            continue

        findings = scan_parameter_file(yaml_file, verbose=verbose)
        all_findings.extend(findings)

    # Group findings by file
    from collections import defaultdict

    findings_by_file = defaultdict(list)
    for finding in all_findings:
        rel_path = finding["file"].replace(str(parameters_dir) + "/", "")
        findings_by_file[rel_path].append(finding)

    return findings_by_file


def main(verbose=False):
    """Main function to scan all parameter files."""
    import sys

    verbose = "--verbose" in sys.argv or "-v" in sys.argv

    parameters_dir = Path(
        "/Users/pavelmakarchuk/policyengine-us/policyengine_us/parameters"
    )

    if not parameters_dir.exists():
        print(f"Error: Parameters directory not found at {parameters_dir}")
        return

    print(
        "Scanning for parameters with annual updates but missing uprating metadata...\n"
    )

    findings_by_file = detect_missing_uprating(parameters_dir, verbose=verbose)

    # Report findings
    if not findings_by_file:
        print(
            "✓ No issues found - all annually-updated parameters have uprating metadata!"
        )
        return

    # Sort files by max years found in any parameter
    sorted_files = sorted(
        findings_by_file.items(),
        key=lambda x: max(len(f["years"]) for f in x[1]),
        reverse=True,
    )

    total_params = sum(len(findings) for findings in findings_by_file.values())
    total_files = len(findings_by_file)
    print(
        f"Found {total_params} parameters in {total_files} files that likely need uprating metadata:\n"
    )

    for rel_path, file_findings in sorted_files:
        # Get summary stats
        max_years = max(len(f["years"]) for f in file_findings)
        min_year = min(min(f["years"]) for f in file_findings if f["years"])
        max_year = max(max(f["years"]) for f in file_findings if f["years"])

        # Get average growth if available
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

        print(f"  • {rel_path}")
        print(f"    Years: {years_str}{growth_str}")
        if len(file_findings) > 1:
            print(
                f"    Parameters: {len(file_findings)} parameters in this file"
            )
        print()


if __name__ == "__main__":
    main()

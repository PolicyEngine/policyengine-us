from typing import Optional

import yaml

from policyengine_us.data.dataset_schema import (
    USSingleYearDataset,
    USMultiYearDataset,
)

# The default end year for dataset extension is derived at runtime from
# the CPI-U parameter YAML (gov.bls.cpi.cpi_u).  When the CPI-U YAML
# is updated with new projection years, datasets will automatically
# extend to match — no hardcoded year constant to maintain.
CPI_U_PARAM_PATH = "gov.bls.cpi.cpi_u"
DEFAULT_MICRODATA_UPRATING = (
    "calibration.gov.cbo.income_by_source.adjusted_gross_income"
)

MICRODATA_UPRATING_OVERRIDES = {
    "american_opportunity_credit": DEFAULT_MICRODATA_UPRATING,
    "cdcc_relevant_expenses": DEFAULT_MICRODATA_UPRATING,
    "employment_income": "calibration.gov.irs.soi.employment_income",
    "employment_income_last_year": "calibration.gov.irs.soi.employment_income",
    "energy_efficient_home_improvement_credit": DEFAULT_MICRODATA_UPRATING,
    "foreign_tax_credit": DEFAULT_MICRODATA_UPRATING,
    "interest_deduction": DEFAULT_MICRODATA_UPRATING,
    "long_term_capital_gains": "calibration.gov.irs.soi.long_term_capital_gains",
    "misc_deduction": DEFAULT_MICRODATA_UPRATING,
    "partnership_income": "calibration.gov.irs.soi.partnership_s_corp_income",
    "partnership_s_corp_income": "calibration.gov.irs.soi.partnership_s_corp_income",
    "partnership_self_employment_net_earnings": "calibration.gov.irs.soi.self_employment_income",
    "person_weight": "calibration.gov.census.populations.total",
    "pre_tax_contributions": DEFAULT_MICRODATA_UPRATING,
    "rent": "gov.bls.cpi.cpi_u",
    "savers_credit": DEFAULT_MICRODATA_UPRATING,
    "self_employment_income": "calibration.gov.irs.soi.self_employment_income",
    "self_employed_health_insurance_ald": DEFAULT_MICRODATA_UPRATING,
    "self_employed_pension_contribution_ald": DEFAULT_MICRODATA_UPRATING,
    "social_security": "calibration.gov.irs.soi.social_security",
    "s_corp_income": "calibration.gov.irs.soi.partnership_s_corp_income",
    "spm_unit_weight": "calibration.gov.census.populations.total",
    "spm_unit_spm_threshold": DEFAULT_MICRODATA_UPRATING,
    "state_and_local_sales_or_income_tax": DEFAULT_MICRODATA_UPRATING,
    "sstb_self_employment_income": "calibration.gov.irs.soi.self_employment_income",
    "taxable_pension_income": "calibration.gov.irs.soi.taxable_pension_income",
    "taxable_unemployment_compensation": DEFAULT_MICRODATA_UPRATING,
    "tax_unit_weight": "calibration.gov.census.populations.total",
    "tax_exempt_pension_income": DEFAULT_MICRODATA_UPRATING,
    "total_self_employment_income": "calibration.gov.irs.soi.self_employment_income",
}


def get_parameter_last_year(parameter) -> int:
    """Return the latest year explicitly defined in a parameter's YAML file.

    Reads the YAML source file (via ``parameter.file_path``), parses
    the ``values`` mapping, sorts its date keys chronologically, and
    returns the year component of the latest entry.

    This deliberately reads the YAML on disk rather than the runtime
    ``values_list``, because ``uprating_extensions.py`` programmatically
    extends many parameters to 2100 after loading — and we want the
    last *authored* year, not the extrapolated one.
    """
    with open(parameter.file_path) as f:
        data = yaml.safe_load(f)
    date_keys = sorted(str(k) for k in data.get("values", {}).keys())
    return int(date_keys[-1][:4])


def _get_default_end_year(system) -> int:
    """Derive the default end year from the CPI-U parameter's YAML."""
    cpi_u = _resolve_parameter(system.parameters, CPI_U_PARAM_PATH)
    return get_parameter_last_year(cpi_u)


def extend_single_year_dataset(
    dataset: USSingleYearDataset,
    end_year: Optional[int] = None,
    system=None,
) -> USMultiYearDataset:
    """Extend a single-year US dataset to multiple years via uprating.

    Builds a frame set for each year from the base year through
    ``end_year`` (shallow copies sharing base-year buffers under pandas
    copy-on-write; deep copies on pandas 2.x), then applies
    multiplicative uprating using growth factors derived from the
    policyengine-us parameter tree.

    If ``end_year`` is not provided, it defaults to the latest year
    covered by the CPI-U parameter (gov.bls.cpi.cpi_u).

    Variables without an uprating parameter are carried forward unchanged.
    """
    if system is None:
        from policyengine_us.system import system as _system

        system = _system

    if end_year is None:
        end_year = _get_default_end_year(system)

    start_year = int(dataset.time_period)
    if end_year < start_year:
        raise ValueError(
            f"end_year ({end_year}) must be >= dataset base year ({start_year})."
        )
    # Copy the base year too, so the returned multi-year dataset never
    # holds the caller's DataFrames directly. ``deep=False`` shares
    # base-year buffers under pandas copy-on-write and falls back to
    # deep copies on pandas 2.x — uprating's whole-column assignments
    # then materialize only the columns they replace.
    datasets = [dataset.copy(deep=False)]
    for year in range(start_year + 1, end_year + 1):
        next_year = dataset.copy(deep=False)
        next_year.time_period = str(year)
        datasets.append(next_year)

    multi_year_dataset = USMultiYearDataset(datasets=datasets)
    # Every year above is a private copy; no defensive copy needed.
    return _apply_uprating(multi_year_dataset, system=system, copy=False)


def _apply_uprating(
    dataset: USMultiYearDataset, system=None, copy: bool = True
) -> USMultiYearDataset:
    """Apply year-over-year uprating to all years in a multi-year dataset.

    With ``copy=False`` the input dataset is modified in place; callers
    passing datasets they own privately (like ``extend_single_year_dataset``)
    use this to skip a full defensive copy.
    """
    if system is None:
        from policyengine_us.system import system as _system

        system = _system

    if copy:
        dataset = dataset.copy()

    years = sorted(dataset.datasets.keys())
    for year in years:
        if year == years[0]:
            continue
        current = dataset.datasets[year]
        previous = dataset.datasets[year - 1]
        _apply_single_year_uprating(current, previous, system)

    return dataset


def _apply_single_year_uprating(current, previous, system):
    """Apply multiplicative uprating from previous year to current year.

    For each variable column in each entity DataFrame, looks up its
    dataset-extension uprating parameter path. Formula and adds/subtracts
    variables cannot use Core variable-level uprating, so their dataset-only
    upraters live in ``MICRODATA_UPRATING_OVERRIDES`` instead.

    Variables without an uprating parameter (or whose uprating parameter
    evaluates to 0 for the previous year) are left unchanged — they carry
    the base-year values forward (sharing base-year buffers under pandas
    copy-on-write; as independent deep copies on pandas 2.x).
    """
    current_year = int(current.time_period)
    previous_year = int(previous.time_period)
    current_period = f"{current_year}-01-01"
    previous_period = f"{previous_year}-01-01"

    for table_name, current_df, prev_df in zip(
        current.table_names, current.tables, previous.tables
    ):
        for col in current_df.columns:
            if col not in system.variables:
                continue
            var = system.variables[col]
            uprating_path = MICRODATA_UPRATING_OVERRIDES.get(col) or getattr(
                var, "uprating", None
            )
            if uprating_path is None:
                continue

            param = _resolve_parameter(system.parameters, uprating_path)
            if param is None:
                continue

            prev_val = param(previous_period)
            curr_val = param(current_period)
            if prev_val == 0:
                continue

            factor = curr_val / prev_val
            # Whole-column assignment is load-bearing: the year frames may
            # be shallow copies sharing base-year buffers (pandas
            # copy-on-write), and assignment replaces just this column in
            # just this year's frame, leaving the shared buffers intact.
            current_df[col] = prev_df[col] * factor


def _resolve_parameter(parameters, path):
    """Resolve a dotted parameter path like 'gov.bls.cpi.cpi_u'."""
    node = parameters
    for part in path.split("."):
        try:
            node = getattr(node, part)
        except AttributeError:
            return None
    return node

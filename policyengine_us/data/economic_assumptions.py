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

    Copies the base-year DataFrames for each year from the base year through
    ``end_year``, then applies multiplicative uprating using growth factors
    derived from the policyengine-us parameter tree.

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
    datasets = [dataset]
    for year in range(start_year + 1, end_year + 1):
        next_year = dataset.copy()
        next_year.time_period = str(year)
        datasets.append(next_year)

    multi_year_dataset = USMultiYearDataset(datasets=datasets)
    return _apply_uprating(multi_year_dataset, system=system)


def _apply_uprating(dataset: USMultiYearDataset, system=None) -> USMultiYearDataset:
    """Apply year-over-year uprating to all years in a multi-year dataset."""
    if system is None:
        from policyengine_us.system import system as _system

        system = _system

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

    For each variable column in each entity DataFrame, looks up the
    variable's uprating parameter path in ``system.variables``.  If the
    variable has an uprating parameter, computes the growth factor as
    ``param(current_year) / param(previous_year)`` and multiplies the
    column by that factor.

    Variables without an uprating parameter (or whose uprating parameter
    evaluates to 0 for the previous year) are left unchanged — they were
    already copied forward by ``dataset.copy()``.
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
            uprating_path = getattr(var, "uprating", None)
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

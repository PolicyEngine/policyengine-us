"""Uprate dollar inputs by per-capita growth rather than aggregate growth.

Household weights grow with total population
(``calibration.gov.census.populations.total``). A dollar input that also
grows with a national total, such as a CBO income projection or an IRS
Statistics of Income series, would count population growth twice: once in
the amount and once in the weight. Dividing each national total by
population makes the weighted total of the input track the national total.

For every national total that a variable uprates by, this module adds a
sibling parameter holding the total divided by population
(``<path>_per_capita``) and points the variable at it. Series that are
already per-person rates or price indices (CMS per-capita spending, CPI-U)
are left alone, as is the population series that uprates the weights.
"""

from policyengine_core.parameters import Parameter
from policyengine_core.parameters.operations.get_parameter import get_parameter
from policyengine_core.periods import instant

POPULATION_PATH = "calibration.gov.census.populations.total"
NATIONAL_TOTAL_PREFIX = "calibration.gov."
POPULATION_PREFIX = "calibration.gov.census.populations."
PER_CAPITA_MARKER = "per_capita"
PER_CAPITA_SUFFIX = "_per_capita"


def is_national_total_path(path: str | None) -> bool:
    """Whether an uprating parameter path names a national total.

    National totals live under ``calibration.gov``. Paths that already say
    ``per_capita`` and the population series itself are excluded.
    """
    if not path:
        return False
    return (
        path.startswith(NATIONAL_TOTAL_PREFIX)
        and not path.startswith(POPULATION_PREFIX)
        and PER_CAPITA_MARKER not in path
    )


def per_capita_path(path: str) -> str:
    return path + PER_CAPITA_SUFFIX


def _per_capita_values(total: Parameter, population: Parameter) -> dict[str, float]:
    """Total divided by population at every instant either series changes.

    Instants are limited to the span the total covers. After its last value
    the total is flat only because the projection ends, so the per-capita
    series is held flat there too and amounts per record stop changing.
    """
    total_instants = [entry.instant_str for entry in total.values_list]
    first, last = min(total_instants), max(total_instants)
    instants = set(total_instants) | {
        entry.instant_str
        for entry in population.values_list
        if first <= entry.instant_str <= last
    }
    values = {}
    for instant_str in sorted(instants):
        total_value = total(instant_str)
        population_value = population(instant_str)
        if total_value is None or not population_value:
            continue
        values[instant_str] = total_value / population_value
    return values


def _add_per_capita_parameter(parameters, path: str) -> None:
    total = get_parameter(parameters, path)
    population = get_parameter(parameters, POPULATION_PATH)
    parent_path, _, name = path.rpartition(".")
    parent = get_parameter(parameters, parent_path)
    sibling_name = name + PER_CAPITA_SUFFIX
    label = total.metadata.get("label", name)
    sibling = Parameter(
        per_capita_path(path),
        {
            "description": (
                f"{path} divided by {POPULATION_PATH}. PolicyEngine derives "
                "this series when it builds the tax-benefit system and uses "
                "it to uprate dollar inputs."
            ),
            "metadata": {
                "unit": total.metadata.get("unit", "currency-USD"),
                "label": f"{label} per capita",
                "economy": False,
                "household": False,
            },
            "values": _per_capita_values(total, population),
        },
    )
    # Rebuilding keeps the series in step with a reform that changed the
    # total or the population after an earlier build.
    if sibling_name in parent.children:
        del parent.children[sibling_name]
    parent.add_child(sibling_name, sibling)


def add_per_capita_uprating(system) -> None:
    """Point every variable that uprates by a national total at its
    per-capita sibling, building the sibling parameters as needed.

    Call this after reforms are applied, so a reform that changes a national
    total or the population series flows into the per-capita series.
    """
    from policyengine_us.data.economic_assumptions import (
        MICRODATA_UPRATING_OVERRIDES,
    )

    paths = {
        variable.uprating
        for variable in system.variables.values()
        if is_national_total_path(variable.uprating)
    }
    paths |= {
        path
        for path in MICRODATA_UPRATING_OVERRIDES.values()
        if is_national_total_path(path)
    }
    # A second call finds variables already pointing at per-capita series;
    # refresh those series from their totals as well.
    paths |= {
        variable.uprating[: -len(PER_CAPITA_SUFFIX)]
        for variable in system.variables.values()
        if variable.uprating
        and variable.uprating.startswith(NATIONAL_TOTAL_PREFIX)
        and variable.uprating.endswith(PER_CAPITA_SUFFIX)
        and _has_parameter(
            system.parameters, variable.uprating[: -len(PER_CAPITA_SUFFIX)]
        )
    }
    for path in sorted(paths):
        _add_per_capita_parameter(system.parameters, path)
    for variable in system.variables.values():
        if is_national_total_path(variable.uprating):
            variable.uprating = per_capita_path(variable.uprating)


def _has_parameter(parameters, path: str) -> bool:
    node = parameters
    for part in path.split("."):
        node = getattr(node, "children", {}).get(part)
        if node is None:
            return False
    return True


__all__ = [
    "POPULATION_PATH",
    "PER_CAPITA_SUFFIX",
    "add_per_capita_uprating",
    "is_national_total_path",
    "per_capita_path",
]

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

Parameters can follow a per-capita series too: a parameter whose ``uprating``
metadata names ``<national total>_per_capita`` gets that sibling built before
parameter uprating runs. Income thresholds projected this way keep pace with
the incomes they are compared against.
"""

import math

from policyengine_core.parameters import Parameter

POPULATION_PATH = "calibration.gov.census.populations.total"
# Families of national totals. A path elsewhere under ``calibration`` may be a
# state total or a head count, where national population is the wrong
# denominator, so those are rejected rather than guessed at.
NATIONAL_TOTAL_PREFIXES = (
    "calibration.gov.cbo.",
    "calibration.gov.irs.soi.",
)
CALIBRATION_PREFIX = "calibration."
PER_CAPITA_MARKER = "per_capita"
PER_CAPITA_SUFFIX = "_per_capita"
DERIVED_FROM = "derived_from"


def is_national_total_path(path: str | None) -> bool:
    """Whether an uprating parameter path names a national total."""
    if not path:
        return False
    return path.startswith(NATIONAL_TOTAL_PREFIXES) and PER_CAPITA_MARKER not in path


def per_capita_path(path: str) -> str:
    return path + PER_CAPITA_SUFFIX


def _is_unclassified_calibration_path(path: str | None) -> bool:
    """A ``calibration`` path this module cannot classify: not a national
    total, not already per capita, not the population series."""
    if not path or not path.startswith(CALIBRATION_PREFIX):
        return False
    return not (
        is_national_total_path(path)
        or PER_CAPITA_MARKER in path
        or path == POPULATION_PATH
    )


def _find(parameters, path: str):
    node = parameters
    for part in path.split("."):
        node = getattr(node, "children", {}).get(part)
        if node is None:
            return None
    return node


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
    total = _find(parameters, path)
    population = _find(parameters, POPULATION_PATH)
    if total is None or population is None:
        raise ValueError(
            f"Cannot build {per_capita_path(path)}: {path} or {POPULATION_PATH} "
            "is missing from the parameter tree."
        )
    parent_path, _, name = path.rpartition(".")
    parent = _find(parameters, parent_path)
    sibling_name = name + PER_CAPITA_SUFFIX
    existing = parent.children.get(sibling_name)
    if existing is not None and existing.metadata.get(DERIVED_FROM) != path:
        raise ValueError(
            f"{per_capita_path(path)} already exists and was not derived from "
            f"{path}. Rename one of them; PolicyEngine derives "
            f"<national total>{PER_CAPITA_SUFFIX} series itself."
        )
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
                DERIVED_FROM: path,
            },
            "values": _per_capita_values(total, population),
        },
    )
    if existing is not None:
        del parent.children[sibling_name]
    parent.add_child(sibling_name, sibling)
    # ``add_child`` leaves at-instant views built earlier without the child.
    parent.clear_parent_cache()


def _uprating_reference(parameter) -> str | None:
    meta = getattr(parameter, "metadata", {}).get("uprating")
    if isinstance(meta, dict):
        meta = meta.get("parameter")
    return meta if isinstance(meta, str) else None


def add_per_capita_parameters_for_parameter_uprating(parameters) -> None:
    """Build the per-capita series that parameters uprate by.

    Call this before parameter uprating runs. Only totals that are complete
    at that point qualify: a total that is itself extended by parameter
    uprating would be divided before its projection exists.
    """
    references = {
        reference
        for parameter in parameters.get_descendants()
        if (reference := _uprating_reference(parameter))
        and reference.endswith(PER_CAPITA_SUFFIX)
        and is_national_total_path(reference[: -len(PER_CAPITA_SUFFIX)])
        and _find(parameters, reference) is None
    }
    for reference in sorted(references):
        total_path = reference[: -len(PER_CAPITA_SUFFIX)]
        if _uprating_reference(_find(parameters, total_path)) is not None:
            raise ValueError(
                f"{reference} is used to uprate a parameter, but {total_path} "
                "is itself extended by parameter uprating, so it is incomplete "
                "when parameter uprating runs."
            )
        _add_per_capita_parameter(parameters, total_path)


def add_per_capita_uprating(system) -> None:
    """Point every variable that uprates by a national total at its
    per-capita sibling, building or refreshing the sibling parameters.

    Runs at the end of system init and again after every parameter reform, so
    a reform to a national total or to the population series reaches the
    series the variables uprate by.
    """
    from policyengine_us.data.economic_assumptions import (
        MICRODATA_UPRATING_OVERRIDES,
    )

    in_use = [variable.uprating for variable in system.variables.values()]
    in_use += list(MICRODATA_UPRATING_OVERRIDES.values())
    unclassified = sorted({p for p in in_use if _is_unclassified_calibration_path(p)})
    if unclassified:
        raise ValueError(
            f"Uprating paths {unclassified} are under 'calibration' but are not "
            f"in a national-total family {NATIONAL_TOTAL_PREFIXES}. Dividing a "
            "state total or a head count by national population would be "
            "wrong, so add the family explicitly if it is a national total."
        )

    totals = {path for path in in_use if is_national_total_path(path)}
    # Series derived earlier, by a previous call or for parameter uprating:
    # refresh them from their totals.
    for path in in_use:
        parameter = _find(system.parameters, path) if path else None
        derived_from = getattr(parameter, "metadata", {}).get(DERIVED_FROM)
        if derived_from:
            totals.add(derived_from)
    for path in sorted(totals):
        _add_per_capita_parameter(system.parameters, path)
    for variable in system.variables.values():
        if is_national_total_path(variable.uprating):
            variable.uprating = per_capita_path(variable.uprating)


def check_per_capita_series_is_current(parameters, total_path: str, period: str):
    """Raise if a derived series no longer equals its total over population.

    A parameter changed without going through ``modify_parameters`` leaves
    the derived series behind; uprating with it would silently ignore the
    change.
    """
    total = _find(parameters, total_path)
    population = _find(parameters, POPULATION_PATH)
    derived = _find(parameters, per_capita_path(total_path))
    if total is None or population is None or derived is None:
        return
    total_value, population_value = total(period), population(period)
    if total_value is None or not population_value:
        return
    expected = total_value / population_value
    if not math.isclose(derived(period), expected, rel_tol=1e-9):
        raise ValueError(
            f"{per_capita_path(total_path)} is out of date at {period}: "
            f"{derived(period)} against {expected}. A parameter changed "
            "outside modify_parameters; call add_per_capita_uprating(system)."
        )


__all__ = [
    "DERIVED_FROM",
    "NATIONAL_TOTAL_PREFIXES",
    "POPULATION_PATH",
    "PER_CAPITA_SUFFIX",
    "add_per_capita_parameters_for_parameter_uprating",
    "add_per_capita_uprating",
    "check_per_capita_series_is_current",
    "is_national_total_path",
    "per_capita_path",
]

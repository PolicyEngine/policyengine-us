from __future__ import annotations

import math
from typing import Any

from policyengine_us.model_api import Reform
from policyengine_us.reforms.ssa.trustees_2025 import (
    TRUSTEES_2025_NAWI_ASSUMPTION,
    apply_trustees_2025_economic_assumptions,
)


TRUSTEES_CORE_THRESHOLD_ASSUMPTION: dict[str, Any] = {
    "name": "trustees-2025-core-thresholds-v1",
    "description": (
        "Best-public Trustees tax-side approximation: keep Social Security "
        "benefit-tax thresholds fixed, but wage-index core ordinary federal "
        "tax thresholds after 2034 using the active NAWI path."
    ),
    "source": "SSA 2025 Trustees Report V.C.7",
    "start_year": 2035,
    "projection_base_year": 2026,
    "parameter_groups": [
        "ordinary_income_brackets",
        "standard_deduction",
        "aged_blind_standard_deduction",
        "capital_gains_thresholds",
        "amt_thresholds",
    ],
    "economic_assumption": TRUSTEES_2025_NAWI_ASSUMPTION["name"],
    "income_uprating_assumption": "trustees-2025-soi-income-nawi-v1",
    "not_default_current_law": True,
}


def _round_amount(amount: float, rounding: dict | None) -> float:
    if not rounding:
        return amount

    interval = float(rounding["interval"])
    rounding_type = rounding["type"]

    if rounding_type == "downwards":
        return math.floor(amount / interval) * interval
    if rounding_type == "nearest":
        return math.floor(amount / interval + 0.5) * interval

    raise ValueError(f"Unsupported rounding type: {rounding_type}")


def _uprating_parameter_name(parameter) -> str | None:
    metadata = getattr(parameter, "metadata", {})
    uprating = metadata.get("uprating")
    if isinstance(uprating, dict):
        return uprating.get("parameter")
    return uprating


def _get_parameter_by_name(parameters, name: str):
    current = parameters
    for part in name.split("."):
        current = getattr(current, part)
    return current


def _nawi_growth_for_tax_year(parameters, year: int) -> float:
    nawi = parameters.gov.ssa.nawi
    return float(nawi(f"{year - 1}-01-01")) / float(nawi(f"{year - 2}-01-01"))


def _iter_updatable_parameters(
    root,
    *,
    uprating_parameter: str | None = None,
) -> list:
    candidates = [root]
    if hasattr(root, "get_descendants"):
        candidates.extend(root.get_descendants())

    result = []
    for candidate in candidates:
        if candidate.__class__.__name__ != "Parameter":
            continue
        uprating_name = _uprating_parameter_name(candidate)
        if uprating_name is None:
            continue
        if uprating_parameter is not None and uprating_name != uprating_parameter:
            continue
        result.append(candidate)
    return result


def _apply_wage_growth_to_parameter(
    parameter,
    *,
    parameters,
    start_year: int,
    end_year: int,
    projection_base_year: int,
) -> None:
    metadata = getattr(parameter, "metadata", {})
    uprating = metadata.get("uprating")
    rounding = uprating.get("rounding") if isinstance(uprating, dict) else None
    uprating_name = _uprating_parameter_name(parameter)
    if uprating_name is None:
        return

    # Validate that the referenced default uprating parameter exists.
    _get_parameter_by_name(parameters, uprating_name)
    values_by_year = {}

    for year in range(projection_base_year + 1, start_year):
        values_by_year[year] = float(parameter(f"{year}-01-01"))

    for year in range(start_year, end_year + 1):
        if year - 1 in values_by_year:
            previous_value = values_by_year[year - 1]
        else:
            previous_value = float(parameter(f"{year - 1}-01-01"))
        updated_value = _round_amount(
            previous_value * _nawi_growth_for_tax_year(parameters, year),
            rounding,
        )
        values_by_year[year] = updated_value

    for year, value in values_by_year.items():
        parameter.update(
            period=f"year:{year}-01-01:1",
            value=value,
        )


def _core_threshold_roots(parameters) -> list:
    return [
        parameters.gov.irs.income.bracket.thresholds,
        parameters.gov.irs.deductions.standard.amount,
        parameters.gov.irs.deductions.standard.aged_or_blind.amount,
        parameters.gov.irs.capital_gains.thresholds,
        parameters.gov.irs.income.amt.brackets,
        parameters.gov.irs.income.amt.exemption.amount,
        parameters.gov.irs.income.amt.exemption.phase_out.start,
        parameters.gov.irs.income.amt.exemption.separate_limit,
    ]


def _parameters_have_long_run_projection(parameters, end_year: int) -> bool:
    parameter = parameters.gov.irs.income.bracket.thresholds.children["1"].SINGLE
    return any(
        value.instant_str == f"{end_year}-01-01" for value in parameter.values_list
    )


def create_trustees_core_thresholds_reform(
    *,
    start_year: int = 2035,
    end_year: int = 2100,
    projection_base_year: int = 2026,
) -> Reform:
    """Return a Trustees-style long-run tax-threshold assumption reform.

    This is an explicit scenario assumption, not default current law. It leaves
    Social Security benefit-tax thresholds unchanged and wage-indexes the core
    IRS thresholds used by the CRFB long-run TOB analysis from ``start_year``.
    """

    def modify_parameters(parameters):
        if not _parameters_have_long_run_projection(parameters, end_year):
            return parameters

        apply_trustees_2025_economic_assumptions(
            parameters,
            end_year=end_year,
        )

        seen = set()
        for root in _core_threshold_roots(parameters):
            for parameter in _iter_updatable_parameters(root):
                if parameter.name in seen:
                    continue
                seen.add(parameter.name)
                _apply_wage_growth_to_parameter(
                    parameter,
                    parameters=parameters,
                    start_year=start_year,
                    end_year=end_year,
                    projection_base_year=projection_base_year,
                )
        return parameters

    class reform(Reform):
        def apply(self):
            self.modify_parameters(modify_parameters)

    return reform


trustees_core_thresholds_reform = create_trustees_core_thresholds_reform()

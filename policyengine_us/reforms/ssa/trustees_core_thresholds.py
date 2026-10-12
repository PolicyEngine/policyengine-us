from __future__ import annotations

import math
from typing import Any

from policyengine_us.model_api import Reform


TRUSTEES_CORE_THRESHOLD_ASSUMPTION: dict[str, Any] = {
    "name": "trustees-2025-core-thresholds-v1",
    "description": (
        "Best-public Trustees tax-side approximation: keep Social Security "
        "benefit-tax thresholds fixed, but wage-index all federal income tax "
        "parameters that otherwise use IRS CPI uprating after 2034 using the "
        "active NAWI path."
    ),
    "source": "SSA 2025 Trustees Report V.C.7 and OACT email clarification, May 6, 2026",
    "start_year": 2035,
    "projection_base_year": 2026,
    "parameter_groups": [
        "all_gov_irs_uprating_parameters",
    ],
    "uprating_parameter": "gov.irs.uprating",
    "wage_index": "gov.ssa.nawi",
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

    base_value = float(parameter(f"{start_year - 1}-01-01"))
    base_nawi = float(parameters.gov.ssa.nawi(f"{start_year - 2}-01-01"))
    for year in range(start_year, end_year + 1):
        nawi_ratio = float(parameters.gov.ssa.nawi(f"{year - 1}-01-01")) / base_nawi
        updated_value = _round_amount(
            base_value * nawi_ratio,
            rounding,
        )
        values_by_year[year] = updated_value

    for year, value in values_by_year.items():
        parameter.update(
            period=f"year:{year}-01-01:1",
            value=value,
        )


def _federal_income_tax_roots(parameters) -> list:
    return [
        parameters.gov.irs,
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
    """Return a Trustees-style long-run federal tax assumption reform.

    This is an explicit scenario assumption, not default current law. It leaves
    Social Security benefit-tax thresholds unchanged and wage-indexes federal
    IRS parameters that otherwise use CPI-linked IRS uprating from
    ``start_year``.
    """

    def modify_parameters(parameters):
        if not _parameters_have_long_run_projection(parameters, end_year):
            return parameters

        seen = set()
        for root in _federal_income_tax_roots(parameters):
            for parameter in _iter_updatable_parameters(
                root,
                uprating_parameter=TRUSTEES_CORE_THRESHOLD_ASSUMPTION[
                    "uprating_parameter"
                ],
            ):
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

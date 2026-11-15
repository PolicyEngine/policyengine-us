from __future__ import annotations

import math
from typing import Any

from policyengine_core.periods import instant

from policyengine_us.model_api import Reform


TRUSTEES_CORE_THRESHOLD_ASSUMPTION: dict[str, Any] = {
    "name": "trustees-2025-core-thresholds-v1",
    "description": (
        "Best-public Trustees tax-side approximation: keep Social Security "
        "benefit-tax thresholds fixed, but wage-index all federal income tax "
        "parameters that otherwise use IRS CPI uprating after 2034 using the "
        "active NAWI path. Parameters that follow one of those, such as the "
        "joint standard deduction at twice the single amount, follow it onto "
        "the wage path. Amounts a statute indexes from a base amount, such "
        "as the head of household standard deduction, round their increase "
        "over that base, as the statute does."
    ),
    "source": "SSA 2025 Trustees Report V.C.7 and OACT email clarification, May 6, 2026",
    "start_year": 2035,
    "projection_base_year": 2026,
    "parameter_groups": [
        "all_gov_irs_uprating_parameters",
    ],
    "uprating_parameters": (
        "gov.irs.uprating",
        "gov.irs.indexing.c_cpi_u",
        "gov.irs.indexing.hsa_c_cpi_u",
    ),
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
    uprating_parameter: str | tuple[str, ...] | None = None,
) -> list:
    """Parameters under ``root`` whose uprating names ``uprating_parameter``.

    ``uprating_parameter`` takes one parameter name or a tuple of them; with
    ``None``, every parameter that names an uprating parameter qualifies.
    """
    if isinstance(uprating_parameter, str):
        uprating_parameter = (uprating_parameter,)
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
        if uprating_parameter is not None and uprating_name not in uprating_parameter:
            continue
        result.append(candidate)
    return result


def _statutory_base(parameter) -> float | None:
    """The base amount of a parameter on core's base-mode uprating, else None.

    That is ``uprating.base.value``, or the parameter's value at
    ``uprating.base.period`` when the block states no value.
    """
    uprating = getattr(parameter, "metadata", {}).get("uprating")
    if not isinstance(uprating, dict) or "base" not in uprating:
        return None
    base = uprating["base"]
    value = base.get("value")
    if value is None:
        value = parameter(instant(base["period"]))
    return float(value)


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
    statutory_base = _statutory_base(parameter)

    for year in range(projection_base_year + 1, start_year):
        values_by_year[year] = float(parameter(f"{year}-01-01"))

    base_value = float(parameter(f"{start_year - 1}-01-01"))
    base_nawi = float(parameters.gov.ssa.nawi(f"{start_year - 2}-01-01"))
    for year in range(start_year, end_year + 1):
        nawi_ratio = float(parameters.gov.ssa.nawi(f"{year - 1}-01-01")) / base_nawi
        if statutory_base is None:
            updated_value = _round_amount(
                base_value * nawi_ratio,
                rounding,
            )
        else:
            # The statute rounds the increase over its base amount, as
            # 63(c)(7)(B)(ii) does over the $23,625 head of household amount,
            # so the wage path keeps the base plus whole rounding steps.
            updated_value = statutory_base + _round_amount(
                base_value * nawi_ratio - statutory_base,
                rounding,
            )
        values_by_year[year] = updated_value

    for year, value in values_by_year.items():
        parameter.update(
            period=f"year:{year}-01-01:1",
            value=value,
        )


def _apply_leader_growth_to_follower(
    parameter,
    leader,
    *,
    start_year: int,
    end_year: int,
) -> None:
    """Re-uprate a follower from its wage-indexed leader, as core does.

    A follower names another parameter as its uprating index, as the joint
    standard deduction names the single amount. Core chains it from its
    last value by the leader's ratio and rounds it, so from ``start_year``
    the follower takes its ``start_year - 1`` value times the leader's
    growth since then.
    """
    uprating = parameter.metadata.get("uprating")
    rounding = uprating.get("rounding") if isinstance(uprating, dict) else None
    base_value = float(parameter(f"{start_year - 1}-01-01"))
    base_leader = float(leader(f"{start_year - 1}-01-01"))
    for year in range(start_year, end_year + 1):
        leader_ratio = float(leader(f"{year}-01-01")) / base_leader
        parameter.update(
            period=f"year:{year}-01-01:1",
            value=_round_amount(base_value * leader_ratio, rounding),
        )


def _federal_income_tax_roots(parameters) -> list:
    return [
        parameters.gov.irs,
    ]


def _wage_indexing_plan(parameters) -> list[tuple[Any, Any]]:
    """The parameters the reform re-projects, each with its leader.

    First every IRS parameter that uprates by one of the assumption's CPI
    indices, in tree order, with no leader; then each parameter that uprates
    by one of those, such as the joint standard deduction, which follows
    the single amount, with that leader; then their own followers, a
    generation at a time. A leader always comes before its followers.
    """
    plan = []
    seen = set()
    leaders = {}
    for root in _federal_income_tax_roots(parameters):
        for parameter in _iter_updatable_parameters(
            root,
            uprating_parameter=TRUSTEES_CORE_THRESHOLD_ASSUMPTION[
                "uprating_parameters"
            ],
        ):
            if parameter.name in seen:
                continue
            seen.add(parameter.name)
            plan.append((parameter, None))
            leaders[parameter.name] = parameter
    while leaders:
        followers = {}
        for root in _federal_income_tax_roots(parameters):
            for parameter in _iter_updatable_parameters(
                root, uprating_parameter=tuple(leaders)
            ):
                if parameter.name in seen:
                    continue
                seen.add(parameter.name)
                plan.append((parameter, leaders[_uprating_parameter_name(parameter)]))
                followers[parameter.name] = parameter
        leaders = followers
    return plan


def trustees_core_threshold_parameters(parameters) -> list:
    """Every parameter the Trustees core-thresholds reform re-projects.

    The IRS parameters that uprate by one of
    ``TRUSTEES_CORE_THRESHOLD_ASSUMPTION["uprating_parameters"]``, in tree
    order, then the parameters that follow one of them (the joint and
    surviving spouse standard deductions follow the single amount) and
    their own followers. The reform re-projects exactly these, in this
    order; some keep their values, such as amounts of zero.
    """
    return [parameter for parameter, _ in _wage_indexing_plan(parameters)]


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
    ``start_year``. Parameters that uprate by one of those follow it.
    """

    def modify_parameters(parameters):
        if not _parameters_have_long_run_projection(parameters, end_year):
            return parameters

        # The same plan trustees_core_threshold_parameters lists, leaders
        # before their followers.
        for parameter, leader in _wage_indexing_plan(parameters):
            if leader is None:
                _apply_wage_growth_to_parameter(
                    parameter,
                    parameters=parameters,
                    start_year=start_year,
                    end_year=end_year,
                    projection_base_year=projection_base_year,
                )
            else:
                _apply_leader_growth_to_follower(
                    parameter,
                    leader,
                    start_year=start_year,
                    end_year=end_year,
                )
        return parameters

    class reform(Reform):
        def apply(self):
            self.modify_parameters(modify_parameters)

    return reform


trustees_core_thresholds_reform = create_trustees_core_thresholds_reform()

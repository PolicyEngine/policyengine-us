"""Shared annual owners' draw arithmetic for the reform and benefit history.

The staged interface preserves the reform's public intermediate input contract:
an overridden gross draw or netting factor remains authoritative downstream.
Without overrides, one call computes a complete annual ledger from pure inputs.
"""

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Any

import numpy as np


@dataclass(frozen=True)
class OwnersDrawInputs:
    """Signed subsets are already included in the supplied entity totals."""

    s_corp_income: Any = 0
    partnership_income: Any = 0
    passive_income: Any = 0
    already_se_income: Any = 0
    subsets_are_disjoint: Any = False
    passive_se_overlap: Any = np.nan
    covered_wages: Any = 0
    existing_covered_se: Any = 0


@dataclass(frozen=True)
class OwnersDrawParameters:
    """Annual parameter values; default activation is deliberately off."""

    in_effect: bool = False
    start_year: int = 2027
    phase_in_years: int = 10
    phase_in_share: float = -1
    material_participation_only: bool = True
    net_earnings_factor: float = 0
    employer_share: float = 0.5
    oasdi_rate: float = 0.124
    hi_rate: float = 0.029
    reporting_floor: float = 400
    current_law_cap: float = np.inf
    room_cap_basis: int = 0
    include_hi: bool = False
    benefit_credit: bool = True

    @classmethod
    def from_policy_parameters(cls, gov, *, year=None, output=None):
        """Read annual policy values, preserving each Variable's lazy lookup.

        A selected stage uses Person overrides for all earlier stages, so it
        reads only its direct parameters. In particular a disabled stage must
        not require historical rate parameters it never used before extraction.
        History calls without ``output`` request the complete annual snapshot.
        """
        draw = gov.contrib.ssa.owners_draw
        if output is not None:
            values = dict(in_effect=draw.in_effect, start_year=draw.start_year)
            enabled = values["in_effect"] and year >= values["start_year"]
            if enabled and output == "active_income":
                values["material_participation_only"] = draw.material_participation_only
            if enabled and output in ("phase_in_share", "planned_gross"):
                values.update(
                    phase_in_years=draw.phase_in_years,
                    phase_in_share=draw.phase_in_share,
                )
            if enabled and output == "net_earnings_factor":
                values["net_earnings_factor"] = draw.net_earnings_factor
                if values["net_earnings_factor"] == 0:
                    values.update(
                        employer_share=gov.irs.ald.misc.employer_share,
                        oasdi_rate=gov.irs.self_employment.rate.social_security,
                        hi_rate=gov.irs.self_employment.rate.medicare,
                    )
            if enabled and output == "gross":
                values["reporting_floor"] = (
                    gov.irs.self_employment.net_earnings_exemption
                )
            if enabled and output == "oasdi_room":
                values["room_cap_basis"] = draw.room_cap_basis
                if values["room_cap_basis"] == 0:
                    values["current_law_cap"] = draw.current_law_cap
            if output == "oasdi_tax":
                values["oasdi_rate"] = gov.irs.self_employment.rate.social_security
            if output == "hi_tax":
                values["include_hi"] = draw.include_hi
                if values["include_hi"]:
                    values["hi_rate"] = gov.irs.self_employment.rate.medicare
            if enabled and output == "niit_exclusion":
                values["include_hi"] = draw.include_hi
            if output == "credited_earnings":
                values["benefit_credit"] = draw.benefit_credit
            return cls(**values)
        return cls(
            in_effect=draw.in_effect,
            start_year=draw.start_year,
            phase_in_years=draw.phase_in_years,
            phase_in_share=draw.phase_in_share,
            material_participation_only=draw.material_participation_only,
            net_earnings_factor=draw.net_earnings_factor,
            employer_share=gov.irs.ald.misc.employer_share,
            oasdi_rate=gov.irs.self_employment.rate.social_security,
            hi_rate=gov.irs.self_employment.rate.medicare,
            reporting_floor=gov.irs.self_employment.net_earnings_exemption,
            current_law_cap=draw.current_law_cap,
            room_cap_basis=draw.room_cap_basis,
            include_hi=draw.include_hi,
            benefit_credit=draw.benefit_credit,
        )


@dataclass(frozen=True)
class OwnersDrawResult:
    active_income: Any
    phase_in_share: Any
    planned_gross: Any
    net_earnings_factor: Any
    gross: Any
    net_earnings: Any
    oasdi_room: Any
    oasdi_base: Any
    oasdi_tax: Any
    hi_tax: Any
    niit_exclusion: Any
    credited_earnings: Any


def compute_owners_draw(
    year: int,
    *,
    inputs: OwnersDrawInputs | Callable[[str], Any] = OwnersDrawInputs(),
    parameters: OwnersDrawParameters = OwnersDrawParameters(),
    output: str | None = None,
    overrides: Mapping[str, Any] | Callable[[str], Any] | None = None,
) -> OwnersDrawResult | Any:
    """Compute one year's draw, optionally evaluating only a requested stage.

    ``overrides`` supplies *dependencies* of the requested stage. The reform
    uses a lazy Person accessor here, retaining direct inputs to every public
    intermediate variable and avoiding validation of unused earlier stages.
    History callers leave it unset and receive every annual amount.

    Covered wages and existing covered SE are the already adjusted tax bases
    used to order the OASDI room. Benefit credit is N_D before this room cap.
    """
    p = parameters
    enabled = p.in_effect and year >= p.start_year
    cache = {}

    def annual_input(name):
        return inputs(name) if callable(inputs) else getattr(inputs, name)

    def dependency(name):
        if callable(overrides):
            return overrides(name)
        if overrides is not None and name in overrides:
            return overrides[name]
        return evaluate(name)

    def evaluate(name):
        if name in cache:
            return cache[name]
        if name == "active_income":
            if not enabled:
                value = 0
            else:
                total = annual_input("s_corp_income") + annual_input(
                    "partnership_income"
                )
                already_se = annual_input("already_se_income")
                if not p.material_participation_only:
                    value = total - already_se
                else:
                    passive = annual_input("passive_income")
                    disjoint = annual_input("subsets_are_disjoint")
                    overlap = annual_input("passive_se_overlap")
                    unknown_overlap = ~np.isfinite(overlap)
                    ambiguous = (
                        (passive != 0)
                        & (already_se != 0)
                        & ~np.asarray(disjoint)
                        & unknown_overlap
                    )
                    if np.any(ambiguous):
                        raise ValueError(
                            "Owners' draw needs a validated disjoint-subset assertion "
                            "or explicit passive/SE overlap when both subsets are nonzero"
                        )
                    if np.any(disjoint & ~unknown_overlap & (overlap != 0)):
                        raise ValueError(
                            "Owners' draw disjoint assertion contradicts supplied overlap"
                        )
                    value = (
                        total
                        - passive
                        - already_se
                        + np.where(unknown_overlap, 0, overlap)
                    )
        elif name == "phase_in_share":
            if not enabled:
                value = 0
            else:
                if p.phase_in_years < 1 or int(p.phase_in_years) != p.phase_in_years:
                    raise ValueError(
                        "Owners' draw phase_in_years must be a positive integer"
                    )
                if p.phase_in_share == -1:
                    value = min(1, (year - p.start_year + 1) / p.phase_in_years)
                elif (
                    not np.isfinite(p.phase_in_share) or not 0 <= p.phase_in_share <= 1
                ):
                    raise ValueError(
                        "Owners' draw phase_in_share must be -1 or in [0, 1]"
                    )
                else:
                    value = p.phase_in_share
        elif name == "planned_gross":
            value = evaluate("phase_in_share") * np.maximum(
                0, dependency("active_income")
            )
        elif name == "net_earnings_factor":
            if not enabled:
                value = 0
            else:
                value = p.net_earnings_factor
                if value == 0:
                    value = 1 - p.employer_share * (p.oasdi_rate + p.hi_rate)
                if not np.isfinite(value) or not 0 < value <= 1:
                    raise ValueError(
                        "Owners' draw net earnings factor must be in (0, 1]"
                    )
        elif name == "gross":
            if not enabled:
                value = 0
            else:
                planned = dependency("planned_gross")
                adjusted = planned * dependency("net_earnings_factor")
                value = np.where(adjusted >= p.reporting_floor, planned, 0)
        elif name == "net_earnings":
            value = dependency("gross") * dependency("net_earnings_factor")
        elif name == "oasdi_room":
            if not enabled:
                value = 0
            elif p.room_cap_basis == 1:
                value = np.inf
            elif p.room_cap_basis != 0:
                raise ValueError(
                    "Owners' draw room_cap_basis must be 0 (current law) or 1 (no ceiling)"
                )
            else:
                value = np.maximum(
                    0,
                    p.current_law_cap
                    - annual_input("covered_wages")
                    - annual_input("existing_covered_se"),
                )
        elif name == "oasdi_base":
            value = np.minimum(dependency("net_earnings"), dependency("oasdi_room"))
        elif name == "oasdi_tax":
            value = p.oasdi_rate * dependency("oasdi_base")
        elif name == "hi_tax":
            value = p.hi_rate * dependency("net_earnings") if p.include_hi else 0
        elif name == "niit_exclusion":
            if not enabled:
                value = 0
            elif p.include_hi:
                value = dependency("gross")
            else:
                value = dependency("oasdi_base") / dependency("net_earnings_factor")
        elif name == "credited_earnings":
            value = dependency("net_earnings") if p.benefit_credit else 0
        else:
            raise ValueError(f"Unknown owners' draw output: {name}")
        cache[name] = value
        return value

    if output is not None:
        return evaluate(output)
    return OwnersDrawResult(
        **{name: evaluate(name) for name in OwnersDrawResult.__dataclass_fields__}
    )

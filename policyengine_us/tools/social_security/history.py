"""Complete, explicitly certified annual earnings for own-record retirement.

Initial earnings are frozen at claim year Q, through Q-1. This is an opt-in
household service, not a replacement for the population variable's rolling
lookback. Annual caps precede E-2 wage indexing; top 35 / 420 is floored.
"""

from dataclasses import dataclass
from decimal import Decimal
from fractions import Fraction
import json
from typing import Mapping

from .earnings import highest_earnings, index_covered_earnings
from .donut import DonutParameters, compute_donut_year, donut_parameters_at
from .owners_draw import OwnersDrawInputs, OwnersDrawParameters, compute_owners_draw
from .mini_pia import blend_mini_pia, compute_mini_pia, mini_pia_share_at
from .pia import _number, compute_pia


def _money(value, name):
    if isinstance(value, bool):
        raise ValueError(f"{name} must be a finite nonnegative amount")
    try:
        amount = Decimal(str(value))
    except (ValueError, ArithmeticError) as error:
        raise ValueError(f"{name} must be a finite nonnegative amount") from error
    if not amount.is_finite() or amount < 0:
        raise ValueError(f"{name} must be a finite nonnegative amount")
    return amount


def _year(value):
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError("History years must be integer calendar years")
    return value


@dataclass(frozen=True)
class EarningsRecord:
    year: int
    covered_wages: Decimal | int | str
    covered_self_employment: Decimal | int | str
    owners_draw: OwnersDrawInputs | dict | None = None


@dataclass(frozen=True)
class EarningsHistory:
    first_year: int
    records: tuple[EarningsRecord, ...] = ()
    certified_zero_years: tuple[int, ...] = ()
    certified_zero_before_first_year: bool = False

    @classmethod
    def from_json(cls, payload):
        """A single structural source preserves every year and exact money.

        Explicit zero records contain both wage and adjusted existing-SE zero.
        Omitted years never inherit another year's value. A zero certification
        cannot also carry an observed record for the same year.
        """
        try:
            data = json.loads(payload, parse_float=Decimal)
            if not isinstance(data, dict):
                raise ValueError("History must be a JSON object")
            records = tuple(EarningsRecord(**row) for row in data.pop("records", []))
            return cls(records=records, **data)
        except (TypeError, KeyError, json.JSONDecodeError) as error:
            raise ValueError("Invalid annual earnings history JSON") from error

    def through_claim(self, claim_year, birth_year=None):
        first = _year(self.first_year)
        claim = _year(claim_year)
        earliest = max(1951, birth_year) if birth_year is not None else 1951
        if first < earliest or first >= claim:
            raise ValueError(
                "History first_year must be within the worker's base years"
            )
        if not isinstance(self.certified_zero_before_first_year, bool):
            raise ValueError("Earlier-zero certification must be a boolean")
        if first > earliest and not self.certified_zero_before_first_year:
            raise ValueError("Certify zero earnings before history first_year")
        records = {}
        for row in self.records:
            year = _year(row.year)
            if year < first:
                raise ValueError("A history record precedes first_year")
            if year in records:
                raise ValueError(f"Duplicate earnings year {year}")
            _money(row.covered_wages, "Covered wages")
            _money(row.covered_self_employment, "Existing covered SE earnings")
            records[year] = row
        zeros = tuple(_year(year) for year in self.certified_zero_years)
        if len(set(zeros)) != len(zeros) or set(zeros) & records.keys():
            raise ValueError("Duplicate or conflicting certified-zero earnings year")
        if any(year < first for year in zeros):
            raise ValueError("A certified-zero year precedes first_year")
        missing = set(range(first, claim)) - records.keys() - set(zeros)
        if missing:
            raise ValueError(f"Missing required earnings years: {sorted(missing)}")
        return tuple(
            records.get(year, EarningsRecord(year, 0, 0, OwnersDrawInputs()))
            for year in range(first, claim)
        )


@dataclass(frozen=True)
class HistoryParameters:
    wage_base: Mapping[int, Decimal | int | str]
    nawi: Mapping[int, Decimal | int | str]
    owners_draw_by_year: Mapping[int, OwnersDrawParameters] | None = None
    mini_share: Decimal | Fraction | int | str = 0
    donut_by_year: Mapping[int, DonutParameters] | None = None
    donut_credit_rate: Decimal | Fraction | int | str | None = None


@dataclass(frozen=True)
class AnnualEarnings:
    year: int
    covered_wages: Decimal
    covered_self_employment: Decimal
    ordinary_cap: Decimal
    ordinary_covered: Decimal
    indexing_factor: Decimal
    indexed_ordinary: Decimal
    e1_gross: Decimal = Decimal(0)
    e1_net_earnings: Decimal = Decimal(0)
    e1_credited: Decimal = Decimal(0)
    e1_oasdi_base: Decimal = Decimal(0)
    e1_niit_exclusion: Decimal = Decimal(0)
    donut_taxed: Decimal = Decimal(0)
    donut_credited: Decimal = Decimal(0)
    indexed_donut: Decimal = Decimal(0)
    donut_tax: Decimal = Decimal(0)
    certified_zero: bool = False
    ordinary_without_e1: Decimal = Decimal(0)
    e1_ordinary_increment: Decimal = Decimal(0)
    e1_active_income: Decimal = Decimal(0)
    e1_phase_in_share: Decimal = Decimal(0)
    e1_net_earnings_factor: Decimal = Decimal(0)
    e1_planned_gross: Decimal = Decimal(0)
    e1_oasdi_room: Decimal = Decimal(0)
    e1_oasdi_tax: Decimal = Decimal(0)
    e1_hi_tax: Decimal = Decimal(0)
    donut_variant: str = ""
    donut_tier_start: Decimal = Decimal(0)


@dataclass(frozen=True)
class HistoryCalculation:
    eligibility_year: int
    claim_year: int
    ledger: tuple[AnnualEarnings, ...]
    aime: int
    mini_share: Fraction = Fraction(0)
    aime_plus: int = 0
    donut_credit_pia: Fraction = Fraction(0)


@dataclass(frozen=True)
class HistoryPIACalculation:
    conventional_pia: Decimal
    mini_pia: Fraction
    annual_mini_pias: tuple[Fraction, ...]
    blended_pia: Fraction
    eligibility_pia: Decimal


def _parameter(path, year, name, *, positive=False):
    if year not in path:
        raise ValueError(f"Missing {name} for year {year}")
    value = _money(path[year], name)
    if positive and not value:
        raise ValueError(f"{name} must be positive")
    return value


def aime_from_indexed(indexed_amounts):
    amounts = tuple(
        _money(value, "Indexed annual earnings") for value in indexed_amounts
    )
    selected = highest_earnings(amounts or (Decimal(0),))
    return int(sum(selected, Decimal(0)) // 420)


def _owners_inputs(row, wages, se):
    supplied = row.owners_draw
    if isinstance(supplied, dict):
        required = {
            "s_corp_income",
            "partnership_income",
            "passive_income",
            "already_se_income",
        }
        if not required <= supplied.keys():
            raise ValueError(f"Missing owners' draw source fields for year {row.year}")
        if supplied.keys() - required - {"subsets_are_disjoint", "passive_se_overlap"}:
            raise ValueError("Unknown owners' draw history input")
        supplied = OwnersDrawInputs(**supplied)
    if not isinstance(supplied, OwnersDrawInputs):
        raise ValueError(f"Supply owners' draw source fields for year {row.year}")
    values = {}
    for name in (
        "s_corp_income",
        "partnership_income",
        "passive_income",
        "already_se_income",
        "passive_se_overlap",
    ):
        raw = getattr(supplied, name)
        if name == "passive_se_overlap" and (raw is None or str(raw).lower() == "nan"):
            values[name] = float("nan")
            continue
        try:
            amount = Decimal(str(raw))
            converted = float(amount)
        except (ValueError, TypeError, ArithmeticError) as error:
            raise ValueError(
                "Owners' draw source amounts must be finite signed numbers"
            ) from error
        if (
            isinstance(raw, bool)
            or not amount.is_finite()
            or not Decimal(str(converted)).is_finite()
        ):
            raise ValueError(
                "Owners' draw source amounts must be finite signed numbers"
            )
        values[name] = converted
    if not isinstance(supplied.subsets_are_disjoint, bool):
        raise ValueError("Owners' draw disjoint-subset assertion must be boolean")
    return OwnersDrawInputs(
        **values,
        subsets_are_disjoint=supplied.subsets_are_disjoint,
        covered_wages=float(wages),
        existing_covered_se=float(se),
    )


def compute_history(
    history, eligibility_year, claim_year, parameters, *, birth_year=None
):
    """Compute a complete career, including earnings after 62 through Q-1."""
    eligibility = _year(eligibility_year)
    if eligibility < 1983:
        raise ValueError("Computation benchmarks before 1983 are unsupported")
    if claim_year < eligibility:
        raise ValueError("Claim year cannot precede eligibility")
    records = history.through_claim(claim_year, birth_year)
    mini_share = _number(parameters.mini_share, "mini-PIA share")
    if not 0 <= mini_share <= 1:
        raise ValueError("mini-PIA share must be between zero and one")
    anchor_year = eligibility - 2
    anchor = _parameter(parameters.nawi, anchor_year, "NAWI", positive=True)
    ledger = []
    credit_rates = set()
    for row in records:
        wages = _money(row.covered_wages, "Covered wages")
        se = _money(row.covered_self_employment, "Existing covered SE earnings")
        cap = _parameter(parameters.wage_base, row.year, "Ordinary cap", positive=True)
        draw_parameters = (parameters.owners_draw_by_year or {}).get(
            row.year, OwnersDrawParameters()
        )
        draw = None
        if draw_parameters.in_effect and row.year >= draw_parameters.start_year:
            draw = compute_owners_draw(
                row.year,
                inputs=_owners_inputs(row, wages, se),
                parameters=draw_parameters,
            )
        # Preserve the existing kernel's arithmetic, then keep decimal earnings
        # through annual cent rounding. Credit is N_D before any room cap.
        credited = Decimal(str(float(draw.credited_earnings))) if draw else Decimal(0)
        covered = min(wages + se + credited, cap)
        nawi = (
            _parameter(parameters.nawi, row.year, "NAWI", positive=True)
            if row.year < anchor_year
            else anchor
        )
        indexed = index_covered_earnings(covered, nawi, anchor, round_cents=True)
        donut_parameters = (parameters.donut_by_year or {}).get(row.year)
        donut = None
        if donut_parameters is not None:
            donut = compute_donut_year(
                row.year,
                covered_wages=wages,
                existing_covered_se=se,
                owners_draw_net_earnings=Decimal(str(float(draw.net_earnings)))
                if draw
                else 0,
                ordinary_cap=cap,
                parameters=donut_parameters,
            )
            if donut.credited_earnings:
                credit_rates.add(
                    _number(donut_parameters.credit_rate, "donut credit rate")
                )
        donut_taxed = (
            Decimal(donut.taxed_earnings.numerator) / donut.taxed_earnings.denominator
            if donut
            else Decimal(0)
        )
        donut_credited = (
            Decimal(donut.credited_earnings.numerator)
            / donut.credited_earnings.denominator
            if donut
            else Decimal(0)
        )
        indexed_donut = index_covered_earnings(
            donut_credited, nawi, anchor, round_cents=True
        )
        ledger.append(
            AnnualEarnings(
                row.year,
                wages,
                se,
                cap,
                covered,
                anchor / nawi,
                indexed,
                e1_gross=Decimal(str(float(draw.gross))) if draw else Decimal(0),
                e1_net_earnings=Decimal(str(float(draw.net_earnings)))
                if draw
                else Decimal(0),
                e1_credited=credited,
                e1_oasdi_base=Decimal(str(float(draw.oasdi_base)))
                if draw
                else Decimal(0),
                e1_niit_exclusion=Decimal(str(float(draw.niit_exclusion)))
                if draw
                else Decimal(0),
                donut_taxed=donut_taxed,
                donut_credited=donut_credited,
                indexed_donut=indexed_donut,
                donut_tax=Decimal(donut.tax.numerator) / donut.tax.denominator
                if donut
                else Decimal(0),
                certified_zero=row.year in history.certified_zero_years,
                ordinary_without_e1=min(wages + se, cap),
                e1_ordinary_increment=covered - min(wages + se, cap),
                e1_active_income=Decimal(str(float(draw.active_income)))
                if draw
                else Decimal(0),
                e1_phase_in_share=Decimal(str(float(draw.phase_in_share)))
                if draw
                else Decimal(0),
                e1_net_earnings_factor=Decimal(str(float(draw.net_earnings_factor)))
                if draw
                else Decimal(0),
                e1_planned_gross=Decimal(str(float(draw.planned_gross)))
                if draw
                else Decimal(0),
                e1_oasdi_room=Decimal(str(float(draw.oasdi_room)))
                if draw
                else Decimal(0),
                e1_oasdi_tax=Decimal(str(float(draw.oasdi_tax)))
                if draw
                else Decimal(0),
                e1_hi_tax=Decimal(str(float(draw.hi_tax))) if draw else Decimal(0),
                donut_variant=donut_parameters.name if donut_parameters else "",
                donut_tier_start=Decimal(donut.threshold.numerator)
                / donut.threshold.denominator
                if donut
                else Decimal(0),
            )
        )
    if parameters.donut_credit_rate is None:
        if len(credit_rates) > 1:
            raise ValueError(
                "Mixed annual donut rates require an explicit eligibility-cohort coefficient"
            )
        credit_rate = next(iter(credit_rates), Fraction(0))
    else:
        credit_rate = _number(parameters.donut_credit_rate, "donut credit rate")
    if credit_rate < 0:
        raise ValueError("Donut credit rate must be nonnegative")
    aime_plus = aime_from_indexed(row.indexed_donut for row in ledger)
    return HistoryCalculation(
        eligibility,
        claim_year,
        tuple(ledger),
        aime_from_indexed(row.indexed_ordinary for row in ledger),
        mini_share,
        aime_plus,
        credit_rate * aime_plus,
    )


def history_pia_details(
    calculation,
    *,
    bend_points,
    formula_path=None,
    payment_year=None,
    recompute_mode="cohort",
):
    conventional = compute_pia(
        calculation.aime,
        calculation.eligibility_year,
        formula_path,
        payment_year,
        recompute_mode,
        bend_points=bend_points,
    )
    minis = compute_mini_pia(
        (row.indexed_ordinary for row in calculation.ledger),
        calculation.eligibility_year,
        bend_points=bend_points,
        formula_path=formula_path,
        payment_year=payment_year,
        recompute_mode=recompute_mode,
    )
    blended = blend_mini_pia(conventional, minis.mini_pia, calculation.mini_share)
    combined = blended + calculation.donut_credit_pia
    return HistoryPIACalculation(
        conventional,
        minis.mini_pia,
        minis.annual_mini_pias,
        blended,
        Decimal((combined * 10).__floor__()) / 10,
    )


def compute_history_pia(
    calculation,
    *,
    bend_points,
    formula_path=None,
    payment_year=None,
    recompute_mode="cohort",
):
    """Combined eligibility PIA, before COLAs and claiming adjustments."""
    return history_pia_details(
        calculation,
        bend_points=bend_points,
        formula_path=formula_path,
        payment_year=payment_year,
        recompute_mode=recompute_mode,
    ).eligibility_pia


def history_parameters_at(
    parameters,
    history,
    eligibility_year,
    claim_year,
    *,
    birth_year=None,
    donut_variant="custom",
):
    years = [row.year for row in history.through_claim(claim_year, birth_year)]
    from types import SimpleNamespace as Node

    owners = {}
    for year in years:
        when = f"{year}-01-01"
        settings = parameters.gov.contrib.ssa.owners_draw(when)
        if not settings.in_effect or year < settings.start_year:
            continue
        # Snapshot only the relevant subtrees, not every US parameter/year.
        gov = Node(
            contrib=Node(ssa=Node(owners_draw=settings)),
            irs=Node(
                ald=Node(misc=parameters.gov.irs.ald.misc(when)),
                self_employment=parameters.gov.irs.self_employment(when),
            ),
        )
        owners[year] = OwnersDrawParameters.from_policy_parameters(gov)
    return HistoryParameters(
        wage_base={
            year: parameters.gov.ssa.social_security(f"{year}-01-01").wage_base
            for year in years
        },
        nawi={
            year: parameters.gov.ssa.nawi(f"{year}-01-01")
            for year in set(years) | {eligibility_year - 2}
        },
        owners_draw_by_year=owners,
        mini_share=mini_pia_share_at(parameters, eligibility_year),
        donut_by_year={
            year: donut_parameters_at(parameters, year, donut_variant) for year in years
        },
        # Annual parameters define the taxed stream. The PIA coefficient is
        # selected at initial eligibility, like the ordinary formula factors.
        donut_credit_rate=donut_parameters_at(
            parameters, eligibility_year, donut_variant
        ).credit_rate,
    )

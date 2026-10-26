"""Opt-in gross Social Security ledger for supplied, identified worker records.

All amounts are monthly dollars. A ledger row is a benefit entitlement month;
its check is paid in the following month. Both annual entitlement and check
totals are returned, so a partial year never becomes annual benefit / 12.
This module does not compute family, disability, WINDEX or minimum benefits.
"""

from dataclasses import dataclass, replace
from datetime import date, timedelta
from decimal import Decimal, ROUND_CEILING
from fractions import Fraction
from typing import Mapping

from policyengine_us.tools.social_security.cola import (
    adjusted_events as adjust_cola_events,
    apply_colas,
    reverse_colas_interval,
)
from policyengine_us.tools.social_security.pia import (
    FormulaPath,
    compute_pia,
    has_active_reform,
    inverse_pia,
)


def decimal(value):
    return Decimal(str(value))


def rational(value):
    return value if isinstance(value, Fraction) else Fraction(str(value))


def as_decimal(value):
    value = rational(value)
    return Decimal(value.numerator) / Decimal(value.denominator)


def truncate_dime(value):
    return Decimal(int(rational(value) * 10)) / 10


def payment_round(value):
    """RS 00601.020: retain a positive benefit below one dollar."""
    value = truncate_dime(value)
    return value if value < 1 else Decimal(int(value))


def month_number(value):
    parts = str(value).split("-")
    if len(parts) != 2 or not 1 <= int(parts[1]) <= 12:
        raise ValueError("A month must have YYYY-MM format")
    return int(parts[0]) * 12 + int(parts[1]) - 1


def month_string(number):
    year, month = divmod(number, 12)
    return f"{year:04d}-{month + 1:02d}"


def attainment_month(birth_date, age_months):
    # GN 00302.400: attain an age the day before the birthday. A January 1
    # birthday also belongs to the preceding birth cohort for FRA/DRCs.
    shifted = birth_date - timedelta(days=1)
    return shifted.year * 12 + shifted.month - 1 + age_months


def cohort_year(birth_date):
    return (birth_date - timedelta(days=1)).year


def full_retirement_age_months(birth_date):
    """42 USC 416(l); birth-cohort age in months (not survivor FRA)."""
    year = cohort_year(birth_date)
    if year < 1938:
        return 780
    if year < 1943:
        return 780 + 2 * (year - 1937)
    if year < 1955:
        return 792
    return min(804, 792 + 2 * (year - 1954))


def delayed_credit_rate(birth_date):
    year = cohort_year(birth_date)
    if year < 1917:
        return Fraction(1, 100)
    if year < 1925:
        return Fraction(3, 100)
    return min(Fraction(8, 100), Fraction(35 + 5 * ((year - 1925) // 2), 1000))


def claiming_factor(birth_date, entitlement_month, benefit_month=None):
    """Exact early months and cohort DRCs, including deferred current-year DRCs.

    Credits in a midyear claim before 70 enter the benefit in January of the
    next year. At 70, all eligible delayed months are credited immediately.
    Sources: RS 00615.101 and RS 00615.690.
    """
    claim = month_number(entitlement_month)
    fra = attainment_month(birth_date, full_retirement_age_months(birth_date))
    if claim < fra:
        early = fra - claim
        return (
            1
            - min(early, 36) * Fraction(1, 180)
            - max(early - 36, 0) * Fraction(1, 240)
        )
    age70 = attainment_month(birth_date, 840)
    end = min(claim, age70)
    benefit = claim if benefit_month is None else month_number(benefit_month)
    if claim < age70 and benefit < age70 and benefit // 12 == claim // 12:
        end = min(end, (claim // 12) * 12)
    credits = max(0, end - fra)
    return 1 + credits * delayed_credit_rate(birth_date) / 12


@dataclass(frozen=True)
class SurvivorBasis:
    worker_birth_year: int
    death_year: int
    provenance: str
    worker_birth_date: date | None = None
    death_date: date | None = None
    authoritative_year: int | None = None
    no_prior_disability: bool = False
    ordinary_non_windex: bool = False
    year_only_not_january_1: bool = False
    same_year_death_before_62: bool | None = None

    def benchmark(self):
        if not self.provenance.strip():
            raise ValueError("Survivor computation-basis provenance is required")
        if not self.ordinary_non_windex:
            raise ValueError(
                "Only ordinary non-WINDEX survivor computations are supported"
            )
        if not self.no_prior_disability and self.authoritative_year is None:
            raise ValueError(
                "Prior disability requires an authoritative computation basis"
            )
        if (
            self.worker_birth_date
            and self.worker_birth_date.year != self.worker_birth_year
        ):
            raise ValueError("Worker birth date and birth year disagree")
        if self.death_date and self.death_date.year != self.death_year:
            raise ValueError("Death date and death year disagree")
        if (
            self.death_date
            and self.worker_birth_date
            and self.death_date < self.worker_birth_date
        ):
            raise ValueError("Death cannot precede birth")
        if self.death_year < self.worker_birth_year:
            raise ValueError("Death cannot precede birth")
        if self.worker_birth_date:
            b = self.worker_birth_date
            # February 29 attains age 62 on February 28 in a non-leap year.
            try:
                birthday62 = b.replace(year=b.year + 62)
            except ValueError:
                birthday62 = date(b.year + 62, 3, 1)
            attained62 = birthday62 - timedelta(days=1)
            year62 = attained62.year
        else:
            if not self.year_only_not_january_1 and self.authoritative_year is None:
                raise ValueError(
                    "Year-only birth basis requires a not-January-1 assertion"
                )
            year62 = self.worker_birth_year + 62
            attained62 = None
        if self.death_year == year62:
            if self.death_date and attained62:
                pre62 = self.death_date < attained62
            elif self.same_year_death_before_62 is not None:
                pre62 = self.same_year_death_before_62
            else:
                raise ValueError(
                    "Same-year death/age-62 attainment needs dates or an assertion"
                )
        else:
            pre62 = self.death_year < year62
        year = (
            self.authoritative_year
            if self.authoritative_year is not None
            else min(year62, self.death_year)
        )
        if year < 1983:
            raise ValueError("Computation benchmarks before 1983 are unsupported")
        return year, pre62


@dataclass(frozen=True)
class SuppliedRecord:
    source: str
    worker_id: str
    birth_date: date  # recipient; worker for an own-retirement record
    entitlement_month: str
    insured: bool
    eligibility_year: int | None = None
    aime: Decimal | int | None = None
    pia: Decimal | int | None = None
    source_basis: str = "unreformed_eligibility"
    supplied_claiming_factor: Decimal | None = None
    survivor: SurvivorBasis | None = None
    monthly_amount: Decimal | None = None
    valuation_month: str | None = None
    composite_ratio: Decimal | None = None
    ratio_description: str = ""
    nonbinding_rib_lim: bool = False
    nonbinding_family_maximum: bool = False
    no_dual_entitlement: bool = False
    no_earnings_test_at_valuation: bool = False
    no_special_monthly_test: bool = False
    no_prior_withholding_adjustment: bool = False
    earnings_test_no_trigger: bool = False

    def benchmark(self):
        if not self.worker_id.strip():
            raise ValueError("An explicit worker record ID is required")
        if self.source not in ("aime", "pia", "survivor"):
            raise ValueError("Choose an explicit aime, pia or survivor source")
        if self.source_basis != "unreformed_eligibility":
            raise ValueError("Only explicitly unreformed source amounts are supported")
        month_number(self.entitlement_month)
        if self.source == "survivor":
            if self.survivor is None:
                raise ValueError("The survivor route requires a deceased-worker basis")
            if month_number(self.entitlement_month) < attainment_month(
                self.birth_date, 720
            ):
                raise ValueError(
                    "The restricted survivor route excludes child, caregiver and disabled-survivor entitlement before age 60"
                )
            return self.survivor.benchmark()[0]
        year = attainment_month(self.birth_date, 744) // 12
        if self.eligibility_year != year:
            raise ValueError(
                "Own-retirement eligibility year must equal age-62 attainment year"
            )
        if year < 1983:
            raise ValueError("Computation benchmarks before 1983 are unsupported")
        # RS 00201.001: the worker must be 62 throughout the first reduced
        # entitlement month. Birthdays on day 1 or 2 permit the birth month.
        earliest = year * 12 + self.birth_date.month - 1
        if self.birth_date.day == 1:
            earliest = attainment_month(self.birth_date, 744) + 1
        elif self.birth_date.day > 2:
            earliest += 1
        if month_number(self.entitlement_month) < earliest:
            raise ValueError("Retirement entitlement precedes the first eligible month")
        if self.survivor is not None:
            raise ValueError(
                "Own-retirement records cannot invoke survivor computation"
            )
        return year


@dataclass(frozen=True)
class BenefitPolicies:
    """Already resolved joint COLA decisions and payment-year factors.

    A withheld COLA has rate zero; changed rates already include any statutory
    floor and policy precision. This accepts E3 decisions without reading tax
    income or constructing a cycle. Medicare deductions are never included.
    """

    cola_rates: Mapping[str, Decimal] | None = None
    across_the_board: Mapping[int, Decimal] | None = None
    payable_share: Mapping[int, Decimal] | None = None
    cola_pp_changes: Mapping[int, Decimal] | None = None
    withheld_cola_years: tuple[int, ...] = ()

    def factor(self, payment_year):
        rate = decimal((self.across_the_board or {}).get(payment_year, 0))
        share = decimal((self.payable_share or {}).get(payment_year, 1))
        if rate < -1 or not 0 <= share <= 1:
            raise ValueError("Benefit rate must be >= -1 and payable share in [0, 1]")
        return (1 + rate) * share


@dataclass(frozen=True)
class EntitlementMonth:
    entitlement_month: str
    payment_month: str
    eligibility_pia: Decimal
    cola_pia: Decimal
    claiming_factor: Decimal
    unrounded_benefit: Decimal
    gross_benefit: Decimal
    earnings_test_reduction: Decimal
    payable_benefit: Decimal


@dataclass(frozen=True)
class AnnualBenefit:
    ledger: tuple[EntitlementMonth, ...]
    entitlement_total: Decimal
    payment_total: Decimal
    earnings_test_reduction: Decimal
    eligibility_pia_interval: tuple[Decimal, Decimal] | None = None
    inferred_aime_interval: tuple[Decimal, Decimal] | None = None


def _source_pia(record, year, bends, baseline_events):
    if record.source == "aime":
        if (
            record.aime is None
            or rational(record.aime) < 0
            or rational(record.aime).denominator != 1
        ):
            raise ValueError(
                "Supplied AIME must be a nonnegative whole monthly dollar amount"
            )
        return compute_pia(record.aime, year, bend_points=bends), record.aime, None
    if record.source == "pia":
        if (
            record.pia is None
            or rational(record.pia) < 0
            or truncate_dime(record.pia) != decimal(record.pia)
        ):
            raise ValueError(
                "Supplied eligibility PIA must be nonnegative and dime-valued"
            )
        return decimal(record.pia), None, None
    if not all(
        (
            record.nonbinding_rib_lim,
            record.nonbinding_family_maximum,
            record.no_dual_entitlement,
            record.no_earnings_test_at_valuation,
        )
    ):
        raise ValueError(
            "Survivor inversion requires nonbinding limits, no dual entitlement and no valuation withholding"
        )
    if record.supplied_claiming_factor is not None:
        raise ValueError(
            "The composite survivor ratio already includes claiming adjustments"
        )
    if (
        not record.ratio_description.strip()
        or record.composite_ratio is None
        or rational(record.composite_ratio) <= 0
    ):
        raise ValueError(
            "A positive composite survivor ratio and its description are required"
        )
    if (
        record.monthly_amount is None
        or rational(record.monthly_amount) < 0
        or record.valuation_month is None
    ):
        raise ValueError(
            "Supply a nonnegative gross monthly payment and its valuation month"
        )
    if month_number(record.valuation_month) <= month_number(record.entitlement_month):
        raise ValueError(
            "Survivor source valuation must be after entitlement commencement"
        )
    if record.survivor.death_year > int(record.valuation_month[:4]):
        raise ValueError("Source valuation precedes the worker's death")
    amount = decimal(record.monthly_amount)
    if 0 < amount < 1 and month_number(record.valuation_month) < month_number(
        "2007-01"
    ):
        raise ValueError(
            "Sub-dollar survivor source checks before January 2007 require "
            "unsupported year-end manual payment timing"
        )
    # Paid-dollar interval is wider than the exact-dime eligibility interval.
    # The sub-dollar exception retains dimes (RS 00601.020).
    width = Decimal("0.1") if amount < 1 else Decimal(1)
    ratio = decimal(record.composite_ratio)
    lower, upper = reverse_colas_interval(
        rational(amount) / rational(ratio),
        rational(amount + width) / rational(ratio),
        year,
        record.valuation_month,
        baseline_events,
    )
    lower = (lower * 10).to_integral_value(rounding=ROUND_CEILING) / 10
    if lower >= upper:
        raise ValueError(
            "Supplied survivor amount has no consistent dime-valued eligibility PIA"
        )
    reproduced = payment_round(
        rational(apply_colas(lower, year, record.valuation_month, baseline_events))
        * rational(ratio)
    )
    if reproduced != amount:
        raise ValueError(
            "Supplied survivor amount is inconsistent with the stated payment rounding"
        )
    return lower, None, (lower, upper)


def calculate_year(
    record,
    year,
    *,
    bend_points,
    formula_path=None,
    cola_events=(),
    policies=None,
    earnings=None,
    pre_fra_earnings=None,
    lower_exempt=None,
    higher_exempt=None,
    recompute_mode="cohort",
    s770_survivor_bend_increase=False,
    _include_previous_check=True,
):
    """Return a 13-row ledger (previous December plus January–December).

    The extra December identifies January's check. Earnings maps are keyed by
    entitlement year; the prior year is required when January's check could
    have been withheld. The ordinary annual test is allocated to the earliest
    affected months. Special monthly/service tests and adjustments for earlier
    withheld months require explicit no-trigger assertions in this route.
    """
    # The inverse, its reproduction check, and the prior-year earnings-test
    # ledger all need the same immutable history, including for iterator input.
    cola_events = tuple(cola_events)
    benchmark = record.benchmark()
    baseline_pia, aime, pia_interval = _source_pia(
        record, benchmark, bend_points, cola_events
    )
    paths = formula_path
    policies = policies or BenefitPolicies()
    if not record.no_special_monthly_test or not record.no_prior_withholding_adjustment:
        raise ValueError(
            "Assert no special monthly/service test and no prior-withholding actuarial adjustment"
        )
    restricted_survivor = False
    if record.source == "survivor":
        _, before62 = record.survivor.benchmark()
        restricted_survivor = (
            before62
            and record.survivor.death_year < 2026
            and record.survivor.no_prior_disability
        )
        death_month = (
            record.survivor.death_date.strftime("%Y-%m")
            if record.survivor.death_date
            else f"{record.survivor.death_year}-01"
        )
        if month_number(record.entitlement_month) < month_number(death_month):
            raise ValueError("Survivor entitlement cannot precede the worker's death")
    policy_events = adjust_cola_events(
        cola_events, policies.cola_pp_changes, policies.withheld_cola_years
    )
    adjusted_events = tuple(
        replace(
            event,
            rate=decimal(policies.cola_rates[event.payment_month]),
            as_paid_rate=decimal(policies.cola_rates[event.payment_month])
            if event.as_paid_rate is not None
            else None,
        )
        if event.payment_month in (policies.cola_rates or {})
        else event
        for event in policy_events
    )
    if any(event.rate < 0 for event in adjusted_events):
        raise ValueError("Joint COLA rates cannot reduce nominal PIA")
    fra = attainment_month(
        record.birth_date, full_retirement_age_months(record.birth_date)
    )
    claim = month_number(record.entitlement_month)
    rows = []
    inferred_interval = None
    for number in range(year * 12 - int(_include_previous_check), (year + 1) * 12):
        entitlement = month_string(number)
        payment = month_string(number + 1)
        payment_year = (number + 1) // 12
        path = (
            paths[payment_year] if isinstance(paths, Mapping) else paths
        ) or FormulaPath()
        # S.770 section 2(c)(1) reaches benefit months from January 2026;
        # the ordinary check for that month follows in February. COLA changes
        # instead key off check months, as specified in their policy contract.
        if number < 2026 * 12 and path.s770:
            path = replace(path, s770=False)
        mode = (
            recompute_mode[payment_year]
            if isinstance(recompute_mode, Mapping)
            else recompute_mode
        )
        flag = (
            s770_survivor_bend_increase[payment_year]
            if isinstance(s770_survivor_bend_increase, Mapping)
            else s770_survivor_bend_increase
        )
        if restricted_survivor and path.s770:
            path = replace(path, s770_increase_first_bend_point=flag)
        # Only infer AIME if the selected path actually changes the baseline.
        pia = baseline_pia
        if payment_year >= benchmark and has_active_reform(
            path, benchmark, payment_year, mode
        ):
            if aime is None and baseline_pia != 0:
                inferred = inverse_pia(baseline_pia, benchmark, bend_points=bend_points)
                aime = inferred.lower
                upper_pia = (
                    pia_interval[1] if pia_interval else baseline_pia + Decimal("0.1")
                )
                inferred_interval = (
                    inferred.lower,
                    inverse_pia(upper_pia, benchmark, bend_points=bend_points).lower,
                )
            reformed = compute_pia(
                aime if aime is not None else 0,
                benchmark,
                path,
                payment_year,
                mode,
                bend_points=bend_points,
            )
            # The supplied unreformed PIA is authoritative; one ratio, once.
            pia = (
                Decimal(0)
                if baseline_pia == 0
                else truncate_dime(
                    rational(baseline_pia)
                    * rational(reformed)
                    / rational(compute_pia(aime, benchmark, bend_points=bend_points))
                )
            )
        cola_pia = apply_colas(pia, benchmark, payment, adjusted_events)
        factor = (
            rational(record.composite_ratio)
            if record.source == "survivor"
            else rational(record.supplied_claiming_factor)
            if record.supplied_claiming_factor is not None
            else claiming_factor(
                record.birth_date, record.entitlement_month, entitlement
            )
        )
        if factor <= 0:
            raise ValueError("Supplied claiming adjustment must be positive")
        raw = rational(cola_pia) * factor
        # Preserve SSA's separate claiming-adjustment dime step before any
        # contributed payable/across-the-board mechanism and dollar payment.
        adjusted_benefit = rational(truncate_dime(raw)) * rational(
            policies.factor(payment_year)
        )
        gross = (
            payment_round(adjusted_benefit)
            if record.insured and number >= claim
            else Decimal(0)
        )
        if 0 < gross < 1 and number < month_number("2006-12"):
            # RS 00601.020 D.3: these benefits were held for manual year-end
            # payment before December 2006, not paid as recurring dime checks.
            raise ValueError(
                "Sub-dollar entitlement before December 2006 requires "
                "unsupported year-end manual payment timing"
            )
        rows.append(
            EntitlementMonth(
                entitlement,
                payment,
                pia,
                cola_pia,
                as_decimal(factor),
                as_decimal(raw),
                gross,
                Decimal(0),
                gross,
            )
        )
    # Evaluate full entitlement years, even when only their last month's check
    # falls in the requested payment year. This makes request order irrelevant.
    by_month = {row.entitlement_month: row for row in rows}
    for earnings_year in (year - 1, year) if _include_previous_check else (year,):
        if (
            earnings_year < 2000
            and not record.earnings_test_no_trigger
            and record.insured
            and claim < (earnings_year + 1) * 12
        ):
            raise ValueError(
                "Earnings testing before 2000 is unsupported; supply an explicit "
                "no-trigger assertion for historical entitlement"
            )
        if earnings_year * 12 >= fra or not record.insured:
            continue
        relevant = [
            n
            for n in range(earnings_year * 12, (earnings_year + 1) * 12)
            if claim <= n < fra
        ]
        if not relevant:
            continue
        if record.earnings_test_no_trigger:
            # A caller asserting no trigger must not also supply excess earnings.
            values = earnings or {}
            high = fra // 12 == earnings_year
            limit = (higher_exempt if high else lower_exempt) or {}
            observed = (
                (pre_fra_earnings or {}).get(earnings_year)
                if high
                else values.get(earnings_year)
            )
            if observed is not None and (
                earnings_year not in limit
                or decimal(observed) > decimal(limit[earnings_year])
            ):
                raise ValueError(
                    "No-earnings-test assertion conflicts with supplied earnings"
                )
            continue
        high = fra // 12 == earnings_year
        values = pre_fra_earnings if high else earnings
        limits = higher_exempt if high else lower_exempt
        if (
            values is None
            or earnings_year not in values
            or limits is None
            or earnings_year not in limits
        ):
            raise ValueError(
                "Supply annual earnings, and pre-FRA-month earnings in the FRA year, plus exempt amounts"
            )
        if decimal(values[earnings_year]) < 0:
            raise ValueError("Earnings-test earnings must be nonnegative")
        remaining = max(
            Decimal(0), decimal(values[earnings_year]) - decimal(limits[earnings_year])
        ) / (3 if high else 2)
        # RS 02501.080: truncate the annual deduction to whole dollars.
        remaining = Decimal(int(remaining))
        # Fill missing earlier months using the same pure ledger calculation.
        if earnings_year == year - 1 and remaining:
            earlier = calculate_year(
                record,
                earnings_year,
                bend_points=bend_points,
                formula_path=paths,
                cola_events=cola_events,
                policies=policies,
                earnings=earnings,
                pre_fra_earnings=pre_fra_earnings,
                lower_exempt=lower_exempt,
                higher_exempt=higher_exempt,
                recompute_mode=recompute_mode,
                s770_survivor_bend_increase=s770_survivor_bend_increase,
                _include_previous_check=False,
            )
            old = earlier.ledger[-1]
            by_month[old.entitlement_month] = old
            continue
        for n in relevant:
            key = month_string(n)
            if key not in by_month:
                continue
            row = by_month[key]
            reduction = min(row.gross_benefit, remaining)
            remaining -= reduction
            by_month[key] = replace(
                row,
                earnings_test_reduction=reduction,
                payable_benefit=row.gross_benefit - reduction,
            )
    rows = tuple(by_month[row.entitlement_month] for row in rows)
    return AnnualBenefit(
        rows,
        sum(
            (
                r.payable_benefit
                for r in rows
                if r.entitlement_month.startswith(str(year))
            ),
            Decimal(0),
        ),
        sum(
            (r.payable_benefit for r in rows if r.payment_month.startswith(str(year))),
            Decimal(0),
        ),
        sum(
            (
                r.earnings_test_reduction
                for r in rows
                if r.entitlement_month.startswith(str(year))
            ),
            Decimal(0),
        ),
        pia_interval,
        inferred_interval,
    )

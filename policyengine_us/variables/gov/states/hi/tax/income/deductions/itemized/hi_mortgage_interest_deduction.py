from policyengine_us.model_api import *
from policyengine_us.variables.household.expense.tax_unit.mortgage_interest_structure import (
    _debt_by_vintage,
)


def _hi_qualified_loan_limit(
    grandfathered_debt,
    other_debt,
    home_acquisition_debt_limit,
    home_equity_debt_limit,
):
    """2017 IRS Publication 936, Table 1, lines 1-8, as Hawaii applies it.

    Hawaii makes IRC 163(h)(3)(F) inoperative, so it never lowers the
    acquisition-debt limit for later debt or suspends home equity interest.
    Grandfathered debt, incurred on or before October 13, 1987, has no dollar
    limit but reduces the acquisition-debt limit for other debt (lines 1-6).
    Debt above the acquisition-debt limit may qualify as home equity debt, up
    to the home equity debt limit (line 7; Publication 936 (2017), Figure A,
    note 3). The home equity debt limit is also capped by each home's fair
    market value less its acquisition debt; PolicyEngine has no home value
    input, so every home is treated as worth at least its mortgages.
    """
    total_debt = grandfathered_debt + other_debt
    # Lines 3-6.
    line_6 = min_(max_(grandfathered_debt, home_acquisition_debt_limit), total_debt)
    # Line 7.
    line_7 = min_(total_debt - line_6, home_equity_debt_limit)
    # Line 8.
    return line_6 + line_7


def _hi_deductible_share(qualified_loan_limit, total_debt):
    """2017 IRS Publication 936, Table 1, line 11.

    The worksheet specifies the qualified loan limit divided by total debt,
    "rounded to three places"; PE uses half-up rounding at ties. Interest is
    treated as within the limits, a share of one, when no balance is
    reported, as in the federal calculation. The
    ratio is computed in double precision: in single precision a ratio just
    below a half-thousandth, such as $1,100,000 / $1,128,784 = .97449999,
    rounds the wrong way.
    """
    limit = np.asarray(qualified_loan_limit, dtype=np.float64)
    debt = np.asarray(total_debt, dtype=np.float64)
    ratio = np.divide(limit, debt, out=np.ones_like(debt), where=debt > 0)
    return np.floor(ratio * 1_000 + 0.5) / 1_000


def _hi_allowed_interest(deductible, non_deductible, deductible_share):
    """N-11 / Publication 936 worksheet with a PE federal-floor safeguard.

    The law does not prescribe allocation rounding, so the N-11 / 2017
    Publication 936 worksheet supplies a gap-fill: line 11 rounds the share
    to three places, and line 12 multiplies interest paid by that share.
    Interest paid (line 10) is the federally deductible and non-deductible
    parts together.

    PE separately floors that worksheet result at its federal deduction.
    This safeguard is PE's chosen approximation, not worksheet line 12; it
    prevents rounded Hawaii interest from falling below PE's unrounded
    federal calculation. When federal law disallows none of the interest,
    keeping the federal amount also passes through a deduction supplied
    directly, which the federal limits have already reduced.
    """
    hawaii = (deductible + non_deductible) * deductible_share
    return where(non_deductible > 0, max_(hawaii, deductible), deductible)


class hi_mortgage_interest_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Hawaii home mortgage interest deduction"
    unit = USD
    definition_period = YEAR
    documentation = (
        "Home mortgage interest Hawaii allows. Hawaii makes IRC 163(h)(3)(F) "
        "inoperative, so it keeps the pre-TCJA limits whenever the debt was "
        "incurred: interest on up to $1,000,000 of home acquisition debt plus "
        "$100,000 of home equity debt ($500,000 and $50,000 for married "
        "filing separately), rather than the federal $750,000 limit for debt "
        "incurred after December 15, 2017. The N-11 / Publication 936 "
        "worksheet fills the law's allocation-rounding gap; PE separately "
        "preserves its federal deduction as a safeguard."
    )
    reference = (
        # HRS 235-2.4(j)(3), 235-2.5(b) and 235-3(a): retained limits,
        # authority to adopt Treasury regulations and conformity of forms.
        # PDF pages 11, 16-17.
        "https://files.hawaii.gov/tax/legal/hrs/hrs_235.pdf#page=11",
        # Act 35, SLH 2026, HRS 235-2.4(i)(3)
        "https://data.capitol.hawaii.gov/sessions/session2026/bills/GM1135_.PDF#page=21",
        # HAR 18-235-2.3(a)(3) adopts federal regulations through January 1,
        # 1979, before the 1987 temporary mortgage-interest regulation.
        "https://files.hawaii.gov/tax/legal/har/har_235.pdf#page=15",
        # Treasury Regulation 1.163-10T(c)-(g): alternative allocation
        # methods without prescribed decimal rounding. PDF pages 3-4, 6.
        "https://www.govinfo.gov/content/pkg/CFR-2025-title26-vol3/pdf/CFR-2025-title26-vol3-sec1-163-10T.pdf#page=3",
        # CCA 201201017 (nonprecedential): reasonable allocation methods
        # and approximations under the later debt limits.
        "https://www.irs.gov/pub/irs-wd/1201017.pdf#page=5",
        # 2025 N-11 instructions, line 21c
        "https://files.hawaii.gov/tax/forms/2025/n11ins.pdf#page=17",
        # 2017 Publication 936, Figure A note 3 (PDF page 3), home equity debt
        # limit (PDF page 10) and Table 1 (PDF page 11, including the
        # three-place rounding and multiplication, without PE's floor).
        "https://www.irs.gov/pub/irs-prior/p936--2017.pdf#page=3",
    )
    defined_for = StateCode.HI

    def formula(tax_unit, period, parameters):
        balances = [
            tax_unit("first_home_mortgage_balance", period).astype(np.float64),
            tax_unit("second_home_mortgage_balance", period).astype(np.float64),
        ]
        origination_years = [
            tax_unit("first_home_mortgage_origination_year", period),
            tax_unit("second_home_mortgage_origination_year", period),
        ]
        p_irs = parameters(period).gov.irs.deductions.itemized.interest.mortgage
        grandfathered_debt, pre_tcja_debt, post_tcja_debt = _debt_by_vintage(
            balances,
            origination_years,
            p_irs.grandfathered_origination_year,
            p_irs.pre_tcja_origination_year,
        )
        # Hawaii has one limit for debt incurred after October 13, 1987,
        # whenever it was incurred.
        other_debt = pre_tcja_debt + post_tcja_debt
        filing_status = tax_unit("filing_status", period)
        p = parameters(period).gov.states.hi.tax.income.deductions.itemized.interest
        qualified_loan_limit = _hi_qualified_loan_limit(
            grandfathered_debt,
            other_debt,
            p.home_acquisition_debt_limit[filing_status],
            p.home_equity_debt_limit[filing_status],
        )
        # Lines 9 and 11. The 2025 N-11 instructions send filers to this
        # worksheet, which supplies the rounding gap-fill; PolicyEngine's
        # federal calculation uses the unrounded ratio.
        total_debt = grandfathered_debt + other_debt
        deductible_share = _hi_deductible_share(qualified_loan_limit, total_debt)
        # Worksheet lines 10 and 12, with PE's separate federal-floor safeguard.
        return _hi_allowed_interest(
            add(tax_unit, period, ["deductible_mortgage_interest"]),
            add(tax_unit, period, ["non_deductible_mortgage_interest"]),
            deductible_share,
        )

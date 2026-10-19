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

    The qualified loan limit divided by the total debt, "rounded to three
    places" (half up). Interest is treated as within the limits, a share of
    one, when no balance is reported, as in the federal calculation.
    """
    ratio = np.divide(
        qualified_loan_limit,
        total_debt,
        out=np.ones_like(total_debt),
        where=total_debt > 0,
    )
    return np.floor(ratio * 1_000 + 0.5) / 1_000


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
        "incurred after December 15, 2017."
    )
    reference = (
        # HRS 235-2.4(j)(3)
        "https://data.capitol.hawaii.gov/hrscurrent/Vol04_Ch0201-0257/HRS0235/HRS_0235-0002_0004.htm",
        # Act 35, SLH 2026, HRS 235-2.4(i)(3)
        "https://data.capitol.hawaii.gov/sessions/session2026/bills/HB2329_CD1_.pdf#page=20",
        # 2025 N-11 instructions, line 21c
        "https://files.hawaii.gov/tax/forms/2025/n11ins.pdf#page=17",
        # 2017 Publication 936, Figure A note 3 (PDF page 3), home equity debt
        # limit (PDF page 10) and Table 1 (PDF page 11)
        "https://www.irs.gov/pub/irs-prior/p936--2017.pdf#page=3",
    )
    defined_for = StateCode.HI

    def formula(tax_unit, period, parameters):
        balances = [
            tax_unit("first_home_mortgage_balance", period),
            tax_unit("second_home_mortgage_balance", period),
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
        # worksheet, which rounds the ratio; the federal calculation uses the
        # exact ratio.
        total_debt = grandfathered_debt + other_debt
        deductible_share = _hi_deductible_share(qualified_loan_limit, total_debt)
        # Line 10: interest before any limit, the federally deductible and
        # non-deductible parts together. Line 12 multiplies it by line 11.
        interest = add(tax_unit, period, ["mortgage_interest"])
        return interest * deductible_share

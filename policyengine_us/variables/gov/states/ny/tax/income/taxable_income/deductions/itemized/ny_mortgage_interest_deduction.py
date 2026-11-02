from policyengine_us.model_api import *


def _ny_qualified_loan_limit(
    grandfathered_debts,
    other_debts,
    non_acquisition_debts,
    fair_market_values,
    home_acquisition_debt_limit,
    home_equity_debt_limit,
):
    """Pre-TCJA IRC 163(h)(3)(B)-(D), which N.Y. Tax Law 615(a) preserves.

    Each argument except the limits is a list with one array per home.

    Grandfathered debt, incurred on or before October 13, 1987, has no dollar
    limit but reduces the acquisition-debt limit for other acquisition debt
    (2017 Publication 936, Table 1, lines 1-6). Acquisition debt above that
    limit, and debt that was never acquisition debt, may qualify as home
    equity debt (Figure A, note 3). On each home, home equity debt cannot
    exceed the home's fair market value less the debt on it treated as
    acquisition or grandfathered debt (IRC 163(h)(3)(C)(i)); across homes it
    cannot exceed the home equity debt limit (line 7).

    The limit on other acquisition debt is shared among homes in proportion
    to each home's other acquisition debt; the statute's aggregate limit does
    not say how to place it on a particular home.
    """
    grandfathered_debt = sum(grandfathered_debts)
    other_debt = sum(other_debts)
    acquisition_debt = grandfathered_debt + other_debt
    # Lines 3-6: debt treated as acquisition or grandfathered debt.
    line_6 = min_(
        max_(grandfathered_debt, home_acquisition_debt_limit), acquisition_debt
    )
    other_debt_treated = line_6 - grandfathered_debt
    home_equity_debt = 0
    for grandfathered, other, non_acquisition, fair_market_value in zip(
        grandfathered_debts, other_debts, non_acquisition_debts, fair_market_values
    ):
        other_share = np.divide(
            other,
            other_debt,
            out=np.zeros_like(other_debt),
            where=other_debt > 0,
        )
        treated = grandfathered + other_debt_treated * other_share
        excess_acquisition = other - other_debt_treated * other_share
        equity_room = max_(fair_market_value - treated, 0)
        home_equity_debt = home_equity_debt + min_(
            excess_acquisition + non_acquisition, equity_room
        )
    # Line 7.
    line_7 = min_(home_equity_debt, home_equity_debt_limit)
    # Line 8.
    return line_6 + line_7


def _ny_deductible_share(qualified_loan_limit, total_debt):
    """2017 Publication 936, Table 1, line 11.

    The worksheet divides the qualified loan limit by total debt, rounded to
    three places; PE rounds half up. Interest is treated as within the
    limits, a share of one, when no balance is reported, as in the federal
    calculation. The ratio is computed in double precision so that single
    precision cannot move a ratio across a rounding boundary.
    """
    limit = np.asarray(qualified_loan_limit, dtype=np.float64)
    debt = np.asarray(total_debt, dtype=np.float64)
    ratio = np.divide(limit, debt, out=np.ones_like(debt), where=debt > 0)
    return np.floor(ratio * 1_000 + 0.5) / 1_000


def _ny_allowed_interest(
    deductible, non_deductible, non_acquisition_debt, deductible_share
):
    """Worksheet lines 10 and 12, with PE's federal pass-through and floor.

    Interest paid (line 10) is the federally deductible and non-deductible
    parts together, the raw interest rather than the federally allowed
    amount. When federal law disallows none of the interest and no
    non-acquisition debt is reported, New York's limits are at least as
    large as the federal ones, so the federal amount passes through; this
    keeps a deduction supplied directly. Otherwise the worksheet result
    applies, floored at the federal deduction when no non-acquisition debt
    is reported so that rounding to three places cannot take New York below
    PE's unrounded federal amount. The federal calculation does not see
    non-acquisition debt, so no floor applies when it is reported.
    """
    worksheet = (deductible + non_deductible) * deductible_share
    has_non_acquisition_debt = non_acquisition_debt > 0
    floor = where(has_non_acquisition_debt, 0, deductible)
    uses_worksheet = (non_deductible > 0) | has_non_acquisition_debt
    return where(uses_worksheet, max_(worksheet, floor), deductible)


class ny_mortgage_interest_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "New York home mortgage interest deduction"
    unit = USD
    definition_period = YEAR
    documentation = (
        "Home mortgage interest New York allows. N.Y. Tax Law 615(a) computes "
        "New York itemized deductions as they existed immediately before "
        "P.L. 115-97, so from 2018 New York keeps interest on up to "
        "$1,000,000 of home acquisition debt plus $100,000 of home equity "
        "debt ($500,000 and $50,000 for married filing separately), rather "
        "than the federal $750,000 limit for debt incurred after December 15, "
        "2017 and the federal suspension of home equity interest. Before 2018 "
        "New York uses the federal amount."
    )
    reference = (
        "https://www.nysenate.gov/legislation/laws/TAX/615",
        # L.2018, chapter 59, Part JJ, sections 3 and 7. PDF pages 42-43.
        "https://legislation.nysenate.gov/pdf/bills/2017/S7509C#page=42",
        "https://www.tax.ny.gov/pit/file/itemized-deductions-2025.htm#interest",
        # 26 U.S.C. 163(h)(3)(B)-(D), 2017 edition.
        "https://www.govinfo.gov/content/pkg/USCODE-2017-title26/html/USCODE-2017-title26-subtitleA-chap1-subchapB-partVI-sec163.htm",
        # 2017 Publication 936: debt definitions, home equity debt limit,
        # Table 1 and grandfathered debt.
        # PDF pages 3, 10-11, 13
        "https://www.irs.gov/pub/irs-prior/p936--2017.pdf#page=3",
    )
    defined_for = StateCode.NY

    def formula(tax_unit, period, parameters):
        # Before 2018, New York's itemized deductions follow the federal ones.
        return add(tax_unit, period, ["deductible_mortgage_interest"])

    def formula_2018(tax_unit, period, parameters):
        balances = [
            tax_unit("first_home_mortgage_balance", period).astype(np.float64),
            tax_unit("second_home_mortgage_balance", period).astype(np.float64),
        ]
        origination_years = [
            tax_unit("first_home_mortgage_origination_year", period),
            tax_unit("second_home_mortgage_origination_year", period),
        ]
        non_acquisition_debts = [
            tax_unit("ny_first_home_non_acquisition_debt", period).astype(np.float64),
            tax_unit("ny_second_home_non_acquisition_debt", period).astype(np.float64),
        ]
        fair_market_values = [
            tax_unit("ny_first_home_fair_market_value", period).astype(np.float64),
            tax_unit("ny_second_home_fair_market_value", period).astype(np.float64),
        ]
        p_irs = parameters(period).gov.irs.deductions.itemized.interest.mortgage
        # The shared origination-year convention: a loan from 1987 or earlier
        # is grandfathered debt, and 0 means unknown, not grandfathered.
        grandfathered_debts = [
            where(
                (year > 0) & (year <= p_irs.grandfathered_origination_year),
                balance,
                0,
            )
            for balance, year in zip(balances, origination_years)
        ]
        other_debts = [
            balance - grandfathered
            for balance, grandfathered in zip(balances, grandfathered_debts)
        ]
        filing_status = tax_unit("filing_status", period)
        p = parameters(period).gov.states.ny.tax.income.deductions.itemized.interest
        qualified_loan_limit = _ny_qualified_loan_limit(
            grandfathered_debts,
            other_debts,
            non_acquisition_debts,
            fair_market_values,
            p.home_acquisition_debt_limit[filing_status],
            p.home_equity_debt_limit[filing_status],
        )
        non_acquisition_debt = sum(non_acquisition_debts)
        # Line 9: total average balances.
        total_debt = sum(balances) + non_acquisition_debt
        deductible_share = _ny_deductible_share(qualified_loan_limit, total_debt)
        return _ny_allowed_interest(
            add(tax_unit, period, ["deductible_mortgage_interest"]),
            add(tax_unit, period, ["non_deductible_mortgage_interest"]),
            non_acquisition_debt,
            deductible_share,
        )

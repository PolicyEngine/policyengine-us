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
    acquisition or grandfathered debt (IRC 163(h)(3)(C)(i)); a value of 0
    means unknown and sets no such limit. Across homes, home equity debt
    cannot exceed the home equity debt limit (line 7).

    PE shares the limit on other acquisition debt among homes in proportion
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
        # 0 means unknown: treat the home as worth at least the debt on it,
        # as the Hawaii calculation does.
        equity_room = where(
            fair_market_value > 0, max_(fair_market_value - treated, 0), np.inf
        )
        home_equity_debt = home_equity_debt + min_(
            excess_acquisition + non_acquisition, equity_room
        )
    # Line 7.
    line_7 = min_(home_equity_debt, home_equity_debt_limit)
    # Line 8.
    return line_6 + line_7


def _ny_deductible_share(qualified_loan_limit, total_debt):
    """2017 Publication 936, Table 1, line 11, or the unrounded ratio.

    Until regulations issue, the House report on OBRA 1987 allows any
    reasonable method of allocating interest on debt above the limits. The
    IRS accepts the worksheet, which rounds the ratio to three places, and
    the regulation's simplified method, which uses the unrounded ratio
    (Treas. Reg. 1.163-10T(d); CCA 201201017). A taxpayer can use either, so
    the larger share applies; PE rounds half up. The share is one when the
    household reports no balance, as in the federal calculation. PE computes the
    ratio in double precision so that single precision cannot move it
    across a rounding boundary.
    """
    limit = np.asarray(qualified_loan_limit, dtype=np.float64)
    debt = np.asarray(total_debt, dtype=np.float64)
    ratio = np.divide(limit, debt, out=np.ones_like(debt), where=debt > 0)
    # Round the scaled ratio first. In binary, 1,001,000 / 2,000,000 x 1,000
    # comes to 500.49999999999994, so the floor alone rounds this exact tie down.
    worksheet = np.floor(np.round(ratio * 1_000, 9) + 0.5) / 1_000
    return np.maximum(worksheet, ratio)


def _ny_allowed_interest(
    deductible, non_deductible, non_acquisition_debt, deductible_share
):
    """Worksheet lines 10 and 12, with PE's federal pass-through.

    Interest paid (line 10) is the federally deductible and non-deductible
    parts together, the raw interest rather than the federally allowed
    amount. When federal law disallows none of the interest and the
    household reports no non-acquisition debt, the federal amount passes
    through, which keeps a deduction supplied directly. Otherwise line 12
    applies. New York's limits never fall below the federal ones for the
    same loans, so without non-acquisition debt the result never falls
    below PE's federal amount.
    """
    worksheet = (deductible + non_deductible) * deductible_share
    uses_worksheet = (non_deductible > 0) | (non_acquisition_debt > 0)
    return where(uses_worksheet, worksheet, deductible)


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
        # 2017 Publication 936: Figure A note 3, home acquisition debt, home
        # equity debt and its limit, grandfathered debt, and Table 1 with its
        # line 7 instructions.
        # PDF pages 3, 9-11, 13
        "https://www.irs.gov/pub/irs-prior/p936--2017.pdf#page=3",
        # Treasury Regulation 1.163-10T(d) and (g): the unrounded simplified
        # method and the taxpayer's choice of method. PDF pages 3-4, 6.
        "https://www.govinfo.gov/content/pkg/CFR-2025-title26-vol3/pdf/CFR-2025-title26-vol3-sec1-163-10T.pdf#page=3",
        # CCA 201201017 (nonprecedential): any reasonable allocation method.
        # PDF pages 4-5.
        "https://www.irs.gov/pub/irs-wd/1201017.pdf#page=4",
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

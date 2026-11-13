from policyengine_us.model_api import *


def _ny_home_equity_debt(
    other_debts_treated,
    grandfathered_debts,
    other_debts,
    non_acquisition_debts,
    fair_market_values,
):
    """Home equity debt on both homes for one placement of the acquisition limit.

    Each argument is a list with one array per home. other_debts_treated is
    the part of each home's other acquisition debt that the placement treats
    as acquisition debt. On each home, the rest of that debt and the debt that
    was never acquisition debt count as home equity debt, up to the home's
    room. The room is the home's fair market value less the debt on it
    treated as acquisition or grandfathered debt (IRC 163(h)(3)(C)(i)). A
    value of 0 means unknown and sets no room limit.
    """
    home_equity_debt = 0
    for treated_other, grandfathered, other, non_acquisition, value in zip(
        other_debts_treated,
        grandfathered_debts,
        other_debts,
        non_acquisition_debts,
        fair_market_values,
    ):
        treated = grandfathered + treated_other
        # 0 means unknown: treat the home as worth at least the debt on it,
        # as the Hawaii calculation does.
        room = where(value > 0, max_(value - treated, 0), np.inf)
        home_equity_debt = home_equity_debt + min_(
            other - treated_other + non_acquisition, room
        )
    return home_equity_debt


def _ny_qualified_loan_limit(
    grandfathered_debts,
    other_debts,
    origination_years,
    non_acquisition_debts,
    fair_market_values,
    home_acquisition_debt_limit,
    home_equity_debt_limit,
):
    """Pre-TCJA IRC 163(h)(3)(B)-(D), which N.Y. Tax Law 615(a) preserves.

    Each argument except the limits is a list with two arrays: the main home,
    then the second home.

    Grandfathered debt, incurred on or before October 13, 1987, has no dollar
    limit but reduces the acquisition-debt limit for other acquisition debt
    (2017 Publication 936, Table 1, lines 1-6). Acquisition debt above that
    limit, and debt that was never acquisition debt, may qualify as home
    equity debt (Figure A, note 3; Rev. Rul. 2010-25). On each home, home
    equity debt cannot exceed the home's fair market value less the debt on
    it treated as acquisition or grandfathered debt (IRC 163(h)(3)(C)(i)).
    Publication 936 caps the total instead: the sum of the homes' rooms. PE
    applies the statute's room home by home. Across homes, home equity debt
    cannot exceed the home equity debt limit (line 7).

    The acquisition limit is an aggregate, so where it falls decides each
    home's room. Grandfathered debt counts in full on its own home. Until
    regulations issue, the House report on OBRA 1987 asks for a reasonable
    method of placing the rest, and names chronological order as one; CCA
    201201017 accepts any reasonable method. PE uses whichever of two methods
    gives more home equity debt. One shares the limit in proportion to each
    home's other acquisition debt. The other places it loan by loan in the
    order the loans were incurred, so the most recent debt is the excess.
    Loans from the same year can go in either order, and a loan with an
    unknown year (0) counts as the most recent, as in the federal vintage
    rule.
    """
    grandfathered_debt = sum(grandfathered_debts)
    other_debt = sum(other_debts)
    # Lines 3-6: debt treated as acquisition or grandfathered debt.
    line_6 = min_(
        max_(grandfathered_debt, home_acquisition_debt_limit),
        grandfathered_debt + other_debt,
    )
    other_debt_treated = line_6 - grandfathered_debt
    # The limit shared in proportion to each home's other acquisition debt.
    proportional = [
        other_debt_treated
        * np.divide(
            other,
            other_debt,
            out=np.zeros_like(other_debt),
            where=other_debt > 0,
        )
        for other in other_debts
    ]
    # The limit placed on one home's loan first, then the other's.
    first_other, second_other = other_debts
    first_home_part = min_(first_other, other_debt_treated)
    first_loan_first = [first_home_part, other_debt_treated - first_home_part]
    second_home_part = min_(second_other, other_debt_treated)
    second_loan_first = [other_debt_treated - second_home_part, second_home_part]

    def home_equity_debt(other_debts_treated):
        return _ny_home_equity_debt(
            other_debts_treated,
            grandfathered_debts,
            other_debts,
            non_acquisition_debts,
            fair_market_values,
        )

    # The older loan goes first. A year of 0 is unknown and counts as the
    # most recent; loans from the same year can go in either order.
    first_year, second_year = [
        where(year > 0, year, np.inf) for year in origination_years
    ]
    in_date_order = max_(
        where(first_year <= second_year, home_equity_debt(first_loan_first), 0),
        where(second_year <= first_year, home_equity_debt(second_loan_first), 0),
    )
    # Line 7: the larger of the two methods, up to the home equity debt limit.
    line_7 = min_(
        max_(home_equity_debt(proportional), in_date_order),
        home_equity_debt_limit,
    )
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
    same loans. So without non-acquisition debt, the result never falls below
    the federal amount PE computes from home_mortgage_interest. A
    deductible_mortgage_interest supplied alongside home_mortgage_interest can
    exceed the result.
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
        "P.L. 115-97. So from 2018 New York keeps interest on up to "
        "$1,000,000 of home acquisition debt plus $100,000 of home equity "
        "debt ($500,000 and $50,000 for married filing separately). Federal "
        "law instead limits debt incurred after December 15, 2017 to $750,000 "
        "and allows no interest on home equity debt. The home values come "
        "from primary_residence_value and second_residence_value, where 0 "
        "means unknown. Before 2018 New York uses the federal amount."
    )
    reference = (
        "https://www.nysenate.gov/legislation/laws/TAX/615",
        # L.2018, chapter 59, Part JJ, sections 3 and 7. PDF pages 42-43.
        "https://legislation.nysenate.gov/pdf/bills/2017/S7509C#page=42",
        "https://www.tax.ny.gov/pit/file/itemized-deductions-2025.htm#interest",
        # 2025 Form IT-196 instructions, Limit on home mortgage interest.
        "https://www.tax.ny.gov/pdf/2025/inc/it196i_2025.pdf#page=2",
        # 26 U.S.C. 163(h)(3)(B)-(D) and (h)(4)(A), 2016 edition, the text in
        # force immediately before P.L. 115-97.
        "https://www.govinfo.gov/content/pkg/USCODE-2016-title26/html/USCODE-2016-title26-subtitleA-chap1-subchapB-partVI-sec163.htm",
        # 2017 Publication 936: Figure A note 3, home acquisition debt, home
        # equity debt and its limit, grandfathered debt, and Table 1 with its
        # line 7 instructions.
        # PDF pages 3, 9-11, 13
        "https://www.irs.gov/pub/irs-prior/p936--2017.pdf#page=3",
        # Rev. Rul. 2010-25, 2010-44 I.R.B. 571: acquisition debt above the
        # $1,000,000 limit can be home equity debt, as Figure A note 3 says.
        "https://www.irs.gov/irb/2010-44_IRB#RR-2010-25",
        # Treasury Regulation 1.163-10T(d) and (g): the unrounded simplified
        # method and the taxpayer's choice of method. PDF pages 3-4, 6.
        "https://www.govinfo.gov/content/pkg/CFR-2025-title26-vol3/pdf/CFR-2025-title26-vol3-sec1-163-10T.pdf#page=3",
        # CCA 201201017 (nonprecedential): the House report on OBRA 1987,
        # whose example of a reasonable allocation is chronological order,
        # and any reasonable method. PDF pages 4-5.
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
            tax_unit("first_home_non_acquisition_debt", period).astype(np.float64),
            tax_unit("second_home_non_acquisition_debt", period).astype(np.float64),
        ]
        # Each member's share of each home's value, summed. Publication 936
        # values a home on the date the last debt was secured by it; PE uses
        # these values and the current balances instead.
        fair_market_values = [
            add(tax_unit, period, ["primary_residence_value"]).astype(np.float64),
            add(tax_unit, period, ["second_residence_value"]).astype(np.float64),
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
            origination_years,
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

from policyengine_us.model_api import *


def _debt_by_vintage(
    balances,
    origination_years,
    grandfathered_origination_year,
    pre_tcja_origination_year,
):
    """Sum loan balances into IRS Publication 936 Table 1 lines 1, 2 and 7.

    Returns grandfathered debt (incurred on or before October 13, 1987), other
    debt incurred on or before December 15, 2017, and later debt. Only the
    calendar year is known, so each cutoff year counts as the older vintage.
    An origination year of 0 or less is unknown and counts as later debt.
    """
    grandfathered_debt = pre_tcja_debt = post_tcja_debt = 0
    for balance, year in zip(balances, origination_years):
        grandfathered = (year > 0) & (year <= grandfathered_origination_year)
        pre_tcja = (year > grandfathered_origination_year) & (
            year <= pre_tcja_origination_year
        )
        grandfathered_debt = grandfathered_debt + where(grandfathered, balance, 0)
        pre_tcja_debt = pre_tcja_debt + where(pre_tcja, balance, 0)
        post_tcja_debt = post_tcja_debt + where(grandfathered | pre_tcja, 0, balance)
    return grandfathered_debt, pre_tcja_debt, post_tcja_debt


def _qualified_loan_limit(
    grandfathered_debt, pre_tcja_debt, post_tcja_debt, pre_tcja_cap, post_tcja_cap
):
    """IRS Publication 936 Table 1, lines 3-6 and 8-11.

    Grandfathered debt has no dollar limit, but it reduces the limit for other
    debt (26 U.S.C. 163(h)(3)(D)). Debt incurred on or before December 15,
    2017 keeps the $1,000,000 limit, and reduces the $750,000 limit for later
    debt (26 U.S.C. 163(h)(3)(F)). The result never depends on which slot a
    loan is in.
    """
    # Lines 3-6.
    line_6 = min_(
        max_(grandfathered_debt, pre_tcja_cap), grandfathered_debt + pre_tcja_debt
    )
    # Lines 8-11.
    return min_(max_(line_6, post_tcja_cap), line_6 + post_tcja_debt)


class first_home_mortgage_balance(Variable):
    value_type = float
    entity = TaxUnit
    label = "First home mortgage balance"
    unit = USD
    definition_period = YEAR
    default_value = 0
    documentation = (
        "Outstanding balance on the first home acquisition mortgage used to "
        "calculate the federal mortgage interest deduction."
    )


class second_home_mortgage_balance(Variable):
    value_type = float
    entity = TaxUnit
    label = "Second home mortgage balance"
    unit = USD
    definition_period = YEAR
    default_value = 0
    documentation = (
        "Outstanding balance on the second home acquisition mortgage used to "
        "calculate the federal mortgage interest deduction."
    )


class first_home_mortgage_interest(Variable):
    value_type = float
    entity = TaxUnit
    label = "First home mortgage interest"
    unit = USD
    definition_period = YEAR
    default_value = 0
    documentation = (
        "DEPRECATED (issue #9275): use the person-level home_mortgage_interest "
        "input instead; the deduction only ever uses the first+second sum, and "
        "this input is read only when no person-level interest is reported. "
        "Kept temporarily so existing datasets that supply it keep working; "
        "removal is scheduled once certified microdata stops exporting it."
    )


class second_home_mortgage_interest(Variable):
    value_type = float
    entity = TaxUnit
    label = "Second home mortgage interest"
    unit = USD
    definition_period = YEAR
    default_value = 0
    documentation = (
        "DEPRECATED (issue #9275): use the person-level home_mortgage_interest "
        "input instead; the deduction only ever uses the first+second sum, and "
        "this input is read only when no person-level interest is reported. "
        "Kept temporarily so existing datasets that supply it keep working; "
        "removal is scheduled once certified microdata stops exporting it."
    )


_ORIGINATION_YEAR_CONVENTION = (
    "The federal debt limits treat 1987 as on or before October 13, 1987 and "
    "2017 as on or before December 15, 2017. A refinancing that still counts as "
    "grandfathered debt takes the original debt's year: up to the principal "
    "refinanced, and only for the original term or, for a balloon loan, the "
    "first refinancing's term up to 30 years (26 U.S.C. 163(h)(3)(D)(iii)-(iv)). "
    "Enter 0 if unknown."
)


class first_home_mortgage_origination_year(Variable):
    value_type = int
    entity = TaxUnit
    label = "First home mortgage origination year"
    definition_period = YEAR
    default_value = 0
    documentation = (
        "Calendar year when the first home acquisition mortgage originated. "
        + _ORIGINATION_YEAR_CONVENTION
    )


class second_home_mortgage_origination_year(Variable):
    value_type = int
    entity = TaxUnit
    label = "Second home mortgage origination year"
    definition_period = YEAR
    default_value = 0
    documentation = (
        "Calendar year when the second home acquisition mortgage originated. "
        + _ORIGINATION_YEAR_CONVENTION
    )


class home_mortgage_interest_tax_unit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Tax unit home mortgage interest"
    unit = USD
    definition_period = YEAR
    documentation = (
        "Total home mortgage interest. The person-level home_mortgage_interest "
        "input is canonical; the deprecated structured first/second interest "
        "inputs are used only when no person-level interest is reported "
        "(existing datasets still supply them — see issue #9275)."
    )

    def formula(tax_unit, period, parameters):
        reported_interest = add(tax_unit, period, ["home_mortgage_interest"])
        structured_interest = add(
            tax_unit,
            period,
            ["first_home_mortgage_interest", "second_home_mortgage_interest"],
        )
        return where(reported_interest > 0, reported_interest, structured_interest)


class deductible_mortgage_interest_tax_unit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Tax unit deductible mortgage interest"
    unit = USD
    definition_period = YEAR
    documentation = (
        "Federal deductible mortgage interest after applying the statutory "
        "acquisition-debt caps to up to two mortgages. Grandfathered debt, "
        "incurred on or before October 13, 1987, has no dollar limit but "
        "reduces the limits for other debt; debt incurred on or before "
        "December 15, 2017 keeps the $1,000,000 limit and reduces the $750,000 "
        "limit for later debt (IRS Publication 936, Table 1)."
    )
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/163#h_3",
        # PDF pages 13-14
        "https://www.irs.gov/pub/irs-prior/p936--2025.pdf#page=13",
    )

    def formula(tax_unit, period, parameters):
        first_balance = tax_unit("first_home_mortgage_balance", period)
        second_balance = tax_unit("second_home_mortgage_balance", period)
        first_year = tax_unit("first_home_mortgage_origination_year", period)
        second_year = tax_unit("second_home_mortgage_origination_year", period)
        total_balance = first_balance + second_balance
        # Falls back to reported person-level interest when the structured
        # first/second inputs are absent.
        total_interest = tax_unit("home_mortgage_interest_tax_unit", period)

        filing_status = tax_unit("filing_status", period)
        p = parameters(period).gov.irs.deductions.itemized.interest.mortgage
        grandfathered_debt, pre_tcja_debt, post_tcja_debt = _debt_by_vintage(
            [first_balance, second_balance],
            [first_year, second_year],
            p.grandfathered_origination_year,
            p.pre_tcja_origination_year,
        )
        limited_balance = _qualified_loan_limit(
            grandfathered_debt,
            pre_tcja_debt,
            post_tcja_debt,
            p.pre_tcja_cap[filing_status],
            p.cap[filing_status],
        )

        # When no acquisition-debt balance is provided, assume the mortgage is
        # within the statutory caps and fully deductible, rather than treating a
        # $0 balance as making the interest entirely non-deductible.
        deductible_share = np.ones_like(total_balance)
        mask = total_balance > 0
        deductible_share[mask] = np.minimum(
            1, limited_balance[mask] / total_balance[mask]
        )
        return total_interest * deductible_share


class non_deductible_mortgage_interest_tax_unit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Tax unit non-deductible mortgage interest"
    unit = USD
    definition_period = YEAR
    documentation = (
        "Home mortgage interest that is not deductible federally because it "
        "exceeds the acquisition-debt caps."
    )

    def formula(tax_unit, period, parameters):
        total_interest = tax_unit("home_mortgage_interest_tax_unit", period)
        deductible_interest = tax_unit("deductible_mortgage_interest_tax_unit", period)
        return max_(0, total_interest - deductible_interest)

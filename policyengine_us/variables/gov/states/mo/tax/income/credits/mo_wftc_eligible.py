from policyengine_us.model_api import *


class mo_wftc_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the Missouri Working Families Tax Credit"
    definition_period = YEAR
    reference = (
        "https://revisor.mo.gov/main/OneSection.aspx?section=143.177&bid=49978&hl=",
        "https://dor.mo.gov/forms/MO-1040%20Instructions_2025.pdf#page=43",
    )
    defined_for = StateCode.MO

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.mo.tax.income.credits.wftc
        # RSMo 143.177.2 defines an eligible taxpayer as one allowed a
        # federal earned income tax credit; Form MO-WFTC Line 1 stops
        # filers without one.
        has_federal_eitc = tax_unit("eitc", period) > 0
        # RSMo 143.177.2 limits the credit to filing statuses of single,
        # head of household, widowed, or married filing combined, excluding
        # married filing separately.
        filing_status = tax_unit("filing_status", period)
        separate = filing_status == filing_status.possible_values.SEPARATE
        # The 2024 and 2025 Form MO-WFTC checklists also stop filers
        # claimed as a dependent on another return; the 2023 form does not.
        excluded_dependent = p.dependent_filers_excluded & tax_unit(
            "head_is_dependent_elsewhere", period
        )
        # Form MO-WFTC applies Missouri's own investment income limit,
        # reflecting IRC Section 32(i) as of January 1, 2021 per RSMo
        # 143.177.3(1), which is far below the current-law federal limit.
        # Missouri defines investment income from Form 1040 lines (taxable
        # and tax-exempt interest, ordinary dividends, and positive capital
        # gain net income, with an IRS Publication 596 worksheet fallback);
        # we approximate it with the federal EITC investment income measure.
        # The 2023 form disqualifies at "equal to or greater than" the limit
        # in both its checklist and its Line 3 instructions, though its own
        # information page says income "cannot exceed" the limit; the 2024
        # and 2025 forms use "greater than" throughout. We follow the strict
        # "exceeds" reading of the statutorily referenced pre-ARPA Section
        # 32(i) in all years.
        investment_income = tax_unit("eitc_relevant_investment_income", period)
        meets_investment_limit = investment_income <= p.investment_income_limit
        return (
            has_federal_eitc & ~separate & ~excluded_dependent & meets_investment_limit
        )

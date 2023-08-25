from policyengine_us.model_api import *


class or_wfhdc_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Oregon income eligible for WFHDC"
    unit = USD
    documentation = "Oregon househod income eligible for Working Family Household and Dependent Care Credit"
    definition_period = YEAR
    reference = (
        "https://www.oregon.gov/dor/forms/FormsPubs/publication-or-17_101-431_2021.pdf#page=121",
        "https://www.oregonlegislature.gov/bills_laws/ors/ors315.html",
    )
    defined_for = StateCode.OR

    def formula(tax_unit, period, parameters):
        # Get the parameter tree for the Oregon WFHDC.
        p = parameters(period).gov.states["or"].tax.income.credits.wfhdc

        # Get the household size.
        household_size = tax_unit("tax_unit_size", period)

        # Get the income threshold based on household size.
        income_threshold = p.eligible.income_threshold[household_size]

        # Get the household income, considered the larger of federal and Oregon AGI.
        federal_agi = tax_unit("adjusted_gross_income", period)
        or_agi = tax_unit("or_income_after_subtractions", period)
        household_income = max_(federal_agi, or_agi)

        # Determine if the household is eligible for the WFHDC.
        return household_income <= income_threshold

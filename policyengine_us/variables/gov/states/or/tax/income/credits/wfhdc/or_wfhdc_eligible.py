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
        p = (
            parameters(period)
            .gov.states["or"]
            .tax.income.credits.wfhdc.eligible
        )

        # Get the household size.
        household_size = tax_unit("tax_unit_size", period)

        # Check that the household size is large enough.
        size_eligible = household_size >= p.min_household_size

        # Get the income threshold based on household size.
        income_threshold = p.income_threshold.calc(household_size)

        # Get household income, the larger of federal and Oregon AGI.
        federal_agi = tax_unit("adjusted_gross_income", period)
        or_agi = tax_unit("or_income_after_subtractions", period)
        household_income = max_(federal_agi, or_agi)

        # Check if household income is below the threshold.
        income_eligible = household_income <= income_threshold

        # Check if the household has a child or disabled member other than the household head.
        # Note that a disabled spouse is a qualifying individual.
        person = tax_unit.members
        age = person("age", period)
        disabled = person("is_disabled", period)
        head = person("is_tax_unit_head", period)
        qualifying_individuals = (
            age <= p.max_qualifying_nondisabled_child_age
        ) | (disabled & ~head)
        has_qualified_individual = tax_unit.any(qualifying_individuals)

        # Determine if the household is eligible for the WFHDC.
        return size_eligible & income_eligible & has_qualified_individual

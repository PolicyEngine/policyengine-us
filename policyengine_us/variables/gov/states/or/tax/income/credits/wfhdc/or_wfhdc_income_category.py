from policyengine_us.model_api import *


class or_wfhdc_income_category(Variable):
    value_type = int
    entity = TaxUnit
    label = "Oregon working family household and dependent care credit percentage table row letter"
    unit = USD
    definition_period = YEAR
    defined_for = "or_wfhdc_eligible"
    reference = "https://www.oregon.gov/dor/forms/FormsPubs/publication-or-wfhdc-tb_101-458_2021.pdf#page=1"

    def formula(tax_unit, period, parameters):
        # Get the parameter tree for the WFHDC table row letter.
        p = (
            parameters(period)
            .gov.states["or"]
            .tax.income.credits.wfhdc.household_size
        )

        # Get the household size.
        household_size = tax_unit("tax_unit_size", period)

        # Get the household income, considered the larger of federal and Oregon AGI.
        federal_agi = tax_unit("adjusted_gross_income", period)
        or_income_after_subtractions = tax_unit(
            "or_income_after_subtractions", period
        )
        household_income = max_(federal_agi, or_income_after_subtractions)

        # Get the table row number based on household size and income.
        return select(
            [
                household_size == 2,
                household_size == 3,
                household_size == 4,
                household_size == 5,
                household_size == 6,
                household_size == 7,
                household_size >= 8,
            ],
            [
                p.two.calc(household_income, right=True),
                p.three.calc(household_income, right=True),
                p.four.calc(household_income, right=True),
                p.five.calc(household_income, right=True),
                p.six.calc(household_income, right=True),
                p.seven.calc(household_income, right=True),
                p.eight_or_more.calc(household_income, right=True),
            ],
            default=0,
        )

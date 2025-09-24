from policyengine_us.model_api import *


class mi_household_resources(Variable):
    value_type = float
    entity = TaxUnit
    label = "Michigan household resources"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MI
    reference = "https://law.justia.com/codes/michigan/2022/chapter-206/statute-act-281-of-1967/division-281-1967-1/division-281-1967-1-9/section-206-508/"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.mi.tax.income
        household_resources = add(tax_unit, period, p.household_resources)
        health_insurance_premiums = add(
            tax_unit, period, ["health_insurance_premiums"]
        )
        above_the_line_deductions = tax_unit(
            "above_the_line_deductions", period
        )
        return max_(
            0,
            household_resources
            - health_insurance_premiums
            - above_the_line_deductions,
        )

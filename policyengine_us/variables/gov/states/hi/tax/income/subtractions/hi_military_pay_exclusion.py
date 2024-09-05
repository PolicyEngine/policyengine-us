from policyengine_us.model_api import *


class hi_military_pay_exclusion(Variable):
    value_type = float
    entity = TaxUnit
    label = "Hawaii military reserve or national guard duty pay exclusion"
    unit = USD
    documentation = (
        "https://files.hawaii.gov/tax/forms/2022/n11ins.pdf#page=13"
    )
    definition_period = YEAR
    defined_for = StateCode.HI

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.hi.tax.income.subtractions.military_pay
        person = tax_unit.members
        military_service_income = person("military_service_income", period)
        capped_military_income = min_(military_service_income, p.cap)
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)

        return tax_unit.sum(capped_military_income * head_or_spouse)

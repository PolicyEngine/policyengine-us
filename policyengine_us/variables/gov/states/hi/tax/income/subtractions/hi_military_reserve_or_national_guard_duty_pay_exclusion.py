from policyengine_us.model_api import *


class hi_military_reserve_or_national_guard_duty_pay_exclusion(Variable):
    value_type = float
    entity = TaxUnit
    label = "Hawaii military reserve or national guard duty pay exclusion"
    unit = USD
    documentation = "https://files.hawaii.gov/tax/forms/2022/n11ins.pdf"
    definition_period = YEAR
    defined_for = StateCode.HI

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.hi.tax.income.subtractions
        military_service_income = person("military_service_income", period)
        # hi_national_guard = 
        return min_(military_service_income, p.military_reserve_or_national_guard_duty_pay_exclusion.amount)
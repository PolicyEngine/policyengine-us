from policyengine_us.model_api import *


class md_hundred_year_exemption(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Maryland hundred year exemption eligibility"
    definition_period = YEAR
    reference = "https://trackbill.com/bill/maryland-house-bill-186-income-tax-subtraction-modification-for-centenarians/2173534/"
    defined_for = StateCode.MD

    def formula(tax_unit, period, parameters):
        age = tax_unit("age_head", period)
        p = parameters(period).gov.states.md.tax.income.agi.subtractions.hundred_year
        return age_head >= p.age_threshold

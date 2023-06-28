from policyengine_us.model_api import *


class mt_aged_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "Montana aged exemption"
    unit = USD
    definition_period = YEAR
    reference = "https://mtrevenue.gov/wp-content/uploads/dlm_uploads/2023/05/Montana-Idividiual-Income-Tax-Return-Form-2-2022v6.2.pdf"
    defined_for = StateCode.MT

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.mt.tax.income.exemptions
        aged_head = (tax_unit("age_head", period) >= p.age).astype(int)
        aged_spouse = (tax_unit("age_spouse", period) >= p.age).astype(int)
        return aged_head * p.amount + aged_spouse * p.amount

from policyengine_us.model_api import *


class mt_base_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "Montana base exemption for head and spouse"
    unit = USD
    definition_period = YEAR
    reference = "https://mtrevenue.gov/wp-content/uploads/dlm_uploads/2023/05/Montana-Idividiual-Income-Tax-Return-Form-2-2022v6.2.pdf"
    defined_for = StateCode.MT

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.mt.tax.income.exemptions
        person = tax_unit.members
        return (
            tax_unit.sum(person("is_tax_unit_spouse", period)) + 1
        ) * p.amount

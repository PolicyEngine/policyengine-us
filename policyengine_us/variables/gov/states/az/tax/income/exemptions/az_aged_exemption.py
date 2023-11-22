from policyengine_us.model_api import *


class az_aged_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arizona aged exemption"
    unit = USD
    definition_period = YEAR
    defined_for = "az_aged_exemption_eligible"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.az.tax.income.exemptions
        person = tax_unit.members

        age = person("age", period)
        amount = p.aged.calc(age)
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)

        eligible_amount = amount * head_or_spouse

        return tax_unit.sum(eligible_amount)

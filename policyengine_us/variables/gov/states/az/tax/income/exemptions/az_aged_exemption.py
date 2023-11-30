from policyengine_us.model_api import *


class az_aged_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arizona aged exemption"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.AZ

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.az.tax.income.exemptions
        person = tax_unit.members

        age = person("age", period)
        amount = p.aged.calc(age)
        eligibility = person("az_aged_exemption_eligible_person", period)
        eligible_amount = amount * eligibility

        return tax_unit.sum(eligible_amount)

from policyengine_us.model_api import *


class az_property_tax_credit_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the Arizona Property Tax Credit"
    definition_period = YEAR
    defined_for = StateCode.AZ

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        p = parameters(period).gov.states.az.tax.income.property_tax_credits

        age = person("age", period)
        age_qualifies = age >= p.min_age

        head = person("is_tax_unit_head", period)

        return head & age_qualifies

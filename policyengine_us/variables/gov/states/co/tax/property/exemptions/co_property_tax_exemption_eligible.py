from policyengine_us.model_api import *


class co_property_tax_exemption_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the Colorado property tax exemption"
    definition_period = YEAR
    defined_for = StateCode.CO

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        age = person("age", period)
        p = parameters(period).gov.states.co.tax.exemptions.property_tax
        return tax_unit.any(age >= p.age_eligiblity)

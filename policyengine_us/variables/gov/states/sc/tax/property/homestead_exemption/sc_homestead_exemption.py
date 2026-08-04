from policyengine_us.model_api import *


class sc_homestead_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "South Carolina homestead exemption"
    unit = USD
    definition_period = YEAR
    reference = "https://dor.sc.gov/property/exempt-property"
    defined_for = "sc_homestead_exemption_eligible"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.sc.tax.property.homestead_exemption
        person = tax_unit.members
        head = person("is_tax_unit_head", period)
        joint_spouse = person("is_tax_unit_spouse", period) & person.tax_unit(
            "tax_unit_is_joint", period
        )
        assessed_value = tax_unit.sum(
            person("assessed_property_value", period) * (head | joint_spouse)
        )
        assessed_exemption_amount = p.amount * p.assessment_rate
        return min_(
            assessed_value,
            assessed_exemption_amount,
        )

from policyengine_us.model_api import *


class oh_homestead_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "Ohio homestead exemption"
    unit = USD
    definition_period = YEAR
    reference = "https://codes.ohio.gov/ohio-revised-code/section-323.152"
    defined_for = "oh_homestead_exemption_eligible"

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        head = person("is_tax_unit_head", period)
        spouse_in_joint = person("is_tax_unit_spouse", period) & person.tax_unit(
            "tax_unit_is_joint", period
        )
        assessed_value = tax_unit.sum(
            person("assessed_property_value", period) * (head | spouse_in_joint)
        )
        p = parameters(period).gov.states.oh.tax.property.homestead_exemption
        assessed_exemption_amount = p.amount * p.assessment_rate
        return min_(
            assessed_value,
            assessed_exemption_amount,
        )

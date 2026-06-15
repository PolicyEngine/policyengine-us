from policyengine_us.model_api import *


class oh_homestead_property_tax_reduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Ohio homestead property tax reduction"
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
        head_or_spouse = head | spouse_in_joint
        assessed_value = tax_unit.sum(
            person("assessed_property_value", period) * head_or_spouse
        )
        real_estate_taxes = tax_unit.sum(
            person("real_estate_taxes", period) * head_or_spouse
        )

        return real_estate_taxes * (
            tax_unit("oh_homestead_exemption", period) / max_(assessed_value, 1)
        )

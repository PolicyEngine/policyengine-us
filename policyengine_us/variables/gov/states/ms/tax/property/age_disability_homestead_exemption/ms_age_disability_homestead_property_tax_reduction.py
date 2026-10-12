from policyengine_us.model_api import *


class ms_age_disability_homestead_property_tax_reduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Mississippi age or disability homestead property tax reduction"
    unit = USD
    definition_period = YEAR
    reference = "https://www.dor.ms.gov/county-services/homestead-exemption"
    defined_for = "ms_age_disability_homestead_exemption_eligible"

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        head = person("is_tax_unit_head", period)
        joint_spouse = person("is_tax_unit_spouse", period) & person.tax_unit(
            "tax_unit_is_joint", period
        )
        head_or_joint_spouse = head | joint_spouse
        assessed_value = tax_unit.sum(
            person("assessed_property_value", period) * head_or_joint_spouse
        )
        real_estate_taxes = tax_unit.sum(
            person("real_estate_taxes", period) * head_or_joint_spouse
        )

        return real_estate_taxes * (
            tax_unit("ms_age_disability_homestead_exemption", period)
            / max_(assessed_value, 1)
        )

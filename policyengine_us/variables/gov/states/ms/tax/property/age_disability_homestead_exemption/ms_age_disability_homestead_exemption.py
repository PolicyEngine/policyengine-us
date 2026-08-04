from policyengine_us.model_api import *


class ms_age_disability_homestead_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "Mississippi age or disability homestead exemption"
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
        assessed_value = tax_unit.sum(
            person("assessed_property_value", period) * (head | joint_spouse)
        )

        return min_(
            assessed_value,
            parameters(
                period
            ).gov.states.ms.tax.property.age_disability_homestead_exemption.amount,
        )

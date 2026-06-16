from policyengine_us.model_api import *


class tn_elderly_property_tax_relief(Variable):
    value_type = float
    entity = TaxUnit
    label = "Tennessee elderly property tax relief"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://comptroller.tn.gov/office-functions/pa/property-taxes/property-tax-programs/tax-relief.html",
        "https://comptroller.tn.gov/content/dam/cot/pa/documents/tax-relief/TaxReliefBrochure.pdf#page=2",
        "https://comptroller.tn.gov/content/dam/cot/pa/documents/tax-relief/TCA%2067-5-701%20through%2067-5-704.pdf#page=3",
    )
    defined_for = "tn_elderly_property_tax_relief_eligible"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.tn.tax.property.elderly_property_tax_relief
        person = tax_unit.members
        head = person("is_tax_unit_head", period)
        joint_spouse = person("is_tax_unit_spouse", period) & person.tax_unit(
            "tax_unit_is_joint", period
        )
        head_or_joint_spouse = head | joint_spouse
        assessed_property_value = tax_unit.sum(
            person("assessed_property_value", period) * head_or_joint_spouse
        )
        real_estate_taxes = tax_unit.sum(
            person("real_estate_taxes", period) * head_or_joint_spouse
        )
        capped_assessed_property_value = min_(
            assessed_property_value,
            p.property_value_cap * p.assessment_rate,
        )
        return (
            real_estate_taxes
            * capped_assessed_property_value
            / max_(assessed_property_value, 1)
        )

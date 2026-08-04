from policyengine_us.model_api import *


class sc_homestead_exemption_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the South Carolina Homestead Exemption"
    definition_period = YEAR
    reference = "https://dor.sc.gov/property/exempt-property"
    defined_for = StateCode.SC

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.sc.tax.property.homestead_exemption
        person = tax_unit.members
        head = person("is_tax_unit_head", period)
        joint_spouse = person("is_tax_unit_spouse", period) & person.tax_unit(
            "tax_unit_is_joint", period
        )
        head_or_joint_spouse = head | joint_spouse
        age = person("age", period.this_year)
        is_disabled = person("is_disabled", period)
        is_blind = person("is_blind", period)
        assessed_value = person("assessed_property_value", period)

        return tax_unit.any(
            ((age >= p.age_threshold) | is_disabled | is_blind) & head_or_joint_spouse,
        ) & (tax_unit.sum(assessed_value * head_or_joint_spouse) > 0)

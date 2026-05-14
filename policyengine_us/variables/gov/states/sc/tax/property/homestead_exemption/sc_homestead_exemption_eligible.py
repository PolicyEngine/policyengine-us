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
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        age = person("age", period.this_year)
        is_disabled = person("is_disabled", period)
        is_blind = person("is_blind", period)

        return tax_unit.any(
            ((age >= p.age_threshold) | is_disabled | is_blind) & head_or_spouse,
        ) & (add(tax_unit, period, ["assessed_property_value"]) > 0)

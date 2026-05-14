from policyengine_us.model_api import *


class ms_age_disability_homestead_exemption_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the Mississippi age or disability Homestead Exemption"
    definition_period = YEAR
    reference = "https://www.dor.ms.gov/county-services/homestead-exemption"
    defined_for = StateCode.MS

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.ms.tax.property.age_disability_homestead_exemption
        person = tax_unit.members
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        age = person("age", period.this_year)
        is_disabled = person("is_disabled", period)

        return tax_unit.any(
            ((age >= p.age_threshold) | is_disabled) & head_or_spouse
        ) & (add(tax_unit, period, ["assessed_property_value"]) > 0)

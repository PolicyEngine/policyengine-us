from policyengine_us.model_api import *


class tx_over_65_or_disabled_school_district_homestead_exemption_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the Texas age 65 or older or disabled school district residence homestead exemption"
    documentation = "Models age, disability, and surviving-spouse eligibility with available person-level inputs; it does not verify the deceased spouse's prior qualification or continued residence occupancy beyond the assessed-property proxy."
    definition_period = YEAR
    reference = "https://comptroller.texas.gov/taxes/property-tax/exemptions/"
    defined_for = StateCode.TX

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.tx.tax.property.school_district_homestead_exemption
        age_or_disability_eligible = (
            tax_unit("greater_age_head_spouse", period) >= p.age_threshold
        ) | tax_unit("disabled_tax_unit_head_or_spouse", period)

        person = tax_unit.members
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        age = person("age", period.this_year)
        is_surviving_spouse = person("is_surviving_spouse", period)
        surviving_spouse = tax_unit.any(
            (age >= p.surviving_spouse_age_threshold)
            & is_surviving_spouse
            & head_or_spouse,
        )

        return (age_or_disability_eligible | surviving_spouse) & tax_unit(
            "tx_school_district_homestead_exemption_eligible", period
        )

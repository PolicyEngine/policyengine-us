from policyengine_us.model_api import *


class tx_over_65_or_disabled_school_district_homestead_exemption_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the Texas age 65 or older or disabled school district residence homestead exemption"
    definition_period = YEAR
    reference = "https://comptroller.texas.gov/taxes/property-tax/exemptions/"
    defined_for = StateCode.TX

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.tx.tax.property.school_district_homestead_exemption
        filing_status = tax_unit("filing_status", period)
        person = tax_unit.members
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        age = person("age", period.this_year)
        is_disabled = person("is_disabled", period)
        age_or_disability_eligible = tax_unit.any(
            ((age >= p.age_threshold) | is_disabled) & head_or_spouse,
        )
        surviving_spouse = (
            filing_status == filing_status.possible_values.SURVIVING_SPOUSE
        ) & tax_unit.any(
            (age >= p.surviving_spouse_age_threshold) & head_or_spouse,
        )

        return (age_or_disability_eligible | surviving_spouse) & tax_unit(
            "tx_school_district_homestead_exemption_eligible", period
        )

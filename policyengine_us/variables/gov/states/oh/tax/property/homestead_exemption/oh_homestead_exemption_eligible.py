from policyengine_us.model_api import *


class oh_homestead_exemption_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the Ohio Homestead Exemption"
    definition_period = YEAR
    reference = "https://codes.ohio.gov/ohio-revised-code/section-323.152"
    defined_for = StateCode.OH

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.oh.tax.property.homestead_exemption
        filing_status = tax_unit("filing_status", period)
        person = tax_unit.members
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        age = person("age", period.this_year)
        is_disabled = person("is_disabled", period)
        aged_or_disabled = tax_unit.any(
            ((age >= p.age_threshold) | is_disabled) & head_or_spouse,
        )
        surviving_spouse = (
            filing_status == filing_status.possible_values.SURVIVING_SPOUSE
        ) & tax_unit.any(
            (age >= p.surviving_spouse_age_threshold) & head_or_spouse,
        )

        return (
            (aged_or_disabled | surviving_spouse)
            & (tax_unit("oh_modified_agi", period) <= p.income_limit)
            & (add(tax_unit, period, ["assessed_property_value"]) > 0)
        )

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
        person = tax_unit.members
        head = person("is_tax_unit_head", period)
        spouse_in_joint = person("is_tax_unit_spouse", period) & person.tax_unit(
            "tax_unit_is_joint", period
        )
        head_or_spouse = head | spouse_in_joint
        age = person("age", period.this_year)
        is_disabled = person("is_permanently_and_totally_disabled", period)
        aged_or_disabled = tax_unit.any(
            ((age >= p.age_threshold) | is_disabled) & head_or_spouse,
        )
        # Surviving spouses age 65+ already qualify through the age path.
        surviving_spouse = tax_unit.any(
            (age >= p.surviving_spouse_age_threshold)
            & person("oh_homestead_exemption_qualifying_surviving_spouse", period)
            & head_or_spouse,
        )
        # PolicyEngine has no principal-residence input, so real estate tax
        # paid by the qualifying owner proxies for ownership and occupancy.
        owns_and_occupies_homestead = tax_unit.any(
            (person("real_estate_taxes", period) > 0) & head_or_spouse
        )

        return (
            (aged_or_disabled | surviving_spouse)
            & (
                tax_unit("oh_homestead_exemption_total_income", period)
                <= p.income_limit
            )
            & owns_and_occupies_homestead
        )

from policyengine_us.model_api import *


class nd_renters_refund_eligible(Variable):
    """Approximate claimant eligibility using the tax-unit head or spouse."""

    value_type = bool
    entity = TaxUnit
    label = "Eligible for the North Dakota Renter's Refund"
    definition_period = YEAR
    reference = (
        "https://ndlegis.gov/cencode/t57c02.pdf#page=15",
        "https://ndlegis.gov/cencode/t57c02.pdf#page=16",
        "https://www.tax.nd.gov/sites/www/files/documents/guidelines/homestead-veterans-renters/credits-for-nd-homeowners-renters-guideline.pdf#page=7",
    )
    defined_for = StateCode.ND

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.nd.tax.property.renters_refund
        person = tax_unit.members
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        age = person("age", period.this_year)
        is_permanently_disabled = person("is_permanently_and_totally_disabled", period)
        age_or_disability_eligible = tax_unit.any(
            ((age >= p.age_threshold) | is_permanently_disabled) & head_or_spouse,
        )
        income = tax_unit("nd_renters_refund_income", period)
        rent = add(tax_unit, period, ["rent"])
        property_tax_exempt = tax_unit("nd_renters_refund_property_tax_exempt", period)

        return (
            age_or_disability_eligible
            & (income <= p.income_limit)
            & ((rent * p.rent_rate - income * p.income_rate) > 0)
            & ~property_tax_exempt
        )

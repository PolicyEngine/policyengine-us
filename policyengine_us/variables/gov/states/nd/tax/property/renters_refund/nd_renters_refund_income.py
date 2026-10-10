from policyengine_us.model_api import *


class nd_renters_refund_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "North Dakota Renter's Refund income"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://ndlegis.gov/cencode/t57c02.pdf#page=16",
        "https://www.tax.nd.gov/sites/www/files/documents/guidelines/homestead-veterans-renters/credits-for-nd-homeowners-renters-guideline.pdf#page=2",
    )
    defined_for = StateCode.ND

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.nd.tax.property.renters_refund
        # NDCC 57-02-08.1(5)(c) excludes income excluded by federal or state
        # law. market_income includes wages before payroll deductions, so
        # subtract the separate pretax premium input once from this base.
        # These premiums are disjoint from itemized_medical_expenses,
        # whose medical definition follows state income tax law.
        excluded_premiums = add(tax_unit, period, ["pre_tax_health_insurance_premiums"])
        return max_(
            add(tax_unit, period, p.income_sources)
            - excluded_premiums
            - tax_unit("itemized_medical_expenses", period),
            0,
        )

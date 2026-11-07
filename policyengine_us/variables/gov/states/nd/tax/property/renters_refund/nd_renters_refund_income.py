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

    documentation = (
        "Renter refund income: the listed income sources, less the parts of "
        "market income that federal law excludes and the unreimbursed medical "
        "costs actually paid, and at least zero. The excluded parts are those "
        "of each person's market income components "
        "(nd_renters_refund_federally_excluded_income) and the federal "
        "exclusions the model deducts above the line (excluded_deductions), "
        "which come out of the market income left after the first. Social "
        "security counts in full. "
        "The paid-cost base restores the self-employed premiums excluded from "
        "the federal subtotal: by the federal formula, or as supplied with a "
        "caller's subtotal in itemized_medical_expenses_applied_exclusion. A "
        "caller-supplied subtotal without that amount is used unchanged, "
        "including when components are supplied. Premium inputs use payer "
        "attribution: each person reports premiums that person paid, including "
        "family coverage regardless of whom it covers."
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.nd.tax.property.renters_refund
        # NDCC 57-02-08.1(5)(c) excludes "any amount excluded from income by
        # federal or state law with the exception of income from social
        # security benefits". market_income counts wages before payroll
        # deductions and the tax-exempt parts of several sources in full, so
        # subtract the parts federal law excludes. Social security stays whole.
        person_exclusions = add(
            tax_unit, period, ["nd_renters_refund_federally_excluded_income"]
        )
        # The model deducts some federal exclusions above the line, so
        # market_income still holds the income they exclude: savings bond
        # interest spent on higher education (IRC 135), employer adoption
        # assistance (IRC 137) and income from Puerto Rico and the specified
        # possessions (IRC 931, 933). A household may record the first two on a
        # dependent, so they come out of the tax unit's market income left after
        # the person-level exclusions, and never out of social security.
        market_income_left = max_(
            add(tax_unit, period, ["market_income"]) - person_exclusions, 0
        )
        deducted_exclusions = min_(
            max_(add(tax_unit, period, p.excluded_deductions), 0),
            market_income_left,
        )
        # Restore premiums excluded from the federal subtotal (computed, or
        # supplied with a caller's subtotal).
        medical_expenses = add(
            tax_unit,
            period,
            [
                "itemized_medical_expenses",
                "itemized_medical_expenses_applied_exclusion",
            ],
        )
        return max_(
            add(tax_unit, period, p.income_sources)
            - person_exclusions
            - deducted_exclusions
            - medical_expenses,
            0,
        )

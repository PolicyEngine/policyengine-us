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
        "market income that federal law excludes "
        "(nd_renters_refund_federally_excluded_income) and the unreimbursed "
        "medical costs actually paid, and at least zero. Social security "
        "counts in full. "
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
        excluded_income = add(
            tax_unit, period, ["nd_renters_refund_federally_excluded_income"]
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
            - excluded_income
            - medical_expenses,
            0,
        )

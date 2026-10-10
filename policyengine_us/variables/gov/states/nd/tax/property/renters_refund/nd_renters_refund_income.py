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
        "Renter refund income after unreimbursed medical costs actually paid. "
        "The paid-cost base adds the excluded self-employed premiums back to "
        "the federal medical expense amount, preserving both caller-supplied "
        "subtotals and computed gross costs. Premium inputs use payer "
        "attribution: each person reports premiums that person paid, including "
        "family coverage regardless of whom it covers."
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.nd.tax.property.renters_refund
        # Restore gross paid costs while retaining supplied federal subtotals.
        medical_expenses = add(
            tax_unit,
            period,
            [
                "itemized_medical_expenses",
                "itemized_medical_expenses_excluded_premiums",
            ],
        )
        return max_(
            add(tax_unit, period, p.income_sources) - medical_expenses,
            0,
        )

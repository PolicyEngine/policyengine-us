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
        "Renter refund income after unreimbursed medical costs actually paid. This "
        "independent paid-cost base retains premiums deducted through the federal "
        "self-employed health insurance ALD; interpreting the guidance's federal- "
        "definition cross-reference as importing that exclusion is an alternative "
        "methodology. Premium inputs use payer attribution: each person reports "
        "premiums that person paid, including family coverage regardless of whom "
        "it covers. "
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.nd.tax.property.renters_refund
        return max_(
            add(tax_unit, period, p.income_sources)
            # The refund uses gross income and medical costs actually paid,
            # rather than expenses net of federal above-the-line deductions.
            - add(
                tax_unit,
                period,
                [
                    "medical_expense_health_insurance_premiums",
                    "other_medical_expenses",
                ],
            ),
            0,
        )

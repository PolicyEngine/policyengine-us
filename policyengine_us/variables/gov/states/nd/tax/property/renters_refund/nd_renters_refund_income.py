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
        "The paid-cost base restores the self-employed premiums excluded from "
        "the federal subtotal: by the federal formula, or as supplied with a "
        "caller's subtotal in itemized_medical_expenses_applied_exclusion. A "
        "caller-supplied subtotal without that amount is used unchanged, "
        "including when components are supplied. Premium inputs use payer "
        "attribution: each person reports premiums that person paid, including "
        "family coverage regardless of whom it covers. The federal subtotal "
        "counts only the head's and spouse's premiums, while NDCC "
        "57-02-08.1(5)(c) also takes out medical expenses paid by the "
        "applicant's dependents, so their own premium payments are added "
        "back, to a supplied subtotal as well, since a Schedule A amount never "
        "includes them."
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.nd.tax.property.renters_refund
        # NDCC 57-02-08.1(5)(c) excludes income excluded by federal or state
        # law. market_income includes wages before payroll deductions, so
        # subtract the separate pretax premium input once from this base.
        # These premiums are disjoint from itemized_medical_expenses,
        # whose medical definition follows state income tax law.
        excluded_premiums = add(tax_unit, period, ["pre_tax_health_insurance_premiums"])
        # Restore premiums excluded from the federal subtotal (computed, or
        # supplied with a caller's subtotal).
        filer_medical_expenses = add(
            tax_unit,
            period,
            [
                "itemized_medical_expenses",
                "itemized_medical_expenses_applied_exclusion",
            ],
        )
        # NDCC 57-02-08.1(5)(c) takes out medical expenses "paid during the
        # year by the applicant or the applicant's dependent". The federal
        # subtotal leaves out the dependents' own premium payments, so add
        # them back.
        person = tax_unit.members
        dependent_premiums = tax_unit.sum(
            person("medical_expense_health_insurance_premiums", period)
            * person("is_tax_unit_dependent", period)
        )
        medical_expenses = filer_medical_expenses + dependent_premiums
        return max_(
            add(tax_unit, period, p.income_sources)
            - excluded_premiums
            - medical_expenses,
            0,
        )

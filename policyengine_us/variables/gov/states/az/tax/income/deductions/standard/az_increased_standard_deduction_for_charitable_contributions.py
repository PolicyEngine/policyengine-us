from policyengine_us.model_api import *


class az_increased_standard_deduction_for_charitable_contributions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arizona increased standard deduction for charitable contributions"
    unit = USD
    reference = (
        "https://www.azleg.gov/viewdocument/?docName=https://www.azleg.gov/ars/43/01041.htm",
        # 2020 Form 140 booklet, Standard Deduction Increase for Charitable
        # Contributions worksheet, Note 1 and line 5C.
        "https://azdor.gov/sites/default/files/2023-03/FORMS_INDIVIDUAL_2020_140BOOKLET.pdf#page=25",
    )
    definition_period = YEAR
    defined_for = StateCode.AZ

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.az.tax.income.deductions.standard.increased
        charitable_deduction = tax_unit("charitable_deduction", period)
        charitable_contributions_credit = tax_unit(
            "az_charitable_contributions_credit_potential", period
        )
        # 2020 worksheet line 5C: contributions already deducted on the
        # federal return by a filer who did not itemize (line 10b).
        federal_non_itemizer_deduction = tax_unit(
            "charitable_contributions_ald", period
        )
        charitable_deduction_after_credit = max_(
            charitable_deduction
            - federal_non_itemizer_deduction
            - charitable_contributions_credit,
            0,
        )
        # Through TY2025, the add-on is a share of charitable contributions
        # (the rate). From TY2026 (HB 4168), the rate is zero and the add-on
        # becomes the full IRC 170(c) charitable contribution amount, capped
        # by filing status. The two regimes do not overlap.
        rate_based_amount = p.rate * charitable_deduction_after_credit
        filing_status = tax_unit("az_filing_status", period)
        capped_full_amount = min_(
            charitable_deduction_after_credit, p.cap[filing_status]
        )
        return rate_based_amount + capped_full_amount

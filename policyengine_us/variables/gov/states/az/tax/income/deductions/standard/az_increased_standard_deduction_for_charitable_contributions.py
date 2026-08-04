from policyengine_us.model_api import *


class az_increased_standard_deduction_for_charitable_contributions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arizona increased standard deduction for charitable contributions"
    unit = USD
    documentation = "https://www.azleg.gov/viewdocument/?docName=https://www.azleg.gov/ars/43/01041.htm"
    definition_period = YEAR
    defined_for = StateCode.AZ

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.az.tax.income.deductions.standard.increased
        charitable_deduction = tax_unit("charitable_deduction", period)
        charitable_contributions_credit = tax_unit(
            "az_charitable_contributions_credit_potential", period
        )
        charitable_deduction_after_credit = max_(
            charitable_deduction - charitable_contributions_credit, 0
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

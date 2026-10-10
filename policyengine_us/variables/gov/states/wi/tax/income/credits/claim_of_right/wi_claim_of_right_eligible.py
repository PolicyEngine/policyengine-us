from policyengine_us.model_api import *


class wi_claim_of_right_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Claim of right repayment qualifies for Wisconsin relief"
    documentation = (
        "Whether the repayment of claim of right income on the return "
        "exceeds the Wisconsin threshold, so that the filer may take the "
        "claim of right credit or subtract the repayment from income."
    )
    definition_period = YEAR
    reference = (
        "https://docs.legis.wisconsin.gov/statutes/statutes/71/i/07/1",
        # 2025 Form 1 instructions, line 32
        "https://www.revenue.wi.gov/TaxForms2025/2025-Form1-Inst.pdf#page=27",
        # 2025 Schedule SB instructions, line 28
        "https://www.revenue.wi.gov/TaxForms2025/2025-ScheduleSB-Inst.pdf#page=11",
    )
    defined_for = StateCode.WI

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.wi.tax.income.credits.claim_of_right
        repayment = tax_unit("tax_unit_claim_of_right_repayment", period)
        return repayment > p.threshold

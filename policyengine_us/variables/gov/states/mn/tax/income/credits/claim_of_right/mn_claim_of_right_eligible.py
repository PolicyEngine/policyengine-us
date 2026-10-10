from policyengine_us.model_api import *


class mn_claim_of_right_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Claim of right repayment qualifies for the Minnesota computation"
    documentation = (
        "Whether the repayment of claim of right income on the return exceeds "
        "the Minnesota threshold, so that Minnesota tax is the lesser of the "
        "tax with a deduction for the repayment and the tax without it less "
        "the decrease in the earlier year's Minnesota tax (Minn. Stat. "
        "290.07, subdivision 4)."
    )
    definition_period = YEAR
    reference = (
        # Minn. Stat. 290.07, subdivision 4
        "https://www.revisor.mn.gov/statutes/cite/290.07",
        # Minn. R. 8007.0300
        "https://www.revisor.mn.gov/rules/8007.0300/",
        # 2025 Schedule M1REF, line 11
        "https://www.revenue.state.mn.us/sites/default/files/2025-12/m1ref-25.pdf#page=3",
    )
    defined_for = StateCode.MN

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.mn.tax.income.credits.claim_of_right
        repayment = tax_unit("tax_unit_claim_of_right_repayment", period)
        return repayment > p.threshold

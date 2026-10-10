from policyengine_us.model_api import *


class wi_claim_of_right_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Wisconsin subtraction for repayment of income previously taxed"
    unit = USD
    documentation = (
        "Repayment of more than the threshold of income included in an "
        "earlier year under a claim of right, subtracted from income when "
        "the filer does not take the claim of right credit for it (Wis. "
        "Stat. 71.05(6)(b)29; Schedule SB, line 28). A filer who does not "
        "itemize federally uses the amount that would be deductible on "
        "federal Schedule A. The model treats the whole repayment "
        "(claim_of_right_repayment) as previously included in Wisconsin "
        "adjusted gross income. Not modeled: a repayment of the threshold "
        "amount or less, a federal miscellaneous itemized deduction subject "
        "to the two percent floor, which Wisconsin's 2018 to 2025 "
        "instructions do not allow."
    )
    definition_period = YEAR
    reference = (
        "https://docs.legis.wisconsin.gov/statutes/statutes/71/i/05/6/b/29",
        # 2025 Schedule SB instructions, line 28
        "https://www.revenue.wi.gov/TaxForms2025/2025-ScheduleSB-Inst.pdf#page=11",
    )
    defined_for = StateCode.WI

    def formula(tax_unit, period, parameters):
        eligible = tax_unit("wi_claim_of_right_eligible", period)
        credit_applies = tax_unit("wi_claim_of_right_credit_applies", period)
        repayment = tax_unit("tax_unit_claim_of_right_repayment", period)
        return where(eligible & ~credit_applies, repayment, 0)

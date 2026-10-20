from policyengine_us.model_api import *


class hi_claim_of_right_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Hawaii claim of right repayment itemized deduction"
    unit = USD
    documentation = (
        "Hawaii itemized deduction for repaying income Hawaii taxed in an "
        "earlier year under a claim of right. When section 1341 applies in "
        "Hawaii (from 2022, repayments over the threshold), the whole "
        "repayment is deducted outside the two percent floor (section "
        "67(b)(9)) unless Hawaii tax is computed with the claim of right "
        "credit. Otherwise the repayment is a miscellaneous itemized "
        "deduction above two percent of Hawaii adjusted gross income while "
        "Hawaii allows those (through 2025). Other miscellaneous expenses "
        "are not modeled, so the floor applies to the repayment alone."
    )
    definition_period = YEAR
    reference = (
        "https://data.capitol.hawaii.gov/sessions/sessionlaws/Years/SLH2023/SLH2023_Act56.pdf#page=3",
        "https://www.law.cornell.edu/uscode/text/26/67#b_9",
        "https://files.hawaii.gov/tax/legal/hrs/hrs_235.pdf#page=11",
        # 2018 Form N-11 instructions: "Repayments under a claim of right over
        # $3,000 are subject to the 2% limitation for Hawaii income tax
        # purposes." (section 1341 not operative)
        "https://files.hawaii.gov/tax/forms/2018/n11ins.pdf#page=21",
        # 2025 Form N-11 instructions, Worksheet A-6, lines 26-29
        "https://files.hawaii.gov/tax/forms/2025/n11ins.pdf#page=34",
    )
    defined_for = StateCode.HI

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.hi.tax.income.deductions.itemized
        repayment = tax_unit("hi_claim_of_right_repayment", period)
        eligible = tax_unit("hi_claim_of_right_section_1341_eligible", period)
        credit_applies = tax_unit("hi_claim_of_right_credit_applies", period)
        section_1341_deduction = where(credit_applies, 0, repayment)
        if p.miscellaneous_deductions_allowed:
            floor = parameters(period).gov.irs.deductions.itemized.misc.floor * max_(
                tax_unit("hi_agi", period), 0
            )
            miscellaneous_deduction = max_(repayment - floor, 0)
        else:
            miscellaneous_deduction = 0
        return where(eligible, section_1341_deduction, miscellaneous_deduction)

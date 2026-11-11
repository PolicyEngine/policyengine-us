from policyengine_us.model_api import *


class hi_claim_of_right_section_1341_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Hawaii claim of right repayment qualifies for section 1341"
    documentation = (
        "Whether section 1341 is operative in Hawaii for the year and the "
        "repayment of income Hawaii taxed exceeds the section 1341(a)(3) "
        "threshold, so that Hawaii tax is the lesser of the tax with a "
        "deduction for the repayment and the tax without it less the "
        "decrease in prior-year Hawaii tax."
    )
    definition_period = YEAR
    reference = (
        "https://data.capitol.hawaii.gov/sessions/sessionlaws/Years/SLH2023/SLH2023_Act56.pdf#page=3",
        "https://files.hawaii.gov/tax/forms/2025/n364_i.pdf",
    )
    defined_for = StateCode.HI

    def formula(tax_unit, period, parameters):
        operative = parameters(
            period
        ).gov.states.hi.tax.income.claim_of_right.section_1341_operative
        threshold = parameters(
            period
        ).gov.irs.deductions.itemized.claim_of_right.threshold
        repayment = tax_unit("hi_claim_of_right_repayment", period)
        return operative & (repayment > threshold)

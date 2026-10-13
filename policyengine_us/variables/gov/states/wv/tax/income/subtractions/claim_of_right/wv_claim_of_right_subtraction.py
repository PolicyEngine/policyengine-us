from policyengine_us.model_api import *


class wv_claim_of_right_subtraction(Variable):
    value_type = float
    entity = Person
    label = "West Virginia IRC 1341 repayments modification"
    unit = USD
    documentation = (
        "West Virginia decreasing modification for repaying income received "
        "in an earlier year under a claim of right (Schedule M, IRC 1341 "
        "Repayments). The amount repaid must be more than $3,000, which the "
        "model applies to the return's total as section 1341 does. Schedule M "
        "has a column for each spouse; the model puts each spouse's own "
        "repayment in their column. The instructions do not depend on the "
        "federal method."
    )
    definition_period = YEAR
    reference = (
        # 2025 IT-140 instructions, Schedule M line 42
        "https://tax.wv.gov/Documents/PIT/2025/it140.PersonalIncomeTaxFormsAndInstructions.2025.pdf#page=29",
        # 2021 IT-140 instructions, Schedule M line 40
        "https://tax.wv.gov/Documents/TaxForms/2021/it140.booklet.pdf#page=24",
        # 2017 IT-140 instructions, Schedule M line 50
        "https://tax.wv.gov/Documents/TaxForms/2017/it140.booklet.pdf#page=23",
    )
    defined_for = StateCode.WV

    def formula(person, period, parameters):
        eligible = person.tax_unit("claim_of_right_section_1341_eligible", period)
        repayment = person("claim_of_right_repayment", period)
        # Dependents' repayments belong on their own returns.
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        return where(eligible & head_or_spouse, repayment, 0)

from policyengine_us.model_api import *


class mt_claim_of_right_deduction(Variable):
    value_type = float
    entity = Person
    label = "Montana claim of right repayment deduction"
    unit = USD
    documentation = (
        "The person's part of the federal claim of right repayment deduction "
        "(Schedule A, line 16), which Montana allowed as an itemized "
        "deduction through 2023 (Form 2 itemized deductions, line 18)."
    )
    definition_period = YEAR
    reference = "https://revenue.mt.gov/files/forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2023_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=39"
    defined_for = StateCode.MT

    def formula(person, period, parameters):
        # The federal deduction is the head's and spouse's repayments when
        # federal tax is computed with the deduction, and zero otherwise.
        deducted = person.tax_unit("claim_of_right_deduction", period) > 0
        repayment = person("claim_of_right_repayment", period)
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        return deducted * head_or_spouse * repayment

from policyengine_us.model_api import *


class mt_itemized_deductions_indiv(Variable):
    value_type = float
    entity = Person
    label = "Montana itemized deductions when married couples are filing separately"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://mtrevenue.gov/wp-content/uploads/dlm_uploads/2023/05/Montana-Idividiual-Income-Tax-Return-Form-2-2022v6.2.pdf#page=7"
        "https://law.justia.com/codes/montana/2022/title-15/chapter-30/part-21/section-15-30-2131/"
        # MT Code § 15-30-2131 (2022) (1)
    )
    defined_for = StateCode.MT

    def formula(person, period, parameters):
        p = parameters(period).gov.irs.deductions
        itm_deds = [
            deduction
            for deduction in p.itemized_deductions
            if deduction
            not in [
                "salt_deduction",
                "casualty_loss_deduction",
                "medical_expense_deduction",
            ]
        ]
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        return head_or_spouse * add(
            person,
            period,
            itm_deds
            + [
                "mt_misc_deductions",
                "mt_medical_expense_deduction_indiv",
                "mt_salt_deduction",
                "mt_federal_income_tax_deduction",
            ],
        )

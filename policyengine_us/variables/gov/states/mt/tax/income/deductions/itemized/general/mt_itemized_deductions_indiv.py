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
        # Since we only compute the federal charitable deduction at the tax unit level,
        # we will split the value between each spouse
        charitable_deduction = (
            person.tax_unit("charitable_deduction", period) * 0.5
        )
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        # The interest deduction is the sum of mortagage and investment interest expenses
        investment_interest = person("investment_interest_expense", period)
        mortgage_interest = person("mortgage_interest", period)
        interest_ded = investment_interest + mortgage_interest
        other_deductions = add(
            person,
            period,
            [
                "mt_misc_deductions",
                "mt_medical_expense_deduction_indiv",
                "mt_salt_deduction",
                "mt_federal_income_tax_deduction_indiv",
            ],
        )
        return head_or_spouse * (
            interest_ded + charitable_deduction + other_deductions
        )

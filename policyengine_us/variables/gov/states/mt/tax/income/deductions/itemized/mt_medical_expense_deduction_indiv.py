from policyengine_us.model_api import *


class mt_medical_expense_deduction_indiv(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = "Montana medical expense deduction when married couples are filing separately"
    reference = (
        "https://mtrevenue.gov/wp-content/uploads/dlm_uploads/2023/05/Montana-Idividiual-Income-Tax-Return-Form-2-2022v6.2.pdf#page=7",
        "https://law.justia.com/codes/montana/2022/title-15/chapter-30/part-21/section-15-30-2131/",
        # MT Code § 15-30-2131 (2022) (1)(g)(i)
    )
    unit = USD
    defined_for = StateCode.MT

    def formula(person, period, parameters):
        expense = person("medical_expense", period)
        p = parameters(period).gov.irs.deductions.itemized.medical
        # Law does not define Montana AGI as the cap.
        # Tax form points to page 1, line 14, which is Montana AGI.
        medical_floor = p.floor * person("mt_agi", period)
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        return is_head_or_spouse * max_(0, expense - medical_floor)

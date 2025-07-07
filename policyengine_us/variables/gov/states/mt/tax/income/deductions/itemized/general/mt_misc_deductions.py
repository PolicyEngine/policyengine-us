from policyengine_us.model_api import *


class mt_misc_deductions(Variable):
    value_type = float
    entity = Person
    label = "Montana miscellaneous deductions"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://mtrevenue.gov/wp-content/uploads/dlm_uploads/2023/05/Montana-Idividiual-Income-Tax-Return-Form-2-2022v6.2.pdf#page=7"
        "https://law.justia.com/codes/montana/2022/title-15/chapter-30/part-21/section-15-30-2131/"
        # Montana Code Annotated MT Code § 15-30-2131 (2022) (1)(a)&(c)
    )
    defined_for = StateCode.MT

    adds = "gov.states.mt.tax.income.deductions.itemized.misc_deductions"

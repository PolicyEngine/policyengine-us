from policyengine_us.model_api import *


class mt_misc_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Montana miscellaneous deduction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://mtrevenue.gov/wp-content/uploads/dlm_uploads/2023/05/Montana-Idividiual-Income-Tax-Return-Form-2-2022v6.2.pdf#page=7"
        "https://leg.mt.gov/bills/mca/title_0150/chapter_0300/part_0210/section_0310/0150-0300-0210-0310.html"
        # Montana Code Annotated 2021 15-30-2131 
    )
    defined_for = StateCode.MT

    adds = "gov.states.mt.tax.income.deductions.itemized.misc_deduction"

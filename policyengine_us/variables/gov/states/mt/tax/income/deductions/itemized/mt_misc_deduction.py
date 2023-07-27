from policyengine_us.model_api import *


class mt_misc_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Montana Miscellaneous Deduction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://mtrevenue.gov/wp-content/uploads/dlm_uploads/2023/05/Montana-Idividiual-Income-Tax-Return-Form-2-2022v6.2.pdf"
        "https://leg.mt.gov/bills/mca/title_0150/chapter_0300/part_0210/section_0310/0150-0300-0210-0310.html"
    )
    defined_for = StateCode.MT

    adds = ["tax_unit_childcare_expenses", "casualty_loss_deduction"]
    # political contribution
    # gambling
    # other

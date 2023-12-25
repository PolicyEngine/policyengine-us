from policyengine_us.model_api import *


class oh_unreimbursed_long_term_care_premiums(Variable):
    value_type = float
    entity = Person
    label = "Ohio Unreimbursed Medical and Health Care Expense Deduction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://tax.ohio.gov/static/forms/ohio_individual/individual/2022/it1040-sd100-instruction-booklet.pdf#page=18",  # Line 36
        "https://tax.ohio.gov/static/forms/ohio_individual/individual/2022/it1040-sd100-instruction-booklet.pdf#page=27",
        "https://codes.ohio.gov/ohio-revised-code/section-5747.01",  # R.C. 5747.01(10)
    )
    defined_for = StateCode.OH

    adds = ["long_term_care_insurance_premiums"]

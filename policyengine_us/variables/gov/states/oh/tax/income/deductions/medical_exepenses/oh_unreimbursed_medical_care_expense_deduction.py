from policyengine_us.model_api import *


class oh_unreimbursed_medical_care_expense_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Ohio unreimbursed medical and health care expense deduction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://tax.ohio.gov/static/forms/ohio_individual/individual/2022/it1040-sd100-instruction-booklet.pdf#page=18",  # Line 36
        "https://tax.ohio.gov/static/forms/ohio_individual/individual/2022/it1040-sd100-instruction-booklet.pdf#page=27",
        "https://codes.ohio.gov/ohio-revised-code/section-5747.01",  # R.C. 5747.01(10)
    )
    defined_for = StateCode.OH

    adds = ["oh_unreimbursed_medical_care_expense_deduction_person"]

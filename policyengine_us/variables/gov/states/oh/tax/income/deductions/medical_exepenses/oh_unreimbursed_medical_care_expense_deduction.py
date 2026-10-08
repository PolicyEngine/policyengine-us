from policyengine_us.model_api import *


class oh_unreimbursed_medical_care_expense_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Ohio unreimbursed medical and health care expense deduction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://codes.ohio.gov/ohio-revised-code/section-5747.01",  # R.C. 5747.01(A)(10)
        "https://dam.assets.ohio.gov/image/upload/v1767095693/tax.ohio.gov/forms/ohio_individual/individual/2025/it1040-booklet.pdf#page=25",  # Line 44
        "https://dam.assets.ohio.gov/image/upload/v1767095693/tax.ohio.gov/forms/ohio_individual/individual/2025/it1040-booklet.pdf#page=41",  # Worksheet
    )
    defined_for = StateCode.OH

    adds = ["oh_unreimbursed_medical_care_expense_deduction_person"]

from policyengine_us.model_api import *


class oh_unreimbursed_medical_care_expense_deduction_person(Variable):
    value_type = float
    entity = Person
    label = "Ohio unreimbursed medical and health care expense deduction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://dam.assets.ohio.gov/image/upload/tax.ohio.gov/forms/ohio_individual/individual/2022/it1040-sd100-instruction-booklet.pdf#page=18",  # Line 36
        "https://dam.assets.ohio.gov/image/upload/v1767095693/tax.ohio.gov/forms/ohio_individual/individual/2025/it1040-booklet.pdf#page=41",  # Worksheet
        "https://codes.ohio.gov/ohio-revised-code/section-5747.01",  # R.C. 5747.01(A)(10)
    )
    defined_for = StateCode.OH

    # The worksheet computes line 8 once for the return. Each person takes
    # their share of it, so the shares sum to the return's amount. Listing
    # the tax unit amount here would give every member the full amount.
    adds = [
        "oh_insured_unreimbursed_medical_care_expenses_person",
        "oh_uninsured_unreimbursed_medical_care_expenses",
        "long_term_health_insurance_premiums",
    ]

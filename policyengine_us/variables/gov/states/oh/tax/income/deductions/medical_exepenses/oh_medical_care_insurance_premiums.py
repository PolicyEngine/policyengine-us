from policyengine_us.model_api import *


class oh_medical_care_insurance_premiums(Variable):
    value_type = float
    entity = Person
    label = "Ohio medical care insurance premiums for the unreimbursed medical care deduction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://codes.ohio.gov/ohio-revised-code/section-5747.01",  # R.C. 5747.01(A)(10)(a)-(b)
        "https://dam.assets.ohio.gov/image/upload/v1767095693/tax.ohio.gov/forms/ohio_individual/individual/2025/it1040-booklet.pdf#page=25",  # Line 44, pp. 25-26
        "https://dam.assets.ohio.gov/image/upload/v1767095693/tax.ohio.gov/forms/ohio_individual/individual/2025/it1040-booklet.pdf#page=41",  # Worksheet lines 1 and 3
    )
    defined_for = StateCode.OH

    def formula(person, period, parameters):
        # Premiums counted as IRC 213 medical care, as in the federal medical
        # expense deduction. Premiums paid through pre-tax payroll deductions
        # are a separate input, excluded from wages, so they are not included.
        premiums = person("medical_expense_health_insurance_premiums", period)
        # Premiums already deducted in computing federal AGI are not deducted
        # again (worksheet line 1 note).
        self_employed_deduction = person(
            "self_employed_health_insurance_ald_person", period
        )
        return max_(premiums - self_employed_deduction, 0)

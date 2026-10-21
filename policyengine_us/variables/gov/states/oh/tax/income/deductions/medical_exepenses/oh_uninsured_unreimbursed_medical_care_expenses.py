from policyengine_us.model_api import *


class oh_uninsured_unreimbursed_medical_care_expenses(Variable):
    value_type = float
    entity = Person
    label = "Ohio unreimbursed medical and health care expense deduction for uninsured expenses"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://codes.ohio.gov/ohio-revised-code/section-5747.01",  # R.C. 5747.01(A)(10)(a)
        "https://dam.assets.ohio.gov/image/upload/v1767095693/tax.ohio.gov/forms/ohio_individual/individual/2025/it1040-booklet.pdf#page=25",  # Line 44, pp. 25-26
        "https://dam.assets.ohio.gov/image/upload/v1767095693/tax.ohio.gov/forms/ohio_individual/individual/2025/it1040-booklet.pdf#page=41",  # Worksheet line 1
    )
    defined_for = StateCode.OH

    def formula(person, period, parameters):
        premiums = person("oh_medical_care_insurance_premiums", period)
        medicare_eligible = person("is_medicare_eligible", period)
        employer_plan_eligible = person.tax_unit(
            "oh_employer_subsidized_health_plan_eligible", period
        )
        # Line 1: premiums paid while eligible for neither Medicare nor an
        # employer-paid plan. Otherwise they go on line 3.
        return premiums * ~(medicare_eligible | employer_plan_eligible)

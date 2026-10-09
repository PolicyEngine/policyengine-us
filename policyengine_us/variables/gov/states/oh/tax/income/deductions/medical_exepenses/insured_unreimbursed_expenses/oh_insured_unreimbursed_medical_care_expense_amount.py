from policyengine_us.model_api import *


class oh_insured_unreimbursed_medical_care_expense_amount(Variable):
    value_type = float
    entity = Person
    label = "Ohio insured unreimbursed medical and health care expense amount"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://codes.ohio.gov/ohio-revised-code/section-5747.01",  # R.C. 5747.01(A)(10)(b)
        "https://dam.assets.ohio.gov/image/upload/v1767095693/tax.ohio.gov/forms/ohio_individual/individual/2025/it1040-booklet.pdf#page=25",  # Line 44, pp. 25-26
        "https://dam.assets.ohio.gov/image/upload/v1767095693/tax.ohio.gov/forms/ohio_individual/individual/2025/it1040-booklet.pdf#page=41",  # Worksheet lines 3 and 4
        "https://tax.ohio.gov/help-center/faqs/income-medical-and-health-care-expenses/income-medical-and-health-care-expenses",  # Q8 and Q9: after-tax premiums go on line 3
    )
    defined_for = StateCode.OH

    def formula(person, period, parameters):
        premiums = person("oh_medical_care_insurance_premiums", period)
        medicare_eligible = person("is_medicare_eligible", period)
        employer_plan_eligible = person.tax_unit(
            "oh_employer_subsidized_health_plan_eligible", period
        )
        # Line 3: premiums paid while eligible for Medicare or an
        # employer-paid plan.
        eligible_premiums = premiums * (medicare_eligible | employer_plan_eligible)
        # Line 4
        other_medical_expenses = person("other_medical_expenses", period)
        return eligible_premiums + other_medical_expenses

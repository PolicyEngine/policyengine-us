from policyengine_us.model_api import *


class oh_insured_unreimbursed_medical_care_expenses_person(Variable):
    value_type = float
    entity = Person
    label = "Ohio insured unreimbursed medical and health care expense deduction for each person"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://tax.ohio.gov/static/forms/ohio_individual/individual/2022/it1040-sd100-instruction-booklet.pdf#page=18",  # Line 36
        "https://tax.ohio.gov/static/forms/ohio_individual/individual/2022/it1040-sd100-instruction-booklet.pdf#page=27",
        "https://codes.ohio.gov/ohio-revised-code/section-5747.01",  # R.C. 5747.01(10)
    )
    defined_for = StateCode.OH

    def formula(person, period, parameters):
        # Prorating the deduction for each person based on the medical expenses
        # and the deduction amount
        medical_expenses = person(
            "oh_insured_unreimbursed_medical_care_expense_amount", period
        )
        total_expenses = person.tax_unit.sum(medical_expenses)
        total_deduction_amount = person.tax_unit(
            "oh_insured_unreimbursed_medical_care_expenses", period
        )

        expense_rate = np.zeros_like(total_expenses)
        mask = total_expenses != 0
        expense_rate[mask] = medical_expenses[mask] / total_expenses[mask]
        return expense_rate * total_deduction_amount

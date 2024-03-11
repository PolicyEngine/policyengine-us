from policyengine_us.model_api import *


class oh_insured_unreimbursed_medical_care_expense_amount(Variable):
    value_type = float
    entity = Person
    label = "Ohio insured unreimbursed medical and health care expense amount"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://tax.ohio.gov/static/forms/ohio_individual/individual/2022/it1040-sd100-instruction-booklet.pdf#page=18",  # Line 36
        "https://tax.ohio.gov/static/forms/ohio_individual/individual/2022/it1040-sd100-instruction-booklet.pdf#page=27",
        "https://codes.ohio.gov/ohio-revised-code/section-5747.01",  # R.C. 5747.01(10)
    )
    defined_for = StateCode.OH

    def formula(person, period, parameters):
        employer_premium_contribution = person(
            "employer_contribution_to_health_insurance_premiums_category",
            period,
        )
        status = employer_premium_contribution.possible_values
        medicare_eligible = person("is_medicare_eligible", period)
        # Line 3
        eligible_premiums = (
            person("health_insurance_premiums", period) * medicare_eligible
        ) * (employer_premium_contribution == status.NONE)
        # Premiums only count if the employer paid none.
        # Line 4
        medical_out_of_pocket_expenses = person(
            "medical_out_of_pocket_expenses", period
        )
        return eligible_premiums + medical_out_of_pocket_expenses
